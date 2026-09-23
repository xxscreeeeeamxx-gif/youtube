#!/usr/bin/env python3
"""YKK回（45_YKKファスナーの誕生 / slug=ykk）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景15種と
章替わりの年号カード9枚を書き出す。

カルピス回（gen_calpis_bgs.py）と同じ方針:
- 場所は性質ごとに束ねる。時間帯の差は BGM と表情で出す
- 年号カードは1つの関数で量産する
- gen_drama_bgs.py 本体は触らない（既存背景を再生成しないため）

実行: PYTHONPATH=. python scripts/gen_ykk_bgs.py
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


# ------------------------------------------------------------ 現代
def ima():
    """現代の部屋。茶番と現代パート。"""
    img = base((248, 242, 232), (226, 216, 200))
    d = _d(img)
    wood_floor(img, FLOOR)
    _window(d, 1180, 180, 1660, 560, sky=(176, 204, 228))
    d.rectangle([620, 760, 1320, 800], fill=(176, 138, 98))
    d.rectangle([660, 800, 690, 1000], fill=(150, 116, 82))
    d.rectangle([1250, 800, 1280, 1000], fill=(150, 116, 82))
    # 壁掛けの棚
    d.rectangle([220, 330, 560, 350], fill=(150, 120, 88))
    for x in range(250, 540, 46):
        d.rectangle([x, 270, x + 30, 330], fill=(190, 170, 148))
    return img


# ------------------------------------------------------------ 富山・少年期
def uozu_ie():
    """魚津の家。明治の土間と板の間。"""
    img = base((96, 82, 66), (62, 52, 42))
    d = _d(img)
    tatami_floor(img, FLOOR)
    for x in (300, 1560):
        d.rectangle([x, 0, x + 40, FLOOR], fill=(64, 50, 40))
    # 障子
    d.rectangle([420, 170, 1420, 690], fill=(224, 216, 196), outline=(96, 78, 60), width=10)
    for gx in range(520, 1420, 200):
        d.line([(gx, 170), (gx, 690)], fill=(158, 140, 116), width=6)
    for gy in range(280, 690, 140):
        d.line([(420, gy), (1420, gy)], fill=(158, 140, 116), width=5)
    hanging_bulb(img, 960, warm=True, ly=40)
    return img


def kyoshitsu():
    """明治の小学校の教室。"""
    img = base((212, 204, 184), (184, 174, 154))
    d = _d(img)
    wood_floor(img, FLOOR, col=(120, 92, 66), line=(100, 76, 54))
    d.rectangle([430, 150, 1490, 610], fill=(46, 58, 50), outline=(88, 70, 52), width=14)
    for y in (250, 360, 470):
        d.line([(490, y), (1430, y)], fill=(96, 112, 100), width=4)
    _window(d, 60, 200, 330, 560)
    _window(d, 1600, 200, 1870, 560)
    return img


# ------------------------------------------------------------ 東京・上海
def nihonbashi():
    """日本橋の店先。中国から来た焼き物を並べた棚。"""
    img = base((226, 212, 186), (196, 182, 156))
    d = _d(img)
    wood_floor(img, FLOOR, col=(128, 96, 66), line=(106, 80, 54))
    d.rectangle([0, 110, W, 290], fill=(70, 84, 94))          # 暖簾
    for x in range(120, W, 260):
        d.line([(x, 110), (x, 290)], fill=(52, 64, 72), width=6)
    for sy in (430, 620):                                      # 棚と焼き物
        d.rectangle([140, sy, 880, sy + 22], fill=(112, 88, 64))
        for x in range(170, 860, 96):
            d.ellipse([x, sy - 78, x + 62, sy], fill=(206, 214, 216),
                      outline=(150, 160, 164), width=4)
    d.rectangle([1120, 660, 1800, 700], fill=(150, 118, 84))   # 帳場
    return img


def shanghai():
    """上海の埠頭。荷と倉庫。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (196, 200, 206), (166, 162, 152)), (0, 0))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(120, 116, 110))
    d.rectangle([0, 620, W, 704], fill=(96, 110, 124))          # 水面
    d.rectangle([1080, 300, 1880, 640], fill=(130, 122, 110),
                outline=(96, 90, 82), width=8)                  # 倉庫
    for x in range(1140, 1840, 130):
        d.rectangle([x, 400, x + 80, 520], fill=(92, 86, 78))
    for i, x in enumerate((180, 400, 620)):                     # 木箱
        d.rectangle([x, 560 + i * 12, x + 170, 700], fill=(150, 116, 80),
                    outline=(112, 86, 58), width=6)
    return img


