#!/usr/bin/env python3
"""escalator プロジェクト用のアニメクリップを生成する。

  esc_loop.mp4        52.2s  ステップ台車のループ（床下回送→黄色い線→速度と手すり）
  ronsou.mp4          33.7s  片側空け論争（輸送力比較→事故・偏荷重）
  wheelchair_step.mp4 37.6s  車椅子モード（鍵→3枚水平化→ストッパー→半分速度→一般客ストップ）
  era_1914.mp4        31.0s  日本初上陸の時代カード
  era_trademark.mp4   22.6s  「エスカレーター」商標の時代カード

フェーズ境界は timing.json のカット実測に同期（コメントの秒数）。
実行: PYTHONPATH=. python3 scripts/gen_escalator_extras.py [クリップ名...]
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
STEP = (70, 84, 110)
YELLOW = (255, 214, 60)

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
    tmp = Path(tempfile.mkdtemp(prefix=f"es_{name}_"))
    for fi in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw_frame(ImageDraw.Draw(img, "RGBA"), fi / FPS)
        img.save(tmp / f"{fi:04d}.png")
    encode(tmp, Path(f"assets/clips/{name}.mp4"))


def _person_s(d, cx, cy, scale=1.0, col=(220, 226, 238)):
    r = int(16 * scale)
    d.ellipse([cx - r, cy - 72 * scale, cx + r, cy - 72 * scale + 2 * r], fill=col)
    d.rounded_rectangle([cx - 18 * scale, cy - 40 * scale, cx + 18 * scale, cy + 26 * scale],
                        radius=int(12 * scale), fill=col)


# ------------------------------------------------------------------
# 1) esc_loop — ステップループ
#    床下=9.91 / (Z=19.95) / 黄線=26.04 / 速度=36.96 / (Z=46.6) / DUR 52.2
# ------------------------------------------------------------------
L_UNDER, L_YELLOW, L_SPEED = 9.91, 26.04, 36.96


def _loop_path(k):
    """0..1 -> ループ上の座標。斜め上り→上で潜る→裏を下る→下で出る。"""
    # 台形ループ: A(360,760)→B(1180,360) 表 / B'(1180,470)→A'(360,870) 裏
    k = k % 1.0
    if k < 0.42:  # 表を上る
        t = k / 0.42
        return 360 + (1180 - 360) * t, 760 + (360 - 760) * t, True
    if k < 0.5:  # 上で潜る
        t = (k - 0.42) / 0.08
        ang = math.pi * t
        return 1180 + 55 * math.sin(ang), 415 - 55 * math.cos(ang), False
    if k < 0.92:  # 裏を下る
        t = (k - 0.5) / 0.42
        return 1180 - (1180 - 360) * t, 470 + (870 - 470) * t, False
    t = (k - 0.92) / 0.08
    ang = math.pi * t
    return 360 - 55 * math.sin(ang), 815 + 55 * math.cos(ang), False


def esc_loop(d, t):
    if t < L_YELLOW:
        _caption(d, "1段1段が、レールを一周する台車" if t < L_UNDER
                 else "床下で平らに畳まれて、回送される")
        # レール
        for pts in ([(360, 760), (1180, 360)], [(1180, 470), (360, 870)]):
            d.line(pts, fill=(50, 64, 92), width=6)
        d.text((640, 930), "床下（見えない回送区間）", font=font(30), fill=GRAY)
        d.rectangle([260, 900, 1320, 906], fill=(50, 64, 92))
        # ステップ台車たち
        n = 12
        for i in range(n):
            k = (t * 0.06 + i / n)
            x, y, front = _loop_path(k)
            hi = i == 0 and t >= L_UNDER
            col = AMBER if hi else (STEP if front else (44, 52, 72))
            d.rounded_rectangle([x - 46, y - 18, x + 46, y + 18], radius=6, fill=col)
            d.ellipse([x - 40, y + 12, x - 24, y + 28], outline=GRAY, width=3)
            d.ellipse([x + 24, y + 12, x + 40, y + 28], outline=GRAY, width=3)
            if front:
                _person_s(d, x, y - 22, 0.9)
        if t >= L_UNDER:
            d.text((1290, 620), "裏側は平らなまま\n下りていく", font=font(30), fill=AMBER)
        return
    if t < L_SPEED:
        _caption(d, "黄色い線 = こすれる境目に立たないで")
        # ステップ拡大
        for i in range(3):
            x0 = 480 + i * 340
            d.rounded_rectangle([x0, 520, x0 + 300, 700], radius=8, fill=STEP)
            d.rectangle([x0, 520, x0 + 300, 540], fill=(56, 70, 96))
            d.rounded_rectangle([x0 - 6, 514, x0 + 306, 546], radius=8, outline=YELLOW, width=8)
        # OK / NG の足
        d.ellipse([700, 590, 760, 660], fill=GREEN)
        ctext(d, 730, 670, "内側 = OK", font(32), GREEN)
        d.ellipse([1092, 560, 1152, 630], fill=RED)
        d.line([1080, 550, 1165, 640], fill=RED, width=10)
        ctext(d, 1122, 670, "境目 = NG", font(32), RED)
        ctext(d, W / 2, 820, "隣の段・壁とこすれる危険地帯の目印", font(36), GRAY)
        return
    _caption(d, "毎分30mは「優しさの速度」")
    # 速度比較バー（手すりの話は後のセリフで扱うのでここでは出さない）
    rows = [("エスカレーター", 30, ACCENT), ("大人の徒歩", 80, GRAY)]
    for i, (s_, v, col) in enumerate(rows):
        y = 480 + i * 170
        d.text((340, y - 50), s_, font=font(34), fill=INK)
        d.rounded_rectangle([340, y, 340 + 1100 * v / 90, y + 56], radius=14, fill=col)
        d.text((360 + 1100 * v / 90, y + 8), f"毎分{v}mくらい", font=font(32), fill=col)
    kk = ease((t - L_SPEED - 5.0) / 0.8)
    if kk > 0:
        ctext(d, W / 2, 850, "誰でも安全に乗り降りできる速さに合わせている",
              font(38), (*GRAY, int(255 * kk)))


# ------------------------------------------------------------------
# 2) ronsou — 片側空け論争（輸送力=5.95 / (Z=17.38) / 事故=23.38 / DUR 33.7）
# ------------------------------------------------------------------
R_CAP, R_ACC = 5.95, 23.38


def ronsou(d, t):
    if t < R_CAP:
        _caption(d, "積み上がる、困った事実")
        items = ["輸送力", "安全", "機械への負担"]
        for i, s_ in enumerate(items):
            kk = ease((t - 0.6 - i * 0.6) / 0.5)
            if kk <= 0:
                continue
            x = 480 + i * 480
            d.rounded_rectangle([x - 190, 460, x + 190, 640], radius=24,
                                fill=(24, 34, 54, int(255 * kk)))
            if kk > 0.5:
                ctext(d, x, 480, f"その{i + 1}", font(30), GRAY)
                ctext(d, x, 535, s_, font(52), AMBER)
        return
    if t < R_ACC:
        _caption(d, "2列で立つほうが、たくさん運べる")
        # 左: 片側空け / 右: 2列
        for side, (x0, label, two) in enumerate(((430, "片側空け", False), (1130, "2列で立つ", True))):
            d.rounded_rectangle([x0 - 190, 330, x0 + 190, 830], radius=20,
                                outline=(70, 92, 130), width=5)
            ctext(d, x0, 290 - 46, label, font(40), INK)
            k = (t - R_CAP)
            rows = 6
            for r_ in range(rows):
                yy = 780 - r_ * 78 - (k * 30 % 78)
                if yy < 350:
                    continue
                if two:
                    _person_s(d, x0 - 60, yy, 1.0, (120, 200, 160))
                    _person_s(d, x0 + 60, yy, 1.0, (120, 200, 160))
                else:
                    _person_s(d, x0 - 60, yy, 1.0)
                    if r_ % 3 == 0:  # たまに歩く人
                        _person_s(d, x0 + 60, yy + (k * 60 % 78), 1.0, (255, 170, 130))
            cnt_one = int(20 + k * 1.6)
            cnt_two = int(20 + k * 2.6)
            d.rounded_rectangle([x0 - 130, 850, x0 + 130, 920], radius=14, fill=(24, 34, 54))
            ctext(d, x0, 862, f"{cnt_two if two else cnt_one} 人", font(40),
                  GREEN if two else GRAY)
        return
    _caption(d, "歩けば事故に、偏れば機械の負担に")
    # 転倒ドミノ
    for i in range(4):
        ang = min(max((t - R_ACC - 0.8) * 2 - i * 0.5, 0), 1) * 0.9
        x = 480 + i * 110
        y = 700
        dx, dy = 90 * math.sin(ang), -90 * math.cos(ang)
        d.line([x, y, x + dx, y + dy], fill=(220, 226, 238), width=16)
        d.ellipse([x + dx - 14, y + dy - 14, x + dx + 14, y + dy + 14], fill=(220, 226, 238))
    ctext(d, 640, 780, "1人の転倒が、後ろを巻き込む", font(34), RED)
    # 偏荷重
    bx = 1310
    tilt = 0.12 * math.sin(t * 1.5)
    d.line([bx - 220, 640 + 90 * tilt, bx + 220, 640 - 90 * tilt], fill=STEP, width=18)
    d.polygon([(bx - 20, 700), (bx + 20, 700), (bx, 655)], fill=GRAY)
    _person_s(d, bx - 150, 610 + 60 * tilt, 1.1, (255, 170, 130))
    ctext(d, bx, 780, "片側だけの重さは、機械もつらい", font(32), AMBER)


# ------------------------------------------------------------------
# 3) wheelchair_step — 車椅子モード
#    鍵=6.22 / 台化=13.4 / (Z=22.98) / 一般停止=28.31 / DUR 37.6
# ------------------------------------------------------------------
W_KEY, W_FLAT, W_STOP = 6.22, 13.4, 28.31


def _wheelchair(d, cx, cy, s=1.0):
    r = int(40 * s)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=6)
    d.ellipse([cx + r * 0.9, cy + r * 0.3, cx + r * 1.5, cy + r * 0.9], outline=INK, width=5)
    d.line([cx, cy - r, cx + r * 0.2, cy - r * 1.7], fill=INK, width=6)  # 背もたれ
    d.line([cx + r * 0.2, cy - r * 1.7, cx + r * 1.1, cy - r * 1.6], fill=INK, width=6)
    _person_s(d, cx + r * 0.5, cy - r * 0.9, 0.9 * s, (120, 200, 160))


def wheelchair_step(d, t):
    # 断面のステップ列（斜め）
    def steps(flat_k=0.0, wc=False):
        base = [(520 + i * 150, 700 - i * 62) for i in range(6)]
        for i, (x, y) in enumerate(base):
            # 中央の3枚（i=2,3,4）が水平化
            if flat_k > 0 and i in (2, 3, 4):
                target_y = 700 - 2 * 62 - (i - 2) * 62 * (1 - flat_k)
                y = y + (target_y - y) * flat_k
                # i=3,4 は i=2 の高さへ寄る
                y = y * (1 - flat_k) + (700 - 2 * 62) * flat_k
            d.rounded_rectangle([x - 72, y - 16, x + 72, y + 16], radius=6, fill=STEP)
            d.rounded_rectangle([x - 72, y - 22, x + 72, y - 14], radius=4, outline=YELLOW, width=4)
        if flat_k > 0.9:
            # ストッパー
            x2, y2 = base[2][0] - 72, 700 - 2 * 62
            k2 = ease((flat_k - 0.9) * 10)
            d.rectangle([x2 - 14, y2 - 70 * k2, x2, y2], fill=RED)
            ctext(d, x2 - 6, y2 - 110, "ストッパー", font(26), RED)
        if wc:
            _wheelchair(d, base[3][0], 700 - 2 * 62 - 52, 1.0)
    if t < W_KEY:
        _caption(d, "一部の機種にある「車椅子モード」")
        steps()
        kk = ease((t - 1.2) / 0.6)
        if kk > 0:
            ctext(d, W / 2, 830, "見た目はふつうのエスカレーター", font(36), GRAY)
        return
    if t < W_FLAT:
        _caption(d, "係員さんが、専用の鍵で切り替える")
        steps()
        # 鍵アイコン
        kx, ky = 1490, 470
        blink = 0.5 + 0.5 * math.sin(t * 4)
        d.ellipse([kx - 40, ky - 40, kx + 40, ky + 40], outline=(255, 190, 80, int(255 * blink)), width=10)
        d.rectangle([kx + 30, ky - 10, kx + 130, ky + 10], fill=AMBER)
        d.rectangle([kx + 100, ky + 10, kx + 114, ky + 34], fill=AMBER)
        ctext(d, kx + 40, ky + 60, "専用キーで操作", font(30), AMBER)
        return
    if t < W_STOP:
        _caption(d, "ステップ3枚が、フラットな台に変形")
        k = ease((t - W_FLAT) / 2.5)
        steps(flat_k=k, wc=k >= 1.0 and t > W_FLAT + 4.0)
        if t > W_FLAT + 6.5:
            # 半分速度
            d.rounded_rectangle([1360, 700, 1800, 830], radius=18, fill=(24, 34, 54))
            ctext(d, 1580, 720, "運転速度", font(30), GRAY)
            ctext(d, 1580, 762, "およそ半分でゆっくり", font(34), GREEN)
        return
    _caption(d, "運転中は、一般の乗車をいったんストップ")
    steps(flat_k=1.0, wc=True)
    # 通行止めサイン
    sx, sy = 380, 430
    d.ellipse([sx - 70, sy - 70, sx + 70, sy + 70], outline=RED, width=14)
    d.line([sx - 46, sy, sx + 46, sy], fill=RED, width=14)
    ctext(d, sx, sy + 90, "しばらくお待ちください", font(30), RED)
    ctext(d, W / 2, 880, "見かけたら、急かさず見守ってね", font(36), GRAY)


# ------------------------------------------------------------------
# 4) 時代カード
# ------------------------------------------------------------------
ERAS = ["1900 商標登録", "1914 日本初上陸", "1950 みんなの言葉に"]


def _silhouette(d, cx, cy, scale, col):
    r = int(58 * scale)
    d.ellipse([cx - r, cy - r * 2.1, cx + r, cy - 0.1 * r], fill=col)
    d.pieslice([cx - r * 2, cy - r * 0.2, cx + r * 2, cy + r * 2.6],
               start=180, end=360, fill=col)


def _timeline(d, t, idx):
    bx0, bx1, by = 560, 1360, 952
    d.line([bx0, by, bx1, by], fill=(50, 64, 92), width=6)
    prog = ease((t - 0.4) / 1.2)
    if idx > 0:
        d.line([bx0, by, bx0 + (bx1 - bx0) * prog * idx / 2, by], fill=(*ACCENT, 255), width=6)
    f_tick = font(24)
    for i, e in enumerate(ERAS):
        x = bx0 + (bx1 - bx0) * i / 2
        cur = i == idx
        r = 13 + (5 * (0.5 + 0.5 * math.sin(t * 3)) if cur else 0)
        col = AMBER if cur else ((150, 158, 175) if i < idx else (60, 72, 98))
        d.ellipse([x - r, by - r, x + r, by + r], fill=col)
        d.text((x - d.textlength(e, font=f_tick) / 2, by + 22), e, font=f_tick,
               fill=INK if cur else GRAY)


def era_1914(d, t):
    k = ease(t / 0.5)
    f_year = font(150)
    yw = d.textlength("1914", font=f_year)
    d.text(((W - yw) / 2, 120 - 40 * (1 - k)), "1914", font=f_year,
           fill=(*AMBER, int(255 * k)))
    k2 = ease((t - 0.35) / 0.4)
    if k2 > 0:
        ctext(d, W / 2, 320, "日本初のエスカレーター", font(72), (*INK, int(255 * k2)))
    k3 = ease((t - 0.7) / 0.4)
    if k3 > 0:
        ctext(d, W / 2, 430, "3月8日、東京大正博覧会で試運転 → 秋には三越に常設",
              font(40), (*GRAY, int(255 * k3)))
    kp = ease((t - 0.9) / 0.5)
    if kp > 0:
        # 斜めのステップと案内係
        for i in range(5):
            x, y = 760 + i * 90, 800 - i * 44
            d.rounded_rectangle([x - 44, y - 12, x + 44, y + 12], radius=5,
                                fill=(46, 66, 100, int(255 * kp)))
        _silhouette(d, 640, 760, kp * 0.9, (46, 66, 100, int(255 * kp)))
        ctext(d, 640, 830, "乗り方の案内係もいた", font(28), (*GRAY, int(255 * kp)))
    _timeline(d, t, 1)


def era_trademark(d, t):
    k = ease(t / 0.5)
    ctext(d, W / 2, 180, "ESCALATOR", font(120), (*AMBER, int(255 * k)))
    k1 = ease((t - 0.4) / 0.4)
    if k1 > 0:
        d.rounded_rectangle([1380, 190, 1520, 260], radius=12, outline=RED, width=6)
        ctext(d, 1450, 200, "商標", font(44), RED)
    k2 = ease((t - 0.9) / 0.5)
    if k2 > 0:
        ctext(d, W / 2, 400, "オーチス社の商品名 → 他社は名乗れない", font(44),
              (*INK, int(255 * k2)))
        ctext(d, W / 2, 490, "日本での呼び名は「自動階段」", font(48), (*ACCENT, int(255 * k2)))
    k3 = ease((t - 5.0) / 0.6)
    if k3 > 0:
        d.line([660, 530, 1260, 530], fill=(*RED, int(200 * k3)), width=8)
        ctext(d, W / 2, 580, "1950年ごろ商標が切れて、誰でも使える言葉に",
              font(42), (*GREEN, int(255 * k3)))
        ctext(d, W / 2, 680, "ホッチキス・セロテープと同じ「元・商品名」",
              font(36), (*GRAY, int(255 * k3)))
    _timeline(d, t, 2)


CLIPS = {
    "esc_loop": (52.2, lambda: esc_loop),
    "ronsou": (33.7, lambda: ronsou),
    "wheelchair_step": (37.6, lambda: wheelchair_step),
    "era_1914": (31.0, lambda: era_1914),
    "era_trademark": (22.6, lambda: era_trademark),
}


def main() -> None:
    names = sys.argv[1:] or list(CLIPS)
    for name in names:
        dur, fn = CLIPS[name]
        render(name, dur, fn())


if __name__ == "__main__":
    main()
