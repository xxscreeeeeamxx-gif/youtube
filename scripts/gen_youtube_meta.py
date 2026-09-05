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
    "banknote": "【お札の秘密】人間の目には見えない仕掛けが入っている【ずんだもん解説】",
    "battery-80-duo": "【スマホ充電の真実】100%は損！80%で止める科学【ずんだもん解説】",
    "auto-door": "【自動ドアの謎】2000年前からあったのに、今も無視される【ずんだもん解説】",
    "escalator": "【エスカレーターの謎】片側を空けると運べる人数が減る【ずんだもん解説】",
    "traffic-light": "【信号機の謎】呼び方に合わせて、法律の方が折れた【ずんだもん解説】",
    # 再現ドラマもの（【〇〇の誕生】+数字先頭フック）
    "momofuku-meme": "【カップ麺の誕生】47歳で全財産ゼロ。裏庭の小屋で世界を変える【ずんだもん解説】",
    "kaiten-meme": "【回転寿司の誕生】人手不足の寿司屋が、ビール工場で答えを見つける【ずんだもん解説】",
    "qr-meme": "【QRコードの誕生】現場の「疲れた」の一言から、世界標準が生まれた【ずんだもん解説】",
    "gastro-meme": "【胃カメラの誕生】胃の中を撮れ。前例なき無茶な依頼【ずんだもん解説】",
    "rice-cooker-meme": "【炊飯器の誕生】大手が匙を投げた難題を、町工場の夫婦が【ずんだもん解説】",
    "tenji-block-meme": "【点字ブロックの誕生】なぜ日本の道路は黄色い突起だらけか【ずんだもん解説】",
    "purikura-meme": "【プリクラの誕生】そんなの持って帰ってどうすんの【ずんだもん解説】",
    "sharp-pencil": "【シャープペンシルの誕生】全部失って、大阪へ【ずんだもん解説】",
    "okano-needle": "【痛くない注射針の誕生】100社が断った仕事を、6人の町工場が【ずんだもん解説】",
    "shinkansen-bird": "【新幹線の秘密】あの長い鼻は、なぜあんな形になったのか【ずんだもん解説】",
    "nishizawa-fiber": "【光ファイバーの誕生】「金は出せない」と、日本に断られた発明【ずんだもん解説】",
    "exit-sign": "【非常口マークの誕生】あの緑の人を描いたのは日本人だった【ずんだもん解説】",
    "nakauchi-daiei": "【ダイエーの興亡】すき焼きを願った男が、日本一になり追われるまで【ずんだもん解説】",
    "yamauchi-nintendo": "【任天堂の再起】タクシーも食品も失敗した男が、世界を取るまで【ずんだもん解説】",
    "yokoi-gunpei": "【ゲームボーイの誕生】性能で負けて、1億台売った男【ずんだもん解説】",
    "ajinomoto": "【味の素の誕生】だしのうまさの正体を突き止めた化学者【ずんだもん解説】",
    "cutter-knife": "【カッターナイフの誕生】世界中が使う日本の発明を生んだ印刷工【ずんだもん解説】",
    "washlet": "【ウォシュレットの誕生】あの角度と温度は、こうして決まった【ずんだもん解説】",
    "yai-denchi": "【乾電池の誕生】5分の遅刻で人生が変わった男が、凍らない電池を作るまで【ずんだもん解説】",
    "masuoka-flash": "【フラッシュメモリの誕生】スマホの記憶を作った男は干された【ずんだもん解説】",
    "kaisatsu-drama": "【自動改札機の誕生】世界が真似しなかった、日本だけの答え【ずんだもん解説】",
    "quartz-astron": "【クオーツ時計の誕生】最下位の工場が、スイスを倒すまで【ずんだもん解説】",
    "karaoke": "【カラオケの誕生】年1億ドルの特許料を、受け取らなかった男【ずんだもん解説】",
}

# Studioのタグ欄に必ず入れる共通タグ。ジャンルを表す一般語だけを置く。
# 他チャンネル名を検索目当てで入れるのは「誤解を招くメタデータ」としてスパム
# ポリシー違反になるうえ、関連動画は共視聴データで決まるので効果もない（2026-08）
BASE_TAGS = ["ずんだもん", "春日部つむぎ", "ゆっくり解説", "再現ドラマ", "雑学", "VOICEVOX",
             "歴史解説", "日本の発明", "偉人", "ものづくり", "開発秘話", "技術史"]


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

    # 本文は script.yaml の meta.summary が正（説明文の修正に再ビルドが要らない）。
    # 読みタグ [表示|よみ] が混じっていても表示テキストだけを取り出す
    body = re.sub(r"\[([^|\]]+)\|[^\]]+\]", r"\1", (meta.get("summary") or "")).strip()
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
    import argparse
    ap = argparse.ArgumentParser(description="概要欄・タイトル・タグを書き出す")
    ap.add_argument("slugs", nargs="*", help="指定するとその slug だけ書き出す")
    # 公開済みは既定では触らない（動画は差し替えられないため）。ただし
    # upload_youtube.py title で YouTube 側のタイトルを直せるようになったので、
    # ローカルの記録だけ現実に合わせたいときは --refresh-uploaded を使う
    ap.add_argument("--refresh-uploaded", action="store_true",
                    help="公開済みの youtube.txt も TITLES に合わせて作り直す")
    _a = ap.parse_args()

    out_all = []
    count = 0
    from ytf.config import Config, iter_projects, is_uploaded
    for p in iter_projects(Config.load().root):
        if not (p / "out" / "video.mp4").exists():
            continue
        # slug はフォルダ名ではなく script.yaml の meta.slug（TITLES のキー）
        try:
            slug = (yaml.safe_load((p / "script.yaml").read_text())
                    or {}).get("meta", {}).get("slug") or p.name
        except Exception:
            slug = p.name
        if _a.slugs and slug not in _a.slugs and p.name not in _a.slugs:
            continue
        if is_uploaded(p) and not _a.refresh_uploaded:
            f = p / "youtube.txt"
            if f.exists():
                out_all.append(f"{'=' * 60}\n【{p.name}】(公開済み)\n{'=' * 60}\n{f.read_text()}")
                count += 1
            continue
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
