#!/usr/bin/env python3
"""富士フイルムの回（90_富士フイルムの逆転 / slug=fujifilm-komori）の背景を生成する。

方針はセガ回・そごう回と同じで、部品もそこから借りる。
実在の会社の商標（ロゴ・社名の文字・製品名・フィルムの箱の意匠）は描かない。
フィルムは「緑の箱と黄の箱」「黒い缶」のように色と形だけで見せる。
差し替え用（_kara・_cosme・_akaji など）は元の絵を呼んで要素を足す。

実行: PYTHONPATH=. python scripts/gen_fujifilm_bgs.py [名前...]
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import H, OUT, W, base, tatami_floor, vgrad, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import _papers, _phone, _table, _window, year_card  # noqa: E402
from scripts.gen_sega_bgs import _chart, _flat_tv, _glow, _person_line, kaiken as _sega_kaiken  # noqa: E402

FLOOR = int(H * 0.86)
GREEN, YELLOW, RED = (40, 140, 80), (240, 196, 40), (200, 50, 50)


def _d(img):
    return ImageDraw.Draw(img, "RGBA")


def _rgb(img):
    return img.convert("RGB") if img.mode != "RGB" else img


def _film_box(d, x, y, s=1.0, col=GREEN):
    d.rectangle([x, y, x + 70 * s, y + 46 * s], fill=col, outline=(30, 30, 30), width=2)
    d.rectangle([x + 8 * s, y + 8 * s, x + 40 * s, y + 20 * s], fill=(250, 250, 250))


def _camera(d, x, y, s=1.0, col=(230, 230, 236)):
    """インスタントカメラ風（左上が x, y）。"""
    d.rounded_rectangle([x, y, x + 150 * s, y + 110 * s], radius=int(18 * s), fill=col, outline=(120, 120, 130), width=3)
    d.ellipse([x + 45 * s, y + 25 * s, x + 105 * s, y + 85 * s], fill=(40, 40, 50), outline=(180, 180, 190), width=4)
    d.rectangle([x + 110 * s, y + 12 * s, x + 136 * s, y + 30 * s], fill=(250, 250, 240))


def _photo(d, x, y, s=1.0, col=(120, 170, 210)):
    d.rectangle([x, y, x + 70 * s, y + 86 * s], fill=(250, 250, 248), outline=(180, 180, 180), width=2)
    d.rectangle([x + 6 * s, y + 6 * s, x + 64 * s, y + 64 * s], fill=col)


def _bottles(d, x0, y, n, s=1.0):
    cols = [(220, 60, 70), (236, 200, 210), (200, 40, 60), (250, 240, 240)]
    for k in range(n):
        x = x0 + k * 70 * s
        h = (90 + (k % 3) * 20) * s
        d.rounded_rectangle([x, y - h, x + 46 * s, y], radius=int(10 * s), fill=cols[k % 4], outline=(150, 60, 70), width=2)
        d.rectangle([x + 12 * s, y - h - 18 * s, x + 34 * s, y - h], fill=(220, 220, 224))


# ---------------------------------------------------------------- 今
def heya(photos=False):
    """今の部屋。棚にインスタントカメラ。photos は壁に写真がいっぱい。"""
    img = _rgb(base((232, 228, 220), (216, 212, 204)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    _window(d, 760, 140, 1160, 420, sky=(200, 220, 236))
    d.rectangle([1340, 560, 1800, 600], fill=(140, 106, 76))
    d.rectangle([1360, 600, 1780, 720], fill=(150, 116, 84))
    _camera(d, 1480, 450, 1.0)
    if photos:
        rnd = random.Random(2)
        for k in range(14):
            x, y = 120 + (k % 7) * 90, 160 + (k // 7) * 110
            _photo(d, x + rnd.randint(-8, 8), y + rnd.randint(-6, 6), 1.0,
                   col=rnd.choice([(120, 170, 210), (220, 160, 120), (140, 200, 140), (230, 200, 120)]))
    return img


def heya_photo():
    return heya(photos=True)


# ---------------------------------------------------------------- 写真の時代
def genzosho(kara=False):
    """1990年代の写真の店（現像の受付）。棚にフィルムの箱。kara は客も箱も無い。"""
    img = _rgb(base((236, 232, 220), (222, 218, 206)))
    wood_floor(img, FLOOR, col=(170, 160, 146), line=(150, 140, 128))
    d = _d(img)
    for r in range(3):
        y = 180 + r * 120
        d.rectangle([120, y + 70, 1000, y + 80], fill=(160, 130, 100))
        if not kara:
            for k in range(11):
                _film_box(d, 140 + k * 78, y + 22, 1.0, col=(GREEN, YELLOW, (40, 40, 44))[k % 3])
    d.rectangle([1100, 560, 1820, 640], fill=(200, 180, 150))                    # 受付カウンター
    d.rectangle([1120, 640, 1800, FLOOR], fill=(180, 160, 130))
    if not kara:
        for k in range(5):
            d.rectangle([1150 + k * 120, 520, 1240 + k * 120, 560], fill=(250, 250, 240), outline=(170, 170, 160))  # 写真の袋
        _person_line(d, 1160, 1040, 8, 1.0)
    else:
        d.rectangle([1300, 300, 1620, 460], fill=(250, 250, 246), outline=(160, 160, 160), width=4)   # 貼り紙（文字なし）
        for k in range(4):
            d.line([(1330, 340 + k * 30), (1590, 340 + k * 30)], fill=(90, 90, 90), width=5)
    return img


def genzosho_kara():
    return genzosho(kara=True)


def kojo():
    """フィルム工場。暗い部屋に、薄い膜を塗る長い機械と、かすかな緑の安全灯。"""
    img = vgrad((W, H), (14, 16, 20), (26, 28, 32))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(30, 32, 36))
    d.rectangle([100, 420, 1820, 620], fill=(60, 64, 70), outline=(90, 94, 100), width=4)
    for k in range(10):
        d.ellipse([140 + k * 170, 440, 260 + k * 170, 560], fill=(80, 84, 90), outline=(120, 124, 130), width=3)
    d.rectangle([100, 500, 1820, 510], fill=(160, 120, 70))                       # 流れる膜
    for x in (300, 960, 1620):
        _glow(img, x, 160, 160, (60, 200, 90), 70)
        d = _d(img)
        d.ellipse([x - 30, 140, x + 30, 180], fill=(60, 200, 90))
    return img


def kenkyujo(cosme=False):
    """研究所。机に顕微鏡とガラス器具。cosme は机に赤い化粧品の瓶が並ぶ。"""
    img = _rgb(base((228, 232, 236), (212, 216, 222)))
    wood_floor(img, FLOOR, col=(190, 194, 200), line=(170, 174, 180))
    d = _d(img)
    _window(d, 760, 120, 1160, 380, sky=(206, 222, 236))
    d.rectangle([300, 640, 1620, 690], fill=(236, 238, 240), outline=(170, 174, 180), width=3)
    d.rectangle([320, 690, 360, 860], fill=(180, 184, 190))
    d.rectangle([1560, 690, 1600, 860], fill=(180, 184, 190))
    d.rectangle([420, 520, 470, 640], fill=(60, 60, 70))                          # 顕微鏡
    d.ellipse([400, 500, 490, 540], fill=(80, 80, 90))
    d.rectangle([380, 620, 520, 640], fill=(60, 60, 70))
    for k in range(4):                                                            # ガラス器具
        x = 600 + k * 90
        d.polygon([(x, 640), (x + 60, 640), (x + 44, 560), (x + 16, 560)], fill=(200, 230, 240, 180), outline=(150, 180, 200))
    if cosme:
        _bottles(d, 1000, 640, 8, 1.0)
        _glow(img, 1250, 560, 300, (255, 200, 210), 70)
    else:
        _photo(d, 1100, 540, 1.0)
        _photo(d, 1200, 550, 1.0, col=(220, 160, 120))
    return img


def kenkyujo_cosme():
    return kenkyujo(cosme=True)


def shachoshitsu():
    """社長室。大きな机と窓の外のビル街、壁に写真の額。"""
    img = _rgb(base((214, 208, 196), (198, 192, 180)))
    wood_floor(img, FLOOR, col=(96, 74, 56), line=(80, 60, 46))
    d = _d(img)
    _window(d, 1300, 110, 1820, 440, sky=(196, 214, 230))
    d.polygon([(1310, 420), (1400, 300), (1480, 360), (1600, 260), (1700, 340), (1810, 420)], fill=(140, 150, 166))
    for k in range(3):
        _photo(d, 200 + k * 160, 200, 1.6, col=((120, 170, 210), (230, 190, 120), (140, 190, 140))[k])
    d.rectangle([700, 640, 1500, 700], fill=(90, 60, 40))
    d.rectangle([720, 700, 760, 860], fill=(70, 48, 32))
    d.rectangle([1440, 700, 1480, 860], fill=(70, 48, 32))
    _papers(d, 800, 630, n=3)
    _phone(d, 1300, 570, 0.6)
    return img


def kaigi(akaji=False):
    """会議室。ボードに下がるグラフ（写真フィルムの需要）。akaji は赤く崩れる。"""
    img = _rgb(base((214, 212, 206), (198, 196, 190)))
    wood_floor(img, FLOOR, col=(106, 96, 86), line=(88, 80, 72))
    d = _d(img)
    pts = [0.9, 0.95, 0.7, 0.42, 0.2, 0.08] if akaji else [0.6, 0.75, 0.88, 0.95, 0.9, 0.8]
    _chart(d, 560, 110, 1360, 500, pts, col=(220, 30, 40) if akaji else (60, 120, 80))
    if akaji:
        d.rectangle([560, 110, 1360, 500], fill=(220, 40, 40, 50))
    d.rectangle([420, 640, 1500, 700], fill=(120, 108, 96))
    _papers(d, 600, 630, n=3)
    _papers(d, 1100, 630, n=2)
    return img


def kaigi_akaji():
    return kaigi(akaji=True)


def hotel_yoru():
    """海外のホテルの部屋の夜。窓の外に街の灯り、机に資料。"""
    img = _rgb(base((30, 30, 48), (44, 40, 58)))
    wood_floor(img, FLOOR, col=(70, 56, 50), line=(58, 46, 42))
    d = _d(img)
    d.rectangle([300, 100, 1620, 520], fill=(14, 18, 40), outline=(90, 80, 70), width=10)
    rnd = random.Random(9)
    for k in range(18):
        x = 320 + k * 72
        h = rnd.randint(120, 330)
        d.rectangle([x, 520 - h, x + 56, 520], fill=(40, 44, 70))
        for j in range(h // 30):
            if rnd.random() < 0.6:
                d.rectangle([x + 10, 520 - h + 10 + j * 30, x + 22, 520 - h + 20 + j * 30], fill=(250, 220, 140))
    d.line([(960, 100), (960, 520)], fill=(90, 80, 70), width=8)
    d.rectangle([600, 660, 1320, 710], fill=(100, 76, 56))
    _papers(d, 700, 650, n=4)
    d.ellipse([1180, 560, 1260, 600], fill=(250, 230, 150))
    _glow(img, 1220, 620, 260, (255, 220, 140), 80)
    return img


def tenpo():
    """化粧品の売り場。白いカウンターと赤い瓶の棚、明るい照明。"""
    img = _rgb(base((250, 246, 242), (238, 232, 228)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(230, 222, 216))
    for k in range(8):
        d.ellipse([120 + k * 240, 40, 240 + k * 240, 80], fill=(255, 252, 236))
    for r in range(3):
        y = 260 + r * 130
        d.rectangle([200, y + 4, 1720, y + 14], fill=(220, 210, 206))
        _bottles(d, 240, y, 21, 1.0)
    d.rectangle([600, 680, 1320, FLOOR], fill=(252, 252, 252), outline=(210, 206, 204), width=4)
    return img


def byoin():
    """病院の検査室。大きな医療機器と画面、白い壁。"""
    img = _rgb(base((236, 242, 246), (222, 230, 236)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(206, 216, 222))
    d.ellipse([560, 240, 1060, 740], fill=(240, 244, 248), outline=(170, 180, 190), width=8)   # 機器の輪
    d.ellipse([700, 380, 920, 600], fill=(200, 210, 220))
    d.rectangle([760, 600, 1500, 680], fill=(220, 226, 232), outline=(170, 180, 190), width=4)  # 寝台
    sx0, sy0, sx1, sy1 = _flat_tv(d, 1300, 180, 1760, 460, screen=(20, 30, 40))
    d.ellipse([sx0 + 120, sy0 + 40, sx0 + 300, sy0 + 220], outline=(200, 220, 240), width=6)
    return img


def america(snow=True):
    """冬のアメリカの大きな会社の建物（文字・マークなし）。雪が降る。"""
    img = vgrad((W, H), (150, 160, 180), (200, 206, 216))
    d = _d(img)
    d.rectangle([520, 120, 1400, FLOOR], fill=(150, 120, 100), outline=(110, 90, 76), width=6)
    for r in range(8):
        for k in range(9):
            d.rectangle([570 + k * 92, 160 + r * 80, 620 + k * 92, 210 + r * 80], fill=(80, 90, 110))
    d.rectangle([0, FLOOR, W, H], fill=(236, 240, 244))
    if snow:
        rnd = random.Random(4)
        for k in range(260):
            x, y = rnd.randint(0, W), rnd.randint(0, H)
            r = rnd.randint(2, 5)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(250, 250, 252, 220))
    return img


def kaigai_office():
    """1970〜80年代の海外の事務所。窓の外に外国の街並み、机にタイプライター。"""
    img = _rgb(base((220, 214, 200), (204, 198, 184)))
    wood_floor(img, FLOOR, col=(116, 92, 70), line=(96, 76, 58))
    d = _d(img)
    _window(d, 700, 120, 1220, 420, sky=(190, 210, 228))
    for k in range(6):
        x = 720 + k * 82
        d.rectangle([x, 300 - (k % 3) * 50, x + 70, 420], fill=(170, 150, 130))
    _table(d, 560, 1360, 640, col=(120, 90, 64))
    d.rectangle([800, 590, 960, 640], fill=(60, 60, 64))                          # タイプライター
    d.rectangle([820, 560, 940, 590], fill=(250, 250, 246))
    _papers(d, 1060, 630, n=3)
    return img


def camera_ten():
    """今のカメラ店。棚にカラフルなインスタントカメラが並ぶ。"""
    img = _rgb(base((244, 240, 232), (230, 226, 218)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(214, 208, 198))
    cols = [(240, 160, 180), (160, 200, 240), (250, 230, 140), (180, 230, 190), (236, 236, 240)]
    for r in range(3):
        y = 200 + r * 160
        d.rectangle([160, y + 120, 1760, y + 132], fill=(200, 180, 150))
        for k in range(11):
            _camera(d, 190 + k * 142, y + 10, 0.8, col=cols[(k + r) % 5])
    return img


def kaiken():
    return _sega_kaiken()


def gendai():
    """今の会社のロビー。壁のモニターに医療と化粧品と半導体（抽象）。"""
    img = vgrad((W, H), (232, 238, 242), (216, 222, 228))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(200, 206, 212))
    for k in range(3):
        sx0, sy0, sx1, sy1 = _flat_tv(d, 300 + k * 460, 200, 680 + k * 460, 430,
                                      screen=((220, 60, 70), (40, 120, 180), (60, 70, 90))[k])
    d.rectangle([760, 700, 1160, 780], fill=(240, 240, 244))
    return img


LOCATIONS = {
    "ff_heya": heya, "ff_heya_photo": heya_photo, "ff_genzosho": genzosho, "ff_genzosho_kara": genzosho_kara,
    "ff_kojo": kojo, "ff_kenkyujo": kenkyujo, "ff_kenkyujo_cosme": kenkyujo_cosme,
    "ff_shachoshitsu": shachoshitsu, "ff_kaigi": kaigi, "ff_kaigi_akaji": kaigi_akaji,
    "ff_hotel_yoru": hotel_yoru, "ff_tenpo": tenpo, "ff_byoin": byoin, "ff_america": america,
    "ff_kaigai_office": kaigai_office, "ff_camera_ten": camera_ten, "ff_kaiken": kaiken, "ff_gendai": gendai,
}

CARDS = ["1934", "1963", "1975", "1986", "1995", "1996", "2000", "2001", "2006", "2008", "2012", "2018", "2021"]


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, fn in LOCATIONS.items():
        if only and name not in only:
            continue
        fn().save(OUT / f"{name}.png")
        print(f"生成完了: {name}.png")
    for y in CARDS:
        if only and f"ff_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"ff_card_{y}.png")
        print(f"生成完了: ff_card_{y}.png")
