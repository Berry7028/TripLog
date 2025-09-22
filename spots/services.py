"""スポット関連APIのデータ取得ロジックをまとめたサービス群。"""

from __future__ import annotations

from typing import Any, Dict, List, MutableMapping, Optional

import requests
from django.conf import settings
from django.db.models import Q

from .models import Spot

DEFAULT_TIMEOUT = 5.0
DEFAULT_ENDPOINTS = {
    'search': '/api/search/',
    'list': '/api/spots/',
    'create': '/api/spots/add/',
}


class SpotServiceError(Exception):
    """スポットサービスで発生したエラーを表す例外。"""

    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


class BaseSpotService:
    """スポット情報を提供するサービスのベースクラス。"""

    def search_spots(self, *, query: str, request) -> List[Dict[str, Any]]:  # pragma: no cover - interface
        raise NotImplementedError

    def list_spots(self, *, request, filter_mode: str) -> List[Dict[str, Any]]:  # pragma: no cover - interface
        raise NotImplementedError

    def create_spot(self, *, request) -> Dict[str, Any]:  # pragma: no cover - interface
        raise NotImplementedError


class LocalSpotService(BaseSpotService):
    """DjangoのローカルDBを利用するサービス。"""

    def search_spots(self, *, query: str, request) -> List[Dict[str, Any]]:
        if not query:
            return []

        spots = Spot.objects.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(address__icontains=query)
            | Q(tags__name__icontains=query)
        ).distinct()[:10]

        return [
            {
                'id': spot.id,
                'title': spot.title,
                'address': spot.address,
                'latitude': spot.latitude,
                'longitude': spot.longitude,
            }
            for spot in spots
        ]

    def list_spots(self, *, request, filter_mode: str) -> List[Dict[str, Any]]:
        spots = Spot.objects.all().select_related('created_by')
        if request.user.is_authenticated and filter_mode in {'mine', 'others'}:
            if filter_mode == 'mine':
                spots = spots.filter(created_by=request.user)
            else:
                spots = spots.exclude(created_by=request.user)

        return [
            {
                'id': spot.id,
                'title': spot.title,
                'description': spot.description,
                'latitude': spot.latitude,
                'longitude': spot.longitude,
                'address': spot.address,
                'image': (spot.image.url if spot.image else (spot.image_url or None)),
                'created_by': spot.created_by.username,
                'created_at': spot.created_at.isoformat(),
                'tags': [tag.name for tag in spot.tags.all()],
            }
            for spot in spots
        ]

    def create_spot(self, *, request) -> Dict[str, Any]:
        title = (request.POST.get('title') or '').strip()
        description = (request.POST.get('description') or '').strip()
        latitude_raw = request.POST.get('latitude')
        longitude_raw = request.POST.get('longitude')
        address = request.POST.get('address', '')
        image = request.FILES.get('image')
        image_url = (request.POST.get('image_url') or '').strip()

        if not title or not description:
            raise SpotServiceError('タイトルと説明は必須です。')

        try:
            latitude = float(latitude_raw)
            longitude = float(longitude_raw)
        except (TypeError, ValueError):
            raise SpotServiceError('座標の形式が正しくありません。')

        spot = Spot.objects.create(
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            address=address,
            image=image,
            image_url=image_url or None,
            created_by=request.user,
        )

        return {
            'id': spot.id,
            'title': spot.title,
            'description': spot.description,
            'latitude': spot.latitude,
            'longitude': spot.longitude,
            'address': spot.address,
            'image': (spot.image.url if spot.image else (spot.image_url or None)),
            'created_by': spot.created_by.username,
            'created_at': spot.created_at.isoformat(),
        }


