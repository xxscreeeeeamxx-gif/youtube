#!/usr/bin/env python3
"""カシオの誕生・樫尾四兄弟回（53_カシオの誕生 / slug=casio-kashio）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針は蚊取り線香回（gen_katori_bgs.py）と同じ。
実在メーカーの商標（ロゴ・製品名の文字）は描かない。

実行: PYTHONPATH=. python scripts/gen_casio_bgs.py [名前...]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, glow, hanging_bulb, tatami_floor, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)


def _d(img):
    return ImageDraw.Draw(img)


def _glow(img, cx, cy, r, color, alpha=110):
    """glow() は RGBA に合成するので、変換した結果を貼り戻す必要がある。"""
    rgba = img.convert("RGBA")
    glow(rgba, cx, cy, r, color, alpha)
    img.paste(rgba.convert("RGB"), (0, 0))


def _window(d, x0, y0, x1, y1, sky=(150, 186, 214), frame=(70, 62, 56)):
    d.rectangle([x0, y0, x1, y1], fill=sky)
    d.rectangle([x0, y0, x1, y1], outline=frame, width=10)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=frame, width=8)


def _desk(d, x0, y, w, col=(130, 100, 72)):
    d.rectangle([x0, y, x0 + w, y + 36], fill=col)
    d.rectangle([x0 + 20, y + 36, x0 + 50, FLOOR], fill=(100, 76, 54))
    d.rectangle([x0 + w - 50, y + 36, x0 + w - 20, FLOOR], fill=(100, 76, 54))


def _big_calc(d, x, y, s=1.0):
    """大きな事務机型の計算機（文字は描かない）。下端中央が x, y。"""
    w, h = 300 * s, 200 * s
    d.rectangle([x - w / 2, y - h, x + w / 2, y], fill=(170, 176, 170), outline=(110, 116, 110), width=5)
    d.rectangle([x - w / 2 + 20 * s, y - h + 20 * s, x + w / 2 - 20 * s, y - h + 60 * s], fill=(40, 44, 40))
    for r in range(3):
        for c in range(4):
            cx = x - 90 * s + c * 60 * s
            cy = y - h + 90 * s + r * 34 * s
            d.rectangle([cx, cy, cx + 40 * s, cy + 24 * s], fill=(230, 226, 214))


def _lathe(d, x, y):
    """旋盤（横長の機械）。"""
    d.rectangle([x, y - 60, x + 420, y], fill=(90, 100, 96), outline=(60, 66, 64), width=5)
    d.rectangle([x + 20, y - 150, x + 120, y - 60], fill=(110, 120, 116), outline=(60, 66, 64), width=5)
    d.ellipse([x + 110, y - 130, x + 170, y - 70], fill=(150, 150, 146))
    d.rectangle([x + 30, y, x + 70, FLOOR], fill=(70, 76, 74))
    d.rectangle([x + 350, y, x + 390, FLOOR], fill=(70, 76, 74))


# ------------------------------------------------------------ 現代
def ima():
    """現代の勉強机。電卓とノート。"""
    img = base((236, 232, 222), (214, 208, 196))
    d = _d(img)
    wood_floor(img, FLOOR, col=(170, 140, 104), line=(150, 122, 90))
    _window(d, 700, 150, 1220, 470, sky=(176, 210, 232))
    _desk(d, 520, 640, 880, col=(180, 150, 110))
    d.rectangle([700, 580, 900, 640], fill=(246, 246, 240), outline=(170, 170, 160), width=3)   # ノート
    d.rounded_rectangle([1000, 560, 1120, 640], radius=10, fill=(60, 64, 72))                   # 電卓
    d.rectangle([1014, 572, 1106, 592], fill=(170, 186, 160))
    for r in range(3):
        for c in range(4):
            d.rectangle([1014 + c * 24, 600 + r * 12, 1030 + c * 24, 608 + r * 12], fill=(200, 200, 204))
    return img


def machi():
    """昭和初めの東京の下町。木造の家並み。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (178, 204, 224), (216, 214, 204)), (0, 0))
    d = _d(img)
    for x0, h in ((0, 300), (320, 260), (620, 320), (1260, 280), (1560, 330)):
        d.rectangle([x0, 640 - h, x0 + 290, 640], fill=(120, 100, 80))
        d.polygon([(x0 - 20, 660 - h), (x0 + 145, 570 - h), (x0 + 310, 660 - h)], fill=(80, 70, 62))
        d.rectangle([x0 + 40, 640 - h + 70, x0 + 250, 640 - h + 110], fill=(200, 190, 170))
    d.line([(0, 200), (W, 240)], fill=(60, 60, 60), width=3)                # 電線
    d.rectangle([0, 640, W, H], fill=(176, 160, 130))
    return img


