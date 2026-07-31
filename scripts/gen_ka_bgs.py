#!/usr/bin/env python3
"""カラオケ再現ドラマ（karaoke）用のイラスト背景7種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
実行: PYTHONPATH=. python3 scripts/gen_ka_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402


def _rgba(img):
    return img.convert("RGBA")


def _mic(d, cx, cy, s=1.0, col=(60, 64, 74)):
    """スタンドマイク。"""
    d.line([cx, cy, cx, cy - 180 * s], fill=col, width=int(10 * s))
    d.line([cx - 40 * s, cy, cx + 40 * s, cy], fill=col, width=int(10 * s))
    d.ellipse([cx - 26 * s, cy - 230 * s, cx + 26 * s, cy - 178 * s],
              fill=(150, 156, 168))


def _notes(d, pts, col=(255, 220, 120)):
    """音符の飾り。"""
    for (x, y, s) in pts:
        d.ellipse([x - 9 * s, y - 6 * s, x + 9 * s, y + 6 * s], fill=col)
        d.line([x + 8 * s, y, x + 8 * s, y - 34 * s], fill=col, width=int(4 * s))
        d.line([x + 8 * s, y - 34 * s, x + 22 * s, y - 26 * s], fill=col,
               width=int(4 * s))


def box_now() -> Image.Image:
    """現代のカラオケボックス個室。"""
    img = _rgba(vgrad((W, H), (34, 24, 52), (18, 12, 30)))
    d = ImageDraw.Draw(img)
    # 壁の飾り照明
    for cx, cy, r, col in [(300, 200, 130, (200, 80, 160)), (1650, 260, 150, (80, 120, 220)),
                           (980, 130, 110, (240, 160, 60))]:
        glow(img, cx, cy, r, col, alpha=70)
        d = ImageDraw.Draw(img)
    # モニタ
    d.rounded_rectangle([700, 150, 1250, 460], radius=18, fill=(14, 16, 22),
                        outline=(70, 74, 88), width=6)
    d.rectangle([740, 190, 1210, 300], fill=(30, 40, 66))
    d.rectangle([760, 330, 1010, 360], fill=(90, 200, 140))
    d.rectangle([760, 390, 1130, 420], fill=(70, 90, 130))
    _notes(d, [(1300, 220, 1.0), (640, 300, 0.8), (1340, 420, 0.7)])
    # ソファ
    d.rounded_rectangle([80, 700, 700, 980], radius=30, fill=(120, 40, 60))
    d.rounded_rectangle([80, 620, 700, 740], radius=24, fill=(140, 50, 72))
    d.rounded_rectangle([1250, 700, 1860, 980], radius=30, fill=(120, 40, 60))
    d.rounded_rectangle([1250, 620, 1860, 740], radius=24, fill=(140, 50, 72))
    # テーブル+ドリンク+デンモク
    d.rounded_rectangle([760, 760, 1190, 980], radius=20, fill=(52, 40, 34))
    d.rectangle([830, 690, 880, 770], fill=(240, 180, 70))
    d.rectangle([920, 700, 965, 770], fill=(120, 200, 240))
    d.rounded_rectangle([1010, 700, 1140, 764], radius=10, fill=(30, 34, 44),
                        outline=(90, 96, 110), width=4)
    return img


def juso_street() -> Image.Image:
    """昭和の大阪・十三の食堂街の夕暮れ。"""
    img = _rgba(vgrad((W, H), (238, 150, 90), (120, 60, 50)))
    d = ImageDraw.Draw(img)
    # 遠景の家並み
    for i, (x0, w_, h_) in enumerate([(0, 340, 320), (330, 300, 380), (620, 360, 300),
                                      (970, 300, 360), (1260, 340, 310), (1590, 330, 380)]):
        col = (96, 62, 56) if i % 2 else (112, 72, 62)
        d.rectangle([x0, 560 - h_ + 260, x0 + w_, 820], fill=col)
        # 窓明かり
        for wx in range(x0 + 40, x0 + w_ - 40, 90):
            d.rectangle([wx, 620, wx + 44, 668], fill=(255, 208, 120))
    # のれん・看板
    d.rectangle([180, 470, 480, 560], fill=(180, 60, 50))
    d.rectangle([210, 560, 240, 640], fill=(180, 60, 50))
    d.rectangle([300, 560, 330, 640], fill=(180, 60, 50))
    d.rectangle([390, 560, 420, 640], fill=(180, 60, 50))
    d.rounded_rectangle([1380, 430, 1560, 700], radius=14, fill=(245, 236, 210))
    d.rectangle([1420, 470, 1520, 500], fill=(190, 70, 50))
    d.rectangle([1420, 530, 1520, 560], fill=(80, 70, 60))
    d.rectangle([1420, 590, 1520, 620], fill=(80, 70, 60))
    # 提灯
    for x in [560, 700, 840, 980, 1120, 1260]:
        d.line([x, 380, x, 430], fill=(70, 50, 40), width=4)
        d.ellipse([x - 36, 430, x + 36, 520], fill=(255, 150, 60))
        glow(img, x, 475, 70, (255, 170, 80), alpha=60)
        d = ImageDraw.Draw(img)
    # 道
    d.rectangle([0, 820, W, H], fill=(70, 52, 48))
    d.line([0, 820, W, 820], fill=(50, 38, 36), width=6)
    return img


def club_stage() -> Image.Image:
    """1960年代・神戸のクラブ（ステージとドラムセット）。"""
    img = _rgba(vgrad((W, H), (30, 16, 34), (14, 8, 20)))
    d = ImageDraw.Draw(img)
    # 赤いカーテン
    d.rectangle([0, 0, W, 500], fill=(96, 22, 40))
    for x in range(0, W, 120):
        d.polygon([(x, 0), (x + 60, 0), (x + 40, 500), (x - 20, 500)],
                  fill=(120, 30, 50))
    d.rectangle([0, 480, W, 520], fill=(160, 120, 40))
    # スポットライト
    glow(img, 500, 260, 320, (255, 220, 140), alpha=40)
    glow(img, 1400, 260, 320, (180, 200, 255), alpha=35)
    d = ImageDraw.Draw(img)
    # ステージ床
    d.rectangle([0, 520, W, 900], fill=(60, 40, 30))
    for x in range(0, W, 160):
        d.line([x, 520, x, 900], fill=(50, 33, 25), width=3)
    # ドラムセット（左奥）
    d.ellipse([250, 620, 470, 840], fill=(180, 70, 60), outline=(230, 200, 160), width=8)
    d.ellipse([210, 560, 330, 620], fill=(200, 170, 120))
    d.ellipse([420, 540, 540, 600], fill=(200, 170, 120))
    d.line([270, 620, 240, 700], fill=(120, 120, 130), width=6)
    d.line([480, 600, 510, 700], fill=(120, 120, 130), width=6)
    # マイク（右）
    _mic(d, 1500, 860, 1.2)
    # 客席のテーブル影
    d.rectangle([0, 900, W, H], fill=(22, 14, 24))
    for x in [200, 700, 1200, 1700]:
        d.ellipse([x - 90, 930, x + 90, 1000], fill=(34, 22, 34))
        d.ellipse([x - 20, 890, x + 20, 940], fill=(255, 190, 90))
    return img


def workshop() -> Image.Image:
    """1971・手作りの作業場。"""
    img = _rgba(vgrad((W, H), (56, 46, 40), (30, 24, 22)))
    d = ImageDraw.Draw(img)
    # 窓の夜景
    d.rectangle([1420, 120, 1800, 420], fill=(24, 30, 52))
    d.rectangle([1600, 120, 1620, 420], fill=(70, 60, 52))
    d.rectangle([1420, 260, 1800, 280], fill=(70, 60, 52))
    d.rectangle([1460, 330, 1500, 360], fill=(255, 210, 120))
    d.rectangle([1700, 180, 1740, 210], fill=(255, 210, 120))
    # 吊り電球
    d.line([700, 0, 700, 150], fill=(60, 50, 44), width=6)
    d.ellipse([670, 150, 730, 220], fill=(255, 216, 130))
    glow(img, 700, 190, 180, (255, 210, 120), alpha=60)
    d = ImageDraw.Draw(img)
    # 棚と部品箱
    d.rectangle([60, 200, 560, 640], fill=(76, 58, 46))
    for y in [320, 450, 580]:
        d.rectangle([60, y, 560, y + 14], fill=(56, 42, 34))
    for i, x in enumerate(range(90, 520, 110)):
        col = [(180, 120, 70), (110, 130, 160), (170, 90, 80), (120, 150, 110)][i % 4]
        d.rectangle([x, 250, x + 90, 316], fill=col)
        d.rectangle([x, 380, x + 90, 446], fill=(90, 76, 62))
    # 作業台
    d.rectangle([0, 800, W, H], fill=(88, 64, 46))
    d.rectangle([0, 780, W, 810], fill=(104, 78, 56))
    # 台上の部品（デッキ・工具・コード）
    d.rounded_rectangle([760, 660, 1120, 780], radius=10, fill=(40, 42, 50),
                        outline=(150, 150, 160), width=5)
    d.rectangle([800, 690, 930, 750], fill=(20, 22, 28))
    d.line([1140, 760, 1320, 700], fill=(200, 90, 70), width=8)
    d.line([1320, 700, 1420, 770], fill=(200, 90, 70), width=8)
    d.rectangle([1440, 720, 1560, 780], fill=(160, 130, 60))
    return img


def snack_bar() -> Image.Image:
    """神戸のスナック店内。"""
    img = _rgba(vgrad((W, H), (52, 26, 40), (26, 14, 24)))
    d = ImageDraw.Draw(img)
    # ボトル棚
    d.rectangle([1200, 120, 1860, 640], fill=(64, 40, 44))
    for y in [260, 400, 540]:
        d.rectangle([1200, y, 1860, y + 16], fill=(46, 28, 32))
        for x in range(1240, 1820, 90):
            col = [(200, 150, 60), (110, 170, 140), (170, 110, 150)][(x // 90) % 3]
            d.rectangle([x, y - 110, x + 44, y], fill=col)
            d.rectangle([x + 12, y - 140, x + 32, y - 110], fill=(90, 70, 60))
    # 暖色照明
    for x in [300, 760]:
        d.line([x, 0, x, 120], fill=(60, 40, 44), width=6)
        d.ellipse([x - 40, 120, x + 40, 200], fill=(255, 170, 90))
        glow(img, x, 170, 160, (255, 160, 90), alpha=55)
        d = ImageDraw.Draw(img)
    # カウンター
    d.rectangle([0, 700, W, 860], fill=(96, 58, 40))
    d.rectangle([0, 680, W, 710], fill=(120, 76, 50))
    d.rectangle([0, 860, W, H], fill=(40, 22, 28))
    # グラスと灰皿
    d.rectangle([420, 620, 470, 690], fill=(180, 220, 240))
    d.rectangle([540, 640, 600, 686], fill=(230, 190, 90))
    d.ellipse([680, 650, 780, 690], fill=(70, 74, 84))
    # 隅の8JUKE(歌う機械)
    d.rounded_rectangle([60, 380, 340, 690], radius=14, fill=(52, 56, 70),
                        outline=(150, 150, 165), width=6)
    d.rectangle([100, 430, 300, 500], fill=(24, 26, 34))
    d.ellipse([120, 540, 180, 600], fill=(220, 170, 70))
    d.rectangle([220, 540, 300, 600], fill=(30, 32, 40))
    _notes(d, [(390, 340, 0.9), (250, 300, 0.7)])
    return img


def showa_office() -> Image.Image:
    """拡大期の事務所。"""
    img = _rgba(vgrad((W, H), (206, 196, 176), (150, 140, 124)))
    d = ImageDraw.Draw(img)
    # 窓と街
    d.rectangle([120, 120, 760, 520], fill=(170, 200, 220))
    d.rectangle([430, 120, 450, 520], fill=(120, 110, 96))
    d.rectangle([120, 310, 760, 330], fill=(120, 110, 96))
    for x, h_ in [(170, 120), (260, 170), (350, 90), (500, 150), (600, 110), (680, 180)]:
        d.rectangle([x, 520 - h_ - 190, x + 60, 310], fill=(130, 150, 170))
    d.rectangle([100, 100, 780, 124], fill=(110, 100, 88))
    d.rectangle([100, 520, 780, 544], fill=(110, 100, 88))
    # 掲示板と地図っぽい紙
    d.rectangle([1250, 150, 1830, 560], fill=(120, 104, 88))
    d.rectangle([1290, 190, 1560, 380], fill=(238, 232, 214))
    d.line([1330, 350, 1420, 240], fill=(190, 90, 70), width=6)
    d.line([1420, 240, 1520, 300], fill=(190, 90, 70), width=6)
    d.rectangle([1600, 190, 1790, 320], fill=(238, 232, 214))
    d.rectangle([1600, 360, 1790, 520], fill=(210, 220, 200))
    # 机と電話・書類
    d.rectangle([0, 760, W, H], fill=(140, 108, 76))
    d.rectangle([0, 740, W, 770], fill=(160, 124, 88))
    d.rounded_rectangle([300, 640, 470, 740], radius=12, fill=(40, 44, 52))
    d.ellipse([320, 600, 450, 660], fill=(40, 44, 52))
    d.rectangle([600, 660, 860, 740], fill=(240, 236, 222))
    d.rectangle([620, 680, 840, 692], fill=(140, 140, 150))
    d.rectangle([620, 706, 800, 718], fill=(140, 140, 150))
    d.rectangle([1500, 660, 1740, 740], fill=(240, 236, 222))
    return img


def harvard_hall() -> Image.Image:
    """2004・ハーバードの講堂（イグノーベル授賞式）。"""
    img = _rgba(vgrad((W, H), (60, 44, 34), (28, 20, 18)))
    d = ImageDraw.Draw(img)
    # 木のパネルとアーチ
    d.rectangle([0, 0, W, 620], fill=(84, 58, 40))
    for x in range(0, W, 240):
        d.rectangle([x + 20, 60, x + 220, 600], fill=(100, 70, 48))
        d.polygon([(x + 20, 60), (x + 120, 10), (x + 220, 60)], fill=(100, 70, 48))
    # 舞台の金の縁とスクリーン
    d.rectangle([560, 120, 1360, 520], fill=(30, 24, 40))
    d.rectangle([560, 120, 1360, 150], fill=(190, 150, 70))
    d.rectangle([560, 490, 1360, 520], fill=(190, 150, 70))
    glow(img, 960, 320, 260, (255, 230, 160), alpha=40)
    d = ImageDraw.Draw(img)
    # 演台
    d.rectangle([870, 560, 1050, 760], fill=(70, 48, 34))
    d.rectangle([850, 540, 1070, 580], fill=(90, 62, 42))
    _mic(d, 960, 560, 0.8)
    # 客席シルエット（前列）
    d.rectangle([0, 760, W, H], fill=(20, 14, 14))
    for i, x in enumerate(range(60, W, 150)):
        y = 800 + (i % 2) * 26
        d.ellipse([x, y, x + 84, y + 84], fill=(34, 26, 26))
        d.rectangle([x - 12, y + 70, x + 96, y + 180], fill=(34, 26, 26))
    return img


PAINTERS = {
    "il_ka_box": box_now,
    "il_ka_juso": juso_street,
    "il_ka_club": club_stage,
    "il_ka_workshop": workshop,
    "il_ka_snack": snack_bar,
    "il_ka_office": showa_office,
    "il_ka_hall": harvard_hall,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
