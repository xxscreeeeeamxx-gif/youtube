#!/usr/bin/env python3
"""traffic-light プロジェクト用のアニメクリップを生成する。

  color_ao.mp4    70.0s  「あお」の色域→1930緑色信号→1947改正→1973色寄せ→世界比較
  led_snow.mp4    64.5s  疑似点灯→LED化→熱の比較→雪張り付き→縦型化
  button_wait.mp4 17.6s  押しボタンの順番待ち（車流ゲージ→タイミングで青）
  era_1868.mp4    28.2s  ロンドンのガス信号→爆発の時代カード
  era_1930.mp4    21.0s  日比谷・日本初の時代カード

フェーズ境界は timing.json のカット実測に同期（コメントの秒数）。
実行: PYTHONPATH=. python3 scripts/gen_signal_extras.py [クリップ名...]
"""

import math
import random
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ytf.config import Config, ffmpeg_bin  # noqa: E402

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

W, H, FPS = 1920, 1080, 30
BG = (8, 12, 22)
INK = (235, 242, 252)
ACCENT = (58, 160, 255)
AMBER = (255, 190, 80)
GREEN = (86, 216, 148)
RED = (255, 100, 80)
GRAY = (150, 158, 175)
SIG_G = (60, 200, 150)   # 信号の緑（青寄り）
SIG_Y = (255, 200, 40)
SIG_R = (255, 80, 70)
BODY = (46, 56, 76)      # 信号機の筐体

_cfg = Config.load()
_font_path = _cfg.find_pillow_font()


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(_font_path, max(size, 8), index=0)


def ease(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def ctext(d, cx, y, s, f, fill):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


def _caption(d, s, col=INK):
    ctext(d, W / 2, 150, s, font(60), col)


def encode(frames: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error",
         "-framerate", str(FPS), "-i", str(frames / "%04d.png"),
         "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", str(out)],
        capture_output=True, text=True)
    for p in frames.glob("*.png"):
        p.unlink()
    frames.rmdir()
    if r.returncode != 0:
        raise SystemExit(f"エンコード失敗 {out.name}: {r.stderr[-400:]}")
    print(f"生成完了: {out}")


def render(name: str, dur: float, draw_frame) -> None:
    tmp = Path(tempfile.mkdtemp(prefix=f"tl_{name}_"))
    for fi in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw_frame(ImageDraw.Draw(img, "RGBA"), fi / FPS)
        img.save(tmp / f"{fi:04d}.png")
    encode(tmp, Path(f"assets/clips/{name}.mp4"))


def _signal3(d, cx, cy, on="G", s=1.0, vertical=False, snow=0.0):
    """3灯信号。on: R/Y/G/ALL/NONE。vertical=縦型。snow=着雪量0-1。"""
    r = int(58 * s)
    gap = int(150 * s)
    if vertical:
        d.rounded_rectangle([cx - r - 24, cy - gap - r - 24, cx + r + 24, cy + gap + r + 24],
                            radius=20, fill=BODY)
        centers = [(cx, cy - gap), (cx, cy), (cx, cy + gap)]
    else:
        d.rounded_rectangle([cx - gap - r - 24, cy - r - 24, cx + gap + r + 24, cy + r + 24],
                            radius=20, fill=BODY)
        centers = [(cx + gap, cy), (cx, cy), (cx - gap, cy)]  # 右から赤黄青
    cols = [SIG_R, SIG_Y, SIG_G]
    keys = ["R", "Y", "G"]
    for (px, py), col, k in zip(centers, cols, keys):
        lit = on == "ALL" or on == k
        cc = col if lit else tuple(int(c * 0.25) for c in col)
        d.ellipse([px - r, py - r, px + r, py + r], fill=cc)
        if lit:
            d.ellipse([px - r - 8, py - r - 8, px + r + 8, py + r + 8], outline=(*col, 90), width=6)
    if snow > 0:
        # 着雪（上に積もる）
        if vertical:
            d.ellipse([cx - r - 26, cy - gap - r - 40, cx + r + 26, cy - gap - r + 10 + 20 * snow],
                      fill=(240, 244, 250, int(240 * snow)))
        else:
            d.rounded_rectangle([cx - gap - r - 26, cy - r - 44, cx + gap + r + 26,
                                 cy - r - 44 + 34 * snow + 10], radius=14,
                                fill=(240, 244, 250, int(240 * snow)))


