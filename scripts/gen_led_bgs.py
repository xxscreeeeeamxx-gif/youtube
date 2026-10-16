#!/usr/bin/env python3
"""青色LEDの裁判の回（91_青色LEDの裁判 / slug=blue-led-nakamura）の背景を生成する。

方針は富士フイルム回・そごう回と同じで、部品もそこから借りる。
実在の会社の商標（ロゴ・社名の文字・製品名）は描かない。
差し替え用（_kemuri・_ao など）は元の絵を呼んで要素を足す。

実行: PYTHONPATH=. python scripts/gen_led_bgs.py [名前...]
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import ImageDraw, ImageFilter  # noqa: E402

from scripts.gen_drama_bgs import H, OUT, W, base, tatami_floor, vgrad, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import _boxes, _papers, _phone, _window, year_card  # noqa: E402
from scripts.gen_sega_bgs import _chart, _flat_tv, _glow, _person_line, kaiken as _sega_kaiken  # noqa: E402
from scripts.gen_sogo_bgs import saibansho as _sogo_saibansho  # noqa: E402

FLOOR = int(H * 0.86)
BLUE = (60, 120, 255)


def _d(img):
    return ImageDraw.Draw(img, "RGBA")


def _rgb(img):
    return img.convert("RGB") if img.mode != "RGB" else img


def _bulb(d, x, y, s=1.0, on=True, col=(255, 250, 230)):
    """天井の照明（平たい円盤）。"""
    d.ellipse([x - 90 * s, y - 18 * s, x + 90 * s, y + 18 * s], fill=col if on else (200, 200, 196),
              outline=(170, 170, 166), width=3)


def _reactor(d, x, y, s=1.0):
    """手作りの装置（炉と配管）。左下が x, y。"""
    d.rectangle([x, y - 300 * s, x + 260 * s, y], fill=(150, 156, 164), outline=(90, 96, 104), width=4)
    d.ellipse([x + 70 * s, y - 230 * s, x + 190 * s, y - 110 * s], fill=(60, 64, 72), outline=(200, 200, 206), width=6)
    for k in range(4):                                                            # 配管
        px = x + 30 * s + k * 60 * s
        d.line([(px, y - 300 * s), (px, y - 420 * s), (px + 300 * s, y - 420 * s - k * 20 * s)],
               fill=(180, 160, 120), width=int(10 * s))
    for k in range(3):                                                            # ガスのボンベ
        bx = x + 320 * s + k * 70 * s
        d.rounded_rectangle([bx, y - 240 * s, bx + 50 * s, y], radius=int(20 * s),
                            fill=((90, 140, 90), (120, 120, 130), (170, 90, 60))[k], outline=(60, 60, 60), width=3)
    d.rectangle([x - 40 * s, y - 90 * s, x + 20 * s, y], fill=(70, 74, 80))      # 計器
    for k in range(3):
        d.ellipse([x - 34 * s, y - 84 * s + k * 26 * s, x + 14 * s, y - 64 * s + k * 26 * s], fill=(230, 230, 220))


# ---------------------------------------------------------------- 今
def heya():
    """今の部屋（夜）。天井のLEDの照明、テレビ、机にスマホ。"""
    img = _rgb(base((228, 228, 232), (212, 212, 218)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    _bulb(d, 960, 40, 1.4)
    _glow(img, 960, 60, 360, (255, 255, 240), 60)
    d = _d(img)
    _window(d, 760, 160, 1160, 420, sky=(30, 40, 80))
    sx0, sy0, sx1, sy1 = _flat_tv(d, 1360, 380, 1800, 620, screen=(40, 80, 150))
    d.rectangle([1400, 640, 1760, 700], fill=(140, 106, 76))
    d.rectangle([160, 640, 640, 700], fill=(150, 116, 84))
    d.rounded_rectangle([360, 610, 400, 636], radius=4, fill=(30, 30, 36))     # スマホ（伏せて置く）
    return img


def machi_yoru():
    """今の街の夜。LEDの信号、ビルの大きな画面、街灯。"""
    img = vgrad((W, H), (10, 14, 36), (30, 34, 60))
    d = _d(img)
    rnd = random.Random(4)
    for k in range(9):                                                            # ビル
        x0 = k * 220 - 40
        top = 200 + rnd.randint(0, 220)
        d.rectangle([x0, top, x0 + 200, FLOOR], fill=(36, 40, 62))
        for r in range((FLOOR - top) // 60):
            for c in range(4):
                if rnd.random() < 0.55:
                    d.rectangle([x0 + 20 + c * 44, top + 20 + r * 60, x0 + 46 + c * 44, top + 50 + r * 60],
                                fill=(250, 250, 236))
    d.rectangle([620, 240, 1180, 520], fill=(20, 20, 30), outline=(80, 80, 90), width=8)   # 大きな画面
    d.rectangle([636, 256, 1164, 504], fill=(60, 140, 255))
    _glow(img, 900, 380, 360, (80, 150, 255), 70)
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(40, 40, 48))
    d.rectangle([1500, 300, 1530, FLOOR], fill=(70, 70, 76))                      # 信号
    d.rounded_rectangle([1420, 240, 1700, 330], radius=20, fill=(40, 40, 44))
    for k, c in enumerate(((40, 220, 160), (70, 60, 40), (70, 40, 40))):
        d.ellipse([1440 + k * 88, 254, 1500 + k * 88, 314], fill=c)
    _glow(img, 1470, 284, 120, (40, 220, 160), 90)
    return img


def stockholm():
    """授賞式の会場。青い壁、花、正面の舞台。"""
    img = vgrad((W, H), (30, 50, 110), (60, 80, 140))
    d = _d(img)
    for k in range(7):
        d.rectangle([60 + k * 280, 80, 200 + k * 280, 560], fill=(40, 64, 130))       # 柱
    d.rectangle([0, 560, W, 640], fill=(200, 170, 90))                                 # 舞台の縁
    d.rectangle([0, 640, W, H], fill=(150, 30, 40))                                    # 赤い絨毯
    rnd = random.Random(11)
    for k in range(40):                                                                # 花
        x, y = rnd.randint(40, W - 40), rnd.randint(540, 600)
        d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=rnd.choice([(250, 250, 250), (240, 200, 210), (250, 220, 120)]))
    return img


# ---------------------------------------------------------------- 徳島の会社
def kojo_soto():
    """徳島の会社。山と田んぼを背に、低い工場の建物が並ぶ。"""
    img = vgrad((W, H), (176, 210, 236), (226, 236, 240))
    d = _d(img)
    d.polygon([(0, 520), (300, 330), (620, 470), (980, 300), (1360, 460), (1700, 320), (W, 450), (W, 620), (0, 620)],
              fill=(90, 130, 96))
    d.rectangle([0, 620, W, H], fill=(140, 170, 100))
    for k in range(10):
        d.line([(0, 660 + k * 44), (W, 640 + k * 44)], fill=(120, 150, 86), width=3)  # 田んぼのあぜ
    for k, (x0, w, h) in enumerate(((240, 520, 200), (820, 380, 160), (1260, 460, 220))):
        d.rectangle([x0, 640 - h, x0 + w, 640], fill=(220, 220, 214), outline=(150, 150, 146), width=4)
        d.polygon([(x0 - 10, 640 - h), (x0 + w // 2, 640 - h - 50), (x0 + w + 10, 640 - h)], fill=(110, 120, 130))
        for c in range(w // 80):
            d.rectangle([x0 + 20 + c * 80, 640 - h + 40, x0 + 70 + c * 80, 640 - h + 90], fill=(180, 210, 230))
    d.rectangle([1600, 300, 1640, 640], fill=(170, 170, 166))                      # 煙突
    return img


def jikken(mode=""):
    """古い実験室。手作りの装置と配管。kemuri は煙と赤い警告灯、ao は暗い部屋に青い光。"""
    if mode == "ao":
        img = _rgb(base((26, 28, 40), (36, 38, 52)))
        wood_floor(img, FLOOR, col=(40, 40, 50), line=(32, 32, 42))
    else:
        img = _rgb(base((206, 206, 198), (190, 190, 182)))
        wood_floor(img, FLOOR, col=(150, 146, 136), line=(130, 126, 118))
    d = _d(img)
    _window(d, 1380, 130, 1780, 380, sky=(30, 34, 60) if mode == "ao" else (200, 218, 232))
    _reactor(d, 560, FLOOR - 20, 1.1)
    d.rectangle([1260, 640, 1820, 690], fill=(170, 160, 144), outline=(120, 112, 100), width=3)   # 作業台
    _papers(d, 1320, 630, n=3)
    if mode == "kemuri":
        sm = img.copy()
        ds = ImageDraw.Draw(sm, "RGBA")
        rnd = random.Random(7)
        for k in range(70):
            x, y, r = rnd.randint(0, W), rnd.randint(0, int(H * 0.8)), rnd.randint(80, 220)
            g = rnd.randint(150, 200)
            ds.ellipse([x - r, y - r, x + r, y + r], fill=(g, g, g, 150))
        img = sm.filter(ImageFilter.GaussianBlur(6))
        d = _d(img)
        d.ellipse([200, 60, 300, 160], fill=(240, 40, 40))
        _glow(img, 250, 110, 220, (255, 40, 40), 110)
    elif mode == "ao":
        _glow(img, 780, FLOOR - 210, 420, BLUE, 140)
        d = _d(img)
        d.ellipse([760, FLOOR - 230, 800, FLOOR - 190], fill=(200, 220, 255))
    return img


def jikken_kemuri():
    return jikken("kemuri")


def jikken_ao():
    return jikken("ao")


def soko():
    """倉庫。売れ残りの段ボールが積まれている。"""
    img = vgrad((W, H), (180, 176, 168), (156, 152, 146))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(130, 126, 120))
    for k in range(4):
        d.line([(0, 90 + k * 34), (W, 90 + k * 34)], fill=(120, 116, 110), width=6)
    for x0 in (60, 700, 1340):
        _boxes(d, x0, FLOOR, n=5, rows=5)
    return img


def shachoshitsu():
    """古い会社の社長室。木の机、壁に額（中身は風景）、窓の外は山。"""
    img = _rgb(base((220, 210, 190), (204, 194, 174)))
    wood_floor(img, FLOOR, col=(110, 80, 56), line=(92, 66, 46))
    d = _d(img)
    _window(d, 1300, 120, 1800, 430, sky=(190, 214, 232))
    d.polygon([(1310, 420), (1450, 300), (1580, 380), (1700, 290), (1790, 420)], fill=(100, 136, 100))
    d.rectangle([240, 160, 620, 400], fill=(200, 180, 140), outline=(110, 80, 50), width=10)   # 額
    d.polygon([(270, 380), (380, 250), (470, 330), (560, 230), (600, 380)], fill=(120, 150, 120))
    d.rectangle([700, 640, 1500, 700], fill=(96, 64, 42))
    d.rectangle([720, 700, 760, 860], fill=(76, 50, 34))
    d.rectangle([1440, 700, 1480, 860], fill=(76, 50, 34))
    _papers(d, 820, 630, n=3)
    _phone(d, 1320, 570, 0.6)
    return img


def jimusho():
    """社内の事務所。机が並び、書類の山。"""
    img = _rgb(base((222, 222, 214), (206, 206, 198)))
    wood_floor(img, FLOOR, col=(150, 140, 126), line=(130, 122, 110))
    d = _d(img)
    _window(d, 120, 120, 560, 400, sky=(200, 218, 232))
    _window(d, 1360, 120, 1800, 400, sky=(200, 218, 232))
    for k in range(3):
        x0 = 160 + k * 560
        d.rectangle([x0, 650, x0 + 460, 700], fill=(170, 170, 176), outline=(120, 120, 126), width=3)
        _papers(d, x0 + 40, 640, n=4)
    return img


def shataku():
    """出張先の会社の部屋（夜）。畳と小さな机、窓の外は街の灯り。"""
    img = _rgb(base((206, 196, 170), (190, 180, 156)))
    tatami_floor(img, int(H * 0.8))
    d = _d(img)
    _window(d, 1240, 140, 1700, 420, sky=(20, 24, 50))
    rnd = random.Random(5)
    for k in range(26):
        x, y = rnd.randint(1260, 1680), rnd.randint(300, 400)
        d.rectangle([x, y, x + 10, y + 8], fill=(250, 230, 160))
    d.rectangle([600, 700, 1100, 740], fill=(120, 86, 56))                         # ちゃぶ台
    d.rectangle([640, 740, 670, 800], fill=(100, 70, 46))
    d.rectangle([1030, 740, 1060, 800], fill=(100, 70, 46))
    for k in range(3):                                                             # 缶ビール
        d.rounded_rectangle([700 + k * 60, 640, 736 + k * 60, 700], radius=6, fill=(200, 196, 180), outline=(120, 116, 100))
    d.rectangle([180, 120, 420, 300], fill=(236, 226, 196), outline=(140, 110, 70), width=6)
    return img


# ---------------------------------------------------------------- 外の世界
def daigaku_us():
    """アメリカの大学の研究室。窓の外にヤシの木と青い空。"""
    img = _rgb(base((230, 232, 236), (214, 216, 222)))
    wood_floor(img, FLOOR, col=(180, 184, 190), line=(160, 164, 170))
    d = _d(img)
    _window(d, 1200, 110, 1800, 440, sky=(120, 190, 240))
    for x in (1320, 1620):
        d.line([(x, 440), (x + 20, 220)], fill=(130, 100, 70), width=14)
        for a in range(5):
            d.line([(x + 20, 220), (x + 20 + (a - 2) * 70, 200 + abs(a - 2) * 30)], fill=(40, 130, 70), width=12)
    d.rectangle([200, 640, 1100, 690], fill=(236, 238, 240), outline=(170, 174, 180), width=3)
    _reactor(d, 260, 640, 0.6)
    return img


def gakkai():
    """学会の会場。スクリーンに青い光の図、並ぶ客席。"""
    img = _rgb(base((50, 52, 64), (64, 66, 80)))
    d = _d(img)
    d.rectangle([520, 90, 1400, 560], fill=(236, 238, 244), outline=(30, 30, 36), width=8)
    d.ellipse([860, 220, 1060, 420], fill=(70, 130, 255))
    _glow(img, 960, 320, 260, BLUE, 90)
    d = _d(img)
    d.rectangle([1500, 520, 1600, 700], fill=(120, 96, 70))                        # 演台
    d.rectangle([0, 760, W, H], fill=(40, 40, 50))
    _person_line(d, 60, 1000, 14, 1.1)
    return img


def bengoshi():
    """弁護士の事務所。壁一面の本棚と、机に書類の山。"""
    img = _rgb(base((212, 206, 196), (196, 190, 180)))
    wood_floor(img, FLOOR, col=(100, 76, 56), line=(84, 62, 46))
    d = _d(img)
    for r in range(5):
        y = 120 + r * 100
        d.rectangle([100, y + 86, 1000, y + 96], fill=(110, 80, 56))
        for k in range(30):
            d.rectangle([110 + k * 29, y + 20, 134 + k * 29, y + 86],
                        fill=((120, 40, 40), (40, 60, 110), (60, 90, 60), (150, 120, 70))[(k + r) % 4])
    d.rectangle([1100, 640, 1800, 700], fill=(96, 64, 42))
    _papers(d, 1160, 630, n=6)
    _papers(d, 1460, 630, n=4)
    return img


def houtei():
    return _sogo_saibansho()


def saibansho_mae():
    """裁判所の前。石の建物と、報道のカメラの列。"""
    img = vgrad((W, H), (190, 206, 222), (220, 226, 232))
    d = _d(img)
    d.rectangle([200, 160, 1720, 700], fill=(200, 196, 188), outline=(150, 146, 140), width=6)
    for r in range(4):
        for c in range(12):
            d.rectangle([260 + c * 122, 210 + r * 120, 330 + c * 122, 290 + r * 120], fill=(120, 140, 160))
    d.rectangle([0, 700, W, H], fill=(170, 168, 164))
    for k in range(10):
        x = 120 + k * 180
        d.rectangle([x, 820, x + 120, 900], fill=(30, 30, 34))
        d.ellipse([x + 80, 836, x + 130, 886], fill=(60, 70, 90))
        d.line([(x + 60, 900), (x + 20, H)], fill=(40, 40, 44), width=6)
        d.line([(x + 60, 900), (x + 100, H)], fill=(40, 40, 44), width=6)
    return img


def kaiken():
    return _sega_kaiken()


def kaigi():
    """会議室。ボードに上がっていく売上のグラフ。"""
    img = _rgb(base((214, 212, 206), (198, 196, 190)))
    wood_floor(img, FLOOR, col=(106, 96, 86), line=(88, 80, 72))
    d = _d(img)
    _chart(d, 560, 110, 1360, 500, [0.06, 0.08, 0.12, 0.3, 0.6, 0.95], col=(40, 90, 220))
    d.rectangle([420, 640, 1500, 700], fill=(120, 108, 96))
    _papers(d, 600, 630, n=3)
    _papers(d, 1100, 630, n=2)
    return img


LOCATIONS = {
    "led_heya": heya, "led_machi_yoru": machi_yoru, "led_stockholm": stockholm,
    "led_kojo_soto": kojo_soto, "led_jikken": jikken, "led_jikken_kemuri": jikken_kemuri, "led_jikken_ao": jikken_ao,
    "led_soko": soko, "led_shachoshitsu": shachoshitsu, "led_jimusho": jimusho, "led_shataku": shataku,
    "led_daigaku_us": daigaku_us, "led_gakkai": gakkai, "led_bengoshi": bengoshi,
    "led_houtei": houtei, "led_saibansho_mae": saibansho_mae, "led_kaiken": kaiken, "led_kaigi": kaigi,
}

CARDS = ["1979", "1988", "1990", "1991", "1993", "2000", "2001", "2002", "2004", "2005"]


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, fn in LOCATIONS.items():
        if only and name not in only:
            continue
        fn().save(OUT / f"{name}.png")
        print(f"生成完了: {name}.png")
    for y in CARDS:
        if only and f"led_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"led_card_{y}.png")
        print(f"生成完了: led_card_{y}.png")
