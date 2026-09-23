#!/usr/bin/env python3
"""牛丼が消えた日・安部修仁回（47_牛丼が消えた日 / slug=yoshinoya-abe）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。

方針は東京タワー回（gen_naito_bgs.py）と同じ。加えて:
- 実在チェーンの看板・ロゴ・店の配色は描かない（商標）。
  牛丼屋は「U字のカウンターと寸胴鍋」だけで表す

実行: PYTHONPATH=. python scripts/gen_gyudon_bgs.py [名前...]
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


def _bowl(d, cx, cy, r, beef=True):
    """丼。beef=False なら空の丼。"""
    d.pieslice([cx - r, cy - r * 0.6, cx + r, cy + r * 0.9], 0, 180, fill=(40, 40, 46))
    d.ellipse([cx - r, cy - r * 0.35, cx + r, cy + r * 0.35], fill=(60, 58, 62),
              outline=(30, 30, 34), width=4)
    if beef:
        d.ellipse([cx - r * 0.86, cy - r * 0.26, cx + r * 0.86, cy + r * 0.26],
                  fill=(150, 96, 60))
        for k in range(5):
            x = cx - r * 0.6 + k * r * 0.3
            d.arc([x - r * 0.2, cy - r * 0.18, x + r * 0.2, cy + r * 0.14], 200, 340,
                  fill=(206, 170, 120), width=3)
    else:
        d.ellipse([cx - r * 0.86, cy - r * 0.26, cx + r * 0.86, cy + r * 0.26],
                  fill=(236, 236, 230))


def _counter(img, y=700):
    """U字カウンターを正面から見た形。店の場面で共用する。"""
    d = _d(img)
    d.rectangle([0, y, W, y + 46], fill=(176, 140, 98))
    d.rectangle([0, y + 46, W, FLOOR + 40], fill=(126, 98, 70))
    for x in range(80, W, 240):                                     # 丸椅子
        d.ellipse([x, FLOOR - 40, x + 110, FLOOR - 4], fill=(120, 44, 40))
        d.rectangle([x + 48, FLOOR - 6, x + 62, FLOOR + 60], fill=(90, 90, 96))


# ------------------------------------------------------------ 現代
def ima():
    """現代の台所つきの部屋。茶番で牛丼を作る。"""
    img = base((248, 242, 232), (226, 216, 200))
    d = _d(img)
    wood_floor(img, FLOOR)
    _window(d, 760, 170, 1160, 520, sky=(176, 204, 228))
    d.rectangle([1320, 560, 1860, 610], fill=(200, 200, 204))       # 台所の天板
    d.rectangle([1320, 610, 1860, FLOOR], fill=(220, 214, 204))
    d.ellipse([1400, 540, 1560, 570], fill=(60, 60, 66))            # 鍋
    d.rectangle([1410, 480, 1550, 556], fill=(150, 152, 158))
    d.rectangle([620, 760, 1300, 800], fill=(176, 138, 98))         # ちゃぶ台
    d.rectangle([660, 800, 690, 1000], fill=(150, 116, 82))
    d.rectangle([1230, 800, 1260, 1000], fill=(150, 116, 82))
    _bowl(d, 960, 740, 70)
    return img


# ------------------------------------------------------------ 明治・築地
def uogashi():
    """明治の日本橋・魚河岸。荷車と桶が並ぶ。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (196, 206, 214), (176, 168, 150)), (0, 0))
    d = _d(img)
    d.rectangle([0, 720, W, H], fill=(128, 116, 98))
    for x in range(0, W, 380):                                      # 商家の屋根
        d.rectangle([x + 20, 300, x + 360, 720], fill=(110, 90, 72), outline=(80, 64, 50), width=6)
        d.polygon([(x, 310), (x + 190, 200), (x + 380, 310)], fill=(70, 66, 64))
        d.rectangle([x + 60, 360, x + 320, 440], fill=(200, 190, 170))  # のれん
    for i, x in enumerate((160, 700, 1300)):                         # 桶
        d.ellipse([x, 760 + i * 10, x + 160, 820 + i * 10], fill=(150, 116, 76),
                  outline=(100, 76, 50), width=6)
        d.rectangle([x, 790 + i * 10, x + 160, 880 + i * 10], fill=(150, 116, 76))
    return img


