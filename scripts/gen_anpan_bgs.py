#!/usr/bin/env python3
"""あんぱんの誕生・木村安兵衛回（55_あんぱんの誕生 / slug=kimuraya-anpan）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針は魚探回（gen_furuno_bgs.py）と同じ。
実在メーカーの商標（ロゴ・店名の文字）は描かない。看板も無地にする。

実行: PYTHONPATH=. python scripts/gen_anpan_bgs.py [名前...]
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


def _bun(d, cx, cy, r, sakura=False, col=(196, 128, 66)):
    """丸いあんぱん。sakura=True なら、へそに桜の塩漬け。"""
    d.ellipse([cx - r, cy - r * 0.62, cx + r, cy + r * 0.62], fill=col, outline=(150, 92, 44), width=3)
    d.ellipse([cx - r * 0.7, cy - r * 0.5, cx + r * 0.2, cy - r * 0.1], fill=(214, 150, 86))
    if sakura:
        d.ellipse([cx - r * 0.22, cy - r * 0.2, cx + r * 0.22, cy + r * 0.12], fill=(236, 150, 170))
    else:
        d.ellipse([cx - r * 0.12, cy - r * 0.1, cx + r * 0.12, cy + r * 0.06], fill=(160, 100, 50))


def _hard_bread(d, cx, cy, w, h):
    """硬い西洋パン（細長い塊）。"""
    d.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], radius=h // 2,
                        fill=(170, 116, 64), outline=(120, 80, 40), width=4)
    for k in range(3):
        x = cx - w // 3 + k * w // 3
        d.line([(x - 20, cy - h // 3), (x + 20, cy + h // 4)], fill=(210, 160, 100), width=5)


def _oven(img, x, y, fire=True, ruined=False, s=1.0):
    """石窯。s で大きさを変える（人物の間に収めるため）。"""
    d = _d(img)
    col = (120, 116, 110) if not ruined else (90, 84, 80)

    def P(a, b):
        return (x + a * s, y + b * s)
    d.rectangle([*P(0, 120), *P(360, 340)], fill=col)
    d.chord([*P(0, 0), *P(360, 240)], 180, 360, fill=col)
    for k in range(4):
        d.line([P(0, 150 + k * 50), P(360, 150 + k * 50)], fill=(96, 92, 86), width=3)
    d.chord([*P(110, 170), *P(250, 310)], 180, 360, fill=(40, 30, 26))
    d.rectangle([*P(110, 240), *P(250, 300)], fill=(40, 30, 26))
    if fire:
        cx, cy = P(180, 260)
        _glow(img, int(cx), int(cy), int(90 * s), (255, 150, 60), 150)
        d = _d(img)
        d.ellipse([*P(140, 250), *P(220, 296)], fill=(255, 170, 70))


def _brick_wall(d, x0, y0, x1, y1, col=(170, 90, 70), line=(140, 70, 54)):
    d.rectangle([x0, y0, x1, y1], fill=col)
    for yy in range(y0, y1, 30):
        d.line([(x0, yy), (x1, yy)], fill=line, width=3)
        off = 0 if (yy - y0) // 30 % 2 == 0 else 40
        for xx in range(x0 + off, x1, 80):
            d.line([(xx, yy), (xx, yy + 30)], fill=line, width=3)


def _sign(d, x0, y0, x1, y1):
    """無地の看板（文字は描かない）。"""
    d.rectangle([x0, y0, x1, y1], fill=(60, 44, 30), outline=(200, 170, 90), width=8)
    d.rectangle([x0 + 20, y0 + 16, x1 - 20, y1 - 16], outline=(120, 96, 60), width=3)


# ------------------------------------------------------------ 現代
def ima():
    """現代の部屋の窓辺。机につぶあんぱんと牛乳、窓の外の鳩。"""
    img = base((236, 232, 222), (214, 208, 196))
    d = _d(img)
    wood_floor(img, FLOOR, col=(170, 140, 104), line=(150, 122, 90))
    d = _d(img)
    _window(d, 700, 120, 1220, 470, sky=(176, 210, 232))
    d.rectangle([700, 400, 1220, 416], fill=(120, 110, 100))              # 手すり
    d.ellipse([1040, 350, 1110, 404], fill=(150, 150, 160))               # 鳩
    d.ellipse([1090, 336, 1126, 370], fill=(140, 140, 152))
    d.polygon([(1124, 350), (1140, 356), (1124, 360)], fill=(230, 170, 60))
    d.rectangle([640, 600, 1280, 650], fill=(180, 150, 110))              # 机
    _bun(d, 860, 580, 70)
    d.rounded_rectangle([1020, 480, 1090, 600], radius=12, fill=(246, 246, 246), outline=(180, 180, 190), width=3)
    d.rectangle([1020, 480, 1090, 510], fill=(90, 140, 210))              # 牛乳パック
    return img


def ima2():
    """シメの窓辺。皿に酒まんじゅう。窓の外に鳩はいない。"""
    img = base((236, 232, 222), (214, 208, 196))
    d = _d(img)
    wood_floor(img, FLOOR, col=(170, 140, 104), line=(150, 122, 90))
    d = _d(img)
    _window(d, 700, 120, 1220, 470, sky=(186, 214, 232))
    d.rectangle([700, 400, 1220, 416], fill=(120, 110, 100))
    d.rectangle([640, 600, 1280, 650], fill=(180, 150, 110))
    d.ellipse([820, 560, 1100, 610], fill=(240, 240, 236), outline=(190, 190, 186), width=3)   # 皿
    for cx in (900, 1010):
        d.ellipse([cx - 56, 540, cx + 56, 596], fill=(246, 236, 214), outline=(200, 184, 150), width=3)
    return img


def mura():
    """江戸時代の常陸の村。水につかった田んぼと農家。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (150, 170, 190), (200, 204, 200)), (0, 0))
    d = _d(img)
    d.ellipse([-200, 360, 900, 640], fill=(96, 120, 96))
    d.rectangle([0, 560, W, H], fill=(110, 130, 140))                    # 水につかった田
    for k in range(8):
        y = 600 + k * 50
        d.line([(0, y), (W, y + 20)], fill=(140, 160, 170), width=3)
    for k in range(12):                                                  # 水面から出た稲
        x = 120 + k * 150
        d.line([(x, 700), (x - 10, 650)], fill=(100, 130, 70), width=5)
    d.rectangle([1300, 360, 1720, 560], fill=(150, 120, 90))             # 農家
    d.polygon([(1260, 380), (1510, 230), (1760, 380)], fill=(120, 110, 80))
    return img


