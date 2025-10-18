import json
import os
import random
import string
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from spots.models import Spot, Tag


# プロバイダー設定
AI_PROVIDER = os.environ.get("AI_PROVIDER", "lmstudio").lower()

if AI_PROVIDER == "openrouter":
    DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL = os.environ.get("OPENROUTER_RECOMMENDATION_MODEL", "x-ai/grok-4-fast:free")
    API_KEY_ENV = "OPENROUTER_API_KEY"
else:  # LM Studio を利用する場合
    DEFAULT_BASE_URL = os.environ.get("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
    DEFAULT_MODEL = os.environ.get("LMSTUDIO_MODEL", "qwen/qwen3-4b-2507")
    API_KEY_ENV = "LMSTUDIO_API_KEY"


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]


def _rand_password(length: int = 16) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def _download_image(url: str) -> Optional[bytes]:
    try:
        resp = requests.get(url, timeout=15)
        if resp.ok:
            return resp.content
    except Exception:
        pass
    return None


def _ensure_user(username: str) -> Any:
    User = get_user_model()
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password(_rand_password())
        user.email = f"{username}@example.invalid"
        user.save()
    return user


def _tool_schema() -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "create_spot",
                "description": "Create a travel spot in the database. Use one call per spot.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Spot name (Japanese)"},
                        "description": {
                            "type": "string",
                            "description": "Short travel description in Japanese (40-120 chars)",
                        },
                        "latitude": {
                            "type": "number",
                            "description": "Latitude in decimal degrees",
                            "minimum": -90,
                            "maximum": 90,
                        },
                        "longitude": {
                            "type": "number",
                            "description": "Longitude in decimal degrees",
                            "minimum": -180,
                            "maximum": 180,
                        },
                        "address": {
                            "type": "string",
                            "description": "Readable address in Japanese",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Topic tags like '絶景', 'カフェ'. Must include 'AI' tag.",
                        },
                        "image_url": {
                            "type": "string",
                            "description": "Optional image URL to download and attach",
                        },
                    },
                    "required": ["title", "description", "latitude", "longitude"],
                    "additionalProperties": False,
                },
            },
        }
    ]


def _create_spot_in_db(user, payload: Dict[str, Any]) -> Dict[str, Any]:
    title = payload.get("title", "").strip()
    description = payload.get("description", "").strip()
    latitude = float(payload.get("latitude"))
    longitude = float(payload.get("longitude"))
    address = (payload.get("address") or "").strip()
    tag_names = payload.get("tags") or []
    image_url = (payload.get("image_url") or "").strip()

    with transaction.atomic():
        # 同一作成者についてはタイトルと緯度経度が完全一致する重複登録を避ける
        spot = Spot.objects.filter(
            title=title, latitude=latitude, longitude=longitude, created_by=user
        ).first()
        if not spot:
            spot = Spot.objects.create(
                title=title,
                description=description or "",
                latitude=latitude,
                longitude=longitude,
                address=address,
                created_by=user,
                is_ai_generated=True,
            )

        # タグを登録
        attached = []
        for name in tag_names:
            name = (name or "").strip()
            if not name:
                continue
            tag, _ = Tag.objects.get_or_create(name=name)
            spot.tags.add(tag)
            attached.append(tag.name)

        # 画像URLが指定されていればダウンロードして保存
        if image_url and not spot.image:
            content = _download_image(image_url)
            if content:
                filename = image_url.split("/")[-1] or "image.jpg"
                spot.image.save(filename, ContentFile(content), save=True)

    return {
        "id": spot.id,
        "title": spot.title,
        "address": spot.address,
        "latitude": spot.latitude,
        "longitude": spot.longitude,
        "tags": attached,
    }


