#!/usr/bin/env python3
"""乾電池の誕生（yai-denchi）用のイラスト背景7種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
実行: PYTHONPATH=. python3 scripts/gen_yi_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402


def _rgba(img):
    return img.convert("RGBA")


def _snow(d, n=90, seed=4):
    import random
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H * 0.8)
        r = rnd.uniform(2, 6)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(240, 244, 252, 200))


def nagaoka() -> Image.Image:
    """雪の越後長岡（武家の町並み）。"""
    img = _rgba(vgrad((W, H), (146, 164, 196), (206, 216, 232)))
    d = ImageDraw.Draw(img)
    # 遠景の山
    d.polygon([(0, 560), (300, 330), (620, 560)], fill=(150, 160, 186))
    d.polygon([(420, 560), (760, 300), (1120, 560)], fill=(136, 148, 176))
    d.polygon([(1000, 560), (1400, 350), (1920, 560)], fill=(150, 160, 186))
    # 家並み（雪の乗った屋根）
    for x0, w_ in [(60, 320), (420, 280), (760, 340), (1160, 300), (1520, 340)]:
        d.rectangle([x0, 560, x0 + w_, 800], fill=(92, 74, 62))
        d.polygon([(x0 - 26, 560), (x0 + w_ // 2, 452), (x0 + w_ + 26, 560)],
                  fill=(64, 52, 46))
        d.polygon([(x0 - 26, 560), (x0 + w_ // 2, 452), (x0 + w_ + 26, 560)],
                  fill=(238, 242, 250), outline=(200, 208, 222))
        for wx in range(x0 + 40, x0 + w_ - 40, 110):
            d.rectangle([wx, 620, wx + 60, 690], fill=(240, 206, 120))
    # 雪の地面
    d.rectangle([0, 800, W, H], fill=(236, 240, 248))
    d.ellipse([-200, 780, 700, 900], fill=(226, 232, 242))
    d.ellipse([1200, 790, 2100, 900], fill=(226, 232, 242))
    _snow(d)
    return img


def tokeiten() -> Image.Image:
    """明治の時計店の作業場。"""
    img = _rgba(vgrad((W, H), (74, 58, 44), (46, 36, 28)))
    d = ImageDraw.Draw(img)
    # 壁の柱時計
    for cx in (300, 560):
        d.rounded_rectangle([cx - 70, 150, cx + 70, 560], radius=14, fill=(96, 70, 50),
                            outline=(58, 42, 30), width=7)
        d.ellipse([cx - 52, 190, cx + 52, 294], fill=(246, 240, 226),
                  outline=(58, 42, 30), width=6)
        d.line([(cx, 242), (cx, 208)], fill=(50, 40, 34), width=6)
        d.line([(cx, 242), (cx + 26, 254)], fill=(50, 40, 34), width=5)
        d.line([(cx, 320), (cx, 470)], fill=(140, 120, 80), width=5)
        d.ellipse([cx - 30, 470, cx + 30, 530], fill=(200, 170, 90))
    # 窓
    d.rectangle([1320, 160, 1800, 470], fill=(150, 176, 200))
    d.rectangle([1550, 160, 1570, 470], fill=(70, 56, 44))
    d.rectangle([1320, 305, 1800, 325], fill=(70, 56, 44))
    # 作業台と工具
    d.rectangle([0, 720, W, H], fill=(104, 78, 54))
    d.rectangle([0, 700, W, 730], fill=(124, 94, 66))
    for x in range(160, 1800, 220):
        d.rectangle([x, 640, x + 90, 700], fill=(58, 46, 38))
        d.ellipse([x + 110, 656, x + 170, 700], fill=(180, 170, 140))
    # 吊りランプ
    d.line([(960, 0), (960, 120)], fill=(60, 48, 38), width=6)
    d.ellipse([916, 120, 1004, 196], fill=(255, 216, 130))
    glow(img, 960, 160, 220, (255, 208, 120), alpha=64)
    return img


def school() -> Image.Image:
    """明治の学校の門（受験の場面）。"""
    img = _rgba(vgrad((W, H), (188, 196, 214), (150, 158, 178)))
    d = ImageDraw.Draw(img)
    # 校舎
    d.rectangle([260, 250, 1660, 700], fill=(206, 198, 182))
    d.polygon([(220, 250), (960, 130), (1700, 250)], fill=(128, 96, 78))
    for wx in range(320, 1600, 160):
        d.rectangle([wx, 330, wx + 90, 450], fill=(96, 112, 136),
                    outline=(70, 62, 54), width=5)
        d.rectangle([wx, 500, wx + 90, 620], fill=(96, 112, 136),
                    outline=(70, 62, 54), width=5)
    # 門柱と門扉
    for x in (420, 1480):
        d.rectangle([x - 40, 520, x + 40, 900], fill=(120, 116, 108),
                    outline=(78, 74, 68), width=6)
        d.rectangle([x - 52, 496, x + 52, 528], fill=(96, 92, 86))
    for gx in range(480, 1440, 60):
        d.rectangle([gx, 580, gx + 14, 890], fill=(66, 70, 78))
    d.rectangle([420, 570, 1480, 592], fill=(66, 70, 78))
    # 地面
    d.rectangle([0, 890, W, H], fill=(120, 116, 106))
    d.rectangle([0, 890, W, 906], fill=(96, 92, 84))
    return img


def room() -> Image.Image:
    """下宿の一室（現代の茶番にも使う中立的な部屋）。"""
    img = _rgba(vgrad((W, H), (86, 74, 66), (58, 48, 44)))
    d = ImageDraw.Draw(img)
    # 障子
    d.rectangle([120, 120, 900, 640], fill=(228, 224, 210))
    for x in range(120, 901, 130):
        d.rectangle([x, 120, x + 12, 640], fill=(120, 100, 78))
    for y in range(120, 641, 130):
        d.rectangle([120, y, 900, y + 12], fill=(120, 100, 78))
    # 棚と本
    d.rectangle([1180, 200, 1820, 620], fill=(96, 74, 56))
    for y in (330, 470):
        d.rectangle([1180, y, 1820, y + 16], fill=(70, 54, 40))
    for i, x in enumerate(range(1220, 1780, 46)):
        col = [(180, 90, 70), (90, 120, 150), (150, 140, 90), (120, 90, 130)][i % 4]
        d.rectangle([x, 236, x + 34, 330], fill=col)
    # 畳
    d.rectangle([0, 760, W, H], fill=(158, 150, 108))
    for x in range(0, W, 320):
        d.line([(x, 760), (x, H)], fill=(142, 134, 96), width=5)
    d.rectangle([0, 745, W, 772], fill=(120, 112, 82))
    # 机とランプ
    d.rectangle([680, 640, 1240, 780], fill=(110, 82, 58))
    d.ellipse([760, 600, 860, 656], fill=(250, 220, 140))
    glow(img, 810, 630, 190, (255, 210, 130), alpha=60)
    return img


def koba() -> Image.Image:
    """屋井の作業場（試作の山）。"""
    img = _rgba(vgrad((W, H), (62, 56, 50), (38, 34, 32)))
    d = ImageDraw.Draw(img)
    # 棚に並ぶ試作の電池
    d.rectangle([80, 180, 720, 660], fill=(84, 66, 52))
    for y in (300, 430, 560):
        d.rectangle([80, y, 720, y + 14], fill=(62, 48, 38))
        for x in range(120, 680, 76):
            d.rounded_rectangle([x, y - 82, x + 46, y], radius=6,
                                fill=(150, 156, 168), outline=(90, 96, 108), width=4)
            d.rectangle([x + 14, y - 92, x + 32, y - 82], fill=(200, 170, 90))
    # 窓
    d.rectangle([1360, 150, 1820, 470], fill=(38, 48, 70))
    d.rectangle([1580, 150, 1600, 470], fill=(72, 62, 52))
    d.rectangle([1360, 300, 1820, 320], fill=(72, 62, 52))
    d.ellipse([1660, 200, 1720, 260], fill=(240, 236, 200))
    # 作業台
    d.rectangle([0, 780, W, H], fill=(96, 72, 50))
    d.rectangle([0, 758, W, 790], fill=(116, 88, 62))
    # 台上: 電池・工具・配線
    d.rounded_rectangle([820, 620, 940, 780], radius=8, fill=(150, 156, 168),
                        outline=(80, 86, 98), width=6)
    d.rectangle([856, 596, 904, 622], fill=(200, 170, 90))
    d.line([(960, 740), (1140, 690)], fill=(190, 80, 60), width=8)
    d.line([(1140, 690), (1240, 760)], fill=(60, 90, 160), width=8)
    d.rectangle([1280, 700, 1420, 770], fill=(120, 110, 90))
    # 吊り電球
    d.line([(560, 0), (560, 140)], fill=(60, 52, 44), width=6)
    d.ellipse([524, 140, 596, 206], fill=(255, 218, 136))
    glow(img, 560, 174, 210, (255, 210, 120), alpha=62)
    return img


def manshu() -> Image.Image:
    """極寒の満洲（電信所の外）。"""
    img = _rgba(vgrad((W, H), (58, 74, 104), (128, 146, 176)))
    d = ImageDraw.Draw(img)
    # 地平と雪原
    d.rectangle([0, 620, W, H], fill=(226, 232, 244))
    d.ellipse([-300, 590, 900, 700], fill=(212, 220, 236))
    d.ellipse([1100, 600, 2200, 710], fill=(212, 220, 236))
    # 電信柱
    for x in (300, 760, 1220, 1680):
        d.rectangle([x - 12, 300, x + 12, 640], fill=(74, 62, 54))
        d.rectangle([x - 70, 340, x + 70, 356], fill=(74, 62, 54))
        d.rectangle([x - 56, 396, x + 56, 410], fill=(74, 62, 54))
    for x0, x1 in [(300, 760), (760, 1220), (1220, 1680)]:
        d.line([(x0, 352), (x1, 372)], fill=(50, 44, 40), width=4)
        d.line([(x0, 406), (x1, 424)], fill=(50, 44, 40), width=4)
    # 兵舎のような小屋
    d.rectangle([1380, 430, 1860, 630], fill=(88, 78, 68))
    d.polygon([(1350, 430), (1620, 350), (1890, 430)], fill=(232, 238, 248))
    d.rectangle([1470, 500, 1560, 630], fill=(56, 48, 42))
    _snow(d, n=140, seed=11)
    return img


def kojo() -> Image.Image:
    """大正期の乾電池工場。"""
    img = _rgba(vgrad((W, H), (96, 100, 112), (62, 66, 76)))
    d = ImageDraw.Draw(img)
    # ノコギリ屋根
    for i in range(6):
        x0 = i * 340 - 60
        d.polygon([(x0, 300), (x0 + 170, 150), (x0 + 170, 300)], fill=(84, 88, 100))
        d.polygon([(x0 + 170, 150), (x0 + 200, 150), (x0 + 200, 300)], fill=(150, 176, 200))
    d.rectangle([0, 300, W, 330], fill=(70, 74, 86))
    # 壁と窓
    d.rectangle([0, 330, W, 720], fill=(112, 108, 100))
    for wx in range(80, 1860, 200):
        d.rectangle([wx, 380, wx + 120, 520], fill=(140, 164, 186),
                    outline=(80, 76, 70), width=5)
    # 作業台とベルト
    d.rectangle([0, 760, W, H], fill=(92, 84, 72))
    d.rectangle([0, 720, W, 770], fill=(74, 78, 90))
    for x in range(60, 1900, 130):
        d.rounded_rectangle([x, 640, x + 60, 760], radius=8, fill=(160, 166, 178),
                            outline=(96, 102, 114), width=5)
        d.rectangle([x + 18, 620, x + 42, 642], fill=(210, 180, 90))
    return img


def gendai() -> Image.Image:
    """現代の部屋（乾電池が転がる机）。"""
    img = _rgba(vgrad((W, H), (48, 52, 70), (30, 34, 48)))
    d = ImageDraw.Draw(img)
    # 窓の夜景
    d.rectangle([1240, 140, 1840, 520], fill=(22, 28, 48))
    for bx, bh in [(1280, 120), (1360, 180), (1450, 90), (1560, 160), (1680, 130), (1780, 190)]:
        d.rectangle([bx, 520 - bh, bx + 60, 520], fill=(38, 46, 72))
        for wy in range(520 - bh + 14, 512, 30):
            d.rectangle([bx + 10, wy, bx + 26, wy + 14], fill=(240, 214, 140))
    d.rectangle([1230, 130, 1850, 150], fill=(70, 76, 96))
    # 壁の時計
    d.ellipse([300, 180, 470, 350], fill=(240, 242, 248), outline=(70, 76, 92), width=8)
    d.line([(385, 265), (385, 210)], fill=(50, 54, 66), width=7)
    d.line([(385, 265), (430, 285)], fill=(50, 54, 66), width=6)
    # 机
    d.rectangle([0, 760, W, H], fill=(96, 74, 56))
    d.rectangle([0, 736, W, 772], fill=(116, 90, 66))
    # 乾電池が2本とリモコン
    for x in (620, 700):
        d.rounded_rectangle([x, 640, x + 54, 760], radius=8, fill=(200, 170, 70),
                            outline=(120, 96, 40), width=5)
        d.rectangle([x + 16, 622, x + 38, 644], fill=(180, 184, 196))
        d.rectangle([x + 6, 690, x + 48, 710], fill=(60, 56, 50))
    d.rounded_rectangle([900, 690, 1120, 770], radius=14, fill=(46, 50, 62),
                        outline=(90, 96, 110), width=5)
    for ry in (706, 736):
        for rx in range(930, 1090, 46):
            d.ellipse([rx, ry, rx + 24, ry + 20], fill=(120, 126, 140))
    return img


PAINTERS = {
    "il_yi_nagaoka": nagaoka,
    "il_yi_tokeiten": tokeiten,
    "il_yi_school": school,
    "il_yi_room": room,
    "il_yi_koba": koba,
    "il_yi_manshu": manshu,
    "il_yi_kojo": kojo,
    "il_yi_gendai": gendai,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
