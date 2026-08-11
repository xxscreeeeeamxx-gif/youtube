#!/usr/bin/env python3
"""自動改札機の誕生（kaisatsu-drama）用のイラスト背景6種。

実行: PYTHONPATH=. python3 scripts/gen_kg_bgs.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from PIL import Image, ImageDraw  # noqa: E402
from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402


def _rgba(img):
    return img.convert("RGBA")


def station() -> Image.Image:
    """1960年代の駅の改札口（ラッシュ）。"""
    img = _rgba(vgrad((W, H), (128, 118, 104), (92, 84, 74)))
    d = ImageDraw.Draw(img)
    # 天井の梁とランプ
    d.rectangle([0, 0, W, 120], fill=(84, 76, 66))
    for x in range(120, W, 300):
        d.ellipse([x, 96, x + 70, 150], fill=(250, 226, 150))
        glow(img, x + 35, 124, 190, (255, 220, 140), alpha=48)
    d = ImageDraw.Draw(img)
    # 改札のラッチ（木の柵）
    for x in range(80, W, 260):
        d.rectangle([x, 430, x + 26, 760], fill=(112, 84, 58))
        d.rectangle([x - 60, 430, x + 86, 462], fill=(130, 98, 66))
    # 案内板
    d.rectangle([700, 150, 1240, 280], fill=(40, 60, 90), outline=(180, 186, 200), width=7)
    for i, y in enumerate((186, 232)):
        d.rectangle([740, y, 1100 - i * 140, y + 26], fill=(220, 226, 238))
    # 床
    d.rectangle([0, 760, W, H], fill=(120, 112, 100))
    for x in range(0, W, 180):
        d.line([(x, 760), (x - 60, H)], fill=(106, 98, 88), width=4)
    return img


def umeda() -> Image.Image:
    """大きなターミナル駅の改札（張り込みの場面）。"""
    img = _rgba(vgrad((W, H), (146, 136, 120), (104, 96, 84)))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 150], fill=(92, 84, 74))
    for x in range(90, W, 240):
        d.rectangle([x, 150, x + 40, 186], fill=(70, 64, 56))
        d.ellipse([x - 10, 120, x + 50, 164], fill=(252, 232, 160))
    # 改札の列（奥行き）
    for i, x in enumerate(range(60, W, 220)):
        h0 = 470 + i * 6
        d.rectangle([x, h0, x + 150, 780], fill=(150, 142, 128), outline=(96, 90, 80), width=6)
        d.rectangle([x + 20, h0 - 30, x + 130, h0], fill=(120, 112, 100))
    d.rectangle([0, 780, W, H], fill=(128, 120, 108))
    d.rectangle([0, 780, W, 800], fill=(108, 100, 90))
    return img


def office() -> Image.Image:
    """会議室（鉄道会社との打ち合わせ）。"""
    img = _rgba(vgrad((W, H), (108, 104, 96), (74, 72, 66)))
    d = ImageDraw.Draw(img)
    d.rectangle([120, 130, 780, 560], fill=(228, 224, 212), outline=(120, 116, 106), width=8)
    for gy in range(170, 540, 46):
        d.line([(150, gy), (750, gy)], fill=(196, 192, 182), width=3)
    d.rectangle([200, 200, 470, 300], outline=(60, 90, 150), width=6)
    d.rectangle([520, 240, 720, 420], outline=(160, 70, 60), width=6)
    d.rectangle([1200, 160, 1830, 500], fill=(150, 172, 194))
    d.rectangle([1510, 160, 1528, 500], fill=(88, 84, 76))
    d.rectangle([1200, 326, 1830, 344], fill=(88, 84, 76))
    d.rectangle([0, 740, W, H], fill=(96, 76, 56))
    d.rectangle([0, 716, W, 752], fill=(116, 94, 70))
    d.rectangle([700, 620, 1240, 740], fill=(120, 98, 72), outline=(84, 66, 48), width=6)
    d.rectangle([760, 596, 920, 624], fill=(242, 240, 232))
    return img


def lab() -> Image.Image:
    """試作の実験室（改札機の試作機）。"""
    img = _rgba(vgrad((W, H), (86, 92, 100), (58, 64, 72)))
    d = ImageDraw.Draw(img)
    # 棚と工具
    d.rectangle([80, 150, 640, 560], fill=(120, 116, 108), outline=(70, 68, 62), width=7)
    for y in (250, 360, 470):
        d.rectangle([80, y, 640, y + 14], fill=(88, 84, 78))
        for x in range(110, 600, 70):
            d.rectangle([x, y - 56, x + 46, y], fill=(160, 156, 148))
    # 試作の改札機（長い箱）
    d.rounded_rectangle([760, 480, 1780, 700], radius=16, fill=(178, 182, 194),
                        outline=(100, 104, 116), width=8)
    d.rectangle([820, 440, 900, 484], fill=(60, 64, 76))          # 投入口
    d.rectangle([1620, 440, 1700, 484], fill=(60, 64, 76))        # 取出口
    for x in range(900, 1620, 90):
        d.rectangle([x, 520, x + 40, 560], fill=(120, 126, 140))
    d.rectangle([0, 740, W, H], fill=(96, 92, 84))
    d.rectangle([0, 716, W, 752], fill=(116, 112, 102))
    return img


def univ() -> Image.Image:
    """大学の研究室（黒板に路線図とビット列）。"""
    img = _rgba(vgrad((W, H), (78, 88, 82), (52, 60, 56)))
    d = ImageDraw.Draw(img)
    d.rectangle([90, 120, 1400, 580], fill=(48, 62, 54), outline=(140, 132, 112), width=10)
    # 路線図もどき
    pts = [(220, 480), (400, 400), (620, 430), (820, 320), (1040, 380), (1240, 300)]
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=(200, 226, 210), width=6)
    for p in pts:
        d.ellipse([p[0] - 14, p[1] - 14, p[0] + 14, p[1] + 14], fill=(240, 244, 238))
    # ビット列
    for k, x in enumerate(range(240, 1300, 52)):
        d.rectangle([x, 200, x + 30, 236], outline=(210, 226, 214), width=4)
        if k % 3 == 0:
            d.rectangle([x + 6, 206, x + 24, 230], fill=(210, 226, 214))
    d.rectangle([1500, 150, 1840, 470], fill=(140, 164, 186))
    d.rectangle([1666, 150, 1682, 470], fill=(84, 80, 74))
    d.rectangle([0, 740, W, H], fill=(92, 74, 56))
    d.rectangle([0, 716, W, 752], fill=(112, 90, 68))
    return img


def kitasenri() -> Image.Image:
    """1967年の新設駅（工事中のニュータウン）。"""
    img = _rgba(vgrad((W, H), (168, 182, 206), (206, 214, 228)))
    d = ImageDraw.Draw(img)
    # 造成中の丘と団地
    d.polygon([(0, 520), (500, 420), (1000, 520)], fill=(158, 152, 134))
    d.polygon([(900, 520), (1500, 400), (1920, 520)], fill=(146, 140, 124))
    for x0 in (240, 620, 1160, 1520):
        d.rectangle([x0, 300, x0 + 220, 520], fill=(206, 202, 192), outline=(150, 146, 138), width=5)
        for wy in range(330, 500, 44):
            for wx in range(x0 + 20, x0 + 200, 52):
                d.rectangle([wx, wy, wx + 30, wy + 26], fill=(150, 168, 188))
    # 駅舎
    d.rectangle([420, 520, 1500, 780], fill=(228, 226, 218), outline=(140, 136, 128), width=8)
    d.polygon([(390, 520), (960, 440), (1530, 520)], fill=(120, 128, 140))
    # 改札機（横一列）
    for i, x in enumerate(range(560, 1380, 150)):
        d.rounded_rectangle([x, 640, x + 110, 764], radius=10, fill=(178, 182, 194),
                            outline=(110, 114, 126), width=6)
        d.rectangle([x + 14, 616, x + 54, 644], fill=(64, 68, 80))
    d.rectangle([0, 780, W, H], fill=(150, 144, 132))
    d.rectangle([0, 780, W, 800], fill=(128, 122, 112))
    return img


def now() -> Image.Image:
    """現代の駅の改札（ICカード）。"""
    img = _rgba(vgrad((W, H), (48, 58, 78), (30, 38, 54)))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 130], fill=(38, 46, 64))
    for x in range(160, W, 340):
        d.rounded_rectangle([x, 30, x + 190, 96], radius=10, fill=(60, 130, 180))
        d.rectangle([x + 20, 52, x + 170, 74], fill=(200, 224, 244))
    # 改札の列
    for i, x in enumerate(range(90, W, 260)):
        d.rounded_rectangle([x, 470, x + 170, 780], radius=14, fill=(196, 200, 212),
                            outline=(120, 124, 138), width=7)
        d.rounded_rectangle([x + 30, 430, x + 140, 478], radius=8, fill=(70, 76, 90))
        d.ellipse([x + 62, 500, x + 118, 552], fill=(90, 190, 240))   # タッチ面
        d.rectangle([x + 40, 600, x + 130, 620], fill=(120, 200, 150))
    d.rectangle([0, 780, W, H], fill=(70, 78, 96))
    for x in range(0, W, 200):
        d.line([(x, 780), (x - 70, H)], fill=(60, 68, 86), width=4)
    return img


PAINTERS = {
    "il_kg_station": station,
    "il_kg_umeda": umeda,
    "il_kg_office": office,
    "il_kg_lab": lab,
    "il_kg_univ": univ,
    "il_kg_kitasenri": kitasenri,
    "il_kg_now": now,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