# ------------------------------------------------------------------
# 1) color_ao — 「あお」の物語
#    例=8.62 / 1930=17.47 / (Z=27.69) / 1947=31.88 / (Z=43.4) / 1973=47.98 / 世界=62.97 / DUR 70
# ------------------------------------------------------------------
A_EX, A_1930, A_1947, A_1973, A_WORLD = 8.62, 17.47, 31.88, 47.98, 68.81


def _spectrum(d, x0, x1, y, h):
    n = 160
    for i in range(n):
        t = i / (n - 1)
        # 青(230,H)→緑(120)のHSV風グラデーション
        hue = 230 - t * 130
        c = _hsv(hue, 0.75, 0.95)
        d.rectangle([x0 + (x1 - x0) * i / n, y, x0 + (x1 - x0) * (i + 1) / n, y + h], fill=c)


def _hsv(h, s, v):
    import colorsys
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


def color_ao(d, t):
    if t < A_1930:
        _caption(d, "昔の「あお」は、青も緑もカバーする言葉")
        _spectrum(d, 360, 1560, 430, 110)
        d.text((360, 560), "いまの「青」", font=font(34), fill=ACCENT)
        d.text((1330, 560), "いまの「緑」", font=font(34), fill=GREEN)
        k = ease(t / 1.2)
        # 「あを」ブラケット
        bx1 = 360 + (1560 - 360) * k
        d.line([360, 400, 360, 370], fill=AMBER, width=8)
        d.line([360, 370, bx1, 370], fill=AMBER, width=8)
        d.line([bx1, 370, bx1, 400], fill=AMBER, width=8)
        ctext(d, (360 + bx1) / 2, 300, "むかしの「あお」", font(44), AMBER)
        if t >= A_EX:
            for i, (s_, col) in enumerate((("青菜", GREEN), ("青竹", GREEN), ("青りんご", GREEN))):
                kk = ease((t - A_EX - i * 0.5) / 0.5)
                if kk <= 0:
                    continue
                x = 560 + i * 400
                d.rounded_rectangle([x - 150, 700, x + 150, 830], radius=18,
                                    fill=(24, 34, 54, int(255 * kk)))
                if kk > 0.6:
                    ctext(d, x, 720, s_, font(46), INK)
                    ctext(d, x, 786, "実際は緑", font(28), col)
        return
    if t < A_1947:
        _caption(d, "1930年 日比谷 = 法令名は「緑色信号」")
        _signal3(d, 700, 560, on="G")
        # 法令書類
        d.rounded_rectangle([1120, 380, 1680, 760], radius=14, fill=(240, 236, 224))
        ctext(d, 1400, 410, "法 令", font(40), (60, 56, 48))
        d.line([1180, 470, 1620, 470], fill=(120, 116, 104), width=3)
        ctext(d, 1400, 520, "緑色信号", font(64), (30, 90, 60))
        for yy in (620, 660, 700):
            d.line([1180, yy, 1620, yy], fill=(190, 186, 174), width=6)
        return
    if t < A_1973:
        _caption(d, "国民の「青」コールに、1947年 法令が折れる")
        _signal3(d, 700, 560, on="G")
        # 吹き出し「青！」
        rr = random.Random(3)
        n_say = min(int((t - A_1947) / 0.5) + 1, 6)
        for i in range(n_say):
            x = 320 + rr.uniform(0, 500)
            y = 300 + rr.uniform(0, 420)
            d.rounded_rectangle([x - 60, y - 36, x + 60, y + 36], radius=18,
                                fill=(24, 34, 54, 230), outline=ACCENT, width=3)
            ctext(d, x, y - 22, "青！", font(38), ACCENT)
        # 書類の書き換え
        d.rounded_rectangle([1120, 380, 1680, 760], radius=14, fill=(240, 236, 224))
        ctext(d, 1400, 410, "法 令", font(40), (60, 56, 48))
        d.line([1180, 470, 1620, 470], fill=(120, 116, 104), width=3)
        k = ease((t - A_1947 - 3.0) / 0.8)
        if k < 0.5:
            ctext(d, 1400, 520, "緑色信号", font(64), (30, 90, 60))
        if k > 0.2:
            d.line([1200, 555, 1200 + 400 * min(k * 2, 1), 555], fill=RED, width=10)
        if k > 0.6:
            ctext(d, 1400, 620, "青信号", font(72), (30, 70, 150))
            ctext(d, 1400, 716, "1947年 改正", font(32), RED)
        return
    if t < A_WORLD:
        _caption(d, "1973年〜 実物の色も、青寄りへ")
        _spectrum(d, 360, 1560, 480, 110)
        # 国際ルールの緑範囲
        gx0, gx1 = 1000, 1560
        d.line([gx0, 450, gx0, 620], fill=INK, width=6)
        d.line([gx1 - 4, 450, gx1 - 4, 620], fill=INK, width=6)
        ctext(d, (gx0 + gx1) / 2, 396, "世界ルールの「緑」の範囲", font(32), INK)
        # マーカーが緑ど真ん中→青端へ
        k = ease((t - A_1973 - 1.5) / 2.5)
        mx = (gx1 - 80) + ((gx0 + 30) - (gx1 - 80)) * k
        d.polygon([(mx - 24, 660), (mx + 24, 660), (mx, 610)], fill=AMBER)
        ctext(d, mx, 680, "日本の青信号", font(34), AMBER)
        if k >= 1.0:
            ctext(d, W / 2, 800, "ルール内で、いちばん青寄りの緑", font(40), GRAY)
        return
    _caption(d, "英語では、そのまま「グリーンライト」")
    _signal3(d, 640, 560, on="G")
    ctext(d, 640, 740, "日本「青信号」", font(44), ACCENT)
    _signal3(d, 1300, 560, on="G")
    ctext(d, 1300, 740, "英語「green light」", font(44), GREEN)
    ctext(d, W / 2, 880, "緑を「青」と呼ぶのは、日本語の歴史の名残", font(38), GRAY)


