#!/usr/bin/env python3
"""カルピス回（44_カルピスの誕生 / slug=calpis）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回で使う 20 種の場所背景と、
章替わりの年号カード 17 枚を書き出す。

■ なぜ別ファイルにしたか
gen_drama_bgs.py の __main__ は登録済みの背景を全部描き直すので、
1本の新作のために既存20枚を再生成することになる。共通部品だけ import して
この回の分だけを書き出すほうが速く、既存回への影響も無い。

■ 場所を20種に束ねている理由
章ごとに書き分けると80種を超え、現実的に描き切れない。
「同じ性質の場所」は1枚に寄せ、時間帯の差は演出（BGM・表情）で出す方針にした。

実行: PYTHONPATH=. python scripts/gen_calpis_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, glow, hanging_bulb, tatami_floor, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)   # 立ち絵の足元。ここより下は床にする


def _d(img):
    return ImageDraw.Draw(img)


def _glow(img, cx, cy, r, color, alpha=110):
    """glow() は RGBA のキャンバスに合成するので、RGB 画像に当てるには
    変換した結果を受け取り直す必要がある。素で glow(img.convert("RGBA"), ...)
    と書くと、変換で作った一時画像に描いて捨てることになる（実際に踏んだ）。"""
    rgba = img.convert("RGBA")
    glow(rgba, cx, cy, r, color, alpha)
    img.paste(rgba.convert("RGB"), (0, 0))


def _window(d, x0, y0, x1, y1, sky=(150, 186, 214), frame=(70, 62, 56)):
    d.rectangle([x0, y0, x1, y1], fill=sky)
    d.rectangle([x0, y0, x1, y1], outline=frame, width=10)
    d.line([( (x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=frame, width=8)


# ---------------------------------------------------------------- 現代
def ima():
    """現代・ずんだもんの部屋。茶番と現代パートで使う。"""
    img = base((250, 244, 232), (228, 218, 200))
    d = _d(img)
    wood_floor(img, FLOOR)
    _window(d, 1180, 180, 1660, 560, sky=(178, 206, 228))
    # 冷蔵庫
    d.rectangle([180, 300, 470, 900], fill=(238, 240, 242), outline=(200, 202, 206), width=6)
    d.line([(180, 520), (470, 520)], fill=(200, 202, 206), width=6)
    d.rectangle([430, 420, 452, 480], fill=(170, 174, 180))
    d.rectangle([430, 560, 452, 620], fill=(170, 174, 180))
    # テーブル
    d.rectangle([620, 760, 1320, 800], fill=(176, 138, 98))
    d.rectangle([660, 800, 690, 1000], fill=(150, 116, 82))
    d.rectangle([1250, 800, 1280, 1000], fill=(150, 116, 82))
    return img


# ---------------------------------------------------------------- 寺
def hondo():
    """寺の本堂。第1章。"""
    img = base((72, 58, 48), (44, 34, 28))
    d = _d(img)
    tatami_floor(img, FLOOR)
    # 柱と欄間
    for x in (250, 780, 1140, 1670):
        d.rectangle([x, 0, x + 46, FLOOR], fill=(58, 44, 36))
    d.rectangle([0, 0, W, 120], fill=(52, 40, 32))
    # 金色の仏具まわり（具体的な像は描かない）
    d.rectangle([880, 240, 1040, 700], fill=(96, 80, 44))
    d.rectangle([916, 280, 1004, 660], fill=(140, 114, 58))
    _glow(img, 960, 420, 240, (240, 208, 120), 60)
    hanging_bulb(img, 960, warm=True, ly=40)
    return img


def kuri_unused():
    return hondo()


# ---------------------------------------------------------------- 河原
def kawara():
    """河原・夕方。母と発声練習をする場面。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (248, 196, 140), (196, 148, 130)), (0, 0))
    d = _d(img)
    # 遠景の山
    d.polygon([(0, 640), (420, 430), (860, 660)], fill=(138, 118, 128))
    d.polygon([(700, 660), (1200, 420), (1720, 670)], fill=(120, 102, 116))
    # 川
    d.rectangle([0, 660, W, 830], fill=(150, 168, 186))
    for i, y in enumerate(range(690, 830, 34)):
        d.line([(120 + i * 60, y), (1500 + i * 40, y)], fill=(184, 200, 214), width=7)
    # 河原の石
    d.rectangle([0, 830, W, H], fill=(196, 186, 168))
    for x in range(60, W, 190):
        d.ellipse([x, 880 + (x % 70), x + 110, 938 + (x % 70)], fill=(176, 166, 150))
    return img


