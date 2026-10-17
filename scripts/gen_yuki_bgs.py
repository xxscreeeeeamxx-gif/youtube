#!/usr/bin/env python3
"""雪印の事件と西宮冷蔵の回（92 / slug=snowbrand-mizutani）の背景を生成する。

方針は青色LED回・富士フイルム回と同じで、部品もそこから借りる。
実在の会社の商標（雪の結晶のマーク・社名の文字・製品名）は描かない。
牛乳は「白い紙パック」、肉は「段ボールの箱」のように色と形だけで見せる。
差し替え用（_kara・_teiden・_yoru など）は元の絵を呼んで要素を足す。

実行: PYTHONPATH=. python scripts/gen_yuki_bgs.py [名前...]
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import H, OUT, W, base, tatami_floor, vgrad, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import _boxes, _papers, _phone, _window, year_card  # noqa: E402
from scripts.gen_sega_bgs import _chart, _flat_tv, _glow, _person_line, kaiken as _sega_kaiken  # noqa: E402
from scripts.gen_sogo_bgs import kokkai as _sogo_kokkai, saibansho as _sogo_saibansho  # noqa: E402

FLOOR = int(H * 0.86)


def _d(img):
    return ImageDraw.Draw(img, "RGBA")


def _rgb(img):
    return img.convert("RGB") if img.mode != "RGB" else img


def _milk(d, x, y, s=1.0, col=(250, 250, 250), band=(70, 130, 200)):
    """牛乳の紙パック（左下が x, y）。文字・マークは描かない。"""
    w, h = 44 * s, 90 * s
    d.rectangle([x, y - h, x + w, y], fill=col, outline=(170, 170, 170), width=2)
    d.polygon([(x, y - h), (x + w / 2, y - h - 18 * s), (x + w, y - h)], fill=(236, 236, 236), outline=(170, 170, 170))
    d.rectangle([x, y - h * 0.45, x + w, y - h * 0.3], fill=band)


def _cold(img, alpha=40):
    """冷気（白いもや）。"""
    d = _d(img)
    rnd = random.Random(3)
    for k in range(40):
        x, y, r = rnd.randint(0, W), rnd.randint(int(H * 0.5), FLOOR), rnd.randint(40, 120)
        d.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=(240, 248, 255, alpha))


# ---------------------------------------------------------------- 今
def heya():
    """今の部屋。台所の冷蔵庫と、机に牛乳の紙パックとコップ。"""
    img = _rgb(base((232, 228, 220), (216, 212, 204)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    _window(d, 760, 140, 1160, 420, sky=(200, 220, 236))
    d.rounded_rectangle([1460, 220, 1760, FLOOR], radius=16, fill=(236, 238, 240), outline=(170, 174, 180), width=4)
    d.line([(1460, 480), (1760, 480)], fill=(170, 174, 180), width=4)
    d.rectangle([1720, 300, 1736, 420], fill=(150, 154, 160))
    d.rectangle([200, 640, 700, 700], fill=(150, 116, 84))
    _milk(d, 330, 640, 1.2)
    d.rectangle([450, 590, 500, 640], fill=(250, 250, 250, 200), outline=(180, 180, 190))
    return img


def gendai():
    """今の乳業の会社のロビー。壁の画面に牧場の絵（抽象）、紙パックの展示。"""
    img = vgrad((W, H), (232, 238, 242), (216, 222, 228))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(200, 206, 212))
    sx0, sy0, sx1, sy1 = _flat_tv(d, 560, 160, 1360, 520, screen=(120, 190, 120))
    d.polygon([(sx0, sy1 - 80), (sx0 + 200, sy1 - 160), (sx0 + 420, sy1 - 90), (sx1, sy1 - 170), (sx1, sy1), (sx0, sy1)],
              fill=(80, 150, 80))
    d.rectangle([700, 700, 1220, 780], fill=(240, 240, 244))
    for k in range(7):
        _milk(d, 730 + k * 70, 700, 0.8, band=((70, 130, 200), (200, 60, 60), (60, 150, 90))[k % 3])
    return img


def kouri(kara=False):
    """スーパーの乳製品の棚。kara は棚がほとんど空で、貼り紙だけ。"""
    img = _rgb(base((238, 238, 234), (224, 224, 220)))
    wood_floor(img, FLOOR, col=(200, 200, 196), line=(184, 184, 180))
    d = _d(img)
    d.rectangle([140, 140, 1780, 760], fill=(210, 220, 228), outline=(150, 160, 170), width=6)
    for r in range(4):
        y = 300 + r * 140
        d.rectangle([160, y, 1760, y + 12], fill=(160, 170, 180))
        n = 3 if kara else 30
        rnd = random.Random(r)
        for k in range(n):
            x = 180 + (k * 53 if not kara else rnd.randint(0, 1500))
            _milk(d, x, y, 0.9, band=((70, 130, 200), (200, 60, 60), (60, 150, 90), (230, 180, 60))[(k + r) % 4])
    if kara:
        d.rectangle([760, 180, 1160, 280], fill=(250, 250, 240), outline=(160, 160, 150), width=4)
        for k in range(2):
            d.line([(790, 210 + k * 34), (1130, 210 + k * 34)], fill=(90, 90, 90), width=6)
    return img


def kouri_kara():
    return kouri(kara=True)


# ---------------------------------------------------------------- 乳業の工場
def kojo(teiden=False):
    """乳業の工場。銀色のタンクと配管。teiden は停電で暗く、赤い非常灯だけ。"""
    img = vgrad((W, H), (200, 206, 212), (180, 186, 192)) if not teiden else vgrad((W, H), (20, 22, 28), (32, 34, 40))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(160, 166, 172) if not teiden else (26, 28, 32))
    for k in range(4):
        x = 160 + k * 420
        col = (220, 224, 230) if not teiden else (60, 62, 70)
        d.rounded_rectangle([x, 160, x + 280, FLOOR - 40], radius=60, fill=col, outline=(140, 146, 152), width=5)
        d.ellipse([x + 110, 220, x + 170, 280], fill=(150, 156, 162) if not teiden else (40, 42, 48))
    for k in range(3):
        d.line([(0, 120 + k * 30), (W, 120 + k * 30)], fill=(150, 156, 162) if not teiden else (50, 52, 58), width=12)
    if teiden:
        for x in (300, 1600):
            _glow(img, x, 80, 200, (255, 40, 40), 90)
            d = _d(img)
            d.rectangle([x - 30, 60, x + 30, 100], fill=(230, 40, 40))
    return img


def kojo_teiden():
    return kojo(teiden=True)


def kaigi(akaji=False):
    """会社の会議室。ボードに売上のグラフ。akaji は赤く急落。"""
    img = _rgb(base((214, 212, 206), (198, 196, 190)))
    wood_floor(img, FLOOR, col=(106, 96, 86), line=(88, 80, 72))
    d = _d(img)
    pts = [0.9, 0.92, 0.5, 0.3, 0.25, 0.2] if akaji else [0.6, 0.68, 0.74, 0.8, 0.84, 0.88]
    _chart(d, 560, 110, 1360, 500, pts, col=(220, 30, 40) if akaji else (60, 100, 180))
    if akaji:
        d.rectangle([560, 110, 1360, 500], fill=(220, 40, 40, 50))
    d.rectangle([420, 640, 1500, 700], fill=(120, 108, 96))
    _papers(d, 600, 630, n=3)
    _papers(d, 1100, 630, n=2)
    return img


def kaigi_akaji():
    return kaigi(akaji=True)


# ---------------------------------------------------------------- 冷蔵倉庫
def soko(kara=False):
    """冷蔵倉庫の中。肉の段ボールが積まれ、白い冷気。kara は空っぽ。"""
    img = vgrad((W, H), (176, 196, 214), (150, 170, 190))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(130, 146, 160))
    for k in range(4):
        d.line([(0, 90 + k * 34), (W, 90 + k * 34)], fill=(120, 136, 150), width=6)
    if not kara:
        for x0 in (60, 700, 1340):
            _boxes(d, x0, FLOOR, n=5, rows=5, col=(206, 178, 130))
    else:
        d.rectangle([800, 640, 1120, 700], fill=(120, 130, 140))                   # 空のパレット
    _cold(img, 26)
    return img


def soko_kara():
    return soko(kara=True)


def soko_soto(shimatta=False):
    """冷蔵倉庫の外。海沿いの白い建物とトラック。shimatta はシャッターが下り、トラックもない。"""
    img = vgrad((W, H), (170, 206, 236), (220, 232, 240))
    d = _d(img)
    d.rectangle([0, 620, W, H], fill=(150, 150, 146))
    d.rectangle([0, 600, W, 620], fill=(100, 140, 180))                            # 海
    d.rectangle([260, 220, 1500, 760], fill=(230, 232, 234), outline=(160, 162, 166), width=6)
    for k in range(3):
        x = 360 + k * 380
        d.rectangle([x, 480, x + 280, 760], fill=(150, 156, 162) if shimatta else (60, 64, 70))
        if shimatta:
            for r in range(10):
                d.line([(x, 490 + r * 27), (x + 280, 490 + r * 27)], fill=(120, 126, 132), width=4)
    if shimatta:
        d.rectangle([700, 360, 940, 450], fill=(250, 250, 240), outline=(160, 160, 150), width=4)   # 貼り紙
        for k in range(2):
            d.line([(720, 385 + k * 30), (920, 385 + k * 30)], fill=(90, 90, 90), width=5)
    else:
        d.rectangle([1560, 600, 1880, 800], fill=(240, 240, 240), outline=(120, 120, 120), width=4)  # トラック
        d.rectangle([1500, 660, 1580, 800], fill=(80, 120, 170))
        for x in (1540, 1660, 1820):
            d.ellipse([x - 34, 780, x + 34, 848], fill=(30, 30, 34))
    return img


def soko_soto_shimatta():
    return soko_soto(shimatta=True)


def soko_jimusho(night=False):
    """倉庫の事務所。机に伝票の束と電話、壁にカレンダー。night は夜で窓が暗い。"""
    img = _rgb(base((218, 214, 204), (202, 198, 188)))
    wood_floor(img, FLOOR, col=(140, 130, 116), line=(122, 112, 100))
    d = _d(img)
    _window(d, 1300, 130, 1760, 400, sky=(20, 24, 50) if night else (190, 214, 232))
    d.rectangle([240, 150, 520, 400], fill=(250, 250, 246), outline=(150, 150, 150), width=4)   # カレンダー
    for r in range(5):
        for c in range(7):
            d.rectangle([256 + c * 36, 200 + r * 38, 284 + c * 36, 228 + r * 38], outline=(190, 190, 190), width=2)
    d.rectangle([500, 640, 1500, 700], fill=(130, 120, 110), outline=(100, 92, 84), width=3)
    _papers(d, 600, 630, n=6)
    _papers(d, 900, 630, n=4)
    _phone(d, 1300, 570, 0.6)
    if night:
        _glow(img, 960, 560, 360, (255, 240, 200), 60)
    return img


def soko_jimusho_yoru():
    return soko_jimusho(night=True)


def nikukojo():
    """食肉の加工場。白い作業台とステンレス、段ボールの箱。"""
    img = _rgb(base((226, 230, 232), (210, 214, 218)))
    wood_floor(img, FLOOR, col=(190, 196, 200), line=(170, 176, 180))
    d = _d(img)
    d.rectangle([200, 600, 1720, 660], fill=(200, 206, 212), outline=(150, 156, 162), width=4)
    for x in (260, 1640):
        d.rectangle([x, 660, x + 40, FLOOR], fill=(160, 166, 172))
    _boxes(d, 300, 600, n=4, rows=2, col=(206, 178, 130))
    _boxes(d, 1100, 600, n=4, rows=2, col=(206, 178, 130))
    d.rectangle([700, 120, 1220, 360], fill=(240, 244, 246), outline=(170, 176, 180), width=4)   # 白い壁の掲示（文字なし）
    return img


def soko_sanran():
    """震災のあとの冷蔵倉庫。段ボールが崩れて床に散らばっている。"""
    img = soko()
    d = _d(img)
    rnd = random.Random(8)
    for k in range(26):
        x, y = rnd.randint(40, W - 160), rnd.randint(FLOOR - 120, FLOOR + 40)
        a = rnd.randint(-30, 30)
        w, h = 104, 76
        pts = [(x, y), (x + w, y + a * 0.3), (x + w - a * 0.4, y + h + a * 0.3), (x - a * 0.4, y + h)]
        d.polygon(pts, fill=(206, 178, 130), outline=(120, 90, 60))
    return img


def kuko():
    """空港の出発ロビー。大きな窓の外に飛行機の尾翼、並ぶ椅子。"""
    img = vgrad((W, H), (214, 222, 230), (196, 204, 212))
    d = _d(img)
    d.rectangle([0, 100, W, 600], fill=(170, 200, 230))
    for k in range(9):
        d.line([(k * 240, 100), (k * 240, 600)], fill=(120, 130, 140), width=10)
    d.polygon([(1300, 600), (1420, 330), (1500, 330), (1460, 600)], fill=(240, 240, 244))
    d.rectangle([0, 600, W, H], fill=(186, 190, 196))
    for k in range(10):
        x = 120 + k * 170
        d.rectangle([x, 760, x + 120, 800], fill=(70, 90, 130))
        d.rectangle([x, 720, x + 120, 760], fill=(80, 100, 140))
    return img


def rikkyo():
    """大阪・梅田の陸橋の上（夕方）。手すりと、奥のビル街。のぼり（文字なし）と本を並べた台。"""
    img = vgrad((W, H), (236, 170, 120), (180, 150, 160))
    d = _d(img)
    rnd = random.Random(6)
    for k in range(12):
        x0 = k * 170 - 20
        top = 160 + rnd.randint(0, 200)
        d.rectangle([x0, top, x0 + 150, 640], fill=(120, 110, 130))
        for r in range((640 - top) // 50):
            for c in range(3):
                if rnd.random() < 0.5:
                    d.rectangle([x0 + 16 + c * 44, top + 16 + r * 50, x0 + 40 + c * 44, top + 36 + r * 50], fill=(250, 230, 170))
    d.rectangle([0, 640, W, H], fill=(150, 146, 140))
    d.rectangle([0, 600, W, 640], fill=(110, 110, 116))                            # 手すり
    for k in range(40):
        d.line([(k * 50, 600), (k * 50, 520)], fill=(110, 110, 116), width=6)
    d.line([(0, 520), (W, 520)], fill=(110, 110, 116), width=10)
    d.line([(1500, FLOOR), (1500, 300)], fill=(90, 90, 90), width=8)               # のぼり
    d.rectangle([1506, 300, 1600, 620], fill=(230, 60, 50))
    d.rectangle([1300, 720, 1700, 780], fill=(150, 110, 70))                       # 本を並べた台
    for k in range(8):
        d.rectangle([1320 + k * 46, 690, 1356 + k * 46, 720], fill=((240, 236, 220), (200, 210, 230))[k % 2])
    return img


def kokkai():
    return _sogo_kokkai()


# ---------------------------------------------------------------- 役所・報道・裁判
def yakusho():
    """役所の部屋。机が並び、書類棚。"""
    img = _rgb(base((222, 222, 214), (206, 206, 198)))
    wood_floor(img, FLOOR, col=(150, 140, 126), line=(130, 122, 110))
    d = _d(img)
    for k in range(6):
        d.rectangle([120 + k * 160, 160, 260 + k * 160, 560], fill=(170, 160, 140), outline=(130, 120, 100), width=3)
        for r in range(4):
            d.rectangle([130 + k * 160, 180 + r * 92, 250 + k * 160, 250 + r * 92], fill=(236, 232, 220))
    d.rectangle([1100, 640, 1800, 700], fill=(150, 150, 156), outline=(120, 120, 126), width=3)
    _papers(d, 1180, 630, n=5)
    return img


def tv():
    """テレビ局の取材の部屋。カメラと照明。"""
    img = _rgb(base((50, 52, 64), (64, 66, 80)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(40, 40, 48))
    for x in (300, 1620):
        d.line([(x, FLOOR), (x, 260)], fill=(80, 80, 88), width=10)
        d.rectangle([x - 70, 200, x + 70, 290], fill=(70, 70, 78))
        _glow(img, x, 300, 260, (255, 250, 220), 60)
        d = _d(img)
    d.rectangle([1300, 560, 1460, 660], fill=(30, 30, 34))
    d.ellipse([1430, 580, 1500, 640], fill=(60, 70, 90))
    d.line([(1380, 660), (1340, FLOOR)], fill=(40, 40, 44), width=8)
    d.line([(1380, 660), (1420, FLOOR)], fill=(40, 40, 44), width=8)
    return img


def houtei():
    return _sogo_saibansho()


def kaiken():
    return _sega_kaiken()


def kaiken_mae():
    """会見場の外の廊下。報道陣の列。"""
    img = _rgb(base((200, 196, 188), (186, 182, 174)))
    wood_floor(img, FLOOR, col=(150, 140, 126), line=(130, 122, 110))
    d = _d(img)
    for k in range(4):
        _window(d, 140 + k * 440, 140, 460 + k * 440, 380, sky=(200, 214, 230))
    _person_line(d, 60, FLOOR + 40, 16, 1.2)
    return img


LOCATIONS = {
    "sb_heya": heya, "sb_gendai": gendai, "sb_kouri": kouri, "sb_kouri_kara": kouri_kara,
    "sb_kojo": kojo, "sb_kojo_teiden": kojo_teiden, "sb_kaigi": kaigi, "sb_kaigi_akaji": kaigi_akaji,
    "sb_soko": soko, "sb_soko_kara": soko_kara, "sb_soko_soto": soko_soto, "sb_soko_soto_shimatta": soko_soto_shimatta,
    "sb_soko_jimusho": soko_jimusho, "sb_soko_jimusho_yoru": soko_jimusho_yoru, "sb_nikukojo": nikukojo,
    "sb_yakusho": yakusho, "sb_soko_sanran": soko_sanran, "sb_kuko": kuko, "sb_rikkyo": rikkyo, "sb_kokkai": kokkai, "sb_tv": tv, "sb_houtei": houtei, "sb_kaiken": kaiken, "sb_kaiken_mae": kaiken_mae,
}

CARDS = ["1995", "2000", "2001", "2002", "2003", "2004"]


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, fn in LOCATIONS.items():
        if only and name not in only:
            continue
        fn().save(OUT / f"{name}.png")
        print(f"生成完了: {name}.png")
    for y in CARDS:
        if only and f"sb_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"sb_card_{y}.png")
        print(f"生成完了: sb_card_{y}.png")