def koba():
    """戦後の小さな町工場。旋盤と作業台。"""
    img = base((196, 186, 168), (160, 150, 134))
    d = _d(img)
    wood_floor(img, FLOOR, col=(110, 96, 80), line=(92, 80, 66))
    _window(d, 700, 140, 1220, 440, sky=(170, 196, 214))
    _lathe(d, 80, 700)
    _desk(d, 1200, 660, 560)
    for k in range(5):
        d.ellipse([1240 + k * 90, 620, 1300 + k * 90, 660], fill=(150, 150, 150))   # 部品
    hanging_bulb(img, 960, warm=True, ly=40)
    return img


def tenji():
    """展示会の会場。台の上の大きな計算機。"""
    img = base((230, 224, 210), (204, 196, 180))
    d = _d(img)
    wood_floor(img, FLOOR, col=(150, 120, 88), line=(128, 102, 74))
    d.rectangle([300, 110, 1620, 190], fill=(60, 80, 120))                  # 横幕（文字なし）
    for x in (120, 1720):
        d.rectangle([x, 100, x + 80, FLOOR], fill=(206, 196, 176))
    d.rectangle([760, 660, 1160, 720], fill=(130, 100, 72))                 # 展示台
    _big_calc(d, 960, 660, 1.0)
    for x in (560, 1360):
        _glow(img, x, 120, 90, (255, 236, 190), 120)
    return img


def _gear_calc(d, x, y, s=1.0):
    """歯車で動く大型の計算機（数字キーではなく、けたごとの縦の列のキー）。"""
    import math as _m
    w, h = 320 * s, 220 * s
    d.rectangle([x - w / 2, y - h, x + w / 2, y], fill=(110, 106, 100), outline=(70, 66, 62), width=5)
    for c in range(8):                                                     # けたごとのキーの列
        for r in range(5):
            cx = x - 140 * s + c * 34 * s
            cy = y - h + 70 * s + r * 26 * s
            d.ellipse([cx, cy, cx + 20 * s, cy + 20 * s], fill=(220, 214, 200))
    for k, gx in enumerate((x - 120 * s, x + 110 * s)):                    # 上にのぞく歯車
        r = 36 * s
        pts = []
        for i in range(24):
            a = i / 24 * 2 * _m.pi
            rr = r * (1.0 if i % 2 == 0 else 0.8)
            pts.append((gx + rr * _m.cos(a), y - h - 10 * s + rr * _m.sin(a)))
        d.polygon(pts, fill=(196, 170, 90), outline=(120, 100, 50))


def tenji0():
    """1949年の展示会の会場。台の上の歯車式の計算機。"""
    img = base((230, 224, 210), (204, 196, 180))
    d = _d(img)
    wood_floor(img, FLOOR, col=(150, 120, 88), line=(128, 102, 74))
    d.rectangle([300, 110, 1620, 190], fill=(60, 80, 120))
    for x in (120, 1720):
        d.rectangle([x, 100, x + 80, FLOOR], fill=(206, 196, 176))
    d.rectangle([760, 660, 1160, 720], fill=(130, 100, 72))
    _gear_calc(d, 960, 660, 1.0)
    for x in (560, 1360):
        _glow(img, x, 120, 90, (255, 236, 190), 120)
    return img


def shousha():
    """昭和30年代の商社の応接。机と書類棚。"""
    img = base((222, 216, 202), (194, 186, 170))
    d = _d(img)
    wood_floor(img, FLOOR, col=(132, 104, 76), line=(112, 88, 64))
    _window(d, 640, 140, 1280, 460, sky=(176, 200, 218))
    for x in (90, 1560):                                                     # 書類棚
        d.rectangle([x, 260, x + 270, FLOOR], fill=(150, 120, 88), outline=(110, 86, 60), width=5)
        for y in range(300, FLOOR - 40, 90):
            d.line([(x, y), (x + 270, y)], fill=(110, 86, 60), width=5)
    _desk(d, 660, 660, 600)
    return img