# ------------------------------------------------------------------
# 2) led_snow — LEDと雪（10カット版）
#    LED=11.39 / 熱の仕組み=28.99 / 負け=59.3 / 雪=71.72 / 縦型=82.2 / DUR 94.6
# ------------------------------------------------------------------
L_LED, L_HEATWHY, L_LOSE, L_SNOW, L_TATE = 11.39, 28.99, 59.3, 71.72, 82.2


def led_snow(d, t):
    if t < L_LED:
        _caption(d, "電球式の弱点 = 西日で全部点いて見える")
        _signal3(d, 760, 560, on="ALL")
        k = 0.6 + 0.4 * math.sin(t * 2)
        sun_x, sun_y = 1560, 320
        d.ellipse([sun_x - 70, sun_y - 70, sun_x + 70, sun_y + 70], fill=(255, 180, 90))
        for i in range(5):
            ang = math.pi * (0.75 + 0.09 * i)
            d.line([sun_x, sun_y, sun_x + 600 * math.cos(ang), sun_y + 600 * math.sin(ang)],
                   fill=(255, 190, 110, int(140 * k)), width=8)
        ctext(d, 760, 760, "どれが点いてるか、わからない（疑似点灯）", font(36), RED)
        return
    if t < L_HEATWHY:
        _caption(d, "LED化 = 反射に騙されない")
        _signal3(d, 640, 560, on="G")
        for i in range(24):
            ang = i / 24 * 2 * math.pi
            rr = 40 * (0.5 + 0.5 * (i % 2))
            d.ellipse([640 - 150 + rr * math.cos(ang) - 4, 560 + rr * math.sin(ang) - 4,
                       640 - 150 + rr * math.cos(ang) + 4, 560 + rr * math.sin(ang) + 4],
                      fill=(180, 255, 220))
        feats = [("疑似点灯なし", GREEN), ("球切れ交換ほぼ不要", AMBER)]
        for i, (s_, col) in enumerate(feats):
            kk = ease((t - L_LED - 1.0 - i * 0.8) / 0.5)
            if kk <= 0:
                continue
            d.rounded_rectangle([1080, 430 + i * 140, 1080 + 520 * kk, 540 + i * 140],
                                radius=16, fill=(24, 34, 54, int(255 * kk)))
            if kk > 0.7:
                d.text((1110, 462 + i * 140), s_, font=font(36), fill=col)
        return
    if t < L_LOSE:
        _caption(d, "電球 = 熱のオマケで光る / LED = 直接光る")
        # 左: 電球（フィラメント＋熱の波）
        cx = 560
        d.ellipse([cx - 130, 400, cx + 130, 660], outline=(230, 220, 200), width=8)
        fil = 0.6 + 0.4 * math.sin(t * 6)
        d.line([cx - 50, 560, cx - 15, 500, ], fill=(255, 170 + int(70 * fil), 80), width=10)
        d.line([cx - 15, 500, cx + 15, 560], fill=(255, 170 + int(70 * fil), 80), width=10)
        d.line([cx + 15, 560, cx + 50, 500], fill=(255, 170 + int(70 * fil), 80), width=10)
        for j in range(3):
            yy = 360 - ((t * 50 + j * 40) % 120)
            d.arc([cx - 60 + j * 45, yy, cx - 20 + j * 45, yy + 50],
                  start=200, end=340, fill=(255, 130, 90, 200), width=6)
        ctext(d, cx, 700, "金属の糸を2000度以上に加熱", font(32), RED)
        ctext(d, cx, 750, "電気のほとんどが熱に化ける", font(30), GRAY)
        # 右: LED（半導体→光の矢印）
        cx2 = 1360
        d.rounded_rectangle([cx2 - 110, 500, cx2 + 110, 600], radius=12,
                            fill=(30, 42, 60), outline=GREEN, width=5)
        ctext(d, cx2, 528, "半導体", font(36), GREEN)
        kk = 0.5 + 0.5 * math.sin(t * 3)
        for j in range(3):
            ang = -math.pi / 2 + (j - 1) * 0.5
            x2, y2 = cx2 + 150 * math.cos(ang), 500 + 130 * math.sin(ang)
            d.line([cx2, 500, x2, y2], fill=(180, 255, 220, int(255 * kk)), width=8)
        ctext(d, cx2, 700, "電気を直接、光に変える", font(32), GREEN)
        k2 = ease((t - L_HEATWHY - 16.0) / 0.8)
        if k2 > 0:
            d.rounded_rectangle([660, 840, 660 + 620 * k2, 960], radius=18,
                                fill=(24, 34, 54, int(255 * k2)))
            if k2 > 0.7:
                ctext(d, 960, 862, "電気は約6分の1・寿命6〜8年", font(36), AMBER)
        return
    if t < L_SNOW:
        _caption(d, "たったひとつの負け = 熱くならない")
        for i, (label, hot) in enumerate((("電球", True), ("LED", False))):
            cx = 640 + i * 640
            _signal3(d, cx, 540, on="G", s=0.9)
            col = RED if hot else ACCENT
            ctext(d, cx, 700, label, font(44), INK)
            ctext(d, cx, 760, "ホカホカ（雪が溶ける）" if hot else "ひんやり（雪が残る）",
                  font(34), col)
            if hot:
                for j in range(3):
                    yy = 420 - ((t * 40 + j * 30) % 90)
                    d.arc([cx - 40 + j * 30, yy, cx - 10 + j * 30, yy + 40],
                          start=200, end=340, fill=(255, 140, 100, 180), width=6)
        return
    if t < L_TATE:
        _caption(d, "吹雪の日、LED信号が見えなくなる")
        snow_k = ease((t - L_SNOW) / 4.0)
        _signal3(d, 960, 560, on="G", snow=snow_k)
        rr = random.Random(int(t * 5))
        for _ in range(60):
            x, y = rr.uniform(0, W), rr.uniform(220, H)
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(240, 244, 250, 200))
        if snow_k > 0.8:
            ctext(d, 960, 790, "張り付いた雪が、そのまま残る", font(38), RED)
        return
    _caption(d, "雪国の答え = 縦型（積もる面積を減らす）")
    k = ease((t - L_TATE) / 1.5)
    if k < 1.0:
        _signal3(d, 600, 540, on="G", s=0.85, snow=0.9)
        ctext(d, 600, 700, "横型 = 雪の受け皿が広い", font(32), RED)
    _signal3(d, 1280, 540, on="G", vertical=True, s=0.85 * max(k, 0.01), snow=0.15)
    if k > 0.7:
        ctext(d, 1280, 800, "縦型 = 上面が最小限", font(34), GREEN)
        ctext(d, W / 2, 920, "深いひさし派・ツルツルのフラット派もいる", font(34), GRAY)


