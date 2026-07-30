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

# 投稿用タイトル（【トピック】フック【ずんだもん解説】形式）。
# 新作を作ったらここに追加する。未登録slugはmetadata.txtのタイトルのまま+警告。
TITLES = {
    # 解説もの（トピックがフックに入っているので前置きなし）
    "banknote": "お札はなぜコピーできないのか【ずんだもん解説】",
    "battery-80-duo": "スマホ充電100%は損！80%の科学【ずんだもん解説】",
    "battery-80": "スマホ充電は80%で止めるべき？バッテリー科学の真実【ずんだもん解説】",
    "auto-door": "自動ドアはなぜ、たまにあなたを無視するのか【ずんだもん解説】",
    "escalator": "エスカレーターの片側空け、実は公式ルールじゃない【ずんだもん解説】",
    "cup-noodle": "カップ麺の3分、何が起きているのか【ずんだもん解説】",
    "flash-memory": "USBメモリはなぜ電源を切っても忘れないのか【ずんだもん解説】",
    "qr-code": "QRコードはなぜ汚れても読めるのか【ずんだもん解説】",
    "ticket-gate": "自動改札機は切符を裏返しで入れてもなぜ通れるのか【ずんだもん解説】",
    "traffic-light": "信号機の「青」、どう見ても緑なのになぜ青なのか【ずんだもん解説】",
    "ice-slippery": "氷が滑る理由、実はまだ解明されていない【ずんだもん解説】",
    # 再現ドラマもの（【〇〇誕生秘話】でトピックを先頭に出す）
    "momofuku-v2": "【カップ麺誕生秘話】財産を失った47歳、裏庭の小屋で世界を変える【ずんだもん解説】",
    "momofuku-meme": "【カップ麺誕生秘話】財産を失った47歳、裏庭の小屋で世界を変える【ずんだもん解説・ミーム版】",
    "momofuku": "【カップ麺誕生秘話】財産を失った48歳、裏庭の小屋で世界を変える【ずんだもん解説】",
    "kaiten-sushi": "【回転寿司誕生秘話】皿を回した男。人手不足の寿司屋がビール工場で見つけた答え【ずんだもん解説】",
    "kaiten-meme": "【回転寿司誕生秘話】皿を回した男。人手不足の寿司屋がビール工場で見つけた答え【ずんだもん解説・ミーム版】",
    "qr-drama": "【QRコード誕生秘話】工場の「疲れた」から生まれた四角、世界標準になる【ずんだもん解説】",
    "qr-meme": "【QRコード誕生秘話】工場の「疲れた」から生まれた四角、世界標準になる【ずんだもん解説・ミーム版】",
    "gastro-camera": "【胃カメラ誕生秘話】胃の中を撮れ。電車で口説かれた技師と医師の挑戦【ずんだもん解説】",
    "gastro-meme": "【胃カメラ誕生秘話】胃の中を撮れ。電車で口説かれた技師と医師の挑戦【ずんだもん解説・ミーム版】",
    "rice-cooker": "【炊飯器誕生秘話】スイッチひとつで、失敗しない。妻が千回炊いた世界初の電気釜【ずんだもん解説】",
    "rice-cooker-meme": "【炊飯器誕生秘話】スイッチひとつで、失敗しない。妻が千回炊いた世界初の電気釜【ずんだもん解説・ミーム版】",
    "tenji-block": "【点字ブロック誕生秘話】黄色いブロックに、全財産。友の失明から生まれた発明【ずんだもん解説】",
    "tenji-block-meme": "【点字ブロック誕生秘話】黄色いブロックに、全財産。友の失明から生まれた発明【ずんだもん解説・ミーム版】",
    "shinkansen-bird": "【新幹線開発秘話】鼻はなぜカワセミなのか。バードウォッチングが世界最速を作った【ずんだもん解説】",
    "yokoi-gunpei": "【ゲームボーイ誕生秘話】白黒画面で、世界を取った男。横井軍平【ずんだもん解説】",
    "ajinomoto": "【味の素誕生秘話】だしの正体「うま味」を、世界の言葉にした男たち【ずんだもん解説】",
    "cutter-knife": "【カッターナイフ誕生秘話】刃を折ったら、世界が切れた。印刷工・岡田良男【ずんだもん解説】",
    "washlet": "【ウォシュレット誕生秘話】社員300人が体を張った、前代未聞の開発計画【ずんだもん解説】",
}

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
    voicevox, se = [], "効果音ラボ"
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
            elif item.startswith("効果音:"):
                se = item.split(":", 1)[1].strip()
    out = ["▼使用素材"]
    if voicevox:
        out.append("音声: VOICEVOX（" + "、".join(voicevox) + "）")
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
    title = TITLES.get(slug)
    if not title:
        title = sec.get("タイトル", meta.get("title", slug)).strip()
        print(f"警告: {slug} は TITLES 未登録。metadata.txt のタイトルをそのまま使用")

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

    note = ("※台本は公開資料をもとに裏取りしていますが、会話や演出は再現ドラマとしての脚色を含みます。"
            "事実と異なる点に気づいた方は、コメントで教えてください。"
            if meta.get("mode") == "drama"
            else "※内容は公開資料をもとに構成していますが、誤りに気づいた方はコメントで教えてください。")

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