def yashiki():
    """江戸の屋敷の米蔵。白壁の蔵と塀、夕方。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (220, 170, 130), (230, 206, 176)), (0, 0))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(170, 156, 130))
    for x0 in (560, 1020):
        d.rectangle([x0, 300, x0 + 380, 700], fill=(236, 232, 222))
        d.polygon([(x0 - 30, 310), (x0 + 190, 200), (x0 + 410, 310)], fill=(60, 60, 64))
        d.rectangle([x0, 600, x0 + 380, 700], fill=(80, 80, 84))          # なまこ壁の腰
        d.rectangle([x0 + 150, 480, x0 + 230, 600], fill=(70, 60, 50))   # 扉
    return img


def ie():
    """長屋の部屋。畳と行灯。"""
    img = base((150, 130, 104), (120, 104, 84))
    tatami_floor(img, int(H * 0.72))
    d = _d(img)
    d.rectangle([700, 150, 1220, 520], fill=(230, 220, 196), outline=(110, 90, 66), width=10)   # 障子
    for x in range(700, 1220, 104):
        d.line([(x, 150), (x, 520)], fill=(110, 90, 66), width=4)
    for y in range(150, 520, 92):
        d.line([(700, y), (1220, y)], fill=(110, 90, 66), width=4)
    _glow(img, 960, 700, 160, (255, 210, 140), 110)
    d = _d(img)
    d.rectangle([920, 640, 1000, 760], fill=(236, 220, 180), outline=(90, 70, 50), width=4)      # 行灯
    return img


def jusanjo():
    """明治初めの職業授産所。机と帳面、机の上に硬いパン。"""
    img = base((214, 204, 184), (184, 174, 156))
    d = _d(img)
    wood_floor(img, FLOOR, col=(130, 104, 78), line=(110, 88, 66))
    d = _d(img)
    _window(d, 120, 150, 560, 450, sky=(170, 196, 214))
    d.rectangle([640, 600, 1280, 650], fill=(140, 110, 80))               # 机
    d.rectangle([1180, 600, 1380, 650], fill=(140, 110, 80))              # 梅吉とつむぎの間の小机
    for k in range(3):
        d.rectangle([660 + k * 90, 560, 740 + k * 90, 600], fill=(236, 230, 214), outline=(160, 150, 130), width=2)
    _hard_bread(d, 1280, 575, 160, 56)
    return img


def bunei():
    """1869年の小さなパン屋の店先。石窯と、棚の硬いパン。"""
    img = base((200, 184, 160), (170, 154, 132))
    d = _d(img)
    wood_floor(img, FLOOR, col=(120, 96, 70), line=(100, 80, 58))
    _oven(img, 700, 380, s=0.83)
    d = _d(img)
    for y in (260, 460):
        d.rectangle([80, y + 70, 560, y + 86], fill=(110, 84, 58))
        for k in range(3):
            _hard_bread(d, 160 + k * 150, y + 40, 120, 44)
    return img


def umi():
    """芝浦の海。夕方の浜。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, 520), (230, 170, 130), (240, 206, 170)), (0, 0))
    img.paste(vgrad((W, H - 520), (100, 110, 140), (60, 70, 100)), (0, 520))
    d = _d(img)
    d.polygon([(0, 820), (W, 760), (W, H), (0, H)], fill=(190, 170, 140))   # 浜
    for k in range(6):
        y = 560 + k * 36
        d.line([(200 + k * 40, y), (1700 - k * 60, y)], fill=(140, 150, 180), width=3)
    return img