# ------------------------------------------------------------------
# 2.5) wavelength_red — なぜ赤が止まれか
#    散乱=9.83 / 夕日=20.04 / 鉄道=34.18 / 3色=47.73 / DUR 68.2
# ------------------------------------------------------------------
R_SCAT, R_SUNSET, R_RAIL, R_THREE = 9.83, 20.04, 34.18, 47.73


def _wave(d, x0, x1, y, wavelength, col, amp=26, width=7, t=0.0):
    pts = []
    x = x0
    while x <= x1:
        pts.append((x, y + amp * math.sin((x - x0) / wavelength * 2 * math.pi + t * 4)))
        x += 6
    d.line(pts, fill=col, width=width, joint="curve")


def wavelength_red(d, t):
    if t < R_SCAT:
        _caption(d, "光には「波長」がある")
        _spectrum(d, 360, 1560, 320, 80)
        _wave(d, 460, 1460, 560, 260, SIG_R, t=t)
        ctext(d, 960, 620, "赤 = 波長がいちばん長い（ゆったりした波）", font(34), SIG_R)
        _wave(d, 460, 1460, 760, 80, (110, 150, 255), amp=18, t=t)
        ctext(d, 960, 820, "青 = 波長が短い（細かい波）", font(34), (110, 150, 255))
        return
    if t < R_SUNSET:
        _caption(d, "波長が長いほど、散らばらずに遠くへ届く")
        # チリの中を進む2本の光
        rr = random.Random(7)
        for _ in range(50):
            x, y = rr.uniform(500, 1500), rr.uniform(420, 820)
            d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(120, 130, 150, 140))
        d.line([300, 540, 1620, 540], fill=(*SIG_R, 240), width=10)
        ctext(d, 1700, 520, "赤", font(40), SIG_R)
        # 青は途中で散乱
        k = ((t - R_SCAT) * 0.5) % 1.0
        bx = 300 + 700 * min(k * 2, 1)
        d.line([300, 700, min(bx, 1000), 700], fill=(110, 150, 255, 240), width=10)
        if k > 0.5:
            for i in range(6):
                ang = i / 6 * 2 * math.pi
                d.line([1000, 700, 1000 + 90 * math.cos(ang), 700 + 90 * math.sin(ang)],
                       fill=(110, 150, 255, 160), width=5)
        ctext(d, 1700, 680, "青", font(40), (110, 150, 255))
        ctext(d, 960, 880, "チリや水滴にぶつかると、青は散らばって消える", font(34), GRAY)
        return
    if t < R_RAIL:
        _caption(d, "夕日が赤いのも、同じ物理")
        # 地平線と夕日
        d.rectangle([0, 700, W, 1080], fill=(30, 30, 44))
        d.ellipse([840, 600, 1080, 840], fill=(255, 120, 70))
        # 大気を長く通る光
        d.line([960, 700, 300, 460], fill=(255, 120, 70, 220), width=10)
        ctext(d, 560, 380, "空気の中を長く進む → 赤だけ生き残る", font(34), (255, 150, 100))
        grad = [(255, 140, 80), (255, 100, 70), (200, 70, 80)]
        for i, c in enumerate(grad):
            d.rectangle([0, 700 - (3 - i) * 60, W, 700 - (2 - i) * 60], fill=(*c, 60))
        return
    if t < R_THREE:
        _caption(d, "「何よりも伝えたい止まれ」に、赤")
        # 鉄道の赤ランプ
        d.rectangle([880, 400, 920, 860], fill=(70, 80, 100))
        blink = 0.6 + 0.4 * math.sin(t * 3)
        d.ellipse([820, 300, 980, 460], fill=(int(255 * blink), 60, 50))
        d.ellipse([800, 280, 1000, 480], outline=(*SIG_R, int(150 * blink)), width=8)
        ctext(d, 900, 900, "鉄道の信号から、世界共通のルールに", font(36), GRAY)
        return
    _caption(d, "3色は、目と物理からの逆算")
    items = [("赤 = 止まれ", "いちばん遠くまで届く", SIG_R),
             ("黄 = 注意", "赤の次に波長が長く目立つ", SIG_Y),
             ("緑 = 進め", "赤と最も見間違えにくい", SIG_G)]
    for i, (s1, s2, col) in enumerate(items):
        kk = ease((t - R_THREE - i * 0.6) / 0.5)
        if kk <= 0:
            continue
        x = 430 + i * 530
        d.rounded_rectangle([x - 230, 420, x + 230, 660], radius=24,
                            fill=(24, 34, 54, int(255 * kk)))
        if kk > 0.5:
            d.ellipse([x - 50, 450, x + 50, 550], fill=col)
            ctext(d, x, 566, s1, font(40), col)
            ctext(d, x, 616, s2, font(26), GRAY)


