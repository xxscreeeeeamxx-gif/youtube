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
    # 解説もの（【トピック】+数字先頭フック。数字は必ず動画内で語っている実数を使う）
    "banknote": "【お札の秘密】偽札は2年で343枚だけ。なぜコピーできないのか【ずんだもん解説】",
    "battery-80-duo": "【スマホ充電の真実】100%は損！80%で止める科学【ずんだもん解説】",
    "auto-door": "【自動ドアの謎】2000年前からあったのに、今もあなたを無視する理由【ずんだもん解説】",
    "escalator": "【エスカレーターの謎】片側空けは誰が決めた？実は公式ルールじゃない【ずんだもん解説】",
    "cup-noodle": "【カップ麺の科学】年1000億食。3分の間に麺の中で起きていること【ずんだもん解説】",
    "ticket-gate": "【自動改札の仕組み】1分で60人。裏返しの切符でもなぜ通れるのか【ずんだもん解説】",
    "traffic-light": "【信号機の謎】どう見ても緑なのに、日本だけ「青」と呼ぶ理由【ずんだもん解説】",
    # 再現ドラマもの（【〇〇の誕生】+数字先頭フック）
    "momofuku-meme": "【カップ麺の誕生】47歳で全財産ゼロ。裏庭の小屋で世界を変える【ずんだもん解説】",
    "kaiten-meme": "【回転寿司の誕生】構想10年。人手不足の寿司屋、ビール工場で答えを見つける【ずんだもん解説】",
    "qr-meme": "【QRコードの誕生】1日1000回の「ピッ」に疲れた工場から、世界標準が生まれた【ずんだもん解説】",
    "gastro-meme": "【胃カメラの誕生】たった2人で挑んだ「胃の中を撮れ」。電車で口説かれた技師と医師【ずんだもん解説】",
    "rice-cooker-meme": "【炊飯器の誕生】妻が千回、米を炊いた。世界初の電気釜ができるまで【ずんだもん解説】",
    "tenji-block-meme": "【点字ブロックの誕生】全財産を道路に敷いた男。友の失明から生まれた黄色いブロック【ずんだもん解説】",
    "shinkansen-bird": "【新幹線の秘密】時速300キロの騒音、一羽のカワセミが解決した【ずんだもん解説】",
    "yokoi-gunpei": "【ゲームボーイの誕生】白黒画面で1億台。時代に逆らった男・横井軍平【ずんだもん解説】",
    "ajinomoto": "【味の素の誕生】昆布12キロから見つけた「5人目の味」、世界の言葉になる【ずんだもん解説】",
    "cutter-knife": "【カッターナイフの誕生】ヒントは板チョコ。9ミリの刃が100の国に届くまで【ずんだもん解説】",
    "washlet": "【ウォシュレットの誕生】社員300人がおしりを差し出した、前代未聞の開発計画【ずんだもん解説】",
    "yai-denchi": "【乾電池の誕生】5分の遅刻で人生が変わった男が、凍らない電池を作るまで【ずんだもん解説】",
    "masuoka-flash": "【フラッシュメモリの誕生】「金がない、却下」から始まった。スマホの記憶を作った男【ずんだもん解説】",
    "karaoke": "【カラオケの誕生】手作りの11台で世界へ。特許を取らなかった男にイグノーベル賞【ずんだもん解説】",
}

# Studioのタグ欄に必ず入れる共通タグ（視聴者には見えない）
BASE_TAGS = ["ずんだもん", "春日部つむぎ", "ゆっくり解説", "再現ドラマ", "雑学", "VOICEVOX"]


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


def build_entry(slug: str, pdir: Path = None):
    pdir = pdir or Path(f"projects/{slug}")
    meta_path = pdir / "out" / "metadata.txt"
    script_path = pdir / "script.yaml"
    if not meta_path.exists() or not script_path.exists():
        return None
    sec = parse_metadata(meta_path)
    meta = yaml.safe_load(script_path.read_text()).get("meta", {})
    title = TITLES.get(slug)
    if not title:
        title = sec.get("タイトル", meta.get("title", slug)).strip()
        print(f"‼ 警告: {slug} は TITLES 未登録。旧タイトルが出力されます（TITLES に追加してください）")

    # 本文は script.yaml の meta.summary が正（説明文の修正に再ビルドが要らない）
    body = (meta.get("summary") or "").strip()
    if not body:
        body = sec.get("概要欄", "").split("▼ 目次")[0].strip()

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

    # Studioのタグ欄用（コンマ区切り・視聴者非表示・上限500文字）
    tags = list(BASE_TAGS)
    for t in (meta.get("tags") or []):
        if t not in tags:
            tags.append(t)
    tag_line = ",".join(tags)

    desc_parts = [body, note, credits]
    description = "\n\n".join(p for p in desc_parts if p)
    return title, description, tag_line


if __name__ == "__main__":
    out_all = []
    count = 0
    from ytf.config import Config, iter_projects, is_uploaded
    for p in iter_projects(Config.load().root):
        if not (p / "out" / "video.mp4").exists():
            continue
        if is_uploaded(p):
            # 公開済みは編集しない。既存の youtube.txt をそのまま集約に載せる
            f = p / "youtube.txt"
            if f.exists():
                out_all.append(f"{'=' * 60}\n【{p.name}】(公開済み)\n{'=' * 60}\n{f.read_text()}")
                count += 1
            continue
        # slug はフォルダ名ではなく script.yaml の meta.slug（TITLES のキー）
        try:
            slug = (yaml.safe_load((p / "script.yaml").read_text())
                    or {}).get("meta", {}).get("slug") or p.name
        except Exception:
            slug = p.name
        if slug in SKIP:
            continue
        entry = build_entry(slug, p)
        if not entry:
            continue
        title, description, tag_line = entry
        text = (f"■タイトル\n{title}\n\n■説明文\n{description}\n\n"
                f"■タグ（Studioのタグ欄用・視聴者には見えない）\n{tag_line}\n")
        (p / "youtube.txt").write_text(text)
        out_all.append(f"{'=' * 60}\n【{slug}】\n{'=' * 60}\n{text}")
        count += 1
    Path("assets/branding").mkdir(exist_ok=True)
    Path("assets/branding/youtube_all.txt").write_text("\n".join(out_all))
    print(f"生成: {count} 本 → projects/*/youtube.txt + assets/branding/youtube_all.txt")
