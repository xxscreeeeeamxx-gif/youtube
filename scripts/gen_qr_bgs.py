#!/usr/bin/env python3
"""QRコード再現ドラマ（qr-code）用のイラスト背景12種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造する（使い回し禁止）。
実行: PYTHONPATH=. python3 scripts/gen_qr_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402


def _floor(d, y, col, line_col):
    d.rectangle([0, y, W, H], fill=col)
    d.line([0, y, W, y], fill=line_col, width=6)


def _window(img, d, x0, y0, x1, y1, sky_top, sky_bot, frame=(70, 76, 96)):
    d.rounded_rectangle([x0 - 16, y0 - 16, x1 + 16, y1 + 16], radius=14, fill=frame)
    sky = vgrad((x1 - x0, y1 - y0), sky_top, sky_bot)
    img.paste(sky, (x0, y0))
    d.line([(x0 + x1) // 2, y0, (x0 + x1) // 2, y1], fill=frame, width=10)
    d.line([x0, (y0 + y1) // 2, x1, (y0 + y1) // 2], fill=frame, width=10)


def _goban(d, cx, cy, s=170):
    """碁盤（上面向き・石数個）。"""
    d.rounded_rectangle([cx - s, cy - s * 0.62, cx + s, cy + s * 0.62],
                        radius=10, fill=(196, 154, 90), outline=(120, 90, 50), width=5)
    for i in range(7):
        x = cx - s * 0.82 + i * (s * 1.64 / 6)
        d.line([x, cy - s * 0.5, x, cy + s * 0.5], fill=(110, 82, 44), width=3)
    for j in range(5):
        y = cy - s * 0.5 + j * (s * 1.0 / 4)
        d.line([cx - s * 0.82, y, cx + s * 0.82, y], fill=(110, 82, 44), width=3)
    for (gx, gy, col) in ((-0.55, -0.25, 0), (-0.27, 0.25, 1), (0.0, 0.0, 0),
                          (0.27, -0.25, 1), (0.55, 0.25, 0)):
        c = (30, 30, 34) if col == 0 else (240, 240, 244)
        r = s * 0.11
        d.ellipse([cx + gx * s * 1.4 - r, cy + gy * s * 0.9 - r,
                   cx + gx * s * 1.4 + r, cy + gy * s * 0.9 + r], fill=c)


def conbini() -> Image.Image:
    """現代のコンビニ店内（フック/締め用・夜）。"""
    img = vgrad((W, H), (238, 242, 248), (216, 222, 232)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (208, 206, 200), (180, 178, 172))
    # 天井の照明帯
    for i in range(3):
        d.rounded_rectangle([260 + i * 520, 60, 660 + i * 520, 100], radius=16,
                            fill=(250, 250, 246))
    # 左右の商品棚
    for sx in (40, W - 480):
        d.rounded_rectangle([sx, 260, sx + 440, int(H * 0.78)], radius=8,
                            fill=(196, 202, 214))
        for r in range(4):
            y = 300 + r * 130
            d.rectangle([sx + 16, y, sx + 424, y + 96], fill=(230, 234, 240))
            for k in range(6):
                d.rounded_rectangle([sx + 28 + k * 66, y + 18, sx + 78 + k * 66, y + 88],
                                    radius=6,
                                    fill=[(240, 150, 120), (150, 200, 240), (250, 220, 130),
                                          (170, 220, 170), (240, 180, 210), (200, 190, 240)][k])
    # 奥のレジカウンター
    d.rounded_rectangle([700, 560, 1220, int(H * 0.78)], radius=10, fill=(120, 130, 148))
    d.rectangle([700, 560, 1220, 590], fill=(96, 106, 124))
    d.rounded_rectangle([930, 440, 1060, 560], radius=8, fill=(70, 78, 94))  # レジ
    d.rectangle([944, 456, 1046, 516], fill=(150, 220, 200))
    # 窓の外は夜
    d.rectangle([700, 150, 1220, 380], fill=(30, 38, 60))
    d.line([700, 150, 1220, 150], fill=(180, 186, 198), width=8)
    d.line([700, 380, 1220, 380], fill=(180, 186, 198), width=8)
    return img


def machikoba() -> Image.Image:
    """昭和30年代・父の町工場（誕生〜幼少期）。"""
    img = vgrad((W, H), (86, 74, 62), (56, 48, 42)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.76), (70, 58, 48), (48, 40, 34))
    _window(img, d, 1360, 140, 1780, 520, (168, 196, 220), (208, 224, 236), (90, 76, 60))
    # 作業台と万力・部品
    d.rounded_rectangle([180, 560, 900, int(H * 0.76)], radius=8, fill=(110, 88, 62))
    d.rectangle([180, 560, 900, 596], fill=(90, 72, 52))
    d.rounded_rectangle([300, 470, 420, 560], radius=8, fill=(84, 90, 100))
    for i in range(4):
        d.ellipse([520 + i * 80, 500, 570 + i * 80, 550], fill=(140, 132, 120))
    # 部品棚（小箱がぎっしり）
    d.rounded_rectangle([980, 240, 1300, int(H * 0.76)], radius=8, fill=(96, 78, 56))
    for r in range(5):
        for k in range(3):
            d.rectangle([1000 + k * 100, 270 + r * 150, 1080 + k * 100, 350 + r * 150],
                        fill=(150, 128, 96) if (r + k) % 2 else (170, 146, 108))
    # 裸電球
    d.line([640, 0, 640, 150], fill=(60, 52, 44), width=6)
    glow(img, 640, 190, 130, (255, 214, 140), 90)
    d.ellipse([612, 150, 668, 226], fill=(255, 226, 150))
    return img


def washitsu_goban() -> Image.Image:
    """実家の和室・ちゃぶ台に碁盤（中学・囲碁）。"""
    img = vgrad((W, H), (94, 80, 66), (66, 58, 50)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 障子
    for sx in (120, 1420):
        d.rounded_rectangle([sx, 120, sx + 380, 700], radius=6, fill=(226, 218, 198))
        for i in range(3):
            d.line([sx + 95 + i * 95, 120, sx + 95 + i * 95, 700], fill=(150, 130, 104), width=8)
        for j in range(4):
            d.line([sx, 180 + j * 130, sx + 380, 180 + j * 130], fill=(150, 130, 104), width=8)
    # 畳
    d.rectangle([0, int(H * 0.72), W, H], fill=(146, 138, 96))
    d.line([0, int(H * 0.72), W, int(H * 0.72)], fill=(110, 104, 74), width=6)
    for i in range(4):
        d.line([i * 520, int(H * 0.72), i * 520 - 160, H], fill=(122, 116, 82), width=5)
    # ちゃぶ台+碁盤
    d.ellipse([720, 760, 1240, 950], fill=(122, 92, 58))
    _goban(d, 980, 830, 170)
    glow(img, 960, 150, 150, (255, 226, 170), 70)
    d.ellipse([930, 90, 990, 165], fill=(255, 232, 170))
    return img


def daigaku() -> Image.Image:
    """1970年代・大学の部室（オーディオと無線）。"""
    img = vgrad((W, H), (74, 82, 96), (52, 58, 70)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.76), (88, 76, 62), (64, 56, 48))
    _window(img, d, 180, 130, 620, 500, (250, 214, 150), (236, 172, 120), (80, 86, 100))
    # スピーカー2本
    for sx in (760, 1000):
        d.rounded_rectangle([sx, 420, sx + 180, int(H * 0.76)], radius=10, fill=(58, 48, 42))
        d.ellipse([sx + 40, 470, sx + 140, 570], fill=(30, 28, 30))
        d.ellipse([sx + 60, 610, sx + 120, 670], fill=(30, 28, 30))
    # アンプ棚（ダイヤル）
    d.rounded_rectangle([1260, 380, 1760, int(H * 0.76)], radius=8, fill=(70, 62, 58))
    for r in range(3):
        d.rounded_rectangle([1280, 410 + r * 160, 1740, 530 + r * 160], radius=8,
                            fill=(96, 88, 82))
        for k in range(4):
            d.ellipse([1310 + k * 110, 440 + r * 160, 1360 + k * 110, 490 + r * 160],
                      fill=(200, 190, 170))
    # 壁のアンテナ線
    d.line([700, 120, 1200, 90], fill=(140, 146, 160), width=4)
    d.line([1200, 90, 1240, 360], fill=(140, 146, 160), width=4)
    return img


def lab() -> Image.Image:
    """デンソーの開発室（80〜90年代・ブラウン管と機材）。"""
    img = vgrad((W, H), (66, 76, 92), (44, 52, 64)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (74, 80, 90), (56, 60, 70))
    # ブラインド窓
    d.rounded_rectangle([220, 120, 700, 520], radius=10, fill=(96, 106, 124))
    for j in range(10):
        d.line([236, 150 + j * 36, 684, 150 + j * 36], fill=(140, 150, 168), width=10)
    # 机+ブラウン管PC
    d.rounded_rectangle([840, 560, 1420, int(H * 0.77)], radius=8, fill=(104, 96, 88))
    d.rectangle([840, 560, 1420, 592], fill=(84, 78, 72))
    d.rounded_rectangle([950, 380, 1180, 560], radius=10, fill=(180, 176, 164))
    d.rectangle([974, 404, 1156, 522], fill=(60, 150, 120))
    for j in range(4):
        d.line([984, 424 + j * 24, 1146, 424 + j * 24], fill=(120, 220, 180), width=4)
    d.rounded_rectangle([1210, 480, 1400, 560], radius=8, fill=(168, 164, 154))
    # 機材ラック（LED）
    d.rounded_rectangle([1520, 260, 1840, int(H * 0.77)], radius=8, fill=(52, 58, 68))
    for r in range(6):
        d.rounded_rectangle([1540, 290 + r * 118, 1820, 380 + r * 118], radius=6,
                            fill=(74, 82, 96))
        for k in range(5):
            col = (240, 120, 100) if (r + k) % 3 == 0 else (120, 220, 160)
            d.ellipse([1560 + k * 40, 306 + r * 118, 1580 + k * 40, 326 + r * 118], fill=col)
    return img


def kojo() -> Image.Image:
    """自動車部品工場（ライン・箱・かんばん）。"""
    img = vgrad((W, H), (78, 86, 98), (56, 62, 72)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (90, 94, 102), (66, 70, 78))
    # 高窓
    for i in range(3):
        d.rectangle([200 + i * 560, 80, 620 + i * 560, 240], fill=(170, 190, 210))
        d.line([410 + i * 560, 80, 410 + i * 560, 240], fill=(96, 104, 118), width=8)
    # 柱
    for x in (140, 1780):
        d.rectangle([x - 40, 240, x + 40, int(H * 0.78)], fill=(108, 114, 126))
    # ベルトコンベア+箱
    d.rounded_rectangle([220, 620, 1700, 720], radius=12, fill=(64, 70, 82))
    for i in range(6):
        d.ellipse([260 + i * 240, 700, 320 + i * 240, 760], fill=(46, 50, 60))
    for i in range(4):
        bx = 320 + i * 340
        d.rounded_rectangle([bx, 520, bx + 220, 620], radius=6, fill=(178, 146, 96))
        d.rectangle([bx + 24, 545, bx + 196, 596], fill=(236, 232, 220))
        for k in range(8):
            d.line([bx + 34 + k * 20, 552, bx + 34 + k * 20, 590],
                   fill=(50, 50, 54), width=4 if k % 3 else 7)
    return img


def kaigi() -> Image.Image:
    """会議室（ホワイトボード・上司への直訴/ISO）。"""
    img = vgrad((W, H), (196, 200, 208), (168, 172, 182)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (140, 132, 122), (114, 108, 100))
    # ホワイトボード
    d.rounded_rectangle([620, 150, 1400, 560], radius=12, fill=(120, 126, 138))
    d.rectangle([646, 176, 1374, 534], fill=(246, 248, 250))
    d.line([690, 260, 1000, 260], fill=(90, 110, 200), width=8)
    d.line([690, 340, 1180, 340], fill=(200, 90, 90), width=6)
    d.line([690, 420, 1080, 420], fill=(90, 90, 100), width=6)
    d.rectangle([646, 534, 1374, 556], fill=(150, 155, 166))
    # 時計
    d.ellipse([1620, 160, 1760, 300], fill=(240, 242, 246), outline=(120, 126, 138), width=8)
    d.line([1690, 230, 1690, 185], fill=(60, 64, 74), width=6)
    d.line([1690, 230, 1725, 245], fill=(60, 64, 74), width=5)
    # 長机
    d.rounded_rectangle([200, 800, 1720, 900], radius=14, fill=(150, 120, 88))
    return img


def insatsu() -> Image.Image:
    """資料室（チラシと雑誌の山・比率調査）。"""
    img = vgrad((W, H), (84, 78, 72), (58, 54, 50)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (72, 64, 58), (52, 48, 44))
    # 紙の山（左右）
    for sx, n in ((150, 7), (1500, 6)):
        for i in range(n):
            y = int(H * 0.77) - 60 - i * 56
            off = (i % 3) * 14 - 14
            col = [(228, 224, 214), (214, 220, 228), (232, 216, 200)][i % 3]
            d.rounded_rectangle([sx + off, y, sx + 300 + off, y + 52], radius=6,
                                fill=col, outline=(150, 146, 138), width=3)
    # 机（開いた雑誌+ルーペ）
    d.rounded_rectangle([700, 620, 1280, int(H * 0.77)], radius=8, fill=(110, 88, 62))
    d.rectangle([700, 620, 1280, 652], fill=(92, 74, 52))
    d.rounded_rectangle([800, 520, 1000, 630], radius=4, fill=(238, 234, 226))
    d.rounded_rectangle([1010, 520, 1200, 630], radius=4, fill=(226, 230, 238))
    for x0, x1 in ((820, 980), (1030, 1180)):
        for j in range(4):
            d.line([x0, 545 + j * 22, x1, 545 + j * 22], fill=(120, 120, 128), width=5)
    d.ellipse([1120, 470, 1200, 550], outline=(200, 190, 150), width=10)
    d.line([1190, 540, 1240, 600], fill=(200, 190, 150), width=12)
    # 電気スタンド
    glow(img, 760, 470, 100, (255, 226, 160), 80)
    d.line([700, 620, 730, 480], fill=(90, 92, 100), width=8)
    d.polygon([(700, 470), (790, 470), (760, 520), (730, 520)], fill=(120, 124, 134))
    return img


def kyukei() -> Image.Image:
    """休憩室（昼休みの囲碁・湯呑み）。"""
    img = vgrad((W, H), (176, 182, 172), (146, 152, 144)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (128, 122, 108), (104, 100, 90))
    _window(img, d, 200, 140, 640, 520, (176, 208, 232), (220, 234, 242), (110, 116, 108))
    # 給茶機
    d.rounded_rectangle([1560, 320, 1800, int(H * 0.78)], radius=10, fill=(120, 126, 132))
    d.rectangle([1590, 360, 1770, 470], fill=(80, 86, 94))
    d.rounded_rectangle([1620, 500, 1740, 560], radius=8, fill=(96, 100, 108))
    # テーブル+碁盤+湯呑み
    d.rounded_rectangle([760, 700, 1360, 820], radius=14, fill=(150, 120, 88))
    _goban(d, 1060, 700, 150)
    for tx in (830, 1290):
        d.ellipse([tx - 30, 660, tx + 30, 700], fill=(90, 130, 110))
        d.ellipse([tx - 24, 656, tx + 24, 676], fill=(210, 226, 218))
    # 壁の標語ポスター
    d.rounded_rectangle([900, 180, 1240, 420], radius=6, fill=(238, 234, 222))
    d.line([950, 250, 1190, 250], fill=(180, 90, 80), width=10)
    d.line([950, 320, 1150, 320], fill=(110, 112, 120), width=7)
    return img


def machi2002() -> Image.Image:
    """2002年の商店街（ケータイの時代）。"""
    img = vgrad((W, H), (250, 214, 160), (236, 178, 130)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.8), (120, 112, 108), (96, 90, 88))
    # 店並び
    for i, col in enumerate(((214, 120, 96), (110, 150, 190), (150, 180, 120), (200, 160, 90))):
        sx = 60 + i * 470
        d.rectangle([sx, 300, sx + 420, int(H * 0.8)], fill=(230, 226, 216))
        d.rectangle([sx, 300, sx + 420, 380], fill=col)
        d.rectangle([sx + 40, 440, sx + 380, int(H * 0.8)], fill=(180, 196, 210))
    # ケータイショップの看板（アンテナ付き電話マーク）
    d.rounded_rectangle([1000, 180, 1360, 300], radius=14, fill=(240, 244, 250))
    d.rounded_rectangle([1050, 205, 1110, 280], radius=10, fill=(90, 110, 190))
    d.line([1105, 205, 1125, 170], fill=(90, 110, 190), width=8)
    d.rectangle([1150, 225, 1320, 245], fill=(120, 126, 140))
    d.rectangle([1150, 258, 1270, 274], fill=(160, 166, 180))
    # 電柱
    d.rectangle([1860, 100, 1900, int(H * 0.8)], fill=(110, 104, 100))
    d.line([1500, 150, 1900, 130], fill=(80, 76, 74), width=5)
    return img


def machinow() -> Image.Image:
    """現代の街（スマホ決済の時代・ガラスビル）。"""
    img = vgrad((W, H), (150, 200, 236), (208, 230, 244)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.8), (168, 172, 180), (140, 144, 152))
    # ガラスビル群
    for i, (bw, bh) in enumerate(((300, 620), (240, 760), (320, 540), (260, 690))):
        bx = 90 + i * 470
        d.rectangle([bx, int(H * 0.8) - bh, bx + bw, int(H * 0.8)], fill=(120, 160, 200))
        for r in range(bh // 90):
            for k in range(bw // 90):
                d.rectangle([bx + 14 + k * 90, int(H * 0.8) - bh + 14 + r * 90,
                             bx + 80 + k * 90, int(H * 0.8) - bh + 74 + r * 90],
                            fill=(190, 216, 240) if (r + k) % 3 else (230, 240, 250))
    # 大型ビジョンにQR風の四角
    d.rounded_rectangle([840, 170, 1250, 430], radius=10, fill=(40, 46, 60))
    d.rectangle([980, 210, 1120, 350], fill=(245, 248, 252))
    for (qx, qy) in ((995, 225), (1075, 225), (995, 305)):
        d.rectangle([qx, qy, qx + 30, qy + 30], fill=(30, 34, 44))
        d.rectangle([qx + 8, qy + 8, qx + 22, qy + 22], fill=(245, 248, 252))
        d.rectangle([qx + 12, qy + 12, qx + 18, qy + 18], fill=(30, 34, 44))
    for k in range(12):
        d.rectangle([1000 + (k * 37) % 100, 270 + (k * 23) % 60,
                     1012 + (k * 37) % 100, 282 + (k * 23) % 60], fill=(30, 34, 44))
    return img


def award() -> Image.Image:
    """授賞式ホール（紅幕・演台・スポットライト）。"""
    img = vgrad((W, H), (46, 34, 40), (28, 22, 28)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 紅幕
    d.rectangle([0, 0, W, int(H * 0.72)], fill=(130, 40, 48))
    for i in range(10):
        x = i * 210
        d.polygon([(x, 0), (x + 105, 0), (x + 70, int(H * 0.72)), (x - 35, int(H * 0.72))],
                  fill=(150, 50, 58) if i % 2 else (118, 34, 42))
    # 舞台床
    d.rectangle([0, int(H * 0.72), W, H], fill=(96, 74, 52))
    d.line([0, int(H * 0.72), W, int(H * 0.72)], fill=(70, 54, 40), width=8)
    # 演台
    d.polygon([(880, 620), (1180, 620), (1150, int(H * 0.9)), (910, int(H * 0.9))],
              fill=(80, 60, 44))
    d.rectangle([860, 590, 1200, 636], fill=(110, 84, 58))
    d.ellipse([1000, 640, 1060, 700], fill=(212, 178, 92))
    # スポットライト
    glow(img, 640, 200, 260, (255, 236, 190), 60)
    glow(img, 1300, 200, 260, (255, 236, 190), 60)
    return img


PAINTERS = {
    "il_qr_conbini": conbini,
    "il_qr_machikoba": machikoba,
    "il_qr_washitsu": washitsu_goban,
    "il_qr_daigaku": daigaku,
    "il_qr_lab": lab,
    "il_qr_kojo": kojo,
    "il_qr_kaigi": kaigi,
    "il_qr_insatsu": insatsu,
    "il_qr_kyukei": kyukei,
    "il_qr_machi2002": machi2002,
    "il_qr_machinow": machinow,
    "il_qr_award": award,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        img = fn().convert("RGB")
        img.save(OUT / f"{name}.png")
        print("背景生成:", name)
