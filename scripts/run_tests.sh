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
    echo "❌ Pythonが見つからないためテストを実行できません" >&2
    exit 1
fi

cd "$ROOT_DIR"

echo "🚀 Djangoテストスイートを実行します..."
if [ $# -gt 0 ]; then
    echo "ℹ️  manage.py test に追加引数を渡します: $*"
fi

if ! "$PYTHON_CMD" manage.py test "$@"; then
    echo "❌ テストが失敗しました" >&2
    exit 1
fi
