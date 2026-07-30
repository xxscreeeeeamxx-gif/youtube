#!/usr/bin/env python3
"""全動画のYouTube投稿用タイトル+説明文を生成する。

各 projects/<slug>/out/metadata.txt（ビルドが生成）を土台に、
クレジットの整形・使用素材ブロック・注記・ハッシュタグを加えた
貼り付け用テキストを projects/<slug>/youtube.txt に保存し、
全動画ぶんを assets/branding/youtube_all.txt に集約する。

実行: PYTHONPATH=. python3 scripts/gen_youtube_meta.py
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml  # noqa: E402

SKIP = {"sample", "drama-test"}

# ハッシュタグに使わない汎用タグ
TAG_SKIP = {"解説", "雑学", "science", "VOICEVOX", "青山龍星", "ゆっくり", "ミーム",
            "再現ドラマ", "ずんだもん"}


def parse_metadata(path: Path):
    text = path.read_text()
    sec = {}
    cur = None
    for line in text.splitlines():
        m = re.match(r"^==== (.+) ====$", line)
        if m:
            cur = m.group(1)
            sec[cur] = []
        elif cur:
            sec[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in sec.items()}


def build_credits(raw: str) -> str:
    """metadata.txtのクレジット行を貼り付け用に整形する。"""
    voicevox, aques, se = [], False, "効果音ラボ"
    for line in raw.splitlines():
        if line.startswith("※"):
            continue
        for item in line.split("/"):
            item = item.strip()
            if not item:
                continue
            if item.startswith("VOICEVOX:"):
                name = item.split(":", 1)[1]
                if name not in voicevox:
                    voicevox.append(name)
            elif "AquesTalk" in item:
                aques = True
            elif item.startswith("効果音:"):
                se = item.split(":", 1)[1].strip()
    out = ["▼使用素材"]
    if voicevox:
        out.append("音声: VOICEVOX（" + "、".join(voicevox) + "）")
    if aques:
        out.append("ゆっくり音声: AquesTalkPlayer（株式会社アクエスト）")
    out.append(f"効果音: {se} / BGM: DOVA-SYNDROME")
    out.append("※本動画は VOICEVOX の音声合成を使用しています。")
    return "\n".join(out)


# モブのvoice ID→VOICEVOXキャラ名（metadata.txtの空スロット補完用）
VOICE_NAMES = {8: "春日部つむぎ", 12: "白上虎太郎", 13: "青山龍星", 42: "ちび式じい"}


def build_entry(slug: str):
    meta_path = Path(f"projects/{slug}/out/metadata.txt")
    script_path = Path(f"projects/{slug}/script.yaml")
    if not meta_path.exists() or not script_path.exists():
        return None
    sec = parse_metadata(meta_path)
    meta = yaml.safe_load(script_path.read_text()).get("meta", {})
    title = sec.get("タイトル", meta.get("title", slug)).strip()

    gaiyou = sec.get("概要欄", "")
    # 概要欄を「本文」「目次」に分解（クレジット以降は作り直す）
    body = gaiyou.split("▼ 目次")[0].strip()
    toc = ""
    m = re.search(r"▼ 目次\n(.*?)(?:\n▼|\Z)", gaiyou, re.S)
    if m:
        lines = m.group(1).strip().splitlines()
        # 先頭章はタイトルそのままなので「オープニング」に置き換える
        if lines and lines[0].startswith("0:00"):
            lines[0] = "0:00 オープニング"
        toc = "▼目次\n" + "\n".join(lines)

    raw_credits = sec.get("概要欄", "").split("▼ クレジット")[-1]
    # モブ音声のクレジット欠け（空スロット）を script.yaml の mobs から補完
    extra = []
    for mob in (meta.get("mobs") or []):
        name = VOICE_NAMES.get(mob.get("voice"))
        if name:
            extra.append(f"VOICEVOX:{name}")
    if extra:
        raw_credits += "\n" + " / ".join(extra)
    credits = build_credits(raw_credits)

    note = ("※台本は公開資料をもとに裏取りしていますが、会話は再現ドラマとしての脚色です。"
            if meta.get("mode") == "drama"
            else "※内容は公開資料をもとに構成しています。")

    tags = [t for t in (meta.get("tags") or []) if t not in TAG_SKIP][:3]
    hashtags = " ".join(["#ずんだもん", "#ゆっくり解説"] + [f"#{t.replace(' ', '')}" for t in tags])

    desc_parts = [body, toc, note, credits, hashtags]
    description = "\n\n".join(p for p in desc_parts if p)
    return title, description


if __name__ == "__main__":
    out_all = []
    count = 0
    for p in sorted(Path("projects").iterdir()):
        slug = p.name
        if slug in SKIP or not (p / "out" / "video.mp4").exists():
            continue
        entry = build_entry(slug)
        if not entry:
            continue
        title, description = entry
        text = f"■タイトル\n{title}\n\n■説明文\n{description}\n"
        (p / "youtube.txt").write_text(text)
        out_all.append(f"{'=' * 60}\n【{slug}】\n{'=' * 60}\n{text}")
        count += 1
    Path("assets/branding").mkdir(exist_ok=True)
    Path("assets/branding/youtube_all.txt").write_text("\n".join(out_all))
    print(f"生成: {count} 本 → projects/*/youtube.txt + assets/branding/youtube_all.txt")
