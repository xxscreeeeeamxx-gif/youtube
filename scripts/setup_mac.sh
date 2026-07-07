#!/usr/bin/env bash
# Mac初回セットアップを1コマンドで行う。
#   ./scripts/setup_mac.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== 1/4 ffmpeg =="
if ! command -v ffmpeg >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then
    brew install ffmpeg
  else
    echo "❌ ffmpeg がありません。Homebrew を入れてから再実行してください: https://brew.sh"
    exit 1
  fi
else
  echo "ffmpeg OK"
fi

echo "== 2/4 Pythonパッケージ =="
pip3 install -e . --quiet
echo "yt-factory OK"

echo "== 3/4 素材の初期化 =="
ytf assets --init

echo "== 4/4 環境チェック =="
ytf doctor || true

cat <<'MSG'

次にやること:
  1. VOICEVOX アプリを起動する（https://voicevox.hiroshiba.jp/ からインストール）
  2. 動作確認:   ytf make sample
  3. 本番立ち絵を assets/characters/zunda/ 等に配置（scripts/import_sprites.py 参照）
  4. n8n セットアップ: automation/README.md
MSG
