#!/usr/bin/env python3
"""クオーツ時計の誕生（quartz-astron）用のイラスト背景7種。

実行: PYTHONPATH=. python3 scripts/gen_qz_bgs.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from PIL import Image, ImageDraw  # noqa: E402
from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402


def _rgba(img):
    return img.convert("RGBA")


def kojo() -> Image.Image:
    """1950年代の時計工場（諏訪）。作業台と万力、窓。"""
    img = _rgba(vgrad((W, H), (150, 142, 124), (108, 100, 86)))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 110], fill=(96, 88, 76))
    # 窓（信州の山が見える）
    for x in (120, 520, 920):
        d.rectangle([x, 150, x + 300, 420], fill=(176, 202, 224),
                    outline=(88, 82, 72), width=9)
        d.polygon([(x + 20, 400), (x + 130, 250), (x + 240, 400)], fill=(150, 168, 176))
        d.polygon([(x + 100, 400), (x + 200, 280), (x + 285, 400)], fill=(128, 148, 158))
        d.line([(x + 150, 150), (x + 150, 420)], fill=(88, 82, 72), width=7)
    # 天井の吊りランプ
    for x in range(230, W, 420):
        d.line([(x, 110), (x, 190)], fill=(70, 64, 56), width=6)
        d.ellipse([x - 46, 190, x + 46, 240], fill=(250, 230, 160))
        glow(img, x, 214, 200, (255, 224, 150), alpha=44)
    d = ImageDraw.Draw(img)
    # 作業台
    d.rectangle([0, 640, W, 700], fill=(126, 92, 60))
    d.rectangle([0, 700, W, H], fill=(104, 76, 50))
    for x in range(90, W, 300):
        # 万力と部品箱
        d.rectangle([x, 570, x + 70, 640], fill=(96, 100, 112), outline=(58, 62, 72), width=6)
        d.rectangle([x + 120, 600, x + 230, 640], fill=(150, 142, 128),
                    outline=(90, 84, 74), width=5)
    return img


def observatory() -> Image.Image:
    """スイス・ヌーシャテル天文台。石造りの建物とドーム、寒色。"""
    img = _rgba(vgrad((W, H), (96, 118, 152), (56, 72, 100)))
    d = ImageDraw.Draw(img)
    # 遠景の山
    d.polygon([(0, 480), (260, 250), (520, 480)], fill=(78, 94, 122))
    d.polygon([(380, 480), (700, 220), (1010, 480)], fill=(66, 82, 110))
    d.polygon([(860, 480), (1120, 280), (W, 480)], fill=(74, 90, 118))
    for pk in ((260, 250), (700, 220), (1120, 280)):
        d.polygon([(pk[0] - 60, pk[1] + 70), (pk[0], pk[1]), (pk[0] + 60, pk[1] + 70)],
                  fill=(226, 234, 244))
    # 天文台の建物
    d.rectangle([420, 400, 900, 780], fill=(178, 176, 168), outline=(110, 108, 102), width=8)
    d.ellipse([540, 250, 780, 440], fill=(196, 194, 186), outline=(110, 108, 102), width=8)
    d.polygon([(640, 300), (740, 250), (760, 300)], fill=(120, 130, 150))
    for x in range(470, 880, 110):
        d.rectangle([x, 480, x + 62, 600], fill=(120, 140, 168), outline=(96, 94, 88), width=5)
    d.rectangle([620, 640, 700, 780], fill=(122, 100, 78), outline=(84, 68, 52), width=6)
    # 雪の地面
    d.rectangle([0, 780, W, H], fill=(216, 224, 236))
    return img


def lab() -> Image.Image:
    """59Aプロジェクトの研究室。計測器のラックと水晶の実験台。"""
    img = _rgba(vgrad((W, H), (108, 116, 132), (68, 74, 88)))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 120], fill=(60, 66, 78))
    for x in range(200, W, 380):
        d.rectangle([x, 120, x + 260, 150], fill=(226, 232, 242))
        glow(img, x + 130, 140, 240, (200, 220, 255), alpha=40)
    d = ImageDraw.Draw(img)
    # 計測器ラック（大型）
    for i, x in enumerate((70, 340)):
        d.rectangle([x, 210, x + 230, 760], fill=(96, 102, 116),
                    outline=(56, 60, 72), width=8)
        for y in range(250, 720, 90):
            d.rectangle([x + 20, y, x + 210, y + 60], fill=(72, 78, 92),
                        outline=(120, 126, 140), width=4)
            d.ellipse([x + 34, y + 18, x + 66, y + 46], fill=(120, 220, 160))
            d.rectangle([x + 90, y + 22, x + 190, y + 40], fill=(58, 64, 76))
    # 実験台
    d.rectangle([620, 560, W, 620], fill=(150, 152, 160))
    d.rectangle([620, 620, W, H], fill=(112, 116, 126))
    # 台上の水晶片とオシロ
    d.rectangle([700, 400, 940, 560], fill=(78, 84, 98), outline=(46, 50, 60), width=7)
    d.ellipse([730, 430, 910, 540], fill=(30, 46, 40), outline=(120, 126, 140), width=5)
    for k in range(3):
        d.line([(740 + k * 4, 500), (760 + k * 4, 450), (790 + k * 4, 520),
                (820 + k * 4, 460), (860 + k * 4, 500)],
               fill=(120, 230, 150), width=4)
    d.polygon([(1010, 540), (1050, 430), (1090, 540)], fill=(210, 228, 244),
              outline=(140, 160, 180))
    return img


def olympic() -> Image.Image:
    """1964年東京五輪の計時室。競技場のスタンドと計時機材。"""
    img = _rgba(vgrad((W, H), (128, 150, 120), (80, 100, 78)))
    d = ImageDraw.Draw(img)
    # スタンド
    d.rectangle([0, 0, W, 300], fill=(96, 104, 116))
    for y in range(40, 300, 52):
        d.rectangle([0, y, W, y + 30], fill=(120, 128, 142))
        for x in range(30, W, 46):
            d.ellipse([x, y + 2, x + 26, y + 26], fill=(180, 150, 130))
    # トラック
    d.rectangle([0, 300, W, 640], fill=(178, 96, 70))
    for y in range(340, 640, 74):
        d.line([(0, y), (W, y)], fill=(232, 228, 220), width=6)
    # 計時ブース
    d.rectangle([760, 380, 1240, 700], fill=(70, 76, 90), outline=(40, 44, 54), width=9)
    d.rectangle([790, 410, 1210, 560], fill=(150, 160, 176), outline=(40, 44, 54), width=6)
    for x in range(810, 1180, 90):
        d.rectangle([x, 590, x + 66, 660], fill=(96, 102, 116), outline=(40, 44, 54), width=5)
        d.ellipse([x + 18, 606, x + 48, 634], fill=(250, 220, 120))
    d.rectangle([0, 700, W, H], fill=(150, 84, 62))
    return img


def kaigi() -> Image.Image:
    """会議室。値段と量産をめぐる詰めの場面。"""
    img = _rgba(vgrad((W, H), (152, 140, 122), (110, 100, 86)))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 100], fill=(98, 90, 78))
    # 窓
    d.rectangle([80, 160, 480, 430], fill=(190, 206, 222), outline=(90, 84, 72), width=9)
    d.line([(280, 160), (280, 430)], fill=(90, 84, 72), width=7)
    # ホワイトボード（グラフ）
    d.rectangle([640, 150, 1210, 470], fill=(238, 240, 244), outline=(120, 114, 100), width=9)
    d.line([(700, 420), (1150, 420)], fill=(90, 96, 110), width=6)
    d.line([(700, 420), (700, 200)], fill=(90, 96, 110), width=6)
    pts = [(720, 400), (820, 360), (920, 300), (1020, 250), (1120, 210)]
    d.line(pts, fill=(210, 70, 60), width=8, joint="curve")
    for p in pts:
        d.ellipse([p[0] - 9, p[1] - 9, p[0] + 9, p[1] + 9], fill=(210, 70, 60))
    # 会議机
    d.rounded_rectangle([120, 640, 1160, 780], radius=30, fill=(126, 92, 60),
                        outline=(88, 64, 42), width=8)
    d.rectangle([0, 780, W, H], fill=(104, 96, 84))
    return img


def ginza_shop() -> Image.Image:
    """1969年12月、銀座の時計店ショーウィンドウ。発売の場面。"""
    img = _rgba(vgrad((W, H), (46, 52, 74), (24, 28, 42)))
    d = ImageDraw.Draw(img)
    # 夜の街とネオン
    for x in range(0, W, 210):
        d.rectangle([x, 60, x + 150, 420], fill=(38, 44, 62))
        for y in range(90, 400, 56):
            for k in range(3):
                if (x + y + k) % 3:
                    d.rectangle([x + 20 + k * 42, y, x + 48 + k * 42, y + 32],
                                fill=(240, 214, 140))
    # 店の庇
    d.rectangle([160, 420, 1120, 480], fill=(150, 40, 48), outline=(90, 22, 28), width=7)
    # ショーウィンドウ
    d.rectangle([220, 480, 1060, 800], fill=(20, 24, 36), outline=(200, 176, 110), width=10)
    d.rectangle([250, 510, 1030, 770], fill=(38, 44, 62))
    for x in range(300, 980, 160):
        d.ellipse([x, 590, x + 96, 686], fill=(226, 200, 120), outline=(120, 96, 40), width=6)
        d.ellipse([x + 16, 606, x + 80, 670], fill=(246, 244, 236))
        glow(img, x + 48, 638, 150, (255, 226, 150), alpha=50)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 800, W, H], fill=(30, 34, 48))
    return img


def now() -> Image.Image:
    """現代。腕時計とスマホが並ぶ、明るい室内。"""
    img = _rgba(vgrad((W, H), (226, 232, 242), (188, 198, 214)))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 90], fill=(206, 214, 228))
    # 窓の光
    d.rectangle([820, 120, 1230, 470], fill=(244, 250, 255), outline=(170, 180, 196), width=8)
    d.line([(1025, 120), (1025, 470)], fill=(170, 180, 196), width=6)
    glow(img, 1025, 300, 420, (255, 255, 255), alpha=60)
    d = ImageDraw.Draw(img)
    # テーブル
    d.rectangle([0, 620, W, 680], fill=(206, 176, 140))
    d.rectangle([0, 680, W, H], fill=(178, 150, 118))
    # 腕時計を並べる
    for x in range(140, 900, 230):
        d.rounded_rectangle([x, 520, x + 120, 620], radius=26,
                            fill=(210, 216, 228), outline=(120, 126, 140), width=7)
        d.ellipse([x + 16, 536, x + 104, 604], fill=(250, 250, 248),
                  outline=(120, 126, 140), width=5)
        d.line([(x + 60, 570), (x + 60, 546)], fill=(60, 64, 78), width=5)
        d.line([(x + 60, 570), (x + 84, 578)], fill=(60, 64, 78), width=5)
    return img


PAINTERS = {
    "il_qz_kojo": kojo,
    "il_qz_observatory": observatory,
    "il_qz_lab": lab,
    "il_qz_olympic": olympic,
    "il_qz_kaigi": kaigi,
    "il_qz_ginza": ginza_shop,
    "il_qz_now": now,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
