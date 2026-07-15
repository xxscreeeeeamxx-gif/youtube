#!/usr/bin/env python3
"""banknote プロジェクト用のアニメクリップを生成する。

  bill_tour.mp4      64.0s  お札の仕掛けツアー（深凹版→識別マーク→すかし→法律の盾→潜像/マイクロ）
  eurion.mp4         37.0s  ユーリオン（丸模様→コピー機が検知して拒否→日本発）
  hologram.mp4       26.0s  3Dホログラム（世界初バッジ→傾けると肖像が回る）
  bill_exchange.mp4  26.0s  破損紙幣の交換基準（2/3全額・2/5半額・未満0円）
  era_1961.mp4       14.3s  チ-37号事件の時代カード

お札はすべて模式図（実物のデザインは再現しない）。
フェーズ境界は timing.json のカット実測に同期（コメントの秒数）。
実行: PYTHONPATH=. python3 scripts/gen_banknote_extras.py [クリップ名...]
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
BILL = (214, 226, 210)     # 模式お札の地色
BILL_DK = (150, 168, 150)  # 模式お札の模様色

_cfg = Config.load()
_font_path = _cfg.find_pillow_font()


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(_font_path, size, index=0)


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
    tmp = Path(tempfile.mkdtemp(prefix=f"bn_{name}_"))
    for fi in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw_frame(ImageDraw.Draw(img, "RGBA"), fi / FPS)
        img.save(tmp / f"{fi:04d}.png")
    encode(tmp, Path(f"assets/clips/{name}.mp4"))


def _bill(d, cx, cy, w=760, h=380, label=True):
    """模式図のお札。実物のデザインは描かない。"""
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                        radius=16, fill=BILL, outline=BILL_DK, width=5)
    # 肖像枠（シルエットのみ）
    ox = cx + w * 0.24
    r = h * 0.22
    d.ellipse([ox - r, cy - r * 1.5, ox + r, cy + r * 0.5], fill=BILL_DK)
    d.pieslice([ox - r * 1.7, cy - r * 0.3, ox + r * 1.7, cy + r * 2.2],
               start=180, end=360, fill=BILL_DK)
    d.rounded_rectangle([cx - w * 0.42, cy - h * 0.30, cx - w * 0.05, cy - h * 0.06],
                        radius=8, outline=BILL_DK, width=4)
    ctext(d, cx - w * 0.235, cy - h * 0.27, "10000", font(44), BILL_DK)
    if label:
        ctext(d, cx, cy + h / 2 + 18, "お札（模式図）", font(28), GRAY)


# ------------------------------------------------------------------
# 1) bill_tour — 仕掛けツアー
#    識別=10.86 / すかし=19.26 / (Z=30.59) / 法律=34.93 / (Z=46.04) / 潜像=51.53 / DUR 64.0
# ------------------------------------------------------------------
B_MARK, B_WM, B_LAW, B_MICRO = 10.86, 19.26, 34.93, 51.53


def bill_tour(d, t):
    if t < B_MARK:
        _caption(d, "深凹版印刷 = インキを盛り上げる")
        # 断面図
        cy = 620
        d.rectangle([460, cy, 1460, cy + 60], fill=(230, 228, 216))
        ctext(d, 960, cy + 70, "紙の断面", font(30), GRAY)
        k = ease(t / 1.5)
        for i, x in enumerate((640, 820, 1000, 1180)):
            hgt = 46 * k
            d.rounded_rectangle([x - 46, cy - hgt, x + 46, cy + 4], radius=8,
                                fill=(40, 80, 50))
        # 指がなぞる
        kk = ((t * 0.35) % 1.0)
        fx = 560 + kk * 800
        fy = cy - 46 * k - 40 + 10 * math.sin(kk * 12)
        d.ellipse([fx - 34, fy - 46, fx + 34, fy + 30], fill=(240, 200, 170))
        ctext(d, 960, 800, "盛り上がった立体の文字 = コピーでは平ら", font(38), GRAY)
        return
    if t < B_WM:
        _caption(d, "識別マーク = 触って金額がわかる")
        _bill(d, 960, 580)
        k = ease((t - B_MARK) / 0.8)
        for i, (x, y) in enumerate(((640, 470), (640, 690), (1280, 470))):
            kk = ease((t - B_MARK - i * 0.5) / 0.5)
            if kk <= 0:
                continue
            d.ellipse([x - 26 * kk, y - 26 * kk, x + 26 * kk, y + 26 * kk],
                      outline=AMBER, width=8)
        ctext(d, 960, 810, "お札の種類ごとに、位置が違う", font(38), AMBER)
        return
    if t < B_LAW:
        _caption(d, "すかし = 紙の厚みで描く絵")
        # 光に透かす表現
        k = ease((t - B_WM) / 1.5)
        _bill(d, 960, 560, label=False)
        # 背後からの光
        for i in range(3):
            r = 240 + i * 90
            a = int(60 * k * (1 - i * 0.3))
            d.ellipse([960 - r, 560 - r * 0.6, 960 + r, 560 + r * 0.6],
                      outline=(255, 240, 180, a), width=20)
        # 浮かぶ肖像
        if k > 0.5:
            a = int(200 * (k - 0.5) * 2)
            cx2, cy2 = 810, 560
            r = 70
            d.ellipse([cx2 - r, cy2 - r * 1.5, cx2 + r, cy2 + r * 0.5],
                      fill=(120, 130, 118, a))
            d.pieslice([cx2 - r * 1.7, cy2 - r * 0.3, cx2 + r * 1.7, cy2 + r * 2.2],
                       start=180, end=360, fill=(120, 130, 118, a))
        ctext(d, 960, 800, "印刷ではなく、紙の厚みの差", font(38), GRAY)
        ctext(d, 960, 856, "厚い = 暗く / 薄い = 明るく 見える", font(32), GRAY)
        return
    if t < B_MICRO:
        _caption(d, "すかし入りの紙は、作るだけで違法")
        _bill(d, 700, 580, w=620, h=310, label=False)
        ctext(d, 700, 760, "すかし入りの紙", font(32), GRAY)
        k = ease((t - B_LAW) / 0.8)
        # 禁止マーク
        r = 190 * k
        if r > 4:
            d.ellipse([700 - r, 580 - r, 700 + r, 580 + r], outline=RED, width=16)
            d.line([700 - r * 0.7, 580 + r * 0.7, 700 + r * 0.7, 580 - r * 0.7],
                   fill=RED, width=16)
        kk = ease((t - B_LAW - 1.0) / 0.6)
        if kk > 0:
            d.rounded_rectangle([1130, 460, 1740, 700], radius=20,
                                fill=(24, 34, 54, int(255 * kk)))
            if kk > 0.6:
                ctext(d, 1435, 495, "法律の先回り", font(42), AMBER)
                ctext(d, 1435, 570, "刷る前 = 紙を作った時点で", font(32), INK)
                ctext(d, 1435, 620, "もう犯罪", font(40), RED)
        return
    _caption(d, "潜像・パールインキ・マイクロ文字")
    _bill(d, 640, 580, w=620, h=310, label=False)
    # 傾き潜像（額面の枠や肖像と重ならない位置に出す）
    tilt = 0.5 + 0.5 * math.sin((t - B_MICRO) * 1.2)
    a = int(220 * tilt)
    ctext(d, 500, 590, "10000", font(60), (90, 110, 96, a))
    ctext(d, 640, 760, "傾けると数字が浮かぶ「潜像」", font(30), GRAY)
    # マイクロ文字ズーム
    d.ellipse([1150, 430, 1560, 760], outline=ACCENT, width=8)
    micro = "ニホンギンコウ " * 3
    for i in range(5):
        d.text((1195, 500 + i * 46), micro, font=font(22), fill=(90, 100, 96))
    ctext(d, 1355, 790, "コピーすると必ずつぶれる細かさ", font(30), ACCENT)


# ------------------------------------------------------------------
# 2) eurion — 隠し模様（拒否=9.07 / (Z=18.96) / 日本発=25.63 / DUR 37.0）
# ------------------------------------------------------------------
E_SCAN, E_JAPAN = 9.07, 25.63
_dots = [(0.18, 0.28), (0.30, 0.62), (0.44, 0.24), (0.58, 0.55),
         (0.70, 0.30), (0.82, 0.66), (0.36, 0.80), (0.64, 0.78)]


def eurion(d, t):
    if t < E_SCAN:
        _caption(d, "散らばる小さな丸 = ユーリオン")
        _bill(d, 960, 580)
        for i, (px, py) in enumerate(_dots):
            x = 960 - 380 + px * 760
            y = 580 - 190 + py * 380
            d.ellipse([x - 13, y - 13, x + 13, y + 13],
                      outline=(70, 110, 80), width=6)
            kk = ease((t - 1.5 - i * 0.3) / 0.4)
            if kk > 0:
                r = 26 * kk
                d.ellipse([x - r, y - r, x + r, y + r], outline=AMBER, width=5)
        if t > 4.5:
            ctext(d, 960, 830, "機械にだけ見える目印", font(40), AMBER)
        return
    if t < E_JAPAN:
        _caption(d, "コピー機が見つけた瞬間、拒否")
        # ガラス面のお札
        _bill(d, 620, 560, w=560, h=280, label=False)
        for (px, py) in _dots:
            x = 620 - 280 + px * 560
            y = 560 - 140 + py * 280
            d.ellipse([x - 10, y - 10, x + 10, y + 10], outline=(70, 110, 80), width=5)
        # スキャンライン
        k = ((t - E_SCAN) / 2.2) % 1.0
        sy = 420 + k * 280
        d.line([340, sy, 900, sy], fill=(120, 220, 160, 220), width=8)
        # 判定パネル
        kk = ease((t - E_SCAN - 1.8) / 0.6)
        if kk > 0:
            blink = (int(t * 2) % 2) == 0
            d.rounded_rectangle([1100, 420, 1740, 720], radius=20, fill=(24, 34, 54))
            ctext(d, 1420, 452, "コピー機の判定", font(34), GRAY)
            if blink:
                ctext(d, 1420, 520, "紙幣を検知", font(56), RED)
            ctext(d, 1420, 620, "印刷拒否 / 真っ黒 / エラー停止", font(32), INK)
        return
    _caption(d, "元の技術は、日本のオムロン")
    # 日本から世界へ広がるリング
    cx, cy = 960, 600
    d.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], fill=(200, 60, 60))
    ctext(d, cx, cy + 80, "日本発", font(40), INK)
    k = t - E_JAPAN
    for i in range(4):
        kk = ((k * 0.5 + i * 0.25) % 1.0)
        r = 80 + kk * 500
        a = int(200 * (1 - kk))
        d.ellipse([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55],
                  outline=(255, 190, 80, a), width=8)
    ctext(d, 960, 880, "世界中のお札に、日本生まれの防犯装置", font(40), GRAY)


# ------------------------------------------------------------------
# 3) hologram — 3Dホログラム（回転=8.81 / DUR 26.0）
# ------------------------------------------------------------------
HG_TILT = 8.81


def hologram(d, t):
    if t < HG_TILT:
        _caption(d, "2024年 新紙幣 = 世界初の3Dホログラム")
        _bill(d, 960, 580)
        # ホロパッチ
        d.rounded_rectangle([620, 460, 760, 700], radius=12,
                            fill=(190, 205, 225), outline=ACCENT, width=6)
        k = ease((t - 1.0) / 0.6)
        if k > 0:
            d.rounded_rectangle([560, 330, 1000, 400], radius=14,
                                fill=(24, 34, 54, int(230 * k)))
            if k > 0.6:
                ctext(d, 780, 344, "銀行券への採用は世界初", font(34), AMBER)
        return
    _caption(d, "傾けると、肖像がくるっと回る")
    # 傾きスライダー
    tilt = math.sin((t - HG_TILT) * 1.2)  # -1..1
    _bill(d, 960, 560, label=False)
    # パッチ内のシルエットが回転（横幅で表現）
    px, py = 690, 580
    d.rounded_rectangle([px - 80, py - 130, px + 80, py + 130], radius=12,
                        fill=(190, 205, 225), outline=ACCENT, width=6)
    r = 46 * max(abs(tilt), 0.15)
    face = tilt >= 0
    col = (110, 125, 150) if face else (80, 95, 120)
    d.ellipse([px - r, py - 90, px + r, py - 90 + 84], fill=col)
    d.pieslice([px - r * 1.8, py - 20, px + r * 1.8, py + 120],
               start=180, end=360, fill=col)
    # 傾きゲージ
    gx = 1350
    d.line([gx - 200, 820, gx + 200, 820], fill=(50, 64, 92), width=6)
    d.ellipse([gx + tilt * 180 - 16, 804, gx + tilt * 180 + 16, 836], fill=AMBER)
    ctext(d, gx, 850, "お札の傾き", font(30), GRAY)
    ctext(d, 960, 930, "印刷でも写真でも、この「動き」は再現できない", font(36), GRAY)


# ------------------------------------------------------------------
# 4) bill_exchange — 交換基準（基準=8.12 / DUR 26.0）
# ------------------------------------------------------------------
X_RULE = 9.21


def bill_exchange(d, t):
    if t < X_RULE:
        _caption(d, "破れたお札の運命は、面積で決まる")
        # お札が破れる
        k = ease((t - 1.0) / 1.2)
        gap = 60 * k
        w, h, cy = 700, 350, 580
        cx = 960
        # 左片（2/3）
        d.rounded_rectangle([cx - w / 2 - gap, cy - h / 2, cx + w * 0.17 - gap, cy + h / 2],
                            radius=14, fill=BILL, outline=BILL_DK, width=5)
        # 右片（1/3）ジグザグ断面
        d.rounded_rectangle([cx + w * 0.17 + gap, cy - h / 2, cx + w / 2 + gap, cy + h / 2],
                            radius=14, fill=BILL, outline=BILL_DK, width=5)
        if k > 0.5:
            ctext(d, cx, 800, "ビリッ", font(44), RED)
        return
    _caption(d, "3分の2で全額・5分の2で半額")
    # 面積ゲージ
    bx, bw, by, bh = 360, 1200, 430, 110
    rows = [("3分の2 以上", 1.0, "全額もらえる", GREEN, 0.85),
            ("5分の2 以上", 0.5, "半額", AMBER, 0.55),
            ("5分の2 未満", 0.0, "0円……", RED, 0.3)]
    for i, (cond, _, verdict, col, frac) in enumerate(rows):
        kk = ease((t - X_RULE - i * 1.2) / 0.6)
        if kk <= 0:
            continue
        y = by + i * 170
        d.rounded_rectangle([bx, y, bx + bw * 0.52, y + bh], radius=14, fill=(24, 34, 54))
        # 残った面積の模式お札
        d.rounded_rectangle([bx + 20, y + 18, bx + 20 + (bw * 0.5 - 40) * frac, y + bh - 18],
                            radius=8, fill=BILL)
        d.text((bx + bw * 0.55, y + 6), cond, font=font(36), fill=INK)
        d.text((bx + bw * 0.55, y + 56), verdict, font=font(40), fill=col)
    if t > X_RULE + 5.0:
        ctext(d, 960, 960, "切れ端も集めて、銀行か日本銀行の窓口へ", font(36), GRAY)


# ------------------------------------------------------------------
# 5) era_1961 — チ-37号事件カード
# ------------------------------------------------------------------
ERAS = ["1961 チ-37号事件", "1963 新札で対抗", "2024 3Dホログラム"]


def era_1961(d, t):
    k = ease(t / 0.5)
    f_year = font(150)
    yw = d.textlength("1961", font=f_year)
    d.text(((W - yw) / 2, 120 - 40 * (1 - k)), "1961", font=f_year,
           fill=(*AMBER, int(255 * k)))
    k2 = ease((t - 0.35) / 0.4)
    if k2 > 0:
        ctext(d, W / 2, 320, "チ-37号事件", font(72), (*INK, int(255 * k2)))
    k3 = ease((t - 0.7) / 0.4)
    if k3 > 0:
        ctext(d, W / 2, 430, "プロでも見分けられない偽千円札、343枚",
              font(42), (*GRAY, int(255 * k3)))
    kp = ease((t - 0.9) / 0.5)
    if kp > 0:
        # 偽札シルエットと「？」の犯人
        _bill(d, 760, 700, w=440, h=220, label=False)
        ctext(d, 760, 830, "精巧な偽札", font(30), GRAY)
        cx = 1240
        r = int(58 * kp)
        col = (46, 66, 100, int(255 * kp))
        d.ellipse([cx - r, 700 - r * 2.1, cx + r, 700 - 0.1 * r], fill=col)
        d.pieslice([cx - r * 2, 700 - r * 0.2, cx + r * 2, 700 + r * 2.6],
                   start=180, end=360, fill=col)
        ctext(d, cx, 590, "？", font(80), (*AMBER, int(255 * kp)))
        ctext(d, cx, 770, "犯人は時効まで不明", font(30), (*GRAY, int(255 * kp)))
    bx0, bx1, by = 560, 1360, 952
    d.line([bx0, by, bx1, by], fill=(50, 64, 92), width=6)
    f_tick = font(24)
    for i, e in enumerate(ERAS):
        x = bx0 + (bx1 - bx0) * i / 2
        cur = i == 0
        r = 13 + (5 * (0.5 + 0.5 * math.sin(t * 3)) if cur else 0)
        col = AMBER if cur else (60, 72, 98)
        d.ellipse([x - r, by - r, x + r, by + r], fill=col)
        d.text((x - d.textlength(e, font=f_tick) / 2, by + 22), e,
               font=f_tick, fill=INK if cur else GRAY)


CLIPS = {
    "bill_tour": (64.0, lambda: bill_tour),
    "eurion": (37.0, lambda: eurion),
    "hologram": (26.0, lambda: hologram),
    "bill_exchange": (27.0, lambda: bill_exchange),
    "era_1961": (14.3, lambda: era_1961),
}


def main() -> None:
    names = sys.argv[1:] or list(CLIPS)
    for name in names:
        dur, fn = CLIPS[name]
        render(name, dur, fn())


if __name__ == "__main__":
    main()