def kaji():
    """火事の焼け跡。石窯だけが残る。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (120, 110, 110), (170, 160, 150)), (0, 0))
    d = _d(img)
    d.rectangle([0, 740, W, H], fill=(70, 60, 56))
    _oven(img, 615, 480, fire=False, ruined=True, s=0.78)
    d = _d(img)
    for x, h in ((200, 200), (360, 120), (1400, 180), (1620, 240)):     # 焼けた柱
        d.rectangle([x, 740 - h, x + 30, 740], fill=(40, 34, 30))
    for k in range(5):                                                    # 煙
        r = 50 + k * 20
        d.ellipse([940 - r + k * 20, 300 - k * 70 - r, 940 + r + k * 20, 300 - k * 70 + r], fill=(150, 146, 146))
    return img


def eki():
    """明治の新橋駅のホーム。蒸気機関車とパンの売店。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (180, 196, 210), (214, 210, 200)), (0, 0))
    d = _d(img)
    d.rectangle([0, 660, W, H], fill=(150, 140, 126))                    # ホーム
    d.rectangle([0, 600, W, 660], fill=(90, 84, 80))                      # 線路側
    d.rectangle([1250, 420, 1900, 600], fill=(40, 40, 44))               # 機関車
    d.rectangle([1300, 330, 1360, 420], fill=(40, 40, 44))
    for x in (1350, 1550, 1750):
        d.ellipse([x - 60, 540, x + 60, 660], fill=(30, 30, 34))
    for k in range(3):
        r = 40 + k * 20
        d.ellipse([1330 - r - k * 40, 300 - k * 60 - r, 1330 + r - k * 40, 300 - k * 60 + r], fill=(220, 220, 224))
    d.rectangle([700, 560, 1180, 700], fill=(140, 110, 80))              # 売店
    d.rectangle([680, 520, 1200, 560], fill=(110, 84, 58))
    for k in range(4):
        _hard_bread(d, 770 + k * 110, 640, 90, 36)
    return img