def soko():
    """店の倉庫。整理のために箱を出した状態。"""
    img = base((150, 140, 126), (104, 96, 86))
    d = _d(img)
    wood_floor(img, FLOOR, col=(104, 84, 62), line=(84, 66, 48))
    for sy in (260, 450):
        d.rectangle([120, sy, 1800, sy + 20], fill=(112, 90, 66))
    for x in range(150, 1780, 210):                             # 空の棚と木箱
        d.rectangle([x, 300, x + 150, 450], fill=(126, 100, 72), outline=(96, 76, 54), width=5)
    for i, x in enumerate((260, 520, 780)):
        d.rectangle([x, 640 + i * 10, x + 180, 800], fill=(146, 112, 76),
                    outline=(108, 82, 56), width=6)
    hanging_bulb(img, 960, warm=True, ly=30)
    return img


def shiire():
    """仕入れ先の帳場。頭を下げに行く場面。"""
    img = base((216, 200, 174), (182, 168, 146))
    d = _d(img)
    tatami_floor(img, FLOOR)
    d.rectangle([0, 620, W, 676], fill=(128, 98, 68))           # 上がりかまち
    d.rectangle([0, 676, W, 940], fill=(150, 118, 84))
    d.rectangle([1180, 140, 1780, 600], fill=(146, 126, 100))   # 帳場格子
    for gx in range(1200, 1780, 52):
        d.line([(gx, 140), (gx, 600)], fill=(104, 86, 66), width=8)
    return img


# ------------------------------------------------------------ 工場
def koba():
    """小さな作業場。創業期。机に半製品が並ぶ。"""
    img = base((196, 186, 168), (150, 142, 128))
    d = _d(img)
    wood_floor(img, FLOOR, col=(118, 92, 66), line=(96, 74, 52))
    d.rectangle([220, 690, 1700, 730], fill=(154, 120, 84))     # 作業台
    d.rectangle([260, 730, 300, 980], fill=(128, 100, 70))
    d.rectangle([1620, 730, 1660, 980], fill=(128, 100, 70))
    for x in range(320, 1560, 130):                              # 半製品の束
        d.rectangle([x, 640, x + 84, 690], fill=(206, 200, 186),
                    outline=(156, 150, 138), width=4)
        for gy in range(648, 688, 10):
            d.line([(x + 6, gy), (x + 78, gy)], fill=(168, 164, 152), width=3)
    _window(d, 1300, 180, 1760, 540)
    hanging_bulb(img, 900, warm=True, ly=30)
    return img


def kikai():
    """機械の前。歯を植える自動機。"""
    img = base((146, 152, 158), (100, 104, 110))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(88, 92, 96))
    d.rectangle([520, 250, 1420, 860], fill=(126, 132, 138),
                outline=(88, 94, 100), width=10)                 # 本体
    d.rectangle([600, 320, 1340, 560], fill=(66, 72, 78))        # 前面の窓
    for x in range(620, 1330, 60):
        d.line([(x, 330), (x, 550)], fill=(150, 158, 166), width=4)
    for cx in (700, 1160):                                       # 円盤
        d.ellipse([cx - 90, 620, cx + 90, 800], fill=(176, 182, 188),
                  outline=(120, 126, 132), width=8)
    d.rectangle([0, 190, W, 220], fill=(140, 146, 152))          # 天井の配管
    return img


def uozu_kojo():
    """魚津の工場。買い取った鉄工所。"""
    img = base((156, 150, 138), (112, 108, 100))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(94, 92, 88))
    for i in range(6):                                           # のこぎり屋根
        x = i * 330 - 40
        d.polygon([(x, 260), (x + 170, 120), (x + 170, 260)], fill=(124, 122, 116))
        d.polygon([(x + 170, 120), (x + 330, 260), (x + 170, 260)], fill=(170, 186, 198))
    d.rectangle([180, 420, 700, 880], fill=(136, 128, 116),
                outline=(100, 94, 86), width=8)                  # 炉と作業台
    d.rectangle([260, 500, 620, 700], fill=(72, 66, 60))
    _glow(img, 440, 600, 170, (240, 150, 70), 80)
    d.rectangle([900, 760, 1800, 800], fill=(120, 112, 100))
    return img


