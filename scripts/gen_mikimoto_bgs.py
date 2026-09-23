#!/usr/bin/env python3
"""養殖真珠の誕生・御木本幸吉回（52_養殖真珠の誕生 / slug=mikimoto-pearl）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針は蚊取り線香回（gen_katori_bgs.py）と同じ。
実在メーカーの商標（ロゴ・店名の文字）は描かない。

実行: PYTHONPATH=. python scripts/gen_mikimoto_bgs.py [名前...]
"""

import math
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


def _pearl(img, cx, cy, r):
    """光る真珠1粒。"""
    d = _d(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(236, 230, 226), outline=(190, 184, 186), width=2)
    d.ellipse([cx - r * 0.5, cy - r * 0.6, cx - r * 0.05, cy - r * 0.15], fill=(255, 255, 255))


def _sea(img, top, col_top, col_bot):
    img.paste(vgrad((W, H - top), col_top, col_bot), (0, top))


def _islands(d, y, col):
    for x0, w, h in ((80, 360, 90), (560, 240, 60), (1320, 420, 110), (1760, 200, 50)):
        d.ellipse([x0, y - h, x0 + w, y + h * 0.4], fill=col)


def _rafts(d, y0, n=5):
    for k in range(n):
        x = 180 + k * 330
        y = y0 + (k % 2) * 40
        d.rectangle([x, y, x + 240, y + 14], fill=(130, 100, 70))
        d.rectangle([x, y + 40, x + 240, y + 54], fill=(130, 100, 70))
        for j in range(5):
            d.line([(x + 20 + j * 50, y + 14), (x + 20 + j * 50, y + 90)], fill=(90, 80, 70), width=3)