# ---------------------------------------------------------------- 学校
def rouka():
    """寄宿舎の廊下。第2章の山場。"""
    img = base((96, 82, 68), (62, 52, 44))
    d = _d(img)
    wood_floor(img, FLOOR, col=(92, 68, 48), line=(74, 54, 38))
    # 障子の連なり（奥行き）
    for i, x in enumerate(range(120, 1800, 300)):
        d.rectangle([x, 150, x + 230, 760], fill=(226, 218, 196), outline=(96, 78, 60), width=8)
        for gy in range(200, 760, 140):
            d.line([(x, gy), (x + 230, gy)], fill=(150, 132, 108), width=5)
    return img


def kyoshitsu():
    """明治の教室。文学寮・山口の中学・北京の学堂で共用。"""
    img = base((214, 206, 186), (186, 176, 156))
    d = _d(img)
    wood_floor(img, FLOOR, col=(120, 92, 66), line=(100, 76, 54))
    d.rectangle([420, 150, 1500, 620], fill=(46, 58, 50), outline=(88, 70, 52), width=14)
    for y in (250, 360, 470):
        d.line([(480, y), (1440, y)], fill=(96, 112, 100), width=4)
    _window(d, 60, 200, 330, 560)
    _window(d, 1600, 200, 1870, 560)
    return img


# ---------------------------------------------------------------- 大陸
def beijing_machi():
    """北京の街。行商と商館。"""
    img = base((226, 206, 172), (200, 178, 146))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(178, 158, 130))
    # 低い瓦屋根の連なり
    for i, x in enumerate(range(-60, W, 340)):
        top = 300 + (i % 3) * 40
        d.rectangle([x, top, x + 300, FLOOR], fill=(168, 146, 120), outline=(120, 100, 80), width=6)
        d.polygon([(x - 26, top), (x + 326, top), (x + 300, top - 54), (x, top - 54)],
                  fill=(96, 82, 70))
        d.rectangle([x + 100, top + 150, x + 200, FLOOR], fill=(110, 78, 58))
    return img


def manshu():
    """満洲の馬市。第4章。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (206, 212, 214), (176, 172, 158)), (0, 0))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(154, 140, 116))
    # 柵
    for x in range(80, W, 160):
        d.rectangle([x, 560, x + 18, 760], fill=(112, 92, 70))
    d.rectangle([0, 600, W, 620], fill=(112, 92, 70))
    d.rectangle([0, 690, W, 706], fill=(112, 92, 70))
    return img


def yuki_sogen():
    """雪の草原。馬がいない、第4章の山場。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (196, 208, 222), (232, 236, 240)), (0, 0))
    d = _d(img)
    d.rectangle([0, 720, W, H], fill=(242, 244, 248))
    d.polygon([(0, 740), (620, 700), (1240, 752), (W, 716), (W, 800), (0, 800)],
              fill=(226, 232, 240))
    for x in range(120, W, 430):
        d.line([(x, 700), (x + 18, 620)], fill=(150, 148, 140), width=8)
    return img


def sogen():
    """草原。牧場・羊・夏の高原。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (150, 190, 222), (206, 220, 196)), (0, 0))
    d = _d(img)
    d.polygon([(0, 640), (760, 560), (1500, 648), (W, 600), (W, H), (0, H)],
              fill=(138, 166, 104))
    d.polygon([(0, 780), (900, 726), (W, 790), (W, H), (0, H)], fill=(116, 148, 88))
    for cx in (320, 900, 1540):
        d.ellipse([cx, 120, cx + 260, 230], fill=(246, 248, 250))
    return img


def pao():
    """パオ（ゲル）の中。第5章＝物語の核心。"""
    img = base((92, 74, 58), (58, 46, 36))
    d = _d(img)
    # 天窓から差す光
    d.ellipse([820, -120, 1120, 190], fill=(206, 190, 150))
    _glow(img, 970, 120, 300, (248, 224, 160), 70)
    # 骨組み
    for i in range(-6, 7):
        d.line([(960, 120), (960 + i * 180, FLOOR)], fill=(122, 98, 74), width=7)
    d.rectangle([0, FLOOR, W, H], fill=(104, 82, 62))
    # 炉
    d.ellipse([840, 820, 1080, 930], fill=(72, 58, 46))
    _glow(img, 960, 872, 150, (240, 150, 70), 90)
    return img


def minato():
    """港。十三年を終えて船に乗る、第6章の山場。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (188, 198, 208), (150, 158, 168)), (0, 0))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(112, 116, 122))
    d.rectangle([0, 640, W, 704], fill=(88, 104, 120))
    # 船体と煙突
    d.rectangle([1040, 330, 1860, 660], fill=(74, 78, 84))
    d.rectangle([1240, 200, 1340, 340], fill=(150, 90, 70))
    d.rectangle([1500, 200, 1600, 340], fill=(150, 90, 70))
    for x in range(1080, 1840, 120):
        d.rectangle([x, 430, x + 60, 490], fill=(196, 200, 206))
    return img