class ExternalSpotService(BaseSpotService):
    """外部のスポットAPIサービスを利用する実装。"""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Optional[MutableMapping[str, str]] = None,
        endpoints: Optional[Dict[str, str]] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not base_url:
            raise ValueError('base_url is required')

        self.base_url = base_url.rstrip('/')
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.headers = dict(headers or {})
        self.session = session or requests.Session()
        self.endpoints = DEFAULT_ENDPOINTS.copy()
        if endpoints:
            self.endpoints.update({key.lower(): value for key, value in endpoints.items()})

    def search_spots(self, *, query: str, request) -> List[Dict[str, Any]]:
        if not query:
            return []

        payload = self._request(
            'get',
            self._endpoint('search'),
            params={'q': query},
        )
        results = payload.get('results', [])
        if not isinstance(results, list):
            raise SpotServiceError('外部スポットAPIの検索結果形式が不正です。', status_code=502)
        return results

    def list_spots(self, *, request, filter_mode: str) -> List[Dict[str, Any]]:
        params = {}
        if filter_mode:
            params['filter'] = filter_mode

        payload = self._request('get', self._endpoint('list'), params=params)
        spots = payload.get('spots', [])
        if not isinstance(spots, list):
            raise SpotServiceError('外部スポットAPIのレスポンス形式が不正です。', status_code=502)
        return spots

    def create_spot(self, *, request) -> Dict[str, Any]:
        data = {
            'title': request.POST.get('title', ''),
            'description': request.POST.get('description', ''),
            'latitude': request.POST.get('latitude', ''),
            'longitude': request.POST.get('longitude', ''),
            'address': request.POST.get('address', ''),
            'image_url': request.POST.get('image_url', ''),
        }

        image = request.FILES.get('image')
        files = None
        if image:
            files = {'image': (image.name, image.file, getattr(image, 'content_type', 'application/octet-stream'))}

        payload = self._request('post', self._endpoint('create'), data=data, files=files)

        if payload.get('success') is False:
            raise SpotServiceError(payload.get('error') or '外部スポットAPIでスポット作成に失敗しました。', status_code=502)

        spot = payload.get('spot')
        if not isinstance(spot, dict):
            raise SpotServiceError('外部スポットAPIのレスポンス形式が不正です。', status_code=502)
        return spot

    def _endpoint(self, key: str) -> str:
        path = self.endpoints.get(key.lower()) or DEFAULT_ENDPOINTS[key.lower()]
        if not path.startswith('/'):
            path = '/' + path
        return f'{self.base_url}{path}'

    def _request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        headers = dict(self.headers)
        extra_headers = kwargs.pop('headers', None)
        if extra_headers:
            headers.update(extra_headers)

        try:
            response = self.session.request(method.upper(), url, headers=headers, timeout=self.timeout, **kwargs)
        except requests.RequestException as exc:
            raise SpotServiceError('外部スポットAPIへの接続に失敗しました。', status_code=502) from exc

        if response.status_code >= 400:
            try:
                error_detail = response.json().get('error')
            except Exception:  # noqa: BLE001 - JSON以外の場合も考慮
                error_detail = response.text
            message = error_detail or f'外部スポットAPIからエラーが返されました（status={response.status_code}）。'
            raise SpotServiceError(message, status_code=response.status_code)

        try:
            return response.json()
        except ValueError as exc:  # pragma: no cover - JSON以外のレスポンスは想定外だが保険として
            raise SpotServiceError('外部スポットAPIのレスポンスがJSONではありません。', status_code=502) from exc


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, str):
        return value.lower() in {'1', 'true', 't', 'yes', 'on'}
    return bool(value)


def _normalize_config(raw_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    config = {
        'use_external': False,
        'base_url': '',
        'timeout': DEFAULT_TIMEOUT,
        'headers': {},
        'endpoints': DEFAULT_ENDPOINTS.copy(),
    }
    if not raw_config:
        return config

    for key, value in raw_config.items():
        lower_key = key.lower()
        if lower_key in {'use_external', 'enabled'}:
            config['use_external'] = _to_bool(value)
        elif lower_key in {'base_url', 'baseurl'}:
            config['base_url'] = (value or '').rstrip('/')
        elif lower_key == 'timeout':
            try:
                config['timeout'] = float(value)
            except (TypeError, ValueError):
                config['timeout'] = DEFAULT_TIMEOUT
        elif lower_key == 'headers' and isinstance(value, dict):
            config['headers'] = value
        elif lower_key == 'endpoints' and isinstance(value, dict):
            config['endpoints'].update({k.lower(): v for k, v in value.items()})

    return config


def get_spot_service() -> BaseSpotService:
    """設定に基づいて利用すべきスポットサービスを返す。"""

    raw_config = getattr(settings, 'SPOT_API_CONFIG', None)
    config = _normalize_config(raw_config)

    if config['use_external'] and config['base_url']:
        return ExternalSpotService(
            config['base_url'],
            timeout=config['timeout'],
            headers=config['headers'],
            endpoints=config['endpoints'],
        )

    return LocalSpotService()