# ------------------------------------------------------------ 現代
def ima():
    """現代の台所。ボウルのアサリと、宝石箱。"""
    img = base((236, 232, 222), (214, 208, 196))
    d = _d(img)
    wood_floor(img, FLOOR, col=(170, 140, 104), line=(150, 122, 90))
    d.rectangle([0, 560, W, 660], fill=(200, 196, 186))                 # 調理台
    d.rectangle([0, 660, W, FLOOR], fill=(150, 130, 108))
    _window(d, 700, 150, 1220, 470, sky=(176, 210, 232))
    d.ellipse([820, 500, 1100, 580], fill=(210, 220, 226), outline=(160, 170, 176), width=4)   # ボウル
    for k in range(10):
        x = 860 + (k % 5) * 44
        y = 520 + (k // 5) * 22
        d.ellipse([x, y, x + 40, y + 24], fill=(150, 130, 110), outline=(100, 86, 70), width=2)
    d.rectangle([1300, 500, 1480, 560], fill=(40, 40, 60), outline=(20, 20, 30), width=3)     # 宝石箱
    for k in range(7):
        _pearl(img, 1320 + k * 24, 530, 10)
    return img


# ------------------------------------------------------------ 鳥羽・少年期
def udonya():
    """明治の鳥羽のうどん屋。釜と、のれん。"""
    img = base((212, 196, 170), (180, 162, 136))
    d = _d(img)
    wood_floor(img, FLOOR, col=(128, 98, 70), line=(106, 80, 56))
    d.rectangle([0, 100, W, 220], fill=(60, 80, 110))                   # のれん
    for x in range(160, W, 300):
        d.line([(x, 100), (x, 220)], fill=(44, 60, 86), width=6)
    d.ellipse([160, 560, 520, 660], fill=(90, 86, 80))                   # 釜
    d.rectangle([200, 600, 480, 760], fill=(110, 90, 70))
    _glow(img, 340, 540, 120, (250, 250, 250), 80)
    d = _d(img)
    d.rectangle([1100, 660, 1800, 700], fill=(140, 108, 76))             # 台
    for k in range(4):
        d.ellipse([1150 + k * 160, 620, 1270 + k * 160, 660], fill=(200, 60, 50))   # 丼
    return img


def minato():
    """明治の鳥羽の港。沖に帆柱の洋船。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (170, 204, 230), (214, 222, 222)), (0, 0))
    _sea(img, 460, (90, 140, 170), (60, 100, 130))
    d = _d(img)
    _islands(d, 470, (96, 124, 96))
    d.polygon([(1100, 560), (1600, 560), (1540, 640), (1160, 640)], fill=(60, 50, 44))   # 船体
    for x in (1240, 1420):
        d.line([(x, 560), (x, 250)], fill=(70, 60, 50), width=10)
        d.polygon([(x - 90, 300), (x + 90, 300), (x + 70, 470), (x - 70, 470)], fill=(236, 232, 220))
    d.rectangle([0, 760, W, H], fill=(150, 130, 100))                    # 岸壁
    return img


def yokohama():
    """明治の横浜の港の倉庫。俵と木箱。"""
    img = base((206, 196, 178), (170, 160, 142))
    d = _d(img)
    wood_floor(img, FLOOR, col=(120, 96, 70), line=(100, 80, 58))
    d.rectangle([640, 120, 1280, 560], fill=(150, 186, 206), outline=(90, 80, 70), width=12)   # 開口部
    d.polygon([(700, 520), (1220, 520), (1180, 480), (740, 480)], fill=(60, 50, 44))
    for row in range(3):
        for k in range(4):
            x, y = 90 + k * 120, FLOOR - 20 - row * 80
            d.ellipse([x, y - 70, x + 110, y], fill=(200, 176, 120), outline=(150, 126, 80), width=3)
    for row in range(3):
        for k in range(3):
            x, y = 1420 + k * 140, FLOOR - 10 - row * 110
            d.rectangle([x, y - 104, x + 130, y], fill=(170, 136, 96), outline=(110, 84, 58), width=4)
    return img


def ie():
    """明治の家の座敷。"""
    img = base((206, 190, 162), (172, 154, 128))
    d = _d(img)
    tatami_floor(img, FLOOR)
    d.rectangle([380, 170, 1160, 620], fill=(226, 216, 196), outline=(110, 90, 70), width=10)
    for gx in range(480, 1160, 130):
        d.line([(gx, 170), (gx, 620)], fill=(170, 150, 124), width=5)
    d.rectangle([1320, 560, 1760, 640], fill=(110, 84, 58))             # 文机
    d.rectangle([1360, 500, 1560, 560], fill=(236, 230, 214))           # 帳面
    return img


def ie_yoru():
    """夜の座敷。行灯。"""
    img = base((96, 84, 72), (60, 52, 46))
    d = _d(img)
    tatami_floor(img, FLOOR)
    d.rectangle([380, 170, 1160, 600], fill=(170, 156, 130), outline=(90, 74, 58), width=10)
    d.rectangle([1480, 560, 1580, 740], fill=(236, 214, 150), outline=(120, 96, 64), width=6)
    _glow(img, 1530, 650, 200, (255, 206, 130), 90)
    return img


def hinpyoukai():
    """明治の品評会の会場。台に並ぶ海産物。"""
    img = base((226, 218, 200), (196, 186, 166))
    d = _d(img)
    wood_floor(img, FLOOR, col=(140, 110, 78), line=(120, 92, 64))
    for x in (120, 1720):
        d.rectangle([x, 100, x + 80, FLOOR], fill=(200, 184, 150))
    d.rectangle([300, 120, 1620, 200], fill=(170, 60, 50))              # 幕
    for x0 in (360, 1160):
        d.rectangle([x0, 640, x0 + 420, 700], fill=(150, 116, 84))
        for k in range(5):
            cx = x0 + 50 + k * 80
            d.ellipse([cx - 30, 600, cx + 30, 640], fill=(170, 160, 140), outline=(120, 110, 96), width=3)
    return img


def rinkai():
    """海辺の臨海実験所。窓の外は海、机に顕微鏡と水槽。"""
    img = base((218, 216, 206), (188, 184, 172))
    d = _d(img)
    wood_floor(img, FLOOR, col=(124, 98, 72), line=(104, 82, 60))
    _window(d, 600, 140, 1320, 480, sky=(120, 170, 200))
    d.rectangle([600, 360, 1320, 480], fill=(80, 130, 160))             # 窓の外の海
    d.rectangle([90, 620, 700, 660], fill=(140, 108, 76))                # 机
    d.rectangle([150, 540, 400, 620], fill=(180, 210, 214), outline=(120, 140, 140), width=4)   # 水槽
    d.rectangle([520, 560, 570, 620], fill=(60, 64, 70))                 # 顕微鏡
    d.line([(545, 560), (590, 500)], fill=(60, 64, 70), width=14)
    return img


def ikada():
    """英虞湾の養殖いかだ。島と、つるした籠。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (176, 208, 232), (214, 224, 226)), (0, 0))
    _sea(img, 440, (70, 130, 150), (40, 90, 110))
    d = _d(img)
    _islands(d, 450, (80, 116, 84))
    _rafts(d, 620)
    return img


