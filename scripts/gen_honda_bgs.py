#!/usr/bin/env python3
"""明治神宮の森・本多静六回（48_明治神宮の森の誕生 / slug=honda-seiroku）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針は東京タワー回（gen_naito_bgs.py）と同じ。
神社の社殿は実在の意匠をなぞらず、屋根と柱だけの簡略形にする。

実行: PYTHONPATH=. python scripts/gen_honda_bgs.py [名前...]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, hanging_bulb, tatami_floor, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)


def _d(img):
    return ImageDraw.Draw(img)


def _window(d, x0, y0, x1, y1, sky=(150, 186, 214), frame=(70, 62, 56)):
    d.rectangle([x0, y0, x1, y1], fill=sky)
    d.rectangle([x0, y0, x1, y1], outline=frame, width=10)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=frame, width=8)


def _conifer(d, x, base_y, h, col=(64, 100, 70)):
    """針葉樹（マツ・スギ・ヒノキ）。三角を重ねる。"""
    d.rectangle([x - h * 0.03, base_y - h * 0.2, x + h * 0.03, base_y], fill=(96, 76, 56))
    for k in range(3):
        top = base_y - h + k * h * 0.22
        w = h * (0.18 + k * 0.08)
        d.polygon([(x, top), (x - w, top + h * 0.38), (x + w, top + h * 0.38)], fill=col)


def _broadleaf(d, x, base_y, h, col=(70, 118, 72)):
    """常緑広葉樹（カシ・シイ・クス）。丸い樹冠。"""
    d.rectangle([x - h * 0.04, base_y - h * 0.45, x + h * 0.04, base_y], fill=(96, 76, 56))
    r = h * 0.32
    for dx, dy in ((0, -0.72), (-0.22, -0.6), (0.22, -0.6), (0, -0.5)):
        cx, cy = x + dx * h, base_y + dy * h
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)


# ------------------------------------------------------------ 現代
def ima():
    """現代の部屋。窓辺に植木鉢。"""
    img = base((248, 242, 232), (226, 216, 200))
    d = _d(img)
    wood_floor(img, FLOOR)
    _window(d, 740, 150, 1180, 540, sky=(176, 204, 228))
    d.rectangle([620, 760, 1300, 800], fill=(176, 138, 98))
    d.rectangle([660, 800, 690, 1000], fill=(150, 116, 82))
    d.rectangle([1230, 800, 1260, 1000], fill=(150, 116, 82))
    d.polygon([(900, 700), (1020, 700), (1000, 762), (920, 762)], fill=(170, 98, 62))  # 鉢
    d.ellipse([900, 690, 1020, 712], fill=(90, 66, 46))
    return img


def mori():
    """現代の深い森。明治神宮の内苑を思わせる常緑広葉樹の森と参道。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (150, 176, 150), (86, 110, 84)), (0, 0))
    d = _d(img)
    d.polygon([(760, H), (1160, H), (1020, 560), (900, 560)], fill=(200, 190, 160))  # 砂利の参道
    for x in list(range(-60, 700, 150)) + list(range(1220, 2000, 150)):
        _broadleaf(d, x, 900 + (x % 60), 620 + (x % 90), col=(58 + (x % 30), 100, 62))
    for x in (60, 330, 600, 1320, 1580, 1840):
        _broadleaf(d, x, 1000, 520, col=(44, 86, 50))
    return img