def kurobe():
    """黒部の工場群。銅を延ばす工場と糸の工場。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (168, 196, 220), (206, 206, 196)), (0, 0))
    d = _d(img)
    d.polygon([(0, 430), (520, 250), (1080, 440), (1500, 300), (W, 450),
               (W, 620), (0, 620)], fill=(126, 132, 146))        # 立山連峰
    d.rectangle([0, 600, W, H], fill=(140, 146, 140))
    for i, x in enumerate((120, 620, 1180)):                     # 工場棟
        h0 = 640 - i * 20
        d.rectangle([x, h0, x + 420, 900], fill=(178, 180, 176),
                    outline=(134, 136, 132), width=7)
        for wx in range(x + 30, x + 400, 70):
            d.rectangle([wx, h0 + 40, wx + 44, h0 + 110], fill=(140, 164, 182))
        d.rectangle([x + 330, h0 - 130, x + 372, h0], fill=(158, 160, 156))  # 煙突
    return img


def yakeato():
    """東京大空襲のあとの焼け跡。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (142, 126, 116), (104, 96, 90)), (0, 0))
    d = _d(img)
    d.rectangle([0, 740, W, H], fill=(96, 90, 84))
    for x in range(120, 1800, 210):                              # 焼け残りの柱
        top = 360 + (x % 130)
        d.rectangle([x, top, x + 26, 740], fill=(70, 64, 60))
    for x in range(80, 1840, 150):                               # 瓦礫
        d.polygon([(x, 740), (x + 96, 676 + (x % 46)), (x + 168, 740)],
                  fill=(118, 108, 100))
    d.rectangle([700, 300, 1250, 330], fill=(84, 78, 72))        # 折れた梁
    return img


# ------------------------------------------------------------ その他
def jimusho():
    """事務所・応接。会社の場面で共用。"""
    img = base((210, 202, 186), (178, 168, 152))
    d = _d(img)
    wood_floor(img, FLOOR, col=(116, 88, 62), line=(96, 72, 50))
    _window(d, 1300, 160, 1800, 580)
    d.rectangle([90, 180, 620, 720], fill=(122, 96, 68))         # 書棚
    for sy in range(230, 700, 120):
        d.rectangle([110, sy, 600, sy + 16], fill=(96, 74, 52))
        for x in range(130, 580, 34):
            d.rectangle([x, sy - 86, x + 24, sy], fill=(168 - (x % 40), 140, 110))
    d.rectangle([720, 700, 1560, 748], fill=(140, 108, 76))      # 机
    d.rectangle([760, 748, 800, 990], fill=(118, 90, 64))
    d.rectangle([1480, 748, 1520, 990], fill=(118, 90, 64))
    return img


def kaigai():
    """海の外。船と港。海外展開の章。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (176, 200, 220), (142, 162, 178)), (0, 0))
    d = _d(img)
    d.rectangle([0, 660, W, H], fill=(92, 116, 136))             # 海
    for i, y in enumerate(range(700, 1000, 46)):
        d.line([(80 + i * 70, y), (1560 + i * 50, y)], fill=(116, 142, 162), width=7)
    d.rectangle([980, 340, 1820, 660], fill=(78, 82, 88))        # 貨物船
    d.rectangle([1180, 210, 1270, 350], fill=(150, 90, 70))
    for x in range(1020, 1800, 150):                             # コンテナ
        d.rectangle([x, 420, x + 110, 520], fill=(160 - (x % 50), 120, 96))
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
    "yk_ima": ima, "yk_uozu_ie": uozu_ie, "yk_kyoshitsu": kyoshitsu,
    "yk_nihonbashi": nihonbashi, "yk_shanghai": shanghai, "yk_soko": soko,
    "yk_shiire": shiire, "yk_koba": koba, "yk_kikai": kikai,
    "yk_uozu_kojo": uozu_kojo, "yk_kurobe": kurobe, "yk_yakeato": yakeato,
    "yk_jimusho": jimusho, "yk_kaigai": kaigai, "yk_shiryo": shiryo,
}

CARDS = ["1908", "1928", "1933", "1934", "1945", "1950", "1953", "1959", "1993"]


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
    for name, fn in LOCATIONS.items():
        fn().save(OUT / f"{name}.png")
        print(f"生成完了: {name}.png")
    for y in CARDS:
        year_card(f"{y}年").save(OUT / f"yk_card_{y}.png")
        print(f"生成完了: yk_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
