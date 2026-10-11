#!/usr/bin/env python3
"""題名・サムネの A/B テスト（Studio の Test & Compare）用の案。

2026-10-11 の調査（docs/再生を伸ばす調査_2026-10-11.md）で、クリック率 1.4% の詰まりは
題名とサムネ側にあると分かった。新しい型が本当に勝つかは YouTube 自身に決めさせる:
  A = 今の型（対照）  B = 断定型  C = 問い型
勝敗は総再生時間の割合で決まるので、釣りの案は勝てない。結果は PUBLISH.md「A/B テストの記録」へ。

事実と数字は台本（script.yaml）にあるものだけ。evidence に台本の該当行を残してある。

実行:
  python scripts/ab_variants.py render [slug ...]   # out/thumbnail_b.png / _c.png を書き出す
  python scripts/ab_variants.py sheet <png>          # A/B/C を168px幅で並べた確認用シート
  python scripts/ab_variants.py titles               # 題名の一覧と字数
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

DATA = Path(__file__).resolve().parent / "ab_variants.json"
SUFFIX = "【ずんだもん解説】"


def load() -> list[dict]:
    return json.loads(DATA.read_text(encoding="utf-8"))


def project_dir(slug: str) -> Path:
    from ytf.config import Config, find_project_dir
    d = find_project_dir(Config.load().root, slug)
    if d is None:
        raise SystemExit(f"プロジェクトが見つかりません: {slug}")
    return d


def render(slugs: list[str]) -> None:
    import gen_thumbnails as g
    for v in load():
        if slugs and v["slug"] not in slugs:
            continue
        out = project_dir(v["slug"]) / "out"
        for k in ("b", "c"):
            spec = dict(v[f"thumb_{k}"])
            spec["_key"] = f'{v["slug"]}#{k}'
            g.layout_conflict(spec).save(out / f"thumbnail_{k}.png")
        print("生成:", v["slug"])
    if g._len_warn:
        print("⚠️ 字数の上限を超えた要素があります（実寸でつぶれる）:")
        print("\n".join(g._len_warn))


def sheet(dst: str) -> None:
    from PIL import Image, ImageDraw
    import gen_thumbnails as g
    vs = load()
    tw, th = 336, 189           # スマホ一覧の約2倍。168px 相当の読みやすさを見る
    img = Image.new("RGB", (tw * 3 + 40, (th + 30) * len(vs) + 10), (240, 240, 240))
    d = ImageDraw.Draw(img)
    f = g.font("w9", 18)
    for i, v in enumerate(vs):
        out = project_dir(v["slug"]) / "out"
        y = 10 + i * (th + 30)
        d.text((10, y), v["slug"], font=f, fill=(0, 0, 0))
        for j, name in enumerate(("thumbnail.png", "thumbnail_b.png", "thumbnail_c.png")):
            p = out / name
            if p.exists():
                im = Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS)
                img.paste(im, (10 + j * (tw + 10), y + 24))
    img.save(dst)
    print("シート:", dst)


def titles() -> None:
    for v in load():
        print(v["slug"])
        for k in ("a", "b", "c"):
            t = v[f"title_{k}"]
            body = t.replace(SUFFIX, "")
            print(f"  {k.upper()} {len(t):>3}字（本文{len(body):>2}） {t}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "titles"
    if cmd == "render":
        render(sys.argv[2:])
    elif cmd == "sheet":
        sheet(sys.argv[2])
    else:
        titles()