def akashio():
    """赤潮の海。茶色く濁った水面と、いかだ。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (186, 170, 160), (200, 190, 180)), (0, 0))
    _sea(img, 440, (150, 70, 50), (110, 50, 40))
    d = _d(img)
    _islands(d, 450, (90, 100, 80))
    _rafts(d, 620)
    return img


def fuyu_umi():
    """冬の赤潮の海。灰色の空と赤茶けた海、いかだ。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (150, 156, 166), (190, 194, 200)), (0, 0))
    _sea(img, 440, (120, 70, 64), (80, 48, 44))                          # 冬の赤潮
    d = _d(img)
    _islands(d, 450, (70, 86, 80))
    _rafts(d, 620)
    for k in range(40):                                                  # 雪
        x, y = (k * 197) % W, (k * 113) % 420
        d.ellipse([x, y, x + 8, y + 8], fill=(240, 244, 248))
    return img


def mise():
    """明治の銀座の真珠店。ガラスの陳列台。"""
    img = base((230, 220, 200), (204, 192, 170))
    d = _d(img)
    wood_floor(img, FLOOR, col=(150, 116, 80), line=(128, 98, 68))
    d.rectangle([640, 130, 1280, 470], fill=(170, 196, 214), outline=(90, 80, 70), width=12)   # 窓
    d.line([(960, 130), (960, 470)], fill=(90, 80, 70), width=10)
    for x0 in (160, 1240):
        d.rectangle([x0, 620, x0 + 520, 760], fill=(130, 96, 64))
        d.rectangle([x0, 520, x0 + 520, 620], fill=(206, 226, 226), outline=(150, 170, 170), width=4)
    for k in range(10):
        _pearl(img, 200 + k * 46, 590, 12)
        _pearl(img, 1280 + k * 46, 590, 12)
    hanging_bulb(img, 960, warm=True, ly=40)
    return img


def london():
    """ロンドンの店の中。洋風の壁と、新聞の束。"""
    img = base((196, 180, 170), (160, 144, 136))
    d = _d(img)
    wood_floor(img, FLOOR, col=(110, 76, 60), line=(90, 62, 50))
    for x in range(0, W, 240):                                          # 壁の羽目板
        d.rectangle([x + 20, 520, x + 220, 760], outline=(130, 110, 100), width=4)
    _window(d, 680, 120, 1240, 460, sky=(180, 186, 196), frame=(80, 60, 50))
    d.rectangle([1380, 640, 1800, 690], fill=(120, 84, 60))              # 机
    for k in range(3):
        d.rectangle([1420 + k * 12, 600 - k * 10, 1640 + k * 12, 640 - k * 10], fill=(236, 232, 220),
                    outline=(170, 166, 156), width=2)
    return img