# ------------------------------------------------------------ 埼玉・少年期
def nouka():
    """埼玉の農村。田んぼと農家。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (172, 204, 228), (214, 218, 200)), (0, 0))
    d = _d(img)
    d.rectangle([0, 560, W, H], fill=(150, 164, 104))
    for y in range(600, H, 70):                                     # 田の畔
        d.line([(0, y), (W, y + 20)], fill=(126, 140, 86), width=6)
    d.rectangle([1260, 380, 1760, 620], fill=(120, 96, 72))         # 農家
    d.polygon([(1210, 400), (1510, 250), (1810, 400)], fill=(150, 130, 90))
    for x in (160, 420):
        _broadleaf(d, x, 600, 360)
    return img


def shosei():
    """明治の東京の家。書生の部屋。"""
    img = base((212, 196, 170), (176, 160, 136))
    d = _d(img)
    tatami_floor(img, FLOOR)
    d.rectangle([380, 170, 1160, 640], fill=(226, 216, 196), outline=(110, 90, 70), width=10)  # 障子
    for gx in range(480, 1160, 130):
        d.line([(gx, 170), (gx, 640)], fill=(170, 150, 124), width=5)
    d.rectangle([1320, 560, 1760, 610], fill=(110, 84, 58))         # 文机と本
    for k in range(4):
        d.rectangle([1360 + k * 70, 500, 1410 + k * 70, 560], fill=(160 - k * 12, 120, 90))
    hanging_bulb(img, 960, warm=True, ly=40)
    return img


def gakko():
    """山林学校の教室。窓の外に林。"""
    img = base((212, 204, 184), (184, 174, 154))
    d = _d(img)
    wood_floor(img, FLOOR, col=(120, 92, 66), line=(100, 76, 54))
    d.rectangle([520, 160, 1400, 580], fill=(46, 58, 50), outline=(88, 70, 52), width=14)
    for y in (250, 340, 430):
        d.line([(580, y), (1200 + (y % 120), y)], fill=(196, 204, 196), width=4)
    for x0 in (60, 1540):
        d.rectangle([x0, 190, x0 + 320, 560], fill=(176, 204, 222))
        for k in range(3):
            _conifer(d, x0 + 60 + k * 100, 560, 260)
        d.rectangle([x0, 190, x0 + 320, 560], outline=(70, 62, 56), width=10)
    return img


def honke():
    """本多家。診療所を兼ねた家の居間。薬棚がある。"""
    img = base((214, 204, 184), (182, 170, 150))
    d = _d(img)
    tatami_floor(img, FLOOR)
    d.rectangle([140, 200, 640, 700], fill=(140, 110, 80), outline=(100, 78, 56), width=8)  # 薬棚
    for gy in range(240, 690, 76):
        for gx in range(170, 620, 90):
            d.rectangle([gx, gy, gx + 70, gy + 56], fill=(176, 146, 110), outline=(120, 94, 68), width=3)
            d.ellipse([gx + 30, gy + 22, gx + 40, gy + 32], fill=(90, 70, 50))
    d.rectangle([900, 200, 1700, 620], fill=(226, 216, 196), outline=(110, 90, 70), width=10)
    hanging_bulb(img, 1300, warm=True, ly=40)
    return img


def doitsu():
    """ドイツの大学町と森。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (170, 196, 222), (206, 206, 196)), (0, 0))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(130, 140, 110))
    for x in range(0, W, 110):                                      # 奥の針葉樹林
        _conifer(d, x, 640, 300, col=(56, 88, 66))
    d.rectangle([620, 300, 1300, 760], fill=(200, 188, 168), outline=(140, 128, 110), width=8)  # 大学
    d.polygon([(580, 310), (960, 170), (1340, 310)], fill=(120, 70, 60))
    for x in range(680, 1260, 110):
        d.rectangle([x, 380, x + 60, 470], fill=(96, 110, 124))
        d.rectangle([x, 560, x + 60, 650], fill=(96, 110, 124))
    return img


# ------------------------------------------------------------ 日比谷
def akichi():
    """明治の日比谷。何もない広い空き地。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (190, 204, 218), (214, 208, 190)), (0, 0))
    d = _d(img)
    d.rectangle([0, 600, W, H], fill=(186, 170, 130))
    for x in range(0, W, 300):                                      # 遠くの洋館
        d.rectangle([x + 40, 440, x + 240, 600], fill=(170, 150, 130), outline=(130, 110, 94), width=4)
    for k in range(6):                                              # 地面のまだら
        x = 200 + k * 290
        d.ellipse([x, 760 + (k % 2) * 60, x + 220, 800 + (k % 2) * 60], fill=(170, 154, 116))
    return img


def ichou():
    """道路脇の大イチョウ。移植の場面。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (176, 200, 222), (216, 212, 196)), (0, 0))
    d = _d(img)
    d.rectangle([0, 720, W, H], fill=(150, 146, 140))               # 道路
    d.rectangle([0, 820, W, 850], fill=(120, 116, 110))
    d.rectangle([920, 330, 1000, 740], fill=(110, 84, 60))           # 幹
    for (cx, cy, r) in ((960, 260, 200), (840, 330, 150), (1080, 330, 150), (960, 380, 170)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(232, 196, 60))
    for x in range(200, 1800, 220):                                  # 移植用のレール
        d.rectangle([x, 880, x + 180, 890], fill=(90, 90, 96))
    d.line([(0, 870), (W, 870)], fill=(90, 90, 96), width=6)
    d.line([(0, 900), (W, 900)], fill=(90, 90, 96), width=6)
    return img