def _parse_tool_calls(resp_json: Dict[str, Any]) -> List[ToolCall]:
    tool_calls: List[ToolCall] = []
    try:
        message = resp_json["choices"][0]["message"]
        calls = message.get("tool_calls") or []
        for c in calls:
            fn = c.get("function", {})
            args_raw = fn.get("arguments") or "{}"
            try:
                args = json.loads(args_raw)
            except Exception:
                # モデルによっては厳密でないJSONを返す場合があるため、フォールバックを試す
                args = json.loads(args_raw.replace("\n", " "))
            tool_calls.append(
                ToolCall(
                    id=c.get("id") or "",
                    name=fn.get("name") or "",
                    arguments=args,
                )
            )
    except Exception:
        pass
    return tool_calls


def _preflight_server(base_url: str, model: str, api_key: str) -> None:
    models_endpoint = f"{base_url}/models"
    headers = {"Authorization": f"Bearer {api_key}"} if api_key != "no-key" else {}
    try:
        r = requests.get(models_endpoint, headers=headers, timeout=8)
    except requests.exceptions.RequestException as e:
        if AI_PROVIDER == "openrouter":
            raise CommandError(
                "OpenRouter に接続できませんでした。\n"
                f"- ベースURL: {models_endpoint}\n"
                "- OPENROUTER_API_KEY が正しく設定されているか確認してください。\n"
                f"詳細: {e}"
            ) from e
        else:
            raise CommandError(
                "LM Studio に接続できませんでした。\n"
                f"- ベースURL: {models_endpoint}\n"
                "- LM Studio の Local Server を起動し、OpenAI 互換APIを有効化してください。\n"
                "- 例: LM Studio の Local Server ポートを 1234 に設定し、/v1 を有効化\n"
                "- 別ポートの場合は環境変数 LMSTUDIO_BASE_URL を変更してください\n"
                f"詳細: {e}"
            ) from e

    if not r.ok:
        raise CommandError(
            f"{AI_PROVIDER.upper()} /models 応答が不正です: HTTP {r.status_code} - {r.text[:200]}"
        )
    try:
        data = r.json()
    except Exception as e:
        raise CommandError(f"/models のJSON解析に失敗しました: {e}") from e

    ids = []
    for item in (data.get("data") or []):
        mid = item.get("id") or item.get("name")
        if mid:
            ids.append(str(mid))

    if model not in ids:
        preview = ", ".join(ids[:10]) or "(なし)"
        if AI_PROVIDER == "openrouter":
            raise CommandError(
                "指定したモデルが OpenRouter 側で見つかりません。\n"
                f"- 指定モデル: {model}\n"
                f"- 利用可能: {preview}\n"
                "OPENROUTER_RECOMMENDATION_MODEL を確認してください。"
            )
        else:
            raise CommandError(
                "指定したモデルが LM Studio 側で見つかりません。\n"
                f"- 指定モデル: {model}\n"
                f"- 利用可能: {preview}\n"
                "LM Studio で当該モデルをダウンロード・ロードしてから再実行してください。\n"
                "モデルIDは Local Server の /models に表示される文字列と一致させてください。"
            )