def tsukiji():
    """築地の小さな牛丼屋。昭和。カウンターの奥に大鍋。"""
    img = base((204, 188, 160), (170, 152, 126))
    d = _d(img)
    wood_floor(img, FLOOR, col=(116, 88, 62), line=(96, 72, 50))
    d.rectangle([0, 150, W, 200], fill=(96, 74, 54))                # 梁
    for x in (420, 1260):                                           # 大鍋と湯気
        d.ellipse([x, 520, x + 240, 580], fill=(70, 70, 76))
        d.rectangle([x + 10, 440, x + 230, 552], fill=(120, 122, 128))
        for k in range(3):
            d.arc([x + 40 + k * 50, 330, x + 110 + k * 50, 440], 180, 360,
                  fill=(236, 236, 236), width=5)
    _counter(img, 640)
    hanging_bulb(img, 960, warm=True, ly=40)
    return img


def tenpo():
    """1970年代のチェーン店の店内。明るい蛍光灯とカウンター。"""
    img = base((236, 232, 222), (212, 204, 190))
    d = _d(img)
    wood_floor(img, FLOOR, col=(150, 120, 90), line=(130, 104, 78))
    for x in range(160, W, 400):                                    # 蛍光灯
        d.rectangle([x, 80, x + 260, 100], fill=(250, 250, 244))
    d.rectangle([200, 220, 1720, 520], fill=(222, 214, 200))        # 厨房の壁
    for x in (480, 1180):
        d.ellipse([x, 460, x + 260, 520], fill=(70, 70, 76))
        d.rectangle([x + 10, 380, x + 250, 490], fill=(160, 162, 168))
    d.rectangle([860, 250, 1060, 330], fill=(250, 248, 240), outline=(170, 160, 146), width=4)  # 品書き
    _counter(img, 620)
    for x in (380, 900, 1500):
        _bowl(d, x, 610, 44)
    return img


def jimusho():
    """本社・事務所。会社の場面で共用。"""
    img = base((210, 202, 186), (178, 168, 152))
    d = _d(img)
    wood_floor(img, FLOOR, col=(116, 88, 62), line=(96, 72, 50))
    _window(d, 1300, 160, 1800, 580)
    d.rectangle([140, 200, 700, 560], fill=(236, 232, 222), outline=(140, 120, 96), width=6)
    for k, h in enumerate((120, 180, 250, 300, 220)):               # 店舗数の棒グラフ
        d.rectangle([200 + k * 100, 520 - h, 260 + k * 100, 520], fill=(180, 90, 60))
    d.rectangle([720, 700, 1560, 748], fill=(140, 108, 76))
    d.rectangle([760, 748, 800, 990], fill=(118, 90, 64))
    d.rectangle([1480, 748, 1520, 990], fill=(118, 90, 64))
    return img


def kojo():
    """加工工場。乾燥肉と粉のたれを作るライン。"""
    img = base((196, 200, 204), (156, 160, 164))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(120, 124, 128))
    d.rectangle([0, 600, W, 660], fill=(90, 94, 100))               # コンベヤ
    for x in range(40, W, 120):
        d.ellipse([x, 640, x + 40, 680], fill=(70, 72, 76))
    for x in range(100, W, 260):                                    # 袋詰めの粉
        d.rectangle([x, 520, x + 120, 600], fill=(226, 214, 180), outline=(170, 158, 120), width=4)
    d.rectangle([700, 180, 1220, 520], fill=(176, 182, 188), outline=(120, 126, 132), width=8)  # 乾燥機
    for k in range(4):
        d.rectangle([760, 230 + k * 70, 1160, 260 + k * 70], fill=(140, 146, 152))
    return img


