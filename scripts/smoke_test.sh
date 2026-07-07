#!/usr/bin/env bash
# パイプライン全体のスモークテスト（VOICEVOX不要・ダミーTTS使用）
set -euo pipefail
cd "$(dirname "$0")/.."

rm -rf projects/sample/audio projects/sample/frames projects/sample/out
ytf assets --init
ytf make sample --tts dummy
ytf qc sample

test -f projects/sample/out/video.mp4
test -f projects/sample/out/short_hook.mp4
test -f projects/sample/out/thumbnail.png
test -f projects/sample/out/metadata.txt

dur=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 projects/sample/out/video.mp4)
echo "video.mp4 duration: ${dur}s"
python3 -c "assert float('${dur}') > 30, '動画が短すぎる'"
echo "✅ smoke test passed"