# ------------------------------------------------------------------
# 3) button_wait — 押しボタンの順番待ち（青=9.88 / DUR 17.6）
# ------------------------------------------------------------------
B_GO = 9.88


def button_wait(d, t):
    _caption(d, "押しボタン = 無視じゃなくて、順番待ち")
    # ボタンと「おまちください」
    d.rounded_rectangle([320, 400, 700, 700], radius=24, fill=BODY)
    pressed = t > 0.8
    d.ellipse([460, 470, 560, 570], fill=(200, 60, 50) if pressed else (120, 40, 36),
              outline=(230, 230, 240), width=6)
    if pressed:
        d.rounded_rectangle([360, 600, 660, 660], radius=10, fill=(40, 30, 20))
        blink = (int(t * 2) % 2) == 0
        if blink and t < B_GO:
            ctext(d, 510, 610, "おまちください", font(30), AMBER)
        if t >= B_GO:
            ctext(d, 510, 610, "わたれます", font(30), GREEN)
    # 車の流れゲージ
    d.text((1000, 400), "車の流れ（周りの信号と連携）", font=font(32), fill=GRAY)
    d.rounded_rectangle([1000, 450, 1700, 520], radius=16, fill=(24, 34, 54))
    k = min(t / B_GO, 1.0)
    d.rounded_rectangle([1000, 450, 1000 + 700 * k, 520], radius=16, fill=AMBER if k < 1 else GREEN)
    ctext(d, 1350, 540, "止めていいタイミングを待機中…" if k < 1 else "いまだ！ → 歩行者青",
          font(32), AMBER if k < 1 else GREEN)
    # 歩行者灯
    px, py = 1350, 700
    d.rounded_rectangle([px - 90, py - 60, px + 90, py + 130], radius=14, fill=BODY)
    top_on = t < B_GO
    d.ellipse([px - 40, py - 40, px + 40, py + 40], fill=SIG_R if top_on else (60, 30, 28))
    d.ellipse([px - 40, py + 50, px + 40, py + 130 - 0], fill=(24, 60, 46) if top_on else SIG_G)


