#!/bin/bash

set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [ -x "$ROOT_DIR/venv/bin/python" ]; then
    PYTHON_CMD="$ROOT_DIR/venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="$(command -v python)"
else
    echo "❌ Pythonが見つからないためおすすめ解析ジョブを実行できません" >&2
    exit 1
fi

cd "$ROOT_DIR"

echo "🤖 ユーザー閲覧おすすめ解析ジョブを実行します..."
if [ $# -gt 0 ]; then
    echo "ℹ️  追加引数: $*"
fi

"$PYTHON_CMD" manage.py run_recommendation_jobs "$@"
