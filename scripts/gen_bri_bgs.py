#!/usr/bin/env python3
"""ブリヂストン・石橋正二郎の再現ドラマ（ishibashi-bridgestone）用の背景4種。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
★商標に触れないため、トレッドパターン・ロゴ・型番は描かない。
  タイヤは「黒い輪」までにとどめ、特定の製品と読めないようにする。
トーンの設計:
  足袋屋   … 畳と木。狭い。ここが出発点
  工場     … ゴムを練る釜の熱。作る側の場所
  倉庫     … **この回の主戦場**。返ってきたタイヤが積み上がる場所
  現代     … いちばん明るい

実行: PYTHONPATH=. python3 scripts/gen_bri_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402
from scripts.gen_yam_bgs import _building, _person, _desk  # noqa: E402


def _tyre(d, cx, cy, r, tilt=0.0):
    """タイヤ。**黒い輪だけ**。溝の模様は商標に触れうるので描かない。"""
    d.ellipse([cx - r, cy - r * (1 - tilt), cx + r, cy + r * (1 - tilt)],
              fill=(44, 44, 48), outline=(24, 24, 28), width=max(2, int(r * 0.09)))
    ir = r * 0.52
    d.ellipse([cx - ir, cy - ir * (1 - tilt), cx + ir, cy + ir * (1 - tilt)],
              fill=(118, 120, 126), outline=(78, 80, 86), width=max(2, int(r * 0.05)))
    d.ellipse([cx - ir * 0.34, cy - ir * 0.34 * (1 - tilt),
               cx + ir * 0.34, cy + ir * 0.34 * (1 - tilt)], fill=(70, 72, 78))


def _tabi(d, x, y, s=1.0, body=(242, 238, 230), sole=(52, 52, 56)):
    """足袋。**親指の割れをはっきり描く**。この回のフックが「もとは足袋屋」なので、
    形が分からないと冒頭が成立しない（2026-09-17に一度、白い塊になった）。
    横向きのシルエットにして、つま先の切れ込みを深く取る。"""
    # 甲（かかとからつま先へ）
    d.polygon([(x, y), (x + 176 * s, y), (x + 210 * s, y - 40 * s),
               (x + 196 * s, y - 96 * s), (x + 74 * s, y - 116 * s),
               (x, y - 70 * s)], fill=body, outline=(150, 144, 132),
              width=max(2, int(5 * s)))
    # 親指の割れ（深い切れ込み）
    d.polygon([(x + 150 * s, y - 4 * s), (x + 210 * s, y - 40 * s),
               (x + 196 * s, y - 70 * s), (x + 150 * s, y - 40 * s)],
              fill=(214, 208, 196), outline=(150, 144, 132),
              width=max(2, int(4 * s)))
    # こはぜ（留め具）。足袋らしさはここで出る
    for k in range(3):
        d.rectangle([x + 8 * s, y - 92 * s + k * 26 * s,
                     x + 30 * s, y - 76 * s + k * 26 * s], fill=(200, 194, 180),
                    outline=(140, 134, 122), width=max(1, int(3 * s)))
    # 底
    d.polygon([(x, y), (x + 176 * s, y), (x + 210 * s, y - 36 * s),
               (x + 210 * s, y - 18 * s), (x + 174 * s, y + 18 * s), (x, y + 18 * s)],
              fill=sole, outline=(30, 30, 34), width=max(2, int(4 * s)))


def tabiya() -> Image.Image:
    """久留米の足袋屋。畳と木の棚。狭くて暖かい。"""
    img = vgrad((W, H), (214, 196, 162), (188, 168, 136)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (196, 180, 142), (150, 136, 104))
    for k in range(6):                       # 畳の目
        d.line([0, 820 + k * 44, W, 820 + k * 44], fill=(176, 162, 126), width=4)
    # 棚（足袋が並ぶ）
    d.rectangle([90, 210, 700, 800], fill=(158, 126, 84), outline=(112, 88, 54),
                width=8)
    for r in range(3):
        yy = 336 + r * 156
        d.rectangle([110, yy, 680, yy + 18], fill=(126, 100, 62))
        for c in range(2):
            _tabi(d, 150 + c * 270, yy - 12, 1.02)
    _window(img, d, 1080, 180, 1780, 520, (232, 220, 186), (248, 240, 214),
            frame=(120, 96, 60))
    d = ImageDraw.Draw(img)
    _desk(d, 1050, 660, 1720, 800, (140, 112, 70), (100, 78, 46))
    _tabi(d, 1120, 656, 1.35)
    d.line([900, 0, 900, 220], fill=(88, 74, 56), width=6)
    d.ellipse([868, 220, 932, 284], fill=(252, 238, 190))
    glow(img, 900, 252, 230, (255, 236, 176), 92)
    return img


def kojo() -> Image.Image:
    """ゴム工場。練る釜の熱と、成形の台。作る側の場所。"""
    img = vgrad((W, H), (156, 146, 140), (128, 118, 112)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 830, (138, 128, 120), (104, 96, 90))
    for x in (110, 1690):
        d.rectangle([x, 0, x + 56, 830], fill=(118, 110, 104))
    # 練り釜
    d.rounded_rectangle([700, 260, 1200, 830], radius=24, fill=(104, 96, 92),
                        outline=(70, 64, 60), width=8)
    d.rounded_rectangle([780, 380, 1120, 620], radius=16, fill=(202, 112, 52),
                        outline=(160, 80, 32), width=8)
    glow(img, 950, 500, 380, (255, 150, 50), 110)
    d = ImageDraw.Draw(img)
    d.rectangle([920, 0, 980, 262], fill=(86, 80, 76))
    for k in range(3):                       # ゴムのロール
        d.ellipse([250 + k * 120, 640, 350 + k * 120, 740], fill=(60, 60, 64),
                  outline=(36, 36, 40), width=6)
    _desk(d, 1300, 690, 1660, 830, (112, 104, 98), (78, 72, 68))
    _tyre(d, 1480, 660, 86, 0.18)
    return img


def souko() -> Image.Image:
    """倉庫。**返ってきたタイヤが積み上がる場所**。この回の主戦場。

    ここが空だと「全部返ってきた」が伝わらないので、意図して埋める。
    """
    img = vgrad((W, H), (122, 118, 116), (150, 144, 140)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 840, (126, 120, 114), (94, 90, 86))
    for x in range(60, W, 300):              # 板張りの壁
        d.rectangle([x, 120, x + 280, 840], fill=(146, 132, 112),
                    outline=(112, 98, 80), width=5)
    d.rectangle([40, 90, W - 40, 140], fill=(110, 98, 80))
    # 積み上がったタイヤ（左右に山）
    for col, base in ((250, 838), (430, 838), (1460, 838), (1650, 838)):
        for r in range(4):
            _tyre(d, col, base - 60 - r * 106, 74, 0.34)
    for col, base in ((360, 700), (1560, 700)):
        for r in range(2):
            _tyre(d, col, base - 40 - r * 100, 66, 0.34)
    # 転がった一本（手前）
    _tyre(d, 840, 832, 92, 0.52)
    d.line([1000, 0, 1000, 210], fill=(80, 74, 68), width=6)
    d.ellipse([968, 210, 1032, 274], fill=(250, 234, 178))
    glow(img, 1000, 242, 240, (255, 230, 160), 96)
    return img


def ima() -> Image.Image:
    """現代。明るい道路。いちばん明るい絵にする。"""
    img = vgrad((W, H), (212, 230, 244), (184, 210, 230)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 810, (150, 154, 160), (118, 122, 128))
    for k in range(4):
        _building(d, 60 + k * 470, 250 + (k % 2) * 80, 400 + k * 470, 810,
                  (176, 190, 202), (140, 154, 168))
    for k in range(6):                       # センターライン
        d.rectangle([120 + k * 320, 930, 300 + k * 320, 960], fill=(244, 244, 236))
    _tyre(d, 330, 880, 118, 0.20)
    _tyre(d, 1560, 880, 118, 0.20)
    glow(img, 1660, 140, 420, (255, 246, 214), 92)
    return img


PAINTERS = {
    "il_bri_tabiya": tabiya,
    "il_bri_kojo": kojo,
    "il_bri_souko": souko,
    "il_bri_ima": ima,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