class Command(BaseCommand):
    help = "Generate Spot records using LM Studio or OpenRouter tool-calling model."

    def add_arguments(self, parser):
        # 位置引数として受け付けるのは count のみ
        parser.add_argument(
            "count",
            type=int,
            help="Number of spots to generate.",
        )

    def handle(self, *args, **options):
        count = int(options["count"]) if options.get("count") is not None else 0
        # デフォルト値: ユーザーが求める最小限のみ設定し、テーマは内部で簡潔に保持
        theme = "日本国内のおすすめ観光スポット"
        username = "ai"
        model = DEFAULT_MODEL
        base_url = DEFAULT_BASE_URL.rstrip("/")
        api_key = os.environ.get(API_KEY_ENV, "no-key")
        max_rounds = 6

        if count <= 0:
            raise CommandError("count must be >= 1")
        if not model:
            raise CommandError("Model name is empty. Set the appropriate model env var.")

        user = _ensure_user(username)

        # 事前確認: サーバーに接続でき、指定モデルが利用可能か検証
        _preflight_server(base_url, model, api_key)

        chat_endpoint = f"{base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        system_prompt = (
            "あなたは旅行スポット登録の自動化アシスタントです。\n"
            "出力は必ずツール呼び出し（create_spot）だけを使って行います。\n"
            "各スポットは以下を満たしてください:\n"
            "- 日本語のタイトル\n"
            "- 40〜120文字程度の説明（日本語）\n"
            "- 妥当な緯度経度 (十進法)\n"
            "- 可能なら住所（日本語）\n"
            "- 関連タグ 0〜5個\n"
            "今回のテーマ: "
            + theme
            + "\n"
            + f"合計で{count}件のスポットを、1スポットにつき1回のツール呼び出しで登録してください。\n"
            "追加のテキストは出力せず、必要な回数だけ create_spot を呼び出してください。"
        )

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    "はじめてください。create_spot を合計回数分だけ呼び出してください。"
                ),
            },
        ]

        created = 0
        round_idx = 0
        self.stdout.write(self.style.NOTICE(
            f"Requesting {AI_PROVIDER.upper()} model '{model}' at {base_url} to create {count} spot(s)..."
        ))

        while created < count and round_idx < max_rounds:
            round_idx += 1
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.5,
                "tools": _tool_schema(),
                "tool_choice": "auto",
            }

            try:
                resp = requests.post(
                    chat_endpoint, headers=headers, json=payload, timeout=120
                )
            except requests.exceptions.RequestException as e:
                if AI_PROVIDER == "openrouter":
                    raise CommandError(
                        "OpenRouter へのリクエストに失敗しました。\n"
                        f"- エンドポイント: {chat_endpoint}\n"
                        "- OPENROUTER_API_KEY が正しく設定されているか確認してください。\n"
                        f"詳細: {e}"
                    ) from e
                else:
                    raise CommandError(
                        "LM Studio へのリクエストに失敗しました。\n"
                        f"- エンドポイント: {chat_endpoint}\n"
                        "- Local Server が起動し、指定モデルがロード済みか確認してください。\n"
                        f"詳細: {e}"
                    ) from e
            if not resp.ok:
                raise CommandError(f"LM Studio error: HTTP {resp.status_code} - {resp.text[:200]}")

            data = resp.json()
            tool_calls = _parse_tool_calls(data)

            if not tool_calls:
                # ツール呼び出しが生成されなかった場合は追加指示で再試行
                messages.append({
                    "role": "user",
                    "content": (
                        "ツール呼び出しがありません。create_spot のツールだけを使って続行してください。"
                    ),
                })
                continue

            # 会話の整合性を保つため、tool_calls を含むアシスタント側メッセージを記録
            messages.append(data["choices"][0]["message"])  # tool_calls を含むアシスタントメッセージ

            # このアシスタントメッセージ内のツール呼び出しを順に実行
            for tc in tool_calls:
                if created >= count:
                    break
                if tc.name != "create_spot":
                    # 未知のツール名は無視してエラー応答を返す
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": tc.name,
                        "content": json.dumps({"error": "unknown tool"}, ensure_ascii=False),
                    })
                    continue

                try:
                    result = _create_spot_in_db(user, tc.arguments)
                    created += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"[{created}/{count}] Created spot: {result.get('title')}"
                    ))
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": "create_spot",
                        "content": json.dumps({
                            "status": "ok",
                            "created": result,
                        }, ensure_ascii=False),
                    })
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to create spot: {e}"))
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": "create_spot",
                        "content": json.dumps({
                            "status": "error",
                            "message": str(e),
                        }, ensure_ascii=False),
                    })

        if created < count:
            raise CommandError(
                f"Requested {count} spot(s) but created {created}. Try increasing --max-rounds or adjusting your theme/model."
            )

        self.stdout.write(self.style.SUCCESS(
            f"Done. Created {created} spot(s) as user '{username}'."
        ))