def ginza0():
    """1874年ごろの銀座の煉瓦街。ぬかるんだ道とガス灯。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (190, 200, 210), (214, 212, 204)), (0, 0))
    d = _d(img)
    _brick_wall(d, 0, 200, 640, 700)
    _brick_wall(d, 1280, 200, W, 700)
    for x in (80, 300, 1360, 1580):
        d.rectangle([x, 300, x + 140, 480], fill=(60, 60, 70))
    d.rectangle([0, 700, W, H], fill=(120, 100, 76))                    # ぬかるみ
    for cx, cy, rx in ((500, 820, 160), (960, 900, 240), (1450, 840, 180)):
        d.ellipse([cx - rx, cy - 30, cx + rx, cy + 30], fill=(100, 110, 120))   # 水たまり
    for x in (700, 1220):                                                # ガス灯
        d.rectangle([x, 380, x + 16, 700], fill=(50, 50, 54))
        d.rectangle([x - 20, 340, x + 36, 390], fill=(230, 220, 170), outline=(50, 50, 54), width=4)
    return img


def kobo():
    """工房。石窯、酒種の桶、米俵、生地の台。"""
    img = base((190, 176, 152), (160, 146, 124))
    d = _d(img)
    wood_floor(img, FLOOR, col=(120, 96, 70), line=(100, 80, 58))
    _oven(img, 1300, 300)
    d = _d(img)
    d.rectangle([620, 600, 900, 650], fill=(150, 116, 80))               # 台
    for k in range(2):
        d.ellipse([640 + k * 130, 560, 750 + k * 130, 606], fill=(236, 226, 200))   # 生地
    d.rectangle([650, 380, 790, 540], fill=(140, 100, 64))               # 桶
    for y in (410, 460, 510):
        d.line([(650, y), (790, y)], fill=(90, 64, 40), width=6)
    d.ellipse([650, 360, 790, 400], fill=(236, 230, 214))                # 桶の中の種
    for k in range(2):                                                    # 米俵
        d.ellipse([960 + k * 110, 480, 1060 + k * 110, 580], fill=(214, 196, 150), outline=(160, 140, 100), width=4)
    return img


def zukai():
    """図解用。米→糖→酵母→泡でふくらむ生地を、キャラの間に縦に並べる。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (40, 44, 56), (22, 24, 32)), (0, 0))
    d = _d(img)
    cx = 960
    for k in range(5):                                                   # 米粒
        d.ellipse([cx - 150 + k * 60, 110, cx - 110 + k * 60, 170], fill=(246, 246, 240))
    d.polygon([(cx - 20, 200), (cx + 20, 200), (cx, 240)], fill=(200, 200, 90))       # 矢印
    for k in range(4):                                                   # 糖（角砂糖）
        d.rectangle([cx - 130 + k * 70, 270, cx - 80 + k * 70, 320], fill=(250, 244, 220))
    d.polygon([(cx - 20, 350), (cx + 20, 350), (cx, 390)], fill=(200, 200, 90))
    for k in range(6):                                                   # 酵母と泡
        x = cx - 150 + k * 60
        d.ellipse([x, 430, x + 36, 466], fill=(220, 190, 120))
        d.ellipse([x + 20, 400, x + 44, 424], outline=(200, 220, 240), width=4)
    d.polygon([(cx - 20, 500), (cx + 20, 500), (cx, 540)], fill=(200, 200, 90))
    d.ellipse([cx - 220, 580, cx + 220, 820], fill=(236, 214, 170))       # ふくらんだ生地
    for k in range(9):
        x, y = cx - 150 + (k * 83) % 300, 620 + (k * 47) % 150
        d.ellipse([x, y, x + 30, y + 30], fill=(206, 180, 136))
    return img


def _oil_lamp(img, lx, ly=140):
    """天井から吊ったランプ（明治の店。電球はまだない）。"""
    d = _d(img)
    d.line([lx, 0, lx, ly], fill=(40, 34, 28), width=5)
    _glow(img, lx, ly + 70, 200, (255, 200, 120), 60)
    d = _d(img)
    d.polygon([(lx - 40, ly), (lx + 40, ly), (lx + 26, ly + 20), (lx - 26, ly + 20)], fill=(90, 80, 60))
    d.ellipse([lx - 22, ly + 20, lx + 22, ly + 90], fill=(250, 226, 170), outline=(120, 100, 70), width=3)
    d.rectangle([lx - 26, ly + 88, lx + 26, ly + 104], fill=(90, 80, 60))


def mise(sakura=True):
    """明治の銀座4丁目の店内。陳列台のあんぱん、上に無地の看板。sakura=True なら桜のへそ入り。"""
    img = base((214, 200, 176), (184, 170, 148))
    d = _d(img)
    wood_floor(img, FLOOR, col=(130, 104, 78), line=(110, 88, 66))
    d = _d(img)
    _sign(d, 700, 80, 1220, 200)
    d.rectangle([640, 520, 1280, 700], fill=(120, 90, 60))               # 陳列台
    d.rectangle([660, 440, 1260, 530], fill=(210, 226, 232), outline=(120, 90, 60), width=6)   # ガラス
    for k in range(5):
        _bun(d, 730 + k * 115, 490, 44, sakura=sakura and (k % 2 == 0))
    _oil_lamp(img, 480)
    return img


def mise0():
    """献上より前の店内。桜のへそはまだ無い。"""
    return mise(sakura=False)


def sakura():
    """向島の屋敷の庭。満開の桜。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (190, 214, 236), (230, 230, 226)), (0, 0))
    d = _d(img)
    d.rectangle([0, 720, W, H], fill=(120, 150, 100))
    d.rectangle([1200, 420, 1920, 720], fill=(190, 170, 140))            # 屋敷
    d.polygon([(1160, 440), (1560, 300), (1960, 440)], fill=(70, 70, 76))
    for cx, cy, r in ((380, 360, 260), (820, 300, 220), (1100, 400, 180)):
        d.rectangle([cx - 18, cy, cx + 18, 740], fill=(90, 70, 60))
        d.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], fill=(244, 196, 210))
        d.ellipse([cx - r * 0.6, cy - r * 0.7, cx + r * 0.4, cy + r * 0.2], fill=(250, 214, 226))
    return img


def yoru():
    """夜の銀座の店先。ガス灯の明かり。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (20, 24, 44), (40, 40, 60)), (0, 0))
    d = _d(img)
    _brick_wall(d, 400, 200, 1520, 760, col=(110, 60, 50), line=(90, 48, 40))
    d.rectangle([700, 420, 1220, 760], fill=(240, 210, 150))             # 明るい店の入口
    _sign(d, 700, 260, 1220, 380)
    for x in (300, 1620):
        d.rectangle([x, 380, x + 16, 820], fill=(30, 30, 34))
        _glow(img, x + 8, 360, 120, (255, 220, 150), 150)
        d = _d(img)
        d.rectangle([x - 20, 340, x + 36, 390], fill=(255, 236, 180))
    d.rectangle([0, 760, W, H], fill=(60, 56, 56))
    return img