# ------------------------------------------------------------------
# 4) 時代カード
# ------------------------------------------------------------------
ERAS = ["1868 ロンドン(ガス)", "1930 日比谷", "1947 青信号に", "LED時代へ"]


def _timeline(d, t, idx):
    bx0, bx1, by = 520, 1400, 952
    d.line([bx0, by, bx1, by], fill=(50, 64, 92), width=6)
    prog = ease((t - 0.4) / 1.2)
    if idx > 0:
        d.line([bx0, by, bx0 + (bx1 - bx0) * prog * idx / 3, by], fill=(*ACCENT, 255), width=6)
    f_tick = font(24)
    for i, e in enumerate(ERAS):
        x = bx0 + (bx1 - bx0) * i / 3
        cur = i == idx
        r = 13 + (5 * (0.5 + 0.5 * math.sin(t * 3)) if cur else 0)
        col = AMBER if cur else ((150, 158, 175) if i < idx else (60, 72, 98))
        d.ellipse([x - r, by - r, x + r, by + r], fill=col)
        d.text((x - d.textlength(e, font=f_tick) / 2, by + 22), e, font=f_tick,
               fill=INK if cur else GRAY)


def era_1868(d, t):
    k = ease(t / 0.5)
    f_year = font(150)
    yw = d.textlength("1868", font=f_year)
    d.text(((W - yw) / 2, 110 - 40 * (1 - k)), "1868", font=f_year,
           fill=(*AMBER, int(255 * k)))
    k2 = ease((t - 0.35) / 0.4)
    if k2 > 0:
        ctext(d, W / 2, 300, "世界初の信号機、ロンドンに", font(70), (*INK, int(255 * k2)))
        ctext(d, W / 2, 400, "ガス灯を警察官がレバーで切り替える手動式", font(38),
              (*GRAY, int(255 * k2)))
    kp = ease((t - 0.9) / 0.5)
    if kp > 0:
        # ガス灯柱
        cx = 760
        d.rectangle([cx - 14, 560, cx + 14, 880], fill=(70, 80, 100))
        d.rounded_rectangle([cx - 60, 480, cx + 60, 580], radius=14,
                            outline=(210, 200, 170), width=6)
        flick = 0.6 + 0.4 * math.sin(t * 7)
        d.polygon([(cx - 18, 566), (cx + 18, 566), (cx, 566 - 50 * flick)],
                  fill=(255, 170, 70, int(255 * kp)))
        _timeline(d, t, 0)
    # 爆発（10.7s以降 = 「3週間で爆発」のカット）
    if t > 10.7:
        kb = ease((t - 10.7) / 0.5)
        cx = 760
        rr = random.Random(9)
        for i in range(10):
            ang = i / 10 * 2 * math.pi
            ln = 130 * kb * (0.7 + 0.6 * rr.random())
            d.line([cx, 540, cx + ln * math.cos(ang), 540 + ln * math.sin(ang)],
                   fill=(255, 150, 60), width=12)
        d.rounded_rectangle([1080, 520, 1660, 700], radius=18, fill=(24, 34, 54, int(255 * kb)))
        if kb > 0.6:
            ctext(d, 1370, 550, "設置から約3週間で爆発", font(40), RED)
            ctext(d, 1370, 620, "警察官が大けが → 撤去", font(34), GRAY)


