#!/usr/bin/env python3
"""プリクラ再現ドラマ（purikura-meme）用のイラスト背景12種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
実行: PYTHONPATH=. python3 scripts/gen_pk_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402

# 90年代のゲーセンの色。CRTの青緑とネオンのマゼンタ
CRT = (108, 216, 200)
NEON = (232, 80, 150)


def _cabinet(d, x, y, w=210, h=300, screen=(24, 56, 64), lit=CRT):
    """アップライト筐体を1台。y は床の位置。"""
    top = y - h
    d.rounded_rectangle([x, top, x + w, y], radius=10, fill=(46, 44, 58))
    # 画面
    sx0, sy0, sx1, sy1 = x + 22, top + 34, x + w - 22, top + int(h * 0.45)
    d.rounded_rectangle([sx0, sy0, sx1, sy1], radius=6, fill=screen)
    for i in range(4):
        d.line([sx0 + 10, sy0 + 16 + i * 18, sx1 - 10, sy0 + 16 + i * 18],
               fill=lit, width=5)
    # コンパネ（ボタンとレバー）
    py = top + int(h * 0.58)
    d.rounded_rectangle([x + 14, py, x + w - 14, py + 54], radius=8, fill=(66, 62, 80))
    d.ellipse([x + 30, py + 16, x + 56, py + 42], fill=(60, 58, 74))
    for k in range(3):
        d.ellipse([x + 78 + k * 34, py + 18, x + 100 + k * 34, py + 40], fill=NEON)
    # マーキー
    d.rounded_rectangle([x + 10, top + 6, x + w - 10, top + 26], radius=5, fill=NEON)


def gamecenter() -> Image.Image:
    """1990年代半ばのゲームセンター。格闘ゲームの筐体が並ぶ薄暗い店内。"""
    img = vgrad((W, H), (26, 24, 40), (16, 14, 26)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 奥の壁とダクト
    d.rectangle([0, 0, W, 200], fill=(20, 18, 32))
    for x in range(80, W, 300):
        d.rounded_rectangle([x, 40, x + 200, 96], radius=14, fill=(40, 38, 54))
    # 筐体を2列
    for i, x in enumerate(range(-40, W, 250)):
        _cabinet(d, x, 640, screen=(20, 48, 58) if i % 2 else (48, 22, 44))
    _floor(d, 640, (48, 44, 60), (36, 32, 46))
    # 床のカーペット模様
    for k in range(9):
        d.line([k * 240 - 120, 640, k * 300 - 400, H], fill=(40, 36, 52), width=8)
    # ネオンの光
    glow(img, 300, 380, 320, NEON, 60)
    glow(img, 1500, 380, 320, CRT, 50)
    return img


def atlas_office() -> Image.Image:
    """神楽坂のアトラス社屋。小さな雑居ビルのオフィス。"""
    img = vgrad((W, H), (96, 100, 116), (74, 78, 92)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _window(img, d, 1420, 150, 1800, 470, (150, 178, 210), (206, 220, 232))
    # スチール棚と資料
    d.rectangle([80, 180, 520, 620], fill=(84, 88, 102))
    for r in range(4):
        d.rectangle([90, 200 + r * 106, 510, 212 + r * 106], fill=(64, 68, 82))
        for c in range(7):
            d.rectangle([104 + c * 56, 216 + r * 106, 144 + c * 56, 296 + r * 106],
                        fill=(190, 176, 150) if (r + c) % 3 else (170, 140, 120))
    # 事務机とブラウン管
    d.rounded_rectangle([620, 520, 1300, 700], radius=8, fill=(126, 108, 84))
    d.rectangle([620, 520, 1300, 548], fill=(104, 88, 68))
    d.rounded_rectangle([760, 340, 1020, 528], radius=12, fill=(216, 212, 200))
    d.rectangle([790, 370, 990, 496], fill=(38, 62, 70))
    for i in range(5):
        d.line([806, 392 + i * 22, 974, 392 + i * 22], fill=(120, 200, 180), width=4)
    # 書類の山
    for k in range(3):
        d.rectangle([1090 + k * 8, 470 - k * 14, 1250 + k * 8, 520 - k * 14],
                    fill=(238, 234, 222), outline=(190, 184, 170), width=3)
    _floor(d, 700, (110, 96, 82), (92, 80, 68))
    return img


def kaigi() -> Image.Image:
    """会議室。ホワイトボードと長机。企画がぶつかる場所。"""
    img = vgrad((W, H), (208, 206, 198), (182, 180, 172)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 床を先に敷く（あとから敷くと机が埋まる）
    _floor(d, 700, (150, 146, 138), (132, 128, 120))
    # ブラインドの窓
    _window(img, d, 120, 180, 470, 520, (170, 198, 224), (222, 232, 240))
    for k in range(9):
        d.line([120, 200 + k * 36, 470, 200 + k * 36], fill=(196, 202, 210), width=10)
    # ホワイトボード
    d.rounded_rectangle([560, 130, 1400, 590], radius=8, fill=(120, 122, 128))
    d.rectangle([578, 148, 1382, 560], fill=(246, 246, 242))
    d.line([640, 240, 900, 240], fill=(40, 90, 170), width=10)
    d.line([640, 300, 1060, 300], fill=(40, 90, 170), width=10)
    d.rounded_rectangle([1080, 210, 1300, 400], radius=10, outline=(200, 50, 60), width=10)
    d.line([1100, 430, 1290, 430], fill=(60, 60, 66), width=8)
    d.rectangle([578, 560, 1382, 590], fill=(200, 200, 196))
    # 長机（床より手前）
    d.rounded_rectangle([200, 720, 1720, 880], radius=14, fill=(158, 132, 100))
    d.rectangle([200, 720, 1720, 758], fill=(134, 110, 82))
    # 机の上の書類と紙コップ
    for bx in (330, 780, 1300):
        d.rectangle([bx, 690, bx + 190, 726], fill=(242, 238, 228),
                    outline=(196, 190, 176), width=3)
        d.polygon([(bx + 230, 726), (bx + 274, 726), (bx + 266, 674), (bx + 238, 674)],
                  fill=(240, 240, 238))
    return img


def yaizu() -> Image.Image:
    """焼津のゲームセンター。海沿いの町の小さな店。"""
    img = vgrad((W, H), (168, 196, 216), (214, 226, 234)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 海と防波堤
    d.rectangle([0, 300, W, 430], fill=(96, 148, 176))
    for k in range(7):
        d.line([60 + k * 280, 350 + (k % 3) * 24, 220 + k * 280, 350 + (k % 3) * 24],
               fill=(150, 190, 210), width=6)
    d.rectangle([0, 430, W, 470], fill=(160, 156, 148))
    # 平屋の店
    d.rectangle([420, 200, 1500, 640], fill=(224, 216, 200))
    d.rectangle([420, 200, 1500, 268], fill=(220, 70, 60))
    for k in range(4):
        d.rounded_rectangle([500 + k * 260, 216, 660 + k * 260, 252], radius=6,
                            fill=(250, 240, 210))
    # ガラス戸とのれん
    for k in range(4):
        d.rectangle([470 + k * 260, 300, 690 + k * 260, 640], fill=(150, 176, 190))
        d.line([580 + k * 260, 300, 580 + k * 260, 640], fill=(200, 196, 186), width=8)
    _floor(d, 640, (176, 172, 164), (156, 152, 146))
    # 自販機
    d.rounded_rectangle([1560, 380, 1740, 640], radius=8, fill=(200, 60, 56))
    for r in range(3):
        d.rectangle([1584, 410 + r * 60, 1716, 452 + r * 60], fill=(236, 230, 216))
    return img


def sega_room() -> Image.Image:
    """セガの社長室。大きな窓と応接セット。"""
    img = vgrad((W, H), (66, 74, 96), (46, 52, 70)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _window(img, d, 1180, 130, 1810, 560, (120, 160, 210), (208, 226, 240))
    # 本棚
    d.rectangle([80, 150, 560, 640], fill=(72, 58, 46))
    for r in range(4):
        d.rectangle([92, 172 + r * 118, 548, 186 + r * 118], fill=(56, 44, 36))
        for c in range(8):
            d.rectangle([106 + c * 54, 192 + r * 118, 146 + c * 54, 288 + r * 118],
                        fill=(150, 60, 54) if (r + c) % 2 else (60, 80, 120))
    # 執務机
    d.rounded_rectangle([640, 560, 1420, 740], radius=10, fill=(88, 66, 50))
    d.rectangle([640, 560, 1420, 594], fill=(70, 52, 40))
    d.rounded_rectangle([900, 500, 1160, 566], radius=8, fill=(226, 222, 212))
    _floor(d, 740, (74, 62, 54), (58, 48, 42))
    # 絨毯
    d.rounded_rectangle([260, 830, 1660, H], radius=18, fill=(96, 60, 62))
    return img


def expo() -> Image.Image:
    """AOUアミューズメントエキスポの会場。展示ブースとスポットライト。"""
    img = vgrad((W, H), (18, 20, 36), (30, 32, 52)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 天井のトラスとスポット
    d.rectangle([0, 0, W, 90], fill=(22, 24, 40))
    for x in range(140, W, 300):
        d.polygon([(x - 40, 90), (x + 40, 90), (x + 12, 130), (x - 12, 130)],
                  fill=(60, 64, 84))
        glow(img, x, 300, 300, (255, 240, 200), 34)
    # 奥のブースの壁
    for i, x in enumerate(range(0, W, 480)):
        col = (44, 52, 88) if i % 2 else (60, 44, 82)
        d.rectangle([x + 20, 200, x + 440, 620], fill=col)
        d.rounded_rectangle([x + 60, 240, x + 400, 320], radius=8, fill=(230, 232, 240))
        d.rectangle([x + 90, 380, x + 370, 620], fill=(30, 34, 56))
    _floor(d, 620, (46, 48, 68), (34, 36, 54))
    # 床のリノリウム
    for k in range(8):
        d.line([k * 260, 620, k * 320 - 300, H], fill=(40, 42, 60), width=6)
    return img


def gyoretsu() -> Image.Image:
    """街のゲームセンター前。プリクラ待ちの行列ができた通り。"""
    img = vgrad((W, H), (176, 200, 226), (222, 232, 240)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 雑居ビル
    for i, (bx, bw, bh) in enumerate([(0, 380, 520), (400, 300, 420),
                                      (1300, 300, 460), (1620, 300, 540)]):
        col = (168, 172, 186) if i % 2 else (150, 154, 170)
        d.rectangle([bx, 600 - bh, bx + bw, 600], fill=col)
        for r in range(bh // 100):
            for c in range(bw // 100):
                d.rectangle([bx + 26 + c * 100, 600 - bh + 26 + r * 100,
                             bx + 82 + c * 100, 600 - bh + 82 + r * 100],
                            fill=(212, 224, 238))
    # ゲーセンの入口（ピンクの看板）
    d.rectangle([720, 250, 1280, 600], fill=(230, 226, 220))
    d.rounded_rectangle([740, 268, 1260, 356], radius=10, fill=NEON)
    d.rectangle([800, 400, 1200, 600], fill=(60, 66, 84))
    # 歩道と車道（先に敷く）
    _floor(d, 600, (198, 198, 202), (176, 176, 182))
    d.rectangle([0, 880, W, H], fill=(120, 124, 132))
    for k in range(7):
        d.rectangle([90 + k * 280, 940, 230 + k * 280, 966], fill=(220, 222, 226))
    # 行列を仕切るポールとベルト（床より手前）
    for k in range(6):
        px = 200 + k * 290
        d.ellipse([px - 26, 846, px + 26, 872], fill=(150, 60, 60))
        d.rectangle([px - 8, 690, px + 8, 858], fill=(180, 70, 70))
        d.ellipse([px - 18, 676, px + 18, 704], fill=(200, 90, 90))
        if k < 5:
            d.rectangle([px + 8, 716, px + 282, 742], fill=(226, 196, 90))
    return img


def yakin() -> Image.Image:
    """深夜のアトラス。鳴り止まない電話と受注伝票の山。"""
    img = vgrad((W, H), (34, 38, 56), (22, 26, 40)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _window(img, d, 1440, 140, 1810, 440, (16, 20, 40), (40, 46, 74))
    # 窓の外の夜景
    for k in range(16):
        d.rectangle([1470 + (k % 6) * 55, 180 + (k // 6) * 74,
                     1500 + (k % 6) * 55, 216 + (k // 6) * 74], fill=(240, 220, 140))
    # 蛍光灯
    d.rounded_rectangle([300, 40, 900, 78], radius=8, fill=(236, 240, 230))
    glow(img, 600, 90, 360, (240, 244, 220), 46)
    # 机と伝票の山
    d.rounded_rectangle([180, 560, 1340, 740], radius=8, fill=(98, 84, 66))
    d.rectangle([180, 560, 1340, 590], fill=(80, 68, 54))
    for i, bx in enumerate([260, 520, 800, 1060]):
        hgt = 90 + (i % 3) * 46
        for k in range(hgt // 14):
            d.rectangle([bx + (k % 3) * 6, 560 - k * 14, bx + 200 + (k % 3) * 6,
                         572 - k * 14], fill=(240, 236, 224), outline=(186, 180, 166),
                        width=2)
    # 黒電話
    d.rounded_rectangle([1180, 470, 1330, 562], radius=12, fill=(40, 42, 52))
    d.rounded_rectangle([1196, 440, 1314, 486], radius=18, fill=(30, 32, 40))
    _floor(d, 740, (58, 52, 46), (44, 40, 36))
    return img


def shibuya() -> Image.Image:
    """1990年代の渋谷。女子高生ブームのころの街。"""
    img = vgrad((W, H), (52, 62, 96), (110, 96, 120)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # ビルと看板
    for i, (bx, bw, bh) in enumerate([(0, 420, 620), (440, 340, 500),
                                      (820, 300, 680), (1160, 380, 540),
                                      (1580, 340, 640)]):
        d.rectangle([bx, 640 - bh, bx + bw, 640], fill=(48, 46, 66) if i % 2 else (38, 38, 56))
        for r in range(bh // 120):
            col = [NEON, (250, 210, 90), CRT, (150, 130, 240)][(i + r) % 4]
            d.rounded_rectangle([bx + 24, 640 - bh + 30 + r * 120,
                                 bx + bw - 24, 640 - bh + 96 + r * 120],
                                radius=6, fill=col)
    glow(img, 620, 420, 420, NEON, 46)
    glow(img, 1400, 380, 380, (250, 210, 90), 40)
    _floor(d, 640, (56, 54, 70), (44, 42, 56))
    # 横断歩道
    d.rectangle([0, 800, W, H], fill=(46, 46, 58))
    for k in range(8):
        d.rectangle([70 + k * 240, 830, 200 + k * 240, H], fill=(206, 208, 214))
    return img


def purikura_corner() -> Image.Image:
    """プリクラ機が並ぶコーナー。ピンクの筐体とカーテン。"""
    img = vgrad((W, H), (250, 214, 230), (238, 186, 212)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 筐体を3台
    for i, x in enumerate([90, 730, 1370]):
        d.rounded_rectangle([x, 130, x + 460, 780], radius=18,
                            fill=(236, 120, 172) if i % 2 else (230, 96, 156))
        d.rounded_rectangle([x + 28, 168, x + 432, 250], radius=10, fill=(255, 248, 252))
        # カーテン
        d.rectangle([x + 40, 280, x + 420, 780], fill=(250, 236, 244))
        for k in range(7):
            d.line([x + 60 + k * 56, 280, x + 60 + k * 56, 780],
                   fill=(232, 206, 222), width=8)
        # 上の照明
        d.rounded_rectangle([x + 60, 190, x + 400, 226], radius=8, fill=(255, 236, 160))
    _floor(d, 780, (226, 200, 216), (208, 178, 198))
    # 床のハート模様
    for k in range(9):
        cx, cy = 130 + k * 210, 880 + (k % 2) * 70
        d.ellipse([cx - 26, cy - 22, cx + 2, cy + 6], fill=(240, 206, 224))
        d.ellipse([cx - 2, cy - 22, cx + 26, cy + 6], fill=(240, 206, 224))
        d.polygon([(cx - 24, cy - 4), (cx + 24, cy - 4), (cx, cy + 30)],
                  fill=(240, 206, 224))
    return img


def kaigo() -> Image.Image:
    """介護施設の日当たりのいい部屋。佐々木のその後。"""
    img = vgrad((W, H), (238, 232, 216), (222, 214, 198)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _window(img, d, 1180, 140, 1800, 560, (176, 206, 232), (232, 240, 246))
    glow(img, 1490, 350, 460, (255, 246, 210), 52)
    # 床を先に敷く
    _floor(d, 660, (206, 190, 168), (188, 172, 152))
    # 手すり
    d.rounded_rectangle([60, 500, 1040, 528], radius=14, fill=(190, 160, 120))
    for x in (140, 520, 940):
        d.rectangle([x, 500, x + 20, 660], fill=(170, 142, 106))
    # テーブルと椅子
    for x in (330, 1090):
        d.rounded_rectangle([x, 740, x + 46, 950], radius=10, fill=(184, 156, 120))
    d.rounded_rectangle([280, 700, 1180, 760], radius=16, fill=(214, 186, 148))
    d.rectangle([280, 700, 1180, 726], fill=(190, 162, 126))
    # 花瓶
    d.ellipse([690, 620, 760, 706], fill=(150, 180, 200))
    for a, c in ((-30, (230, 140, 160)), (0, (250, 220, 140)), (30, (200, 170, 220))):
        d.ellipse([718 + a - 22, 578, 718 + a + 22, 622], fill=c)
    return img


def heya_now() -> Image.Image:
    """現代の部屋（茶番用）。ずんだもんが自撮りをしている場所。"""
    img = vgrad((W, H), (238, 230, 240), (216, 206, 224)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _window(img, d, 1360, 150, 1810, 500, (168, 200, 232), (226, 236, 244))
    # 壁に貼ったシールの台紙
    d.rounded_rectangle([180, 160, 620, 560], radius=10, fill=(250, 246, 240))
    for r in range(4):
        for c in range(4):
            d.rounded_rectangle([210 + c * 100, 190 + r * 92, 290 + c * 100,
                                 262 + r * 92], radius=8,
                                fill=(246, 200, 216) if (r + c) % 2 else (206, 226, 244))
    # 床を先に敷く
    _floor(d, 660, (200, 186, 200), (182, 168, 184))
    # 観葉植物
    for a in (-70, -20, 30, 80):
        d.ellipse([1670 + a - 40, 560, 1670 + a + 40, 730], fill=(96, 156, 96))
    d.rounded_rectangle([1600, 700, 1740, 880], radius=10, fill=(180, 128, 96))
    # ローテーブルとスマホ
    d.rounded_rectangle([700, 740, 1300, 900], radius=14, fill=(186, 158, 126))
    d.rectangle([700, 740, 1300, 774], fill=(158, 132, 102))
    d.rounded_rectangle([930, 690, 1034, 754], radius=10, fill=(48, 50, 60))
    d.rounded_rectangle([940, 698, 1024, 746], radius=6, fill=(140, 196, 220))
    return img


PAINTERS = {
    "il_pk_gamecenter": gamecenter,
    "il_pk_atlas": atlas_office,
    "il_pk_kaigi": kaigi,
    "il_pk_yaizu": yaizu,
    "il_pk_sega": sega_room,
    "il_pk_expo": expo,
    "il_pk_gyoretsu": gyoretsu,
    "il_pk_yakin": yakin,
    "il_pk_shibuya": shibuya,
    "il_pk_purikura": purikura_corner,
    "il_pk_kaigo": kaigo,
    "il_pk_heya": heya_now,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
