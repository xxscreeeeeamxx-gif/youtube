#!/usr/bin/env python3
"""ダイエー・中内㓛の再現ドラマ（nakauchi-daiei）用のイラスト背景14種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
戦場と焼け跡は低彩度、店の場面は明るく、転落期はまた彩度を落とす、で章のトーンを分ける。
実行: PYTHONPATH=. python3 scripts/gen_dai_bgs.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402


def _shelf(d, x0, y0, x1, y1, tiers=3, col=(206, 190, 168), goods=True):
    """商店の棚。tiers 段ぶんの棚板と、載っている商品。"""
    d.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=col)
    d.rectangle([x0, y0, x1, y0 + 26], fill=tuple(max(0, c - 24) for c in col))
    step = (y1 - y0 - 40) / tiers
    for r in range(tiers):
        ty = y0 + 40 + step * r
        d.rectangle([x0 + 10, ty, x1 - 10, ty + 10],
                    fill=tuple(max(0, c - 34) for c in col))
        if not goods:
            continue
        for j in range(int((x1 - x0 - 40) // 62)):
            gx = x0 + 24 + j * 62
            hue = (r * 3 + j) % 5
            gc = [(196, 84, 70), (70, 120, 176), (222, 178, 70),
                  (96, 158, 104), (168, 110, 168)][hue]
            d.rounded_rectangle([gx, ty - 40, gx + 44, ty], radius=4, fill=gc)


def _price_tag(d, x, y, w=110, h=58, red=True):
    """手書きの値札（赤札）。数字は描かず、線で雰囲気だけ出す。"""
    body = (222, 62, 52) if red else (250, 248, 240)
    ink = (252, 250, 244) if red else (200, 60, 50)
    d.polygon([(x, y), (x + w, y - 8), (x + w, y + h - 8), (x, y + h)], fill=body)
    for k in range(2):
        d.rectangle([x + 16, y + 14 + k * 18, x + w - 20, y + 22 + k * 18], fill=ink)


# ---------------------------------------------------------------- 戦前・戦中
def kobe1930() -> Image.Image:
    """1930年代の神戸の家。裸電球の下のちゃぶ台。すき焼きの記憶の場面。"""
    img = vgrad((W, H), (74, 62, 52), (48, 40, 34)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 760, (128, 104, 74), (104, 84, 60))
    # 障子
    d.rectangle([120, 150, 780, 720], fill=(214, 202, 176))
    for c in range(4):
        d.line([120 + c * 165, 150, 120 + c * 165, 720], fill=(150, 130, 100), width=8)
    for r in range(5):
        d.line([120, 150 + r * 114, 780, 150 + r * 114], fill=(150, 130, 100), width=8)
    # 裸電球
    d.line([1180, 0, 1180, 300], fill=(60, 52, 44), width=6)
    d.ellipse([1140, 300, 1220, 380], fill=(255, 236, 170))
    glow(img, 1180, 340, 620, (255, 220, 140), 92)
    d = ImageDraw.Draw(img, "RGBA")
    # ちゃぶ台と鉄鍋
    d.ellipse([880, 700, 1480, 900], fill=(150, 110, 70), outline=(120, 88, 56), width=8)
    d.ellipse([1040, 720, 1320, 830], fill=(58, 54, 54), outline=(38, 36, 36), width=7)
    d.ellipse([1070, 736, 1290, 812], fill=(150, 96, 60))
    for k in range(5):
        d.ellipse([1100 + k * 34, 748 + (k % 2) * 22, 1140 + k * 34, 776 + (k % 2) * 22],
                  fill=(196, 130, 88))
    return img


def senjo() -> Image.Image:
    """ルソン島。夜のジャングルと遠い砲火。ミーム禁止の章で使う。

    真っ黒にすると立ち絵しか見えない画になるので、月明かりで空だけ起こし、
    木と土嚢はシルエットで抜く。暗さは彩度で出して、明度では出さない。
    """
    img = vgrad((W, H), (58, 74, 92), (26, 34, 44)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 月
    d.ellipse([1500, 90, 1620, 210], fill=(226, 232, 236))
    glow(img, 1560, 150, 520, (200, 216, 236), 60)
    # 遠い砲火（地平線の向こう）
    glow(img, 380, 560, 620, (240, 140, 60), 96)
    glow(img, 1180, 590, 420, (240, 160, 70), 66)
    d = ImageDraw.Draw(img, "RGBA")
    # 遠景の山
    d.polygon([(0, 620), (420, 470), (900, 600), (1400, 480), (W, 590), (W, 780), (0, 780)],
              fill=(34, 44, 50))
    _floor(d, 760, (30, 38, 34), (24, 30, 28))
    # ヤシの木（シルエット）
    for x, hgt in ((180, 500), (640, 400), (1280, 450), (1720, 370)):
        d.line([x, 770, x - 30, 770 - hgt], fill=(20, 26, 26), width=22)
        for a in range(-80, 81, 32):
            ex = x - 30 + math.cos(math.radians(a - 90)) * 210
            ey = 770 - hgt + math.sin(math.radians(a - 90)) * 130
            d.line([x - 30, 770 - hgt, ex, ey], fill=(18, 24, 24), width=15)
    # 手前の土嚢
    for k in range(7):
        bx = 60 + k * 270
        for r in range(2):
            for c in range(3 - r):
                d.ellipse([bx + c * 74 + r * 37, 880 - r * 52,
                           bx + c * 74 + r * 37 + 88, 936 - r * 52],
                          fill=(46, 44, 38), outline=(34, 32, 28), width=4)
    return img


def yakeato() -> Image.Image:
    """1945年の焼け跡。外壁が焼け落ちて柱と梁だけが残ったビル。

    窓のある建物を描くと普通の街に見えてしまうので、**外壁を描かない**。
    残った骨組みの向こうに空が透けるのが焼け跡の絵になる。
    """
    img = vgrad((W, H), (198, 182, 162), (172, 158, 142)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 740, (150, 136, 120), (128, 116, 102))
    for x, hgt, w_, cols in ((110, 400, 320, 3), (640, 300, 260, 2), (1240, 460, 380, 4)):
        top = 740 - hgt
        burn = (86, 78, 72)
        # 柱
        for c in range(cols + 1):
            px = x + c * (w_ / cols)
            d.rectangle([px - 11, top, px + 11, 740], fill=burn)
        # 梁（床のスラブ）
        for r in range(3):
            ry = top + r * (hgt / 3)
            d.rectangle([x - 14, ry, x + w_ + 14, ry + 16], fill=burn)
        # 折れた梁を1本
        d.line([x + w_ * 0.3, top + 12, x + w_ * 0.75, top + hgt * 0.42],
               fill=burn, width=14)
    # 手前の瓦礫の山
    for k in range(40):
        bx = 30 + (k * 149) % (W - 60)
        by = 770 + (k * 71) % 230
        sz = 26 + (k * 37) % 44
        d.polygon([(bx, by), (bx + sz, by - sz * 0.4), (bx + sz * 1.3, by + sz * 0.5),
                   (bx + sz * 0.2, by + sz * 0.6)],
                  fill=(124, 112, 100) if k % 3 else (104, 94, 86))
    # 焼け残った電柱
    d.line([1720, 760, 1706, 300], fill=(78, 70, 64), width=16)
    d.line([1620, 372, 1800, 344], fill=(78, 70, 64), width=8)
    return img


def yamiichi() -> Image.Image:
    """闇市。板とむしろの露店が並ぶ。"""
    img = vgrad((W, H), (196, 176, 146), (162, 144, 120)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 780, (138, 118, 92), (114, 98, 76))
    for k, x in enumerate((60, 520, 980, 1440)):
        d.polygon([(x, 300), (x + 400, 260), (x + 400, 320), (x, 360)],
                  fill=(150, 130, 100))
        d.line([x + 20, 360, x + 20, 780], fill=(120, 100, 76), width=12)
        d.line([x + 370, 320, x + 370, 780], fill=(120, 100, 76), width=12)
        d.rounded_rectangle([x + 10, 620, x + 390, 700], radius=4, fill=(160, 138, 106))
        for j in range(4):
            d.rounded_rectangle([x + 40 + j * 86, 566, x + 100 + j * 86, 622],
                                radius=6, fill=[(190, 92, 74), (86, 132, 176),
                                                (214, 176, 84), (110, 158, 112)][j])
    return img


# ---------------------------------------------------------------- 店の時代
def senbayashi() -> Image.Image:
    """1957年、千林商店街の1号店。狭い間口に商品を積み上げた店先。"""
    img = vgrad((W, H), (214, 198, 172), (186, 170, 146)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 790, (152, 132, 106), (128, 110, 88))
    # アーケードの梁
    d.rectangle([0, 60, W, 130], fill=(150, 134, 110))
    for k in range(0, W, 180):
        d.rectangle([k, 130, k + 40, 200], fill=(132, 116, 94))
    # 店の間口
    d.rectangle([260, 200, 1180, 790], fill=(226, 214, 190))
    d.rectangle([260, 200, 1180, 280], fill=(196, 62, 52))
    for k in range(4):
        d.rectangle([330 + k * 200, 218, 420 + k * 200, 262], fill=(250, 246, 236))
    _shelf(d, 300, 380, 700, 790, tiers=3)
    _shelf(d, 740, 380, 1140, 790, tiers=3)
    _price_tag(d, 470, 300)
    _price_tag(d, 900, 300)
    # 隣の店
    d.rectangle([1260, 240, 1860, 790], fill=(206, 192, 168))
    d.rectangle([1260, 240, 1860, 300], fill=(74, 108, 150))
    return img


def seinikuuriba() -> Image.Image:
    """精肉売り場。ガラスケースと、赤札。牛肉39円の場面。"""
    img = vgrad((W, H), (232, 226, 214), (206, 200, 188)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 800, (176, 170, 162), (152, 146, 138))
    # 天井の蛍光灯
    for k in range(4):
        d.rounded_rectangle([200 + k * 420, 80, 500 + k * 420, 116], radius=8,
                            fill=(250, 250, 244))
        glow(img, 350 + k * 420, 100, 300, (255, 255, 230), 40)
    d = ImageDraw.Draw(img, "RGBA")
    # 冷蔵ケース
    d.rounded_rectangle([180, 520, 1740, 810], radius=10, fill=(200, 206, 212))
    d.rectangle([180, 520, 1740, 560], fill=(176, 184, 192))
    d.rounded_rectangle([210, 570, 1710, 700], radius=6, fill=(230, 238, 244))
    for k in range(9):
        gx = 250 + k * 160
        d.rounded_rectangle([gx, 600, gx + 120, 680], radius=8, fill=(196, 72, 66))
        d.rounded_rectangle([gx + 14, 612, gx + 106, 640], radius=6, fill=(228, 170, 158))
    for x in (330, 780, 1230, 1560):
        _price_tag(d, x, 430)
    return img


def honbu() -> Image.Image:
    """ダイエー本部の会議室。全国の店舗地図と、売上のグラフ。"""
    img = vgrad((W, H), (198, 194, 186), (170, 166, 160)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 750, (146, 140, 134), (124, 118, 112))
    # 日本地図のパネル（形は描かず、点の分布で示す）
    d.rounded_rectangle([120, 150, 760, 620], radius=8, fill=(226, 222, 212),
                        outline=(150, 144, 136), width=8)
    for k in range(34):
        x = 200 + (k * 91) % 500
        y = 220 + (k * 137) % 340
        d.ellipse([x, y, x + 16, y + 16], fill=(200, 62, 52))
    # 右肩上がりのグラフ
    d.rounded_rectangle([1080, 150, 1800, 620], radius=8, fill=(232, 230, 224),
                        outline=(150, 144, 136), width=8)
    pts = [(1130 + i * 100, 560 - i * 62) for i in range(7)]
    d.line(pts, fill=(60, 120, 180), width=10)
    for x, y in pts:
        d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(60, 120, 180))
    d.rounded_rectangle([200, 780, 1720, 900], radius=8, fill=(140, 124, 100))
    return img


def kaden() -> Image.Image:
    """家電売り場。テレビが並び、値引きの札が下がる。松下との対立の章。"""
    img = vgrad((W, H), (218, 214, 206), (192, 188, 180)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 790, (168, 162, 154), (144, 138, 130))
    _shelf(d, 120, 300, 860, 790, tiers=2, col=(196, 192, 184), goods=False)
    _shelf(d, 1020, 300, 1780, 790, tiers=2, col=(196, 192, 184), goods=False)
    for gx in (160, 470, 1060, 1370):
        for gy in (360, 600):
            d.rounded_rectangle([gx, gy, gx + 250, gy + 160], radius=10, fill=(66, 66, 72))
            d.rounded_rectangle([gx + 16, gy + 16, gx + 234, gy + 132], radius=6,
                                fill=(118, 140, 150))
    for x in (300, 620, 1200, 1520):
        _price_tag(d, x, 240, 130, 66)
    return img


def dome() -> Image.Image:
    """1988年、球場。ナイターの照明とスタンド。拡大の狂騒の章。"""
    img = vgrad((W, H), (28, 40, 66), (16, 24, 44)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 芝
    d.ellipse([-400, 700, W + 400, 1500], fill=(46, 104, 60))
    d.ellipse([600, 780, 1320, 1080], fill=(140, 100, 66))
    # スタンド
    d.polygon([(0, 700), (W, 700), (W, 420), (0, 420)], fill=(46, 52, 74))
    for r in range(5):
        for c in range(0, W, 26):
            d.rectangle([c, 440 + r * 50, c + 16, 470 + r * 50],
                        fill=(200, 190, 170) if (c // 26 + r) % 3 else (180, 90, 80))
    # 照明塔
    for x in (240, 1680):
        d.line([x, 420, x, 120], fill=(90, 96, 110), width=16)
        d.rounded_rectangle([x - 120, 60, x + 120, 140], radius=10, fill=(120, 128, 144))
        for k in range(5):
            d.ellipse([x - 100 + k * 44, 78, x - 72 + k * 44, 106], fill=(255, 250, 210))
        glow(img, x, 100, 640, (255, 244, 190), 62)
    return img


def shinsai() -> Image.Image:
    """1995年、被災した街。倒れたビルと、灯りのついた1軒。ミーム禁止の章。"""
    img = vgrad((W, H), (72, 70, 76), (46, 44, 50)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 780, (86, 82, 80), (68, 64, 62))
    # 傾いたビル
    d.polygon([(120, 780), (480, 780), (540, 260), (200, 200)], fill=(96, 92, 92))
    d.polygon([(1400, 780), (1760, 780), (1740, 300), (1380, 340)], fill=(90, 86, 88))
    for bx, by in ((240, 300), (1440, 380)):
        for r in range(4):
            for c in range(3):
                d.rectangle([bx + c * 90, by + r * 100, bx + 52 + c * 90, by + 66 + r * 100],
                            fill=(56, 54, 56))
    # 灯りのついた店
    d.rounded_rectangle([700, 480, 1180, 790], radius=8, fill=(150, 142, 132))
    d.rectangle([740, 540, 1140, 720], fill=(255, 238, 180))
    glow(img, 940, 630, 620, (255, 232, 160), 78)
    d = ImageDraw.Draw(img, "RGBA")
    # 瓦礫
    for k in range(20):
        x = 40 + (k * 173) % (W - 80)
        y = 800 + (k * 61) % 200
        d.polygon([(x, y), (x + 46, y - 14), (x + 60, y + 16), (x + 10, y + 22)],
                  fill=(78, 74, 74))
    return img


# ---------------------------------------------------------------- 転落
def gara_ten() -> Image.Image:
    """客の減った店内。棚に隙間があり、照明が半分落ちている。"""
    img = vgrad((W, H), (176, 174, 172), (146, 144, 144)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 800, (150, 146, 142), (128, 124, 120))
    for k in range(4):
        on = k % 2 == 0
        d.rounded_rectangle([200 + k * 420, 80, 500 + k * 420, 116], radius=8,
                            fill=(240, 240, 232) if on else (150, 150, 146))
        if on:
            glow(img, 350 + k * 420, 100, 260, (255, 255, 230), 26)
    d = ImageDraw.Draw(img, "RGBA")
    # 歯抜けの棚
    for x in (120, 700, 1280):
        d.rounded_rectangle([x, 340, x + 500, 800], radius=6, fill=(198, 194, 186))
        d.rectangle([x, 340, x + 500, 366], fill=(176, 172, 164))
        for r in range(3):
            ty = 400 + r * 132
            d.rectangle([x + 10, ty, x + 490, ty + 10], fill=(168, 164, 156))
            for j in range(7):
                if (r * 7 + j + x // 100) % 3 == 0:
                    continue
                gx = x + 24 + j * 66
                d.rounded_rectangle([gx, ty - 44, gx + 46, ty], radius=4,
                                    fill=(178, 172, 166))
    return img


def kaigi_kurai() -> Image.Image:
    """暗い役員会議室。銀行の資料が積まれた長机。"""
    img = vgrad((W, H), (72, 74, 84), (46, 48, 58)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 760, (62, 60, 68), (50, 48, 54))
    _window(img, d, 1240, 160, 1820, 520, (60, 70, 96), (96, 106, 130))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([160, 770, 1560, 900], radius=8, fill=(78, 64, 54))
    d.rectangle([160, 770, 1560, 806], fill=(64, 52, 44))
    for k in range(5):
        d.rounded_rectangle([260 + k * 260, 690, 420 + k * 260, 776], radius=4,
                            fill=(220, 216, 208), outline=(160, 156, 150), width=3)
    d.rounded_rectangle([120, 200, 700, 560], radius=6, fill=(58, 60, 70),
                        outline=(90, 92, 104), width=8)
    pts = [(180 + i * 90, 300 + i * 36) for i in range(6)]
    d.line(pts, fill=(210, 90, 80), width=9)
    return img


def sobo() -> Image.Image:
    """夜の病室の窓辺。静かな場面（晩年・逝去）。ミーム禁止の章。"""
    img = vgrad((W, H), (52, 56, 68), (34, 36, 46)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 790, (64, 62, 66), (52, 50, 54))
    _window(img, d, 1100, 180, 1780, 640, (26, 32, 52), (58, 66, 92))
    d = ImageDraw.Draw(img, "RGBA")
    for k in range(26):
        x = 1140 + (k * 211) % 600      # 素数の歩幅にしないと点が斜めに並んで線に見える
        y = 220 + (k * 157) % 380
        d.ellipse([x, y, x + 7, y + 7], fill=(240, 236, 200))
    d.rounded_rectangle([180, 640, 860, 900], radius=10, fill=(226, 222, 214))
    d.rounded_rectangle([180, 600, 860, 660], radius=10, fill=(206, 202, 194))
    d.rounded_rectangle([920, 700, 1060, 900], radius=8, fill=(150, 146, 142))
    d.ellipse([950, 640, 1030, 706], fill=(200, 196, 190))
    return img


def ima_super() -> Image.Image:
    """現代のスーパー。明るい売り場。冒頭と締めで使う。"""
    img = vgrad((W, H), (238, 238, 234), (214, 214, 210)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 810, (196, 194, 190), (172, 170, 166))
    for k in range(5):
        d.rounded_rectangle([120 + k * 360, 70, 400 + k * 360, 104], radius=8,
                            fill=(252, 252, 248))
        glow(img, 260 + k * 360, 88, 300, (255, 255, 240), 34)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([100, 500, 820, 812], radius=10, fill=(206, 212, 218))
    d.rounded_rectangle([130, 546, 790, 690], radius=6, fill=(234, 240, 246))
    for k in range(5):
        gx = 170 + k * 122
        d.rounded_rectangle([gx, 578, gx + 84, 652], radius=8, fill=(198, 74, 68))
    _shelf(d, 1080, 380, 1840, 812, tiers=3, col=(224, 220, 212))
    for x in (300, 640, 1300, 1620):
        d.rounded_rectangle([x, 430, x + 96, 476], radius=6, fill=(250, 226, 60))
    return img


PAINTERS = {
    "il_dai_kobe1930": kobe1930,
    "il_dai_senjo": senjo,
    "il_dai_yakeato": yakeato,
    "il_dai_yamiichi": yamiichi,
    "il_dai_senbayashi": senbayashi,
    "il_dai_seiniku": seinikuuriba,
    "il_dai_honbu": honbu,
    "il_dai_kaden": kaden,
    "il_dai_dome": dome,
    "il_dai_shinsai": shinsai,
    "il_dai_garaten": gara_ten,
    "il_dai_kaigi": kaigi_kurai,
    "il_dai_sobo": sobo,
    "il_dai_ima": ima_super,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
