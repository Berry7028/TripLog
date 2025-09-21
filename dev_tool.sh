set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEVHUB_SCRIPT="$ROOT_DIR/scripts/devhub/devhub.sh"

if [ -x "$DEVHUB_SCRIPT" ]; then
    exec "$DEVHUB_SCRIPT" "$@"
fi

echo "❌ scripts/devhub/devhub.sh が見つかりません。リポジトリが最新か確認してください。"
exit 1