def zukai():
    """図解用。リレー（電磁石と接点）と、そろばんの珠。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (32, 38, 50), (18, 22, 30)), (0, 0))
    d = _d(img)
    d.rectangle([760, 380, 880, 620], fill=(180, 110, 60))                  # コイル
    for y in range(390, 620, 16):
        d.line([(760, y), (880, y)], fill=(140, 80, 40), width=4)
    d.line([(820, 360), (1120, 330)], fill=(200, 200, 210), width=10)       # 接点の板
    d.ellipse([1100, 310, 1140, 350], fill=(236, 206, 90))
    d.ellipse([1100, 380, 1140, 420], fill=(236, 206, 90))
    d.line([(1120, 420), (1120, 560)], fill=(200, 200, 210), width=6)
    for k in range(5):                                                      # そろばんの珠
        d.ellipse([700 + k * 110, 700, 780 + k * 110, 760], fill=(160, 120, 80))
    d.ellipse([700 + 5 * 110 + 40, 640, 780 + 5 * 110 + 40, 700], fill=(200, 150, 90))
    d.line([(680, 730), (1360, 730)], fill=(120, 110, 100), width=4)
    return img


def haneda():
    """昭和30年代の空港。プロペラ機。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (170, 200, 226), (214, 218, 216)), (0, 0))
    d = _d(img)
    d.rectangle([0, 620, W, H], fill=(150, 150, 146))
    d.ellipse([1000, 440, 1760, 560], fill=(210, 214, 220))                # 胴体
    d.polygon([(1240, 500), (1520, 500), (1420, 620), (1320, 620)], fill=(190, 194, 200))   # 翼
    d.polygon([(1700, 470), (1780, 360), (1800, 470)], fill=(190, 194, 200))                 # 尾翼
    for x in (1300, 1460):
        d.ellipse([x - 10, 460, x + 10, 540], fill=(80, 80, 86))
    d.rectangle([120, 520, 600, 620], fill=(190, 176, 150))                # 荷物台
    for k in range(3):
        d.rectangle([160 + k * 140, 450, 280 + k * 140, 520], fill=(150, 120, 90), outline=(110, 86, 60), width=4)
    return img


def hotel():
    """夜の宿の部屋。机に広げた計算機と工具。"""
    img = base((100, 92, 84), (66, 60, 56))
    d = _d(img)
    tatami_floor(img, FLOOR)
    _window(d, 700, 150, 1220, 440, sky=(40, 46, 70), frame=(70, 60, 54))
    d.rectangle([500, 640, 1420, 690], fill=(120, 92, 66))                  # 座卓
    _big_calc(d, 960, 640, 0.8)
    for k in range(20):                                                     # 配線
        d.line([(830 + k * 13, 640), (800 + k * 17, 700 + (k % 4) * 10)], fill=(200, 60 + k * 8, 60), width=3)
    _glow(img, 1500, 300, 180, (255, 210, 140), 80)
    return img


def jimusho():
    """1957年の事務所。机と黒板。"""
    img = base((224, 218, 204), (196, 188, 172))
    d = _d(img)
    wood_floor(img, FLOOR, col=(130, 102, 76), line=(110, 86, 64))
    d.rectangle([600, 170, 1320, 460], fill=(54, 70, 62), outline=(110, 90, 66), width=12)
    for x in (120, 1440):
        _desk(d, x, 660, 380)
    return img


def setsumei():
    """販売店向けの説明会の会場。並んだ椅子と演台。"""
    img = base((218, 214, 204), (190, 184, 172))
    d = _d(img)
    wood_floor(img, FLOOR, col=(140, 112, 84), line=(120, 94, 70))
    d.rectangle([300, 120, 1620, 200], fill=(120, 60, 60))
    d.rectangle([820, 560, 1100, 700], fill=(130, 100, 72))                 # 演台
    for row in range(2):
        for k in range(8):
            x = 160 + k * 220
            y = 760 + row * 80
            d.rectangle([x, y, x + 120, y + 20], fill=(90, 100, 110))
    return img


