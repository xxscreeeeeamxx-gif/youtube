#!/usr/bin/env python3
"""痛くない注射針の再現ドラマ（okano-needle）用のイラスト背景12種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
下町の町工場（油と鉄の色）と、テルモ側の清潔な白、の対比で場面を分けている。
実行: PYTHONPATH=. python3 scripts/gen_nd_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402

STEEL = (150, 158, 168)
OIL = (96, 88, 76)


def _press(d, x, y, w=250, h=330, body=(84, 94, 104)):
    """プレス機を1台。y は床の位置。"""
    top = y - h
    d.rounded_rectangle([x, top + h * 0.42, x + w, y], radius=8, fill=body)
    # コラム（門型）
    d.rectangle([x + 18, top, x + 54, top + int(h * 0.5)], fill=body)
    d.rectangle([x + w - 54, top, x + w - 18, top + int(h * 0.5)], fill=body)
    d.rounded_rectangle([x + 6, top, x + w - 6, top + 54], radius=6, fill=(66, 76, 86))
    # スライド（上下する部分）
    d.rectangle([x + 62, top + 62, x + w - 62, top + 128], fill=(110, 120, 130))
    # ボルスタ（下の台）
    d.rectangle([x + 40, top + int(h * 0.42) - 26, x + w - 40, top + int(h * 0.42)],
                fill=(120, 130, 140))
    # 操作盤
    d.rounded_rectangle([x + w - 46, y - 130, x + w - 8, y - 40], radius=6, fill=(60, 68, 78))
    for k in range(3):
        d.ellipse([x + w - 38, y - 118 + k * 26, x + w - 20, y - 100 + k * 26],
                  fill=[(220, 80, 70), (230, 200, 90), (110, 190, 130)][k])


def koba() -> Image.Image:
    """岡野工業の作業場。プレス機が並ぶ下町の町工場。"""
    img = vgrad((W, H), (128, 124, 116), (100, 96, 90)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 700, (110, 100, 86), (88, 80, 68))
    # 波板の壁
    for x in range(0, W, 46):
        d.line([x, 0, x, 700], fill=(116, 112, 104), width=6)
    # 高窓
    for x in (700, 1140):
        _window(img, d, x, 90, x + 320, 300, (176, 196, 214), (218, 228, 236))
    # プレス機3台
    for x in (60, 620, 1180):
        _press(d, x, 700)
    # 材料のコイルと油缶
    d.ellipse([1560, 520, 1800, 700], fill=(138, 146, 156), outline=(104, 112, 122), width=8)
    d.ellipse([1630, 570, 1730, 650], fill=(96, 96, 100))
    for i, x in enumerate([1520, 1620, 1720]):
        d.rounded_rectangle([x, 760, x + 76, 880], radius=6,
                            fill=(180, 130, 60) if i % 2 else (150, 110, 50))
    return img


def koba_yoru() -> Image.Image:
    """夜の作業場。20代のころ、夕方5時から翌朝まで借りていた時間帯。"""
    img = vgrad((W, H), (46, 46, 54), (32, 32, 40)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 700, (58, 52, 46), (44, 40, 36))
    for x in range(0, W, 46):
        d.line([x, 0, x, 700], fill=(52, 50, 50), width=6)
    for x in (700, 1140):
        _window(img, d, x, 90, x + 320, 300, (18, 20, 34), (28, 30, 46))
    _press(d, 300, 700, body=(58, 66, 76))
    _press(d, 1160, 700, body=(58, 66, 76))
    # 手元の裸電球ひとつだけ
    d.line([880, 0, 880, 140], fill=(70, 66, 60), width=5)
    d.ellipse([836, 138, 924, 220], fill=(240, 220, 150))
    glow(img, 880, 190, 560, (250, 226, 150), 42)
    # 作業台
    d.rounded_rectangle([700, 620, 1120, 700], radius=6, fill=(84, 70, 54))
    return img


def jimusho() -> Image.Image:
    """岡野工業の事務所。図面と電話と茶。"""
    img = vgrad((W, H), (192, 184, 168), (168, 160, 146)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 660, (148, 130, 104), (124, 108, 86))
    _window(img, d, 1400, 140, 1800, 440, (176, 198, 218), (222, 232, 238))
    # 図面を貼った壁
    d.rectangle([90, 130, 700, 520], fill=(206, 200, 186))
    for i, (x, y) in enumerate([(120, 160), (330, 150), (530, 175), (150, 340), (390, 330)]):
        d.rectangle([x, y, x + 160, y + 130], fill=(238, 236, 228),
                    outline=(168, 164, 152), width=4)
        for j in range(3):
            d.line([x + 16, y + 30 + j * 30, x + 144, y + 30 + j * 30],
                   fill=(130, 150, 180), width=3)
    # スチール机
    d.rounded_rectangle([760, 560, 1360, 720], radius=6, fill=(118, 118, 112))
    d.rectangle([760, 560, 1360, 592], fill=(96, 96, 92))
    # 黒電話と湯呑み
    d.rounded_rectangle([840, 470, 990, 562], radius=12, fill=(44, 44, 50))
    d.rounded_rectangle([856, 442, 974, 486], radius=18, fill=(32, 32, 38))
    d.ellipse([1120, 500, 1190, 560], fill=(226, 220, 206))
    return img


def terumo() -> Image.Image:
    """テルモの開発室。白くて明るい、町工場と対照的な空間。"""
    img = vgrad((W, H), (232, 238, 242), (208, 216, 224)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 660, (204, 212, 220), (184, 192, 202))
    _window(img, d, 1300, 130, 1810, 480, (166, 200, 226), (226, 236, 244))
    # 白い実験台
    d.rounded_rectangle([120, 560, 1180, 700], radius=8, fill=(238, 242, 246))
    d.rectangle([120, 560, 1180, 596], fill=(214, 222, 230))
    # 試験管立てと器具
    d.rounded_rectangle([200, 470, 420, 566], radius=6, fill=(210, 218, 226))
    for k in range(5):
        d.rectangle([222 + k * 40, 420, 246 + k * 40, 540], fill=(226, 238, 244),
                    outline=(178, 194, 208), width=3)
    # ディスプレイ
    d.rounded_rectangle([620, 380, 960, 556], radius=8, fill=(236, 240, 244),
                        outline=(180, 190, 200), width=6)
    d.rectangle([648, 408, 932, 528], fill=(56, 92, 128))
    for j in range(4):
        d.line([668, 432 + j * 24, 912, 432 + j * 24], fill=(140, 190, 230), width=4)
    # 棚
    d.rectangle([70, 140, 560, 460], fill=(224, 230, 236), outline=(196, 204, 212), width=6)
    for r in range(2):
        d.rectangle([82, 168 + r * 148, 548, 180 + r * 148], fill=(202, 210, 218))
    return img


def byoin() -> Image.Image:
    """病院の処置室。子どもが毎日インスリンを打つ場所。"""
    img = vgrad((W, H), (226, 236, 232), (204, 216, 214)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 660, (206, 214, 210), (186, 194, 192))
    _window(img, d, 1340, 140, 1800, 470, (180, 208, 226), (226, 238, 244))
    glow(img, 1570, 300, 420, (255, 252, 236), 40)
    # カーテンレールとカーテン
    d.rectangle([80, 130, 900, 152], fill=(178, 186, 190))
    d.rectangle([80, 152, 620, 640], fill=(206, 226, 224))
    for k in range(7):
        d.line([110 + k * 74, 152, 110 + k * 74, 640], fill=(186, 210, 208), width=8)
    # 診察台
    d.rounded_rectangle([700, 560, 1240, 700], radius=10, fill=(226, 232, 236))
    d.rounded_rectangle([700, 520, 900, 576], radius=10, fill=(212, 220, 226))
    for x in (740, 1180):
        d.rectangle([x, 700, x + 26, 830], fill=(178, 186, 194))
    # ワゴンとトレー
    d.rounded_rectangle([1300, 600, 1560, 640], radius=6, fill=(214, 220, 226))
    d.rectangle([1330, 640, 1350, 800], fill=(186, 194, 202))
    d.rectangle([1510, 640, 1530, 800], fill=(186, 194, 202))
    d.rounded_rectangle([1340, 570, 1520, 604], radius=6, fill=(230, 236, 240))
    return img


def kaigi_ita() -> Image.Image:
    """テルモの会議室。断られ続けた企画を持ち込む場所。"""
    img = vgrad((W, H), (222, 224, 226), (198, 200, 204)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 700, (176, 178, 182), (156, 158, 164))
    # ホワイトボード
    d.rounded_rectangle([540, 130, 1420, 560], radius=8, fill=(150, 154, 160))
    d.rectangle([558, 148, 1402, 530], fill=(248, 248, 246))
    # 針の断面図（メガホン型）
    d.polygon([(660, 300), (1180, 250), (1180, 350), (660, 320)], outline=(40, 90, 170), width=8)
    d.line([660, 310, 1180, 300], fill=(200, 60, 60), width=6)
    for k in range(6):
        d.line([700 + k * 90, 400, 700 + k * 90, 440], fill=(90, 92, 98), width=5)
    d.rectangle([558, 530, 1402, 560], fill=(226, 226, 224))
    # 長机
    d.rounded_rectangle([200, 720, 1720, 880], radius=12, fill=(206, 208, 212))
    d.rectangle([200, 720, 1720, 756], fill=(184, 186, 192))
    for bx in (400, 900, 1380):
        d.rectangle([bx, 690, bx + 170, 726], fill=(246, 246, 242),
                    outline=(206, 206, 200), width=3)
    return img


def kanagata() -> Image.Image:
    """金型の棚。作り直した数百個が積み上がっている。"""
    img = vgrad((W, H), (96, 92, 86), (72, 68, 64)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 720, (86, 78, 66), (68, 62, 52))
    # スチール棚に金型を並べる
    for sx in (60, 700, 1340):
        d.rectangle([sx, 130, sx + 520, 700], fill=(78, 82, 88))
        for r in range(4):
            y = 158 + r * 138
            d.rectangle([sx + 12, y, sx + 508, y + 14], fill=(60, 64, 70))
            for c in range(4):
                bx = sx + 30 + c * 120
                d.rounded_rectangle([bx, y - 96, bx + 90, y], radius=5,
                                    fill=STEEL if (r + c) % 2 else (128, 136, 146))
                d.rectangle([bx + 30, y - 96, bx + 60, y - 66], fill=(94, 102, 112))
    glow(img, 960, 380, 700, (240, 230, 200), 18)
    return img


def teatsu() -> Image.Image:
    """手元の拡大図を描くための作業台。ルーペと極小の部品。"""
    img = vgrad((W, H), (74, 70, 64), (54, 52, 48)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.62), (104, 92, 74), (84, 74, 60))
    # 作業台の天板
    d.rectangle([0, int(H * 0.62), W, H], fill=(118, 104, 84))
    for x in range(0, W, 260):
        d.line([x, int(H * 0.62), x, H], fill=(104, 92, 74), width=5)
    # 手元灯
    d.polygon([(1500, 60), (1700, 60), (1780, 210), (1420, 210)], fill=(80, 84, 90))
    glow(img, 1600, 300, 620, (255, 244, 200), 46)
    # ルーペ
    d.ellipse([220, 420, 520, 700], outline=(180, 186, 194), width=18,
              fill=(210, 226, 236))
    d.rounded_rectangle([500, 660, 760, 706], radius=18, fill=(120, 126, 134))
    # ピンセットと極小の筒
    d.polygon([(900, 700), (1180, 620), (1190, 640), (910, 720)], fill=(186, 192, 200))
    d.polygon([(900, 740), (1180, 660), (1190, 680), (910, 760)], fill=(166, 172, 180))
    d.rectangle([1240, 664, 1330, 676], fill=(214, 220, 228))
    return img


def shukka() -> Image.Image:
    """出荷場。箱が積まれ、外は明るい。完成後の場面。"""
    img = vgrad((W, H), (196, 200, 206), (172, 176, 184)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 680, (154, 148, 138), (132, 126, 118))
    # シャッターと外の光
    d.rectangle([1200, 120, 1810, 680], fill=(206, 212, 218))
    for y in range(120, 420, 26):
        d.line([1200, y, 1810, y], fill=(184, 190, 198), width=8)
    d.rectangle([1200, 420, 1810, 680], fill=(228, 238, 246))
    glow(img, 1500, 520, 520, (255, 254, 240), 44)
    # 段ボールの山
    for i, (x, n) in enumerate([(90, 4), (400, 3), (700, 5), (980, 3)]):
        for k in range(n):
            d.rounded_rectangle([x, 680 - 96 - k * 92, x + 230, 680 - 8 - k * 92], radius=4,
                                fill=(196, 164, 118) if k % 2 else (182, 150, 106),
                                outline=(150, 120, 82), width=4)
            d.line([x + 115, 680 - 96 - k * 92, x + 115, 680 - 8 - k * 92],
                   fill=(150, 120, 82), width=4)
    return img


def hyoushou() -> Image.Image:
    """表彰の会場。壇上と幕。グッドデザイン大賞の場面。"""
    img = vgrad((W, H), (44, 38, 58), (28, 24, 40)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 幕
    d.rectangle([0, 0, W, 180], fill=(88, 34, 48))
    for x in range(0, W, 90):
        d.polygon([(x, 180), (x + 45, 240), (x + 90, 180)], fill=(104, 42, 58))
    # 背景パネル
    d.rounded_rectangle([340, 240, 1580, 660], radius=10, fill=(56, 50, 74))
    d.rounded_rectangle([420, 300, 1500, 420], radius=8, fill=(230, 226, 236))
    for k in range(3):
        d.rectangle([520 + k * 300, 480, 760 + k * 300, 560], fill=(76, 68, 96))
    _floor(d, 700, (52, 46, 66), (40, 36, 52))
    # 演台
    d.rounded_rectangle([760, 700, 1160, 960], radius=8, fill=(96, 74, 62))
    d.rectangle([760, 700, 1160, 740], fill=(76, 58, 48))
    for x in (300, 1620):
        glow(img, x, 300, 420, (255, 240, 200), 30)
    return img


def gakko() -> Image.Image:
    """向島の国民学校のあと。少年期の場面に使う下町の路地。"""
    img = vgrad((W, H), (198, 198, 190), (222, 220, 210)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 板塀と長屋
    for bx in range(-40, W, 420):
        d.polygon([(bx - 20, 300), (bx + 200, 200), (bx + 420, 300)], fill=(98, 82, 66))
        d.rectangle([bx, 300, bx + 380, 620], fill=(158, 138, 112))
        for k in range(6):
            d.line([bx + 50 + k * 56, 300, bx + 50 + k * 56, 620], fill=(134, 116, 94), width=5)
        d.rectangle([bx + 100, 400, bx + 280, 620], fill=(104, 90, 74))
    _floor(d, 620, (180, 170, 152), (156, 148, 132))
    # 側溝と電柱
    d.rectangle([0, 800, W, 850], fill=(160, 152, 138))
    d.rectangle([1620, 140, 1660, 620], fill=(112, 98, 80))
    d.rectangle([1560, 190, 1720, 218], fill=(112, 98, 80))
    return img


def ima_heya() -> Image.Image:
    """現代の部屋（茶番用）。腕まくりと消毒綿。"""
    img = vgrad((W, H), (234, 238, 240), (212, 218, 224)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _window(img, d, 1380, 140, 1810, 470, (178, 206, 230), (226, 238, 244))
    _floor(d, 660, (198, 198, 202), (178, 178, 184))
    # ポスター（体のイラスト風）
    d.rounded_rectangle([170, 160, 560, 540], radius=8, fill=(246, 248, 250),
                        outline=(200, 206, 212), width=6)
    d.ellipse([320, 210, 410, 300], fill=(214, 226, 236))
    d.rounded_rectangle([300, 310, 430, 500], radius=20, fill=(214, 226, 236))
    # 机と診察の小物
    d.rounded_rectangle([620, 700, 1300, 860], radius=10, fill=(196, 186, 172))
    d.rectangle([620, 700, 1300, 736], fill=(172, 162, 148))
    d.rounded_rectangle([700, 650, 830, 710], radius=6, fill=(240, 244, 248),
                        outline=(200, 206, 212), width=4)
    for k in range(3):
        d.ellipse([880 + k * 60, 664, 920 + k * 60, 704], fill=(238, 242, 246),
                  outline=(198, 204, 210), width=4)
    return img


PAINTERS = {
    "il_nd_koba": koba,
    "il_nd_yoru": koba_yoru,
    "il_nd_jimusho": jimusho,
    "il_nd_terumo": terumo,
    "il_nd_byoin": byoin,
    "il_nd_kaigi": kaigi_ita,
    "il_nd_kanagata": kanagata,
    "il_nd_teatsu": teatsu,
    "il_nd_shukka": shukka,
    "il_nd_hyoushou": hyoushou,
    "il_nd_gakko": gakko,
    "il_nd_ima": ima_heya,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