def kaigi():
    """造営局の会議室。机に森の図面。"""
    img = base((210, 202, 186), (178, 168, 152))
    d = _d(img)
    wood_floor(img, FLOOR, col=(116, 88, 62), line=(96, 72, 50))
    d.rectangle([220, 170, 1700, 560], fill=(236, 232, 214), outline=(140, 120, 96), width=8)  # 断面図
    d.line([(280, 500), (1640, 500)], fill=(120, 100, 80), width=4)
    for k in range(4):                                               # 4段階の予想図
        x0 = 300 + k * 350
        d.rectangle([x0, 200, x0 + 300, 500], outline=(170, 150, 120), width=3)
        for j in range(3):
            x = x0 + 60 + j * 90
            if k < 2:
                _conifer(d, x, 500, 200 + k * 40, col=(80 + k * 10, 120, 80))
            if k >= 1:
                _broadleaf(d, x + 30, 500, 80 + k * 50, col=(70, 118, 72))
    d.rectangle([720, 700, 1560, 748], fill=(140, 108, 76))
    d.rectangle([760, 748, 800, 990], fill=(118, 90, 64))
    d.rectangle([1480, 748, 1520, 990], fill=(118, 90, 64))
    return img


def yoyogi():
    """大正初めの代々木。畑と野原、ところどころに木。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (180, 204, 224), (220, 216, 196)), (0, 0))
    d = _d(img)
    d.rectangle([0, 560, W, H], fill=(176, 170, 110))
    for y in range(600, H, 56):                                     # 畑の畝
        d.line([(0, y), (W, y + 14)], fill=(150, 140, 90), width=6)
    for x in (260, 1500, 1700):
        _broadleaf(d, x, 600, 300, col=(96, 130, 80))
    d.polygon([(0, 560), (500, 520), (900, 560)], fill=(164, 170, 120))
    return img


def genba():
    """植樹の現場。並んだ苗木と、運ばれてきた木。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (180, 204, 224), (214, 210, 190)), (0, 0))
    d = _d(img)
    d.rectangle([0, 600, W, H], fill=(140, 118, 86))
    for row, y in enumerate((660, 760, 880)):
        for x in range(60 + row * 40, W, 180):
            if row == 0:
                _conifer(d, x, y, 150, col=(76, 110, 72))
            else:
                _broadleaf(d, x, y, 110 + row * 20, col=(80, 126, 76))
    for x in (1500, 1640):                                           # 根巻きの木
        d.ellipse([x, 520, x + 110, 590], fill=(120, 96, 70))
    return img


def shaden():
    """鎮座のころの社殿。屋根と柱だけの簡略形。まだ若い木が囲む。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (190, 206, 222), (220, 214, 196)), (0, 0))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(214, 206, 186))               # 玉砂利
    d.polygon([(560, 360), (960, 230), (1360, 360)], fill=(96, 110, 100))  # 屋根
    d.rectangle([640, 360, 1280, 700], fill=(200, 176, 140), outline=(140, 116, 86), width=6)
    for x in range(700, 1240, 110):
        d.rectangle([x, 360, x + 24, 700], fill=(150, 116, 80))
    for x in (140, 360, 1560, 1780):
        _conifer(d, x, 720, 280, col=(80, 116, 76))
    return img


def kuushu():
    """空襲の夜。赤い空と、黒い森のシルエット。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (60, 30, 30), (160, 70, 40)), (0, 0))
    d = _d(img)
    for x in range(-60, W, 140):
        _broadleaf(d, x, 900, 520 + (x % 80), col=(20, 24, 22))
    d.rectangle([0, 880, W, H], fill=(24, 22, 22))
    return img


def chichibu():
    """秩父の山並み。寄付した山林。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (170, 200, 226), (210, 216, 206)), (0, 0))
    d = _d(img)
    d.polygon([(0, 520), (400, 280), (760, 460), (1180, 240), (1600, 420), (W, 300),
               (W, H), (0, H)], fill=(84, 118, 88))
    d.polygon([(0, 700), (600, 560), (1200, 680), (W, 560), (W, H), (0, H)], fill=(70, 104, 76))
    for x in range(40, W, 120):
        _conifer(d, x, 860 + (x % 50), 220, col=(52, 86, 60))
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
    "hs_ima": ima, "hs_mori": mori, "hs_nouka": nouka, "hs_shosei": shosei,
    "hs_gakko": gakko, "hs_honke": honke, "hs_doitsu": doitsu, "hs_akichi": akichi,
    "hs_ichou": ichou, "hs_kaigi": kaigi, "hs_yoyogi": yoyogi, "hs_genba": genba,
    "hs_shaden": shaden, "hs_kuushu": kuushu, "hs_chichibu": chichibu, "hs_shiryo": shiryo,
}

CARDS = ["1866", "1884", "1890", "1901", "1912", "1920", "1945"]


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
        if only and f"hs_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"hs_card_{y}.png")
        print(f"生成完了: hs_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