def ginza():
    """にぎわう銀座の通り。煉瓦の店と、宣伝の旗（文字なし）。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (180, 206, 228), (220, 218, 210)), (0, 0))
    d = _d(img)
    _brick_wall(d, 0, 220, 620, 720)
    _brick_wall(d, 1300, 220, W, 720)
    d.rectangle([0, 720, W, H], fill=(176, 164, 140))
    for x in (700, 900, 1100):                                            # 旗
        d.line([(x, 300), (x, 700)], fill=(90, 70, 50), width=6)
        d.rectangle([x + 3, 300, x + 70, 520], fill=(220, 70, 60) if x != 900 else (240, 200, 70))
    # 大太鼓（宣伝隊とつむぎの間）。胴の側面とばちを描いて太鼓に見えるように
    d.rectangle([1200, 560, 1300, 700], fill=(150, 90, 50), outline=(90, 50, 30), width=4)      # 胴
    d.ellipse([1170, 560, 1230, 700], fill=(236, 220, 190), outline=(90, 50, 30), width=5)      # 皮（左）
    d.ellipse([1270, 560, 1330, 700], fill=(220, 204, 176), outline=(90, 50, 30), width=5)      # 皮（右）
    for y in (590, 630, 670):
        d.line([(1215, y), (1285, y)], fill=(110, 60, 36), width=3)
    d.line([(1150, 520), (1195, 610)], fill=(120, 80, 50), width=8)                            # ばち
    d.ellipse([1186, 600, 1206, 620], fill=(240, 230, 210))
    return img


def yuugure():
    """夕暮れの店の中。静かな場面で使う。"""
    img = base((120, 96, 84), (80, 64, 60))
    d = _d(img)
    wood_floor(img, FLOOR, col=(90, 70, 56), line=(70, 54, 44))
    d = _d(img)
    _window(d, 700, 160, 1220, 500, sky=(230, 150, 110))
    _glow(img, 960, 330, 260, (250, 170, 120), 90)
    d = _d(img)
    d.rectangle([760, 600, 1160, 640], fill=(110, 84, 60))
    return img


def gendai():
    """今のパン屋の棚。あんぱん、ジャムパン、クリームパン。"""
    img = base((244, 240, 232), (226, 220, 210))
    d = _d(img)
    wood_floor(img, FLOOR, col=(190, 160, 120), line=(170, 140, 104))
    d = _d(img)
    for row, y in enumerate((260, 460, 660)):
        d.rectangle([620, y + 60, 1300, y + 76], fill=(160, 130, 96))
        for k in range(5):
            x = 690 + k * 130
            if row == 0:
                _bun(d, x, y + 20, 48, sakura=True)
            elif row == 1:
                _bun(d, x, y + 20, 48, col=(200, 140, 70))
                d.ellipse([x - 14, y + 10, x + 14, y + 30], fill=(190, 40, 60))      # ジャム
            else:
                d.chord([x - 54, y - 20, x + 54, y + 60], 180, 360, fill=(230, 180, 100),
                        outline=(170, 120, 60), width=3)                               # クリームパン
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
    "an_ima": ima, "an_ima2": ima2, "an_mura": mura, "an_yashiki": yashiki, "an_ie": ie,
    "an_jusanjo": jusanjo, "an_bunei": bunei, "an_umi": umi, "an_kaji": kaji, "an_eki": eki,
    "an_ginza0": ginza0, "an_kobo": kobo, "an_zukai": zukai, "an_mise": mise, "an_mise0": mise0, "an_sakura": sakura,
    "an_yoru": yoru, "an_ginza": ginza, "an_yuugure": yuugure, "an_gendai": gendai, "an_shiryo": shiryo,
}

CARDS = ["1868", "1869", "1874", "1875", "1887", "1900"]


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
        if only and f"an_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"an_card_{y}.png")
        print(f"生成完了: an_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