# ---------------------------------------------------------------- 日本・仕事場
def jitaku():
    """自宅の座敷。土倉の家・三島の家で共用。"""
    img = base((206, 194, 170), (176, 162, 140))
    d = _d(img)
    tatami_floor(img, FLOOR)
    d.rectangle([260, 140, 1000, 700], fill=(226, 220, 200), outline=(120, 100, 78), width=10)
    for gx in range(320, 1000, 150):
        d.line([(gx, 140), (gx, 700)], fill=(160, 142, 118), width=5)
    # 床の間
    d.rectangle([1180, 120, 1700, 720], fill=(150, 130, 104))
    d.rectangle([1300, 200, 1580, 620], fill=(224, 216, 194))
    return img


def sagyoba():
    """本郷の作業場。桶と瓶が並ぶ、第8章。"""
    img = base((164, 158, 146), (120, 114, 104))
    d = _d(img)
    wood_floor(img, FLOOR, col=(104, 86, 66), line=(86, 70, 54))
    # 棚と瓶
    for sy in (240, 430):
        d.rectangle([120, sy, 900, sy + 22], fill=(112, 92, 70))
        for x in range(150, 880, 90):
            d.rectangle([x, sy - 92, x + 54, sy], fill=(196, 206, 200), outline=(150, 160, 156), width=4)
    # 桶
    for i, x in enumerate((1150, 1430, 1710)):
        d.ellipse([x - 120, 640, x + 120, 720], fill=(140, 112, 82))
        d.rectangle([x - 120, 680, x + 120, 940], fill=(156, 126, 92))
        d.ellipse([x - 120, 900, x + 120, 980], fill=(132, 106, 78))
    hanging_bulb(img, 960, warm=True, ly=30)
    return img


def kojo():
    """工場。タンクとラインのある大きな空間。"""
    img = base((150, 158, 164), (104, 110, 116))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(92, 96, 100))
    # のこぎり屋根
    for i in range(7):
        x = i * 290 - 60
        d.polygon([(x, 250), (x + 150, 110), (x + 150, 250)], fill=(122, 130, 136))
        d.polygon([(x + 150, 110), (x + 290, 250), (x + 150, 250)], fill=(176, 196, 210))
    # タンク
    for x in (240, 620, 1000):
        d.rectangle([x, 380, x + 240, 900], fill=(186, 192, 196), outline=(140, 146, 150), width=8)
        d.ellipse([x, 340, x + 240, 420], fill=(204, 210, 214))
    # 配管
    d.rectangle([0, 320, W, 350], fill=(150, 156, 160))
    return img


def misesaki():
    """店先。小売・問屋・百貨店の試飲台で共用。"""
    img = base((226, 212, 186), (196, 182, 158))
    d = _d(img)
    wood_floor(img, FLOOR, col=(128, 96, 66), line=(106, 80, 54))
    # 暖簾
    d.rectangle([0, 120, W, 300], fill=(72, 86, 96))
    for x in range(120, W, 260):
        d.line([(x, 120), (x, 300)], fill=(54, 66, 74), width=6)
    # 台と箱
    d.rectangle([260, 660, 1660, 700], fill=(150, 118, 84))
    d.rectangle([300, 700, 340, 940], fill=(128, 100, 72))
    d.rectangle([1580, 700, 1620, 940], fill=(128, 100, 72))
    for x in range(420, 1500, 200):
        d.rectangle([x, 560, x + 140, 660], fill=(206, 196, 176), outline=(150, 140, 120), width=5)
    return img