def kaigi():
    """1970年代の会議室。長机とホワイトボード。"""
    img = base((226, 226, 222), (198, 198, 194))
    d = _d(img)
    wood_floor(img, FLOOR, col=(150, 132, 110), line=(130, 114, 94))
    d.rectangle([600, 170, 1320, 460], fill=(246, 246, 244), outline=(160, 160, 156), width=10)
    d.rectangle([200, 700, 1720, 750], fill=(160, 130, 96))
    for x in range(260, 1700, 240):
        d.rectangle([x, 620, x + 90, 700], fill=(80, 96, 120))
    return img


def kinenkan():
    """記念館の展示室。台の上の古い計算機に光。"""
    img = base((70, 66, 64), (40, 38, 38))
    d = _d(img)
    wood_floor(img, FLOOR, col=(80, 64, 52), line=(64, 52, 42))
    d.rectangle([740, 640, 1180, 720], fill=(110, 90, 70))
    _big_calc(d, 960, 640, 1.0)
    _glow(img, 960, 420, 320, (255, 230, 180), 90)
    return img


def shiryo():
    """新聞・書類の面。論争の章で使う。"""
    img = base((238, 234, 224), (212, 206, 194))
    d = _d(img)
    d.rectangle([180, 90, 1740, 990], fill=(250, 248, 242), outline=(168, 160, 146), width=8)
    d.rectangle([240, 150, 1680, 170], fill=(120, 112, 100))
    for y in range(230, 950, 46):
        w = 1440 if (y // 46) % 5 else 900
        d.rectangle([240, y, 240 + w, y + 18], fill=(196, 190, 178))
    return img


def sekai():
    """暗い地に世界地図の点。現代の広がりの章で使う。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (20, 36, 50), (12, 20, 30)), (0, 0))
    d = _d(img)
    lands = [(330, 330, 300, 170), (470, 700, 130, 190), (960, 330, 140, 110),
             (1010, 620, 160, 210), (1330, 360, 330, 180), (1500, 640, 90, 60),
             (1620, 780, 150, 90), (1590, 400, 30, 60)]
    for y in range(120, 980, 26):
        for x in range(60, 1880, 26):
            for cx, cy, rx, ry in lands:
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1:
                    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(110, 190, 170))
                    break
    for cx, cy in ((1590, 420), (1450, 520), (960, 330), (330, 330), (1030, 620)):
        _glow(img, cx, cy, 60, (255, 220, 140), 150)
    return img


LOCATIONS = {
    "cs_ima": ima, "cs_machi": machi, "cs_tenji0": tenji0, "cs_koba": koba, "cs_tenji": tenji, "cs_shousha": shousha,
    "cs_zukai": zukai, "cs_haneda": haneda, "cs_hotel": hotel, "cs_jimusho": jimusho,
    "cs_setsumei": setsumei, "cs_kaigi": kaigi, "cs_kinenkan": kinenkan, "cs_shiryo": shiryo,
    "cs_sekai": sekai,
}

CARDS = ["1946", "1949", "1954", "1956", "1957", "1964", "1972"]


def year_card(text: str) -> Image.Image:
    """黒地に年号だけのカード。キャラと同居させない単独シーンで使う。"""
    img = Image.new("RGB", (W, H), (18, 18, 20))
    d = _d(img)
    from ytf.config import Config, resolve_font
    Config.load()
    font = ImageFont.truetype(resolve_font("w9"), 150)
    bb = d.textbbox((0, 0), text, font=font)
    d.text(((W - (bb[2] - bb[0])) // 2, (H - (bb[3] - bb[1])) // 2 - 40),
           text, font=font, fill=(238, 234, 226))
    d.line([(W // 2 - 220, H // 2 + 130), (W // 2 + 220, H // 2 + 130)],
           fill=(150, 146, 138), width=4)
    return img


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, fn in LOCATIONS.items():
        if only and name not in only:
            continue
        fn().save(OUT / f"{name}.png")
        print(f"生成完了: {name}.png")
    for y in CARDS:
        if only and f"cs_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"cs_card_{y}.png")
        print(f"生成完了: cs_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