def era_1930(d, t):
    k = ease(t / 0.5)
    f_year = font(150)
    yw = d.textlength("1930", font=f_year)
    d.text(((W - yw) / 2, 110 - 40 * (1 - k)), "1930", font=f_year,
           fill=(*AMBER, int(255 * k)))
    k2 = ease((t - 0.35) / 0.4)
    if k2 > 0:
        ctext(d, W / 2, 300, "日本初の自動信号機、日比谷に", font(70), (*INK, int(255 * k2)))
        ctext(d, W / 2, 400, "電気式がアメリカから世界へ、そして日本へ", font(38),
              (*GRAY, int(255 * k2)))
    kp = ease((t - 0.9) / 0.5)
    if kp > 0:
        _signal3(d, 960, 640, on="G", s=0.9 * kp)
    _timeline(d, t, 1)


CLIPS = {
    "color_ao": (80.3, lambda: color_ao),
    "led_snow": (94.6, lambda: led_snow),
    "wavelength_red": (68.2, lambda: wavelength_red),
    "button_wait": (17.6, lambda: button_wait),
    "era_1868": (28.2, lambda: era_1868),
    "era_1930": (12.2, lambda: era_1930),
}


def main() -> None:
    names = sys.argv[1:] or list(CLIPS)
    for name in names:
        dur, fn = CLIPS[name]
        render(name, dur, fn())


if __name__ == "__main__":
    main()