def edison():
    """発明家の研究所。電球と、棚の機械。"""
    img = base((150, 132, 110), (110, 96, 80))
    d = _d(img)
    wood_floor(img, FLOOR, col=(100, 76, 56), line=(80, 60, 44))
    for y in (300, 480):
        d.rectangle([80, y, 760, y + 16], fill=(90, 68, 48))
        for x in range(110, 740, 110):
            d.rectangle([x, y - 70, x + 70, y], fill=(120, 110, 100), outline=(70, 64, 60), width=3)
    for k, x in enumerate((1100, 1300, 1500, 1700)):                    # 電球
        d.line([(x, 0), (x, 180 + k % 2 * 40)], fill=(40, 34, 28), width=4)
        _glow(img, x, 200 + k % 2 * 40, 60, (255, 220, 140), 140)
        d = _d(img)
        d.ellipse([x - 22, 180 + k % 2 * 40, x + 22, 226 + k % 2 * 40], fill=(255, 236, 180))
    return img


def kobe():
    """神戸の建物の前。焼却の煙。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (180, 196, 214), (214, 214, 206)), (0, 0))
    d = _d(img)
    d.rectangle([300, 160, 1620, 700], fill=(196, 186, 170), outline=(140, 130, 116), width=8)   # 建物
    for x in range(380, 1560, 200):
        d.rectangle([x, 240, x + 110, 400], fill=(120, 140, 160))
        d.rectangle([x, 480, x + 110, 640], fill=(120, 140, 160))
    d.rectangle([0, 700, W, H], fill=(170, 164, 150))
    d.ellipse([820, 760, 1100, 840], fill=(90, 80, 70))                  # 焼却の火
    _glow(img, 960, 760, 120, (255, 140, 60), 150)
    for k in range(4):
        _glow(img, 940 + k * 30, 640 - k * 90, 80, (120, 120, 120), 120)
    return img


def zukai():
    """図解用。真珠の断面（核と、重なった層）。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (30, 36, 50), (16, 20, 30)), (0, 0))
    d = _d(img)
    cx, cy = 960, 540
    for k in range(18, 0, -1):                                           # 層
        r = 150 + k * 9
        c = 190 + (k % 2) * 30
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(c, c - 6, c - 10))
    d.ellipse([cx - 150, cy - 150, cx + 150, cy + 150], fill=(206, 190, 160))   # 核
    for k in range(8):
        a = k * math.pi / 4
        d.line([(cx + 150 * math.cos(a), cy + 150 * math.sin(a)),
                (cx + 312 * math.cos(a), cy + 312 * math.sin(a))], fill=(180, 170, 170), width=1)
    return img


def hama():
    """今の真珠の選別台。並べた真珠と作業机。"""
    img = base((230, 230, 228), (206, 206, 204))
    d = _d(img)
    wood_floor(img, FLOOR, col=(150, 140, 126), line=(130, 120, 108))
    _window(d, 640, 130, 1280, 440, sky=(160, 200, 226))
    d.rectangle([600, 360, 1320, 440], fill=(70, 130, 150))
    d.rectangle([520, 640, 1400, 690], fill=(60, 70, 90))                # 選別台
    for row in range(3):
        for k in range(16):
            _pearl(img, 560 + k * 52, 600 - row * 26 + 40, 10)
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


LOCATIONS = {
    "mk_ima": ima, "mk_udonya": udonya, "mk_minato": minato, "mk_yokohama": yokohama,
    "mk_ie": ie, "mk_ie_yoru": ie_yoru, "mk_hinpyoukai": hinpyoukai, "mk_rinkai": rinkai,
    "mk_ikada": ikada, "mk_akashio": akashio, "mk_fuyu_umi": fuyu_umi, "mk_mise": mise,
    "mk_london": london, "mk_edison": edison, "mk_kobe": kobe, "mk_zukai": zukai,
    "mk_hama": hama, "mk_shiryo": shiryo,
}

CARDS = ["1858", "1878", "1888", "1892", "1893", "1905", "1932"]


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
        if only and f"mk_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"mk_card_{y}.png")
        print(f"生成完了: mk_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