def america():
    """1970年代のアメリカの大学町。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (170, 200, 226), (210, 208, 196)), (0, 0))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(128, 150, 104))
    d.rectangle([520, 300, 1400, 760], fill=(170, 110, 86), outline=(120, 76, 60), width=8)  # レンガの校舎
    d.polygon([(480, 310), (960, 170), (1440, 310)], fill=(90, 80, 76))
    for x in range(580, 1360, 110):
        for y in (380, 520):
            d.rectangle([x, y, x + 60, y + 90], fill=(220, 226, 230))
    for x in (120, 1600):                                           # 木
        d.rectangle([x + 60, 560, x + 90, 780], fill=(96, 76, 56))
        d.ellipse([x, 400, x + 150, 600], fill=(96, 136, 84))
    return img


def heya():
    """狭い部屋と電話。倒産を知らされる場面。"""
    img = base((150, 140, 126), (110, 102, 92))
    d = _d(img)
    tatami_floor(img, FLOOR)
    _window(d, 1300, 180, 1700, 520, sky=(90, 100, 124))
    d.rectangle([200, 640, 520, 700], fill=(120, 96, 70))           # 小机と黒電話
    d.rectangle([280, 590, 440, 640], fill=(30, 30, 34))
    d.ellipse([300, 560, 420, 600], fill=(40, 40, 44))
    hanging_bulb(img, 960, warm=True, ly=30)
    return img


def kaigi():
    """会議室。再建の話し合い。"""
    img = base((200, 196, 188), (164, 160, 152))
    d = _d(img)
    wood_floor(img, FLOOR, col=(110, 90, 70), line=(92, 74, 56))
    d.rectangle([300, 180, 1620, 520], fill=(62, 74, 66), outline=(90, 76, 60), width=12)  # 黒板
    for y in (250, 330, 410):
        d.line([(380, y), (1100 + (y % 200), y)], fill=(200, 208, 200), width=4)
    d.rectangle([200, 700, 1720, 750], fill=(130, 100, 72))         # 長机
    return img


def shukai():
    """社員が集まるホール。支援先が決まった場面。"""
    img = base((190, 180, 164), (150, 140, 126))
    d = _d(img)
    wood_floor(img, FLOOR, col=(140, 110, 80), line=(120, 94, 68))
    d.rectangle([520, 200, 1400, 330], fill=(160, 40, 40))          # 壇上の幕
    d.rectangle([600, 330, 1320, 380], fill=(120, 30, 30))
    for x in range(40, W, 130):                                     # 並んだ椅子
        d.rectangle([x, 820, x + 80, 860], fill=(90, 90, 96))
    return img


def gyoretsu():
    """店の前の行列。夕方。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (236, 190, 150), (170, 150, 150)), (0, 0))
    d = _d(img)
    d.rectangle([0, 780, W, H], fill=(120, 116, 112))
    d.rectangle([1100, 260, 1880, 780], fill=(214, 206, 192), outline=(150, 140, 126), width=8)
    d.rectangle([1180, 440, 1800, 780], fill=(240, 226, 180))       # 明るい店内
    d.rectangle([1100, 300, 1880, 380], fill=(150, 140, 126))       # 無地の看板
    for k in range(9):                                              # 並ぶ人の影
        x = 80 + k * 110
        d.ellipse([x, 560, x + 60, 620], fill=(80, 76, 86))
        d.rectangle([x - 6, 620, x + 66, 780], fill=(80, 76, 86))
    return img


def bokujo():
    """牧場。世界の牛肉の産地を調べる場面。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (168, 200, 228), (216, 218, 200)), (0, 0))
    d = _d(img)
    d.polygon([(0, 560), (600, 470), (1300, 520), (W, 460), (W, H), (0, H)], fill=(140, 170, 100))
    for x in range(0, W, 160):                                      # 柵
        d.rectangle([x, 700, x + 12, 820], fill=(150, 120, 86))
    d.rectangle([0, 730, W, 744], fill=(150, 120, 86))
    for (x, y) in ((500, 600), (1250, 620)):                        # 牛の影
        d.ellipse([x, y, x + 220, y + 110], fill=(70, 56, 46))
        d.ellipse([x + 190, y - 20, x + 270, y + 50], fill=(70, 56, 46))
        for lx in (20, 70, 140, 190):
            d.rectangle([x + lx, y + 90, x + lx + 16, y + 160], fill=(70, 56, 46))
    return img


def shiryo():
    """新聞・書類の面。ニュースと論争の章で使う。"""
    img = base((238, 234, 224), (212, 206, 194))
    d = _d(img)
    d.rectangle([180, 90, 1740, 990], fill=(250, 248, 242), outline=(168, 160, 146), width=8)
    d.rectangle([240, 150, 1680, 170], fill=(120, 112, 100))
    for y in range(230, 950, 46):
        w = 1440 if (y // 46) % 5 else 900
        d.rectangle([240, y, 240 + w, y + 18], fill=(196, 190, 178))
    return img


LOCATIONS = {
    "gd_ima": ima, "gd_uogashi": uogashi, "gd_tsukiji": tsukiji, "gd_tenpo": tenpo,
    "gd_jimusho": jimusho, "gd_kojo": kojo, "gd_america": america,
    "gd_heya": heya, "gd_kaigi": kaigi, "gd_shukai": shukai, "gd_gyoretsu": gyoretsu,
    "gd_bokujo": bokujo, "gd_shiryo": shiryo,
}

CARDS = ["1899", "1968", "1980", "1992", "2003", "2004", "2006"]


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
        if only and f"gd_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"gd_card_{y}.png")
        print(f"生成完了: gd_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