def jimusho():
    """事務所・応接室。会社の場面すべてで共用（最も出番が多い）。"""
    img = base((212, 204, 188), (180, 170, 154))
    d = _d(img)
    wood_floor(img, FLOOR, col=(116, 88, 62), line=(96, 72, 50))
    _window(d, 1300, 160, 1800, 580)
    # 書棚
    d.rectangle([90, 180, 620, 720], fill=(122, 96, 68))
    for sy in range(230, 700, 120):
        d.rectangle([110, sy, 600, sy + 16], fill=(96, 74, 52))
        for x in range(130, 580, 34):
            d.rectangle([x, sy - 86, x + 24, sy], fill=(168 - (x % 40), 140, 110))
    # 机
    d.rectangle([720, 700, 1560, 748], fill=(140, 108, 76))
    d.rectangle([760, 748, 800, 990], fill=(118, 90, 64))
    d.rectangle([1480, 748, 1520, 990], fill=(118, 90, 64))
    return img


def yakusho():
    """役所。平和物資の判を押される第11章。"""
    img = base((196, 196, 190), (160, 160, 154))
    d = _d(img)
    wood_floor(img, FLOOR, col=(110, 100, 86), line=(92, 84, 72))
    # カウンター
    d.rectangle([0, 640, W, 700], fill=(130, 118, 98))
    d.rectangle([0, 700, W, 960], fill=(148, 136, 116))
    # 掲示板
    d.rectangle([620, 160, 1300, 560], fill=(214, 208, 190), outline=(120, 110, 92), width=10)
    for y in range(210, 540, 62):
        d.line([(660, y), (1260, y)], fill=(168, 160, 142), width=6)
    return img


def shinsai():
    """関東大震災の街。第10章。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (156, 132, 116), (116, 100, 92)), (0, 0))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(104, 94, 86))
    # 傾いた建物と瓦礫
    d.polygon([(120, 760), (200, 300), (430, 330), (390, 760)], fill=(140, 126, 112))
    d.polygon([(1420, 760), (1500, 360), (1760, 340), (1800, 760)], fill=(132, 118, 106))
    for x in range(200, 1700, 130):
        d.polygon([(x, 760), (x + 90, 700 + (x % 50)), (x + 150, 760)], fill=(126, 114, 104))
    return img


def shiryo():
    """新聞・社史・包装紙など、紙の面を見せる背景。第13〜14章。"""
    img = base((238, 234, 224), (214, 208, 196))
    d = _d(img)
    d.rectangle([180, 90, 1740, 990], fill=(250, 248, 242), outline=(168, 160, 146), width=8)
    d.rectangle([240, 150, 1680, 170], fill=(120, 112, 100))
    for y in range(230, 950, 46):
        w = 1440 if (y // 46) % 5 else 900
        d.rectangle([240, y, 240 + w, y + 18], fill=(196, 190, 178))
    return img


def okuma():
    """大隈邸。門と座敷を兼ねる。第6章。"""
    img = base((196, 190, 172), (162, 156, 140))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(128, 122, 108))
    # 門
    d.rectangle([300, 180, 380, FLOOR], fill=(92, 72, 56))
    d.rectangle([1540, 180, 1620, FLOOR], fill=(92, 72, 56))
    d.polygon([(240, 190), (1680, 190), (1600, 110), (320, 110)], fill=(70, 58, 48))
    # 生け垣
    d.rectangle([0, 700, 300, 900], fill=(96, 122, 86))
    d.rectangle([1620, 700, W, 900], fill=(96, 122, 86))
    return img


LOCATIONS = {
    "cp_ima": ima, "cp_hondo": hondo, "cp_kawara": kawara, "cp_rouka": rouka,
    "cp_kyoshitsu": kyoshitsu, "cp_beijing_machi": beijing_machi,
    "cp_manshu": manshu, "cp_yuki_sogen": yuki_sogen, "cp_sogen": sogen,
    "cp_pao": pao, "cp_minato": minato, "cp_jitaku": jitaku,
    "cp_sagyoba": sagyoba, "cp_kojo": kojo, "cp_misesaki": misesaki,
    "cp_jimusho": jimusho, "cp_yakusho": yakusho, "cp_shinsai": shinsai,
    "cp_shiryo": shiryo, "cp_okuma": okuma,
}

# 章替わりの年号カード。キーはファイル名の接尾辞、値は画面に出す文字
CARDS = {
    "1878": "1878年", "1891": "1891年", "1902": "1902年", "1904": "1904年",
    "1905": "1905年", "1909": "1909年", "1915": "1915年", "1916": "1916年",
    "1917": "1917年", "1918": "1918年", "19190707": "1919年7月7日",
    "1922": "1922年", "1923": "1923年", "1937": "1937年", "1943": "1943年",
    "1950": "1950年", "1974": "1974年",
}


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
    for key, text in CARDS.items():
        year_card(text).save(OUT / f"cp_card_{key}.png")
        print(f"生成完了: cp_card_{key}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
