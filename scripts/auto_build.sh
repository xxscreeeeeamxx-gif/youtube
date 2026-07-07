#!/usr/bin/env bash
# 承認済み（.approved）で未ビルド/台本更新済みのプロジェクトを自動ビルドする。
# n8n の Execute Command や cron から定期実行する想定。
#
# 環境変数:
#   YTF_NOTIFY_WEBHOOK  Discord/Slack の Incoming Webhook URL（任意、通知用）
#   YTF_TTS             dummy を指定するとVOICEVOXなしで検証ビルド（任意）
set -uo pipefail
cd "$(dirname "$0")/.."

notify() {
  echo "$1"
  if [ -n "${YTF_NOTIFY_WEBHOOK:-}" ]; then
    # Discordは content、Slackは text を読む（両方入れておけばどちらでも動く）
    curl -s -X POST -H 'Content-Type: application/json' \
      -d "{\"content\": \"$1\", \"text\": \"$1\"}" \
      "$YTF_NOTIFY_WEBHOOK" >/dev/null || true
  fi
}

built=0
shopt -s nullglob
for marker in projects/*/.approved; do
  proj_dir=$(dirname "$marker")
  slug=$(basename "$proj_dir")
  script="$proj_dir/script.yaml"
  out="$proj_dir/out/video.mp4"
  [ -f "$script" ] || continue
  # ビルド済みかつ台本より新しければスキップ
  if [ -f "$out" ] && [ "$out" -nt "$script" ]; then
    continue
  fi
  notify "🎬 ビルド開始: $slug"
  if ytf make "$slug" ${YTF_TTS:+--tts "$YTF_TTS"} > "$proj_dir/build.log" 2>&1; then
    notify "✅ 完成: $slug — 動画を確認したら \`ytf release $slug\` でアップロード待ちへ"
    built=$((built + 1))
  else
    notify "❌ ビルド失敗: $slug — projects/$slug/build.log を確認"
  fi
done

if [ "$built" -eq 0 ]; then
  echo "ビルド対象なし"
fi
