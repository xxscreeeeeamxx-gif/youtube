#!/usr/bin/env python3
"""シャープペンシル再現ドラマ（sharp-pencil）用のイラスト背景14種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
明治の下町 → 大正の工場 → 震災 → 大阪の再起 → 現代、と時代で色調を変えている。
実行: PYTHONPATH=. python3 scripts/gen_sp_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402


def _nagaya(d, y0, y1, x0=0, x1=W, wall=(150, 132, 108), roof=(92, 78, 62)):
    """明治の長屋の連なり。板壁と瓦屋根。"""
    for bx in range(x0, x1, 380):
        d.polygon([(bx - 30, y0), (bx + 200, y0 - 110), (bx + 410, y0)], fill=roof)
        d.rectangle([bx, y0, bx + 360, y1], fill=wall)
        for k in range(5):
            d.line([bx + 60 + k * 60, y0, bx + 60 + k * 60, y1], fill=(126, 110, 88), width=5)
        d.rectangle([bx + 90, y0 + 90, bx + 270, y1], fill=(96, 84, 68))


def deno_ie() -> Image.Image:
    """出野家の土間。内職の箱が積まれ、灯りが乏しい。"""
    img = vgrad((W, H), (74, 64, 54), (52, 44, 38)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.72), (86, 72, 58), (66, 55, 44))
    # 板壁
    for x in range(0, W, 120):
        d.line([x, 0, x, int(H * 0.72)], fill=(64, 55, 46), width=6)
    # 障子（暗い）
    d.rounded_rectangle([1360, 130, 1780, 620], radius=6, fill=(158, 148, 128))
    for i in range(3):
        d.line([1360 + 105 * (i + 1), 130, 1360 + 105 * (i + 1), 620], fill=(96, 82, 66), width=8)
    for j in range(4):
        d.line([1360, 228 + j * 98, 1780, 228 + j * 98], fill=(96, 82, 66), width=8)
    # 内職の箱を積む
    for i, bx in enumerate([120, 330, 540]):
        hgt = 3 + i % 2
        for k in range(hgt):
            d.rectangle([bx, int(H * 0.72) - 90 - k * 86, bx + 190, int(H * 0.72) - 8 - k * 86],
                        fill=(140, 118, 90), outline=(104, 86, 66), width=5)
    # 裸電球
    d.line([900, 0, 900, 110], fill=(70, 62, 52), width=5)
    d.ellipse([858, 108, 942, 186], fill=(226, 206, 150))
    glow(img, 900, 150, 400, (240, 220, 150), 34)
    return img


def michi_meiji() -> Image.Image:
    """明治の下町の道。長屋が続き、朝の光。手を引かれて歩いた道。"""
    img = vgrad((W, H), (196, 202, 200), (226, 224, 214)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _nagaya(d, 250, 620)
    _floor(d, 620, (176, 164, 146), (152, 142, 126))
    # 土の道の轍
    for k in range(3):
        d.line([200 + k * 640, 620, 60 + k * 900, H], fill=(160, 148, 130), width=10)
    # 電柱と物干し
    d.rectangle([1560, 130, 1596, 620], fill=(106, 92, 74))
    d.line([300, 300, 700, 320], fill=(140, 128, 110), width=5)
    for k in range(4):
        d.rectangle([340 + k * 90, 320, 400 + k * 90, 420],
                    fill=(214, 210, 198) if k % 2 else (180, 190, 200))
    return img


def kazariya() -> Image.Image:
    """錺屋（金属細工）の仕事場。作業台と工具、火床。"""
    img = vgrad((W, H), (78, 70, 62), (56, 50, 44)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.70), (110, 92, 70), (88, 74, 56))
    # 道具棚
    d.rectangle([80, 150, 620, 600], fill=(92, 76, 58))
    for r in range(3):
        d.rectangle([92, 172 + r * 142, 608, 186 + r * 142], fill=(72, 60, 46))
        for c in range(9):
            d.rectangle([110 + c * 54, 196 + r * 142, 124 + c * 54, 296 + r * 142],
                        fill=(186, 190, 198))
            d.ellipse([104 + c * 54, 286 + r * 142, 130 + c * 54, 316 + r * 142],
                      fill=(150, 120, 84))
    # 作業台と万力
    d.rounded_rectangle([700, 560, 1420, int(H * 0.70)], radius=6, fill=(120, 96, 66))
    d.rectangle([700, 560, 1420, 596], fill=(98, 78, 54))
    d.rectangle([1180, 486, 1280, 566], fill=(120, 126, 134))
    d.rectangle([1150, 470, 1310, 496], fill=(140, 146, 154))
    # 火床
    d.rounded_rectangle([1520, 480, 1800, 640], radius=10, fill=(86, 70, 56))
    d.ellipse([1580, 500, 1740, 580], fill=(220, 120, 50))
    glow(img, 1660, 540, 300, (255, 150, 60), 46)
    return img


def kojo_taisho() -> Image.Image:
    """大正の町工場。旋盤が並び、ベルトが天井から下がる。"""
    img = vgrad((W, H), (128, 130, 128), (98, 100, 100)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 天井のシャフトとベルト
    d.rectangle([0, 80, W, 118], fill=(80, 74, 66))
    for x in range(160, W, 290):
        d.polygon([(x - 20, 118), (x + 20, 118), (x + 46, 470), (x + 6, 470)], fill=(120, 112, 98))
    _floor(d, 660, (140, 136, 128), (116, 112, 106))
    # 旋盤
    for i, x in enumerate(range(60, W, 290)):
        d.rounded_rectangle([x, 470, x + 210, 660], radius=8, fill=(70, 86, 96))
        d.rectangle([x + 16, 440, x + 194, 480], fill=(96, 112, 122))
        d.ellipse([x + 140, 430, x + 200, 490], fill=(150, 160, 168))
    # 高窓
    for x in (760, 1120):
        _window(img, d, x, 150, x + 300, 380, (168, 190, 210), (214, 226, 236))
    return img


def tenpo() -> Image.Image:
    """文具問屋の店先。帳場と品物の棚。"""
    img = vgrad((W, H), (210, 198, 172), (186, 172, 146)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 640, (156, 132, 100), (132, 110, 82))
    # 商品棚
    d.rectangle([60, 140, 700, 620], fill=(140, 114, 84))
    for r in range(4):
        d.rectangle([72, 164 + r * 116, 688, 178 + r * 116], fill=(112, 90, 66))
        for c in range(11):
            d.rectangle([88 + c * 54, 188 + r * 116, 122 + c * 54, 272 + r * 116],
                        fill=[(190, 70, 60), (60, 90, 150), (220, 200, 120), (90, 140, 90)][(r + c) % 4])
    # 帳場（低い机と算盤）
    d.rounded_rectangle([880, 560, 1620, 700], radius=6, fill=(126, 98, 68))
    d.rectangle([880, 560, 1620, 596], fill=(104, 80, 56))
    d.rounded_rectangle([1080, 520, 1400, 566], radius=6, fill=(80, 62, 44))
    for k in range(11):
        d.line([1100 + k * 28, 524, 1100 + k * 28, 562], fill=(160, 140, 110), width=4)
    # のれん
    d.rectangle([0, 0, W, 120], fill=(60, 50, 42))
    for k in range(6):
        d.rectangle([120 + k * 300, 0, 340 + k * 300, 120], fill=(74, 62, 52))
    return img


def yokohama() -> Image.Image:
    """横浜の商館。洋風の建物と港。海外からの注文が来た場所。"""
    img = vgrad((W, H), (170, 200, 224), (218, 230, 238)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 海と船
    d.rectangle([0, 330, W, 450], fill=(104, 148, 176))
    d.polygon([(1420, 450), (1460, 300), (1500, 450)], fill=(220, 216, 206))
    d.rectangle([1330, 390, 1600, 452], fill=(80, 74, 70))
    # 洋館
    d.rectangle([180, 160, 1180, 640], fill=(224, 216, 200))
    d.polygon([(150, 160), (680, 70), (1210, 160)], fill=(140, 92, 74))
    for r in range(3):
        for c in range(7):
            d.rounded_rectangle([250 + c * 130, 220 + r * 140, 340 + c * 130, 336 + r * 140],
                                radius=40, fill=(120, 150, 172), outline=(190, 180, 164), width=6)
    d.rectangle([620, 480, 760, 640], fill=(110, 84, 66))
    _floor(d, 640, (196, 190, 178), (172, 166, 156))
    # 石畳
    for k in range(9):
        d.line([k * 230, 640, k * 260 - 200, H], fill=(180, 174, 162), width=5)
    return img


def jitaku_taisho() -> Image.Image:
    """早川家の住まい。ちゃぶ台と縁側。家族の場面。"""
    img = vgrad((W, H), (206, 190, 158), (182, 166, 138)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 畳
    d.rectangle([0, int(H * 0.66), W, H], fill=(200, 194, 148))
    for k in range(5):
        d.line([k * 400, int(H * 0.66), k * 400, H], fill=(178, 172, 128), width=6)
    d.line([0, int(H * 0.66), W, int(H * 0.66)], fill=(160, 154, 112), width=8)
    # 縁側と庭
    _window(img, d, 1300, 150, 1810, 560, (150, 186, 210), (216, 230, 238))
    d.ellipse([1420, 380, 1700, 540], fill=(120, 160, 110))
    # 障子
    d.rounded_rectangle([90, 130, 560, 620], radius=6, fill=(238, 232, 216))
    for i in range(3):
        d.line([90 + 118 * (i + 1), 130, 90 + 118 * (i + 1), 620], fill=(150, 128, 100), width=8)
    for j in range(4):
        d.line([90, 228 + j * 98, 560, 228 + j * 98], fill=(150, 128, 100), width=8)
    # ちゃぶ台
    d.ellipse([700, 700, 1240, 880], fill=(150, 106, 66))
    d.ellipse([720, 690, 1220, 850], fill=(176, 128, 82))
    return img


def shinsai() -> Image.Image:
    """1923年9月1日。焼けた街。空が赤く、瓦礫だけが残る。"""
    img = vgrad((W, H), (120, 60, 40), (58, 36, 30)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    glow(img, 1400, 260, 900, (220, 110, 50), 44)
    glow(img, 420, 320, 700, (200, 90, 40), 34)
    # 崩れた建物の輪郭
    for i, (bx, bw, bh) in enumerate([(0, 420, 300), (460, 300, 180), (900, 360, 260),
                                      (1340, 280, 150), (1660, 260, 320)]):
        d.polygon([(bx, 620), (bx, 620 - bh), (bx + bw * 0.4, 620 - bh * 0.55),
                   (bx + bw * 0.7, 620 - bh * 0.9), (bx + bw, 620 - bh * 0.3), (bx + bw, 620)],
                  fill=(52, 38, 34) if i % 2 else (44, 32, 30))
    _floor(d, 620, (70, 52, 44), (54, 40, 36))
    # 瓦礫
    for i, x in enumerate(range(40, W, 130)):
        y = 660 + (i % 4) * 70
        d.polygon([(x, y), (x + 70, y - 26), (x + 110, y + 16), (x + 30, y + 30)],
                  fill=(60, 46, 42) if i % 2 else (76, 58, 50))
    # 焼け残った柱
    d.polygon([(1180, 700), (1214, 700), (1226, 380), (1196, 372)], fill=(38, 28, 26))
    return img


def kawa() -> Image.Image:
    """川辺。避難の途中、火に追われて飛び込んだ場所。"""
    img = vgrad((W, H), (86, 56, 48), (44, 34, 34)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    glow(img, 300, 240, 800, (200, 96, 44), 40)
    glow(img, 1620, 200, 700, (190, 88, 40), 34)
    # 対岸
    d.rectangle([0, 400, W, 470], fill=(48, 38, 36))
    for x in range(60, W, 240):
        d.rectangle([x, 300, x + 160, 400], fill=(40, 30, 30))
    # 川面
    d.rectangle([0, 470, W, H], fill=(48, 58, 72))
    for k in range(14):
        d.line([-100 + k * 180, 520 + (k % 5) * 90, 120 + k * 180, 520 + (k % 5) * 90],
               fill=(74, 88, 104), width=7)
    # 川面に映る火
    for k in range(5):
        d.line([260 + k * 340, 500, 260 + k * 340, H], fill=(140, 78, 52), width=26)
    # 護岸
    d.rectangle([0, 440, W, 476], fill=(70, 60, 56))
    return img


def yakosha() -> Image.Image:
    """夜行列車の車内。窓の外は焼け跡。大阪へ向かう夜。"""
    img = vgrad((W, H), (44, 44, 58), (30, 30, 42)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 窓（外は暗く、遠くに小さな灯り）
    for x in (140, 760, 1380):
        _window(img, d, x, 180, x + 420, 520, (18, 18, 30), (34, 32, 44))
        for k in range(4):
            d.ellipse([x + 60 + k * 100, 400 + (k % 3) * 40, x + 76 + k * 100,
                       416 + (k % 3) * 40], fill=(200, 150, 80))
    # 網棚
    d.rectangle([0, 130, W, 150], fill=(70, 66, 78))
    # 座席の背もたれ
    d.rounded_rectangle([0, 620, W, 860], radius=8, fill=(64, 54, 62))
    d.rectangle([0, 620, W, 660], fill=(80, 68, 76))
    for x in range(120, W, 400):
        d.rectangle([x, 620, x + 16, 860], fill=(50, 42, 50))
    _floor(d, 860, (52, 48, 56), (40, 36, 44))
    # 天井灯
    for x in (480, 1440):
        d.ellipse([x - 46, 40, x + 46, 106], fill=(210, 196, 150))
        glow(img, x, 80, 300, (230, 210, 150), 26)
    return img


def osaka_koba() -> Image.Image:
    """大阪の小さな作業場。机が3つだけ。ゼロからの再起。"""
    img = vgrad((W, H), (168, 160, 146), (140, 132, 120)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.68), (128, 108, 84), (106, 90, 70))
    _window(img, d, 1420, 160, 1810, 470, (176, 200, 220), (222, 232, 240))
    # 板壁
    for x in range(0, 1400, 150):
        d.line([x, 0, x, int(H * 0.68)], fill=(150, 142, 128), width=5)
    # 作業机3つ（従業員3人ではじめた）
    for i, x in enumerate([120, 560, 1000]):
        d.rounded_rectangle([x, 560, x + 340, 700], radius=6, fill=(140, 112, 78))
        d.rectangle([x, 560, x + 340, 592], fill=(116, 92, 64))
        d.rectangle([x + 60, 520, x + 200, 566], fill=(180, 186, 194))
        d.ellipse([x + 240, 526, x + 300, 566], fill=(150, 156, 164))
    # 積んだ材料
    for k in range(4):
        d.rectangle([1500, int(H * 0.68) - 60 - k * 52, 1780, int(H * 0.68) - 12 - k * 52],
                    fill=(158, 150, 138), outline=(126, 118, 108), width=4)
    return img


def radio_ba() -> Image.Image:
    """ラジオの試作場。真空管と配線、鉱石ラジオの部品。"""
    img = vgrad((W, H), (62, 68, 88), (44, 48, 64)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.70), (86, 76, 66), (68, 60, 52))
    # 部品棚と真空管
    d.rectangle([70, 150, 640, 610], fill=(74, 78, 96))
    for r in range(3):
        d.rectangle([82, 176 + r * 146, 628, 190 + r * 146], fill=(58, 62, 78))
        for c in range(7):
            cx = 120 + c * 72
            d.rounded_rectangle([cx - 22, 206 + r * 146, cx + 22, 292 + r * 146],
                                radius=20, fill=(210, 190, 140))
            d.line([cx, 226 + r * 146, cx, 276 + r * 146], fill=(240, 170, 90), width=5)
    glow(img, 360, 380, 420, (250, 190, 110), 30)
    # 作業台と受信機
    d.rounded_rectangle([740, 540, 1500, int(H * 0.70)], radius=6, fill=(118, 96, 70))
    d.rectangle([740, 540, 1500, 574], fill=(96, 78, 56))
    d.rounded_rectangle([880, 420, 1320, 548], radius=8, fill=(120, 92, 64))
    d.ellipse([930, 452, 1010, 522], fill=(60, 62, 74))
    d.ellipse([1060, 452, 1140, 522], fill=(60, 62, 74))
    d.rectangle([1180, 452, 1290, 522], fill=(200, 190, 160))
    # アンテナ線
    d.line([1320, 430, 1810, 240], fill=(160, 160, 150), width=5)
    return img


def kojo_shitsumei() -> Image.Image:
    """目の不自由な人が働く工場。手で触れて分かるよう整えられた作業場。"""
    img = vgrad((W, H), (196, 200, 196), (170, 174, 172)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 660, (162, 152, 136), (138, 130, 116))
    _window(img, d, 1380, 140, 1810, 480, (186, 210, 230), (226, 236, 242))
    glow(img, 1590, 300, 460, (255, 250, 220), 40)
    # 床の誘導線
    d.rectangle([0, 780, W, 826], fill=(206, 176, 90))
    for x in range(40, W, 120):
        d.rectangle([x, 790, x + 60, 816], fill=(176, 148, 70))
    # 手すり
    d.rounded_rectangle([60, 560, 1240, 586], radius=12, fill=(150, 136, 116))
    for x in (160, 620, 1120):
        d.rectangle([x, 560, x + 18, 660], fill=(132, 118, 100))
    # 作業台（プレス機）
    for i, x in enumerate([180, 700]):
        d.rounded_rectangle([x, 400, x + 380, 660], radius=8, fill=(96, 104, 112))
        d.rectangle([x + 60, 330, x + 320, 410], fill=(120, 128, 136))
        d.rectangle([x + 150, 250, x + 230, 340], fill=(140, 148, 156))
    return img


def ima_tsukue() -> Image.Image:
    """現代の机（茶番用）。シャープペンシルとノート。"""
    img = vgrad((W, H), (236, 234, 228), (214, 212, 206)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _window(img, d, 1380, 140, 1810, 470, (176, 204, 230), (226, 236, 244))
    # 壁のコルクボード
    d.rounded_rectangle([160, 160, 640, 520], radius=10, fill=(198, 162, 110))
    for i, (x, y) in enumerate([(200, 200), (360, 230), (500, 195), (240, 360), (430, 380)]):
        d.rectangle([x, y, x + 120, y + 96],
                    fill=(250, 246, 236) if i % 2 else (226, 236, 246))
    _floor(d, 660, (196, 190, 182), (176, 170, 162))
    # 机
    d.rounded_rectangle([560, 700, 1500, 900], radius=10, fill=(178, 146, 112))
    d.rectangle([560, 700, 1500, 738], fill=(152, 124, 94))
    # ノートとシャーペン
    d.rounded_rectangle([700, 650, 1060, 716], radius=6, fill=(250, 248, 242),
                        outline=(200, 196, 186), width=4)
    for k in range(3):
        d.line([730, 668 + k * 16, 1030, 668 + k * 16], fill=(180, 196, 214), width=4)
    d.polygon([(1140, 712), (1156, 712), (1168, 636), (1148, 632)], fill=(60, 120, 190))
    d.polygon([(1148, 632), (1168, 636), (1158, 612)], fill=(180, 186, 194))
    return img


PAINTERS = {
    "il_sp_deno": deno_ie,
    "il_sp_michi": michi_meiji,
    "il_sp_kazariya": kazariya,
    "il_sp_kojo": kojo_taisho,
    "il_sp_tenpo": tenpo,
    "il_sp_yokohama": yokohama,
    "il_sp_jitaku": jitaku_taisho,
    "il_sp_shinsai": shinsai,
    "il_sp_kawa": kawa,
    "il_sp_yakosha": yakosha,
    "il_sp_osaka": osaka_koba,
    "il_sp_radio": radio_ba,
    "il_sp_shitsumei": kojo_shitsumei,
    "il_sp_ima": ima_tsukue,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
