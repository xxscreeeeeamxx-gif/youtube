#!/usr/bin/env python3
"""任天堂・山内溥の再現ドラマ（yamauchi-nintendo）用のイラスト背景12種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
京都の工房は木と紙の暖色、多角化の場面は寒色で散らし、
再起の工場でまた暖色に戻す、で章のトーンを分けている。
実行: PYTHONPATH=. python3 scripts/gen_ym_bgs.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402


def _cards(d, x, y, n=5, w=52, h=78, col=(248, 244, 236), face=(196, 70, 60)):
    """札を少しずつずらして重ねる。花札にもトランプにも使う。"""
    for k in range(n):
        cx = x + k * (w * 0.62)
        d.rounded_rectangle([cx, y - k * 3, cx + w, y + h - k * 3], radius=6,
                            fill=col, outline=(150, 140, 128), width=3)
        d.rounded_rectangle([cx + 9, y + 10 - k * 3, cx + w - 9, y + h - 14 - k * 3],
                            radius=4, fill=face)


def _crate(d, x, y, w=180, h=130, col=(168, 132, 88)):
    """木箱・段ボール箱。積み上げに使う。"""
    d.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=col,
                        outline=tuple(max(0, c - 40) for c in col), width=5)
    d.line([x + 8, y + h * 0.42, x + w - 8, y + h * 0.42],
           fill=tuple(max(0, c - 30) for c in col), width=6)


# ---------------------------------------------------------------- 花札の時代
def karuta() -> Image.Image:
    """1930年代、京都の花札工房。木の作業台と、干された札。"""
    img = vgrad((W, H), (196, 172, 138), (166, 144, 114)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 760, (142, 114, 78), (118, 94, 64))
    # 障子と格子
    d.rectangle([100, 130, 820, 700], fill=(220, 210, 186))
    for c in range(5):
        d.line([100 + c * 180, 130, 100 + c * 180, 700], fill=(146, 122, 92), width=9)
    for r in range(4):
        d.line([100, 130 + r * 190, 820, 130 + r * 190], fill=(146, 122, 92), width=9)
    # 干し場（紐に札を吊るす）
    for r in range(2):
        ly = 210 + r * 150
        d.line([900, ly, 1860, ly - 16], fill=(120, 100, 72), width=6)
        for k in range(9):
            _cards(d, 930 + k * 100, ly + 6 - k * 2, n=1, w=56, h=84,
                   face=(60, 110, 72) if k % 2 else (196, 70, 60))
    # 作業台
    d.rounded_rectangle([880, 620, 1880, 760], radius=6, fill=(154, 120, 80))
    d.rectangle([880, 620, 1880, 656], fill=(132, 102, 68))
    _cards(d, 980, 540, n=6)
    _cards(d, 1440, 546, n=5, face=(60, 110, 72))
    return img


def shacho() -> Image.Image:
    """任天堂の社長室。木の大机と、창のある落ち着いた部屋。"""
    img = vgrad((W, H), (168, 148, 124), (140, 122, 100)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 740, (110, 84, 58), (90, 68, 46))
    # 板張りの壁
    for k in range(0, W, 150):
        d.line([k, 100, k, 740], fill=(152, 132, 108), width=6)
    _window(img, d, 1240, 160, 1830, 540, (176, 194, 214), (216, 226, 236))
    d = ImageDraw.Draw(img, "RGBA")
    # 書棚
    d.rounded_rectangle([90, 200, 620, 740], radius=6, fill=(126, 98, 68))
    for r in range(3):
        d.rectangle([106, 300 + r * 140, 604, 314 + r * 140], fill=(104, 80, 54))
        for j in range(9):
            d.rectangle([124 + j * 52, 232 + r * 140, 160 + j * 52, 300 + r * 140],
                        fill=[(150, 70, 62), (70, 96, 132), (176, 148, 84),
                              (96, 122, 92)][(r + j) % 4])
    # 大机
    d.rounded_rectangle([700, 700, 1760, 880], radius=8, fill=(122, 92, 62))
    d.rectangle([700, 700, 1760, 744], fill=(102, 76, 52))
    _cards(d, 820, 640, n=4)
    return img


def america() -> Image.Image:
    """1958年、アメリカのトランプ工場。天井の高い広い建屋と機械。"""
    img = vgrad((W, H), (198, 202, 208), (170, 174, 182)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 780, (150, 152, 156), (128, 130, 134))
    # 三角屋根の骨組み
    for k in range(4):
        x = 120 + k * 480
        d.line([x, 260, x + 240, 120, x + 480, 260], fill=(140, 144, 150), width=12)
        d.line([x, 260, x + 480, 260], fill=(140, 144, 150), width=10)
        d.line([x + 240, 120, x + 240, 260], fill=(140, 144, 150), width=8)
    # 巨大な機械の列
    for k in range(3):
        bx = 120 + k * 600
        d.rounded_rectangle([bx, 400, bx + 460, 780], radius=8, fill=(92, 100, 116))
        d.rectangle([bx + 30, 440, bx + 430, 560], fill=(56, 64, 80))
        for j in range(4):
            d.ellipse([bx + 60 + j * 96, 600, bx + 128 + j * 96, 668],
                      fill=(150, 156, 168))
        d.rounded_rectangle([bx + 40, 700, bx + 420, 740], radius=6, fill=(190, 194, 200))
    # ベルトの上のトランプの山
    for k in range(7):
        _cards(d, 180 + k * 250, 640, n=3, w=44, h=64)
    return img


# ---------------------------------------------------------------- 多角化
def taxi() -> Image.Image:
    """タクシー会社の営業所。並んだ車と、配車の黒板。"""
    img = vgrad((W, H), (186, 190, 198), (158, 162, 172)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 700, (120, 122, 128), (100, 102, 108))
    d.rectangle([0, 700, W, 730], fill=(196, 190, 160))
    # 車を3台（横から見た簡略形）
    for k, x in enumerate((80, 720, 1360)):
        col = [(206, 208, 214), (68, 84, 120), (204, 176, 72)][k]
        d.rounded_rectangle([x, 620, x + 470, 760], radius=22, fill=col)
        d.polygon([(x + 90, 620), (x + 350, 620), (x + 300, 520), (x + 150, 520)],
                  fill=(150, 172, 190))
        d.ellipse([x + 70, 720, x + 180, 830], fill=(46, 46, 52))
        d.ellipse([x + 300, 720, x + 410, 830], fill=(46, 46, 52))
        d.rounded_rectangle([x + 190, 486, x + 270, 522], radius=6, fill=(236, 232, 224))
    # 配車の黒板
    d.rounded_rectangle([620, 130, 1360, 440], radius=6, fill=(58, 72, 62),
                        outline=(120, 100, 72), width=12)
    for r in range(4):
        d.line([680, 200 + r * 60, 680 + 200 + r * 130, 200 + r * 60],
               fill=(214, 216, 210), width=5)
    return img


def shokuhin() -> Image.Image:
    """食品工場のライン。ベルトの上を袋が流れる。"""
    img = vgrad((W, H), (222, 224, 220), (194, 198, 194)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 790, (168, 172, 168), (146, 150, 146))
    for k in range(5):
        d.rounded_rectangle([120 + k * 350, 80, 380 + k * 350, 112], radius=6,
                            fill=(250, 250, 244))
        glow(img, 250 + k * 350, 96, 260, (255, 255, 240), 30)
    d = ImageDraw.Draw(img, "RGBA")
    # ベルトコンベア
    d.rounded_rectangle([0, 600, W, 690], radius=8, fill=(120, 126, 132))
    d.rectangle([0, 600, W, 622], fill=(150, 156, 162))
    for k in range(0, W, 90):
        d.ellipse([k, 690, k + 60, 750], fill=(96, 102, 108))
    # 流れる袋
    for k in range(9):
        x = 60 + k * 210
        d.rounded_rectangle([x, 500, x + 130, 604], radius=10, fill=(226, 196, 108),
                            outline=(178, 150, 76), width=5)
        d.rectangle([x + 22, 530, x + 108, 560], fill=(196, 84, 70))
    # 奥のタンク
    for x in (200, 1500):
        d.rounded_rectangle([x, 200, x + 260, 560], radius=40, fill=(178, 184, 190))
        d.ellipse([x, 170, x + 260, 250], fill=(200, 206, 212))
    return img


def copyki() -> Image.Image:
    """返品されたコピー機が積まれた倉庫。多角化の失敗の象徴。"""
    img = vgrad((W, H), (128, 128, 136), (98, 98, 106)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 780, (104, 104, 110), (86, 86, 92))
    # 高い窓から差す光
    _window(img, d, 1420, 100, 1800, 380, (140, 152, 176), (176, 186, 204))
    glow(img, 1600, 240, 700, (220, 226, 236), 40)
    d = ImageDraw.Draw(img, "RGBA")
    # 積まれた段ボールとコピー機
    for r in range(3):
        for c in range(6 - r):
            x = 100 + c * 210 + r * 105
            y = 760 - r * 140
            _crate(d, x, y - 130, 190, 130, (150, 122, 84))
    for k, x in enumerate((260, 880, 1180)):
        d.rounded_rectangle([x, 480, x + 300, 780], radius=10, fill=(178, 180, 186))
        d.rounded_rectangle([x + 20, 500, x + 280, 580], radius=6, fill=(96, 100, 110))
        d.rectangle([x + 40, 620, x + 260, 700], fill=(140, 144, 152))
    return img


def kaihatsu() -> Image.Image:
    """開発室。工具と部品、試作の散らかった机。"""
    img = vgrad((W, H), (212, 206, 194), (184, 178, 168)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 790, (150, 138, 118), (128, 118, 100))
    # 有孔ボードと工具
    d.rounded_rectangle([120, 160, 900, 560], radius=6, fill=(198, 190, 176),
                        outline=(160, 152, 140), width=8)
    for r in range(4):
        for c in range(11):
            d.ellipse([160 + c * 66, 200 + r * 90, 172 + c * 66, 212 + r * 90],
                      fill=(160, 152, 140))
    for k, x in enumerate((220, 400, 600, 760)):
        d.line([x, 250, x, 250 + 90 + k * 24], fill=(90, 96, 106), width=14)
        d.rounded_rectangle([x - 26, 250 + 90 + k * 24, x + 26, 250 + 130 + k * 24],
                            radius=6, fill=[(190, 80, 70), (70, 110, 160),
                                            (210, 170, 70), (110, 150, 110)][k])
    _window(img, d, 1400, 180, 1840, 520, (180, 198, 218), (218, 228, 238))
    d = ImageDraw.Draw(img, "RGBA")
    # 作業机と試作品
    d.rounded_rectangle([160, 660, 1780, 820], radius=8, fill=(158, 130, 96))
    d.rectangle([160, 660, 1780, 700], fill=(136, 110, 80))
    for k in range(6):
        x = 260 + k * 250
        d.rounded_rectangle([x, 596, x + 110, 664], radius=8,
                            fill=(200, 200, 206) if k % 2 else (196, 100, 88))
    return img


def laser() -> Image.Image:
    """レーザークレー射撃場。暗い室内に光の的とスクリーン。"""
    img = vgrad((W, H), (34, 40, 56), (20, 24, 36)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 790, (40, 44, 56), (32, 36, 46))
    # 大スクリーン
    d.rounded_rectangle([300, 140, 1620, 660], radius=8, fill=(46, 58, 78),
                        outline=(96, 104, 124), width=10)
    # 空と的
    d.rectangle([330, 170, 1590, 630], fill=(58, 78, 108))
    for k, (cx, cy) in enumerate(((620, 300), (960, 250), (1300, 340))):
        glow(img, cx, cy, 260, (255, 200, 90), 70)
    d = ImageDraw.Draw(img, "RGBA")
    for cx, cy in ((620, 300), (960, 250), (1300, 340)):
        d.ellipse([cx - 44, cy - 44, cx + 44, cy + 44], fill=(250, 216, 120),
                  outline=(200, 150, 60), width=6)
    # 射撃台
    for x in (240, 900, 1500):
        d.rounded_rectangle([x, 700, x + 240, 790], radius=8, fill=(70, 76, 92))
        d.line([x + 40, 700, x + 200, 640], fill=(120, 126, 142), width=16)
    return img


def ginko() -> Image.Image:
    """銀行の応接室。重い机とソファ、灰色の空気。"""
    img = vgrad((W, H), (176, 174, 178), (146, 144, 150)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 750, (120, 112, 108), (100, 94, 90))
    _window(img, d, 1300, 150, 1840, 520, (168, 178, 194), (200, 208, 220))
    d = ImageDraw.Draw(img, "RGBA")
    # 壁の絵と時計
    d.rounded_rectangle([180, 200, 620, 500], radius=6, fill=(196, 186, 170),
                        outline=(140, 124, 100), width=14)
    d.rectangle([220, 240, 580, 460], fill=(150, 160, 150))
    d.ellipse([840, 200, 960, 320], fill=(232, 228, 220), outline=(140, 134, 126), width=8)
    d.line([900, 260, 900, 220], fill=(90, 86, 82), width=6)
    d.line([900, 260, 936, 276], fill=(90, 86, 82), width=6)
    # 応接テーブルと書類
    d.rounded_rectangle([420, 720, 1500, 860], radius=10, fill=(96, 76, 62))
    d.rectangle([420, 720, 1500, 756], fill=(78, 62, 50))
    for k in range(4):
        d.rounded_rectangle([520 + k * 250, 650, 700 + k * 250, 728], radius=4,
                            fill=(238, 234, 226), outline=(180, 174, 166), width=4)
    return img


def kojo() -> Image.Image:
    """量産の工場。ラインが動き、箱が積み上がる。再起の場面。"""
    img = vgrad((W, H), (216, 218, 214), (188, 190, 188)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 790, (162, 164, 162), (140, 142, 140))
    for k in range(5):
        d.rounded_rectangle([100 + k * 360, 70, 380 + k * 360, 104], radius=6,
                            fill=(252, 252, 246))
        glow(img, 240 + k * 360, 88, 280, (255, 255, 240), 34)
    d = ImageDraw.Draw(img, "RGBA")
    # ライン
    d.rounded_rectangle([0, 560, W, 650], radius=8, fill=(128, 134, 140))
    d.rectangle([0, 560, W, 582], fill=(158, 164, 170))
    for k in range(0, W, 88):
        d.ellipse([k, 650, k + 58, 706], fill=(102, 108, 114))
    # 流れる小さな筐体
    for k in range(11):
        x = 40 + k * 172
        d.rounded_rectangle([x, 486, x + 108, 566], radius=10, fill=(220, 216, 208),
                            outline=(170, 166, 160), width=4)
        d.rounded_rectangle([x + 16, 502, x + 92, 536], radius=4, fill=(120, 140, 130))
    # 積み上がった出荷箱
    for r in range(3):
        for c in range(4 - r):
            _crate(d, 1180 + c * 190 + r * 95, 780 - r * 128, 175, 124, (196, 172, 132))
    return img


def ima() -> Image.Image:
    """現代のリビング。テレビとゲーム機。冒頭と締めで使う。"""
    img = vgrad((W, H), (232, 228, 222), (206, 202, 196)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 800, (176, 156, 130), (152, 134, 112))
    _window(img, d, 1360, 170, 1830, 520, (186, 206, 226), (222, 232, 240))
    d = ImageDraw.Draw(img, "RGBA")
    # テレビ台とテレビ
    d.rounded_rectangle([180, 700, 1080, 840], radius=10, fill=(150, 122, 96))
    d.rounded_rectangle([260, 320, 1000, 700], radius=12, fill=(44, 46, 54))
    d.rounded_rectangle([282, 342, 978, 660], radius=6, fill=(96, 140, 170))
    for k in range(3):
        d.rounded_rectangle([360 + k * 200, 420, 500 + k * 200, 560], radius=10,
                            fill=[(226, 96, 84), (86, 150, 200), (232, 200, 96)][k])
    # ゲーム機とコントローラ
    d.rounded_rectangle([1180, 720, 1400, 800], radius=10, fill=(58, 60, 68))
    d.ellipse([1200, 742, 1240, 782], fill=(120, 200, 160))
    d.rounded_rectangle([1480, 730, 1660, 810], radius=24, fill=(224, 222, 216),
                        outline=(180, 176, 170), width=5)
    d.ellipse([1510, 752, 1546, 788], fill=(120, 126, 134))
    for k in range(2):
        d.ellipse([1590 + k * 34, 748, 1616 + k * 34, 774], fill=(196, 84, 76))
    return img


def sobo() -> Image.Image:
    """夜の京都の街を望む窓辺。静かな場面（晩年）。"""
    img = vgrad((W, H), (44, 48, 62), (28, 30, 40)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 790, (58, 56, 62), (46, 44, 50))
    _window(img, d, 900, 150, 1820, 640, (24, 30, 48), (52, 58, 82))
    d = ImageDraw.Draw(img, "RGBA")
    # 街の灯り
    for k in range(60):
        x = 930 + (k * 211) % 860
        y = 380 + (k * 157) % 240
        d.rectangle([x, y, x + 9, y + 9], fill=(246, 224, 150))
    # 山の稜線
    d.polygon([(900, 400), (1180, 300), (1450, 380), (1700, 290), (1820, 360),
               (1820, 400)], fill=(30, 34, 46))
    # 手前の座卓と湯呑
    d.rounded_rectangle([160, 700, 820, 830], radius=8, fill=(96, 74, 56))
    d.rectangle([160, 700, 820, 736], fill=(80, 62, 48))
    d.ellipse([420, 646, 500, 710], fill=(208, 202, 190))
    _cards(d, 240, 640, n=3, w=44, h=64)
    return img


PAINTERS = {
    "il_ym_karuta": karuta,
    "il_ym_shacho": shacho,
    "il_ym_america": america,
    "il_ym_taxi": taxi,
    "il_ym_shokuhin": shokuhin,
    "il_ym_copyki": copyki,
    "il_ym_kaihatsu": kaihatsu,
    "il_ym_laser": laser,
    "il_ym_ginko": ginko,
    "il_ym_kojo": kojo,
    "il_ym_ima": ima,
    "il_ym_sobo": sobo,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
