#!/usr/bin/env python3
"""battery-80 用のインフォグラフィック動画クリップを4本生成する。

すべて battery-80 の該当カット実測尺（timing.json）に合わせ、
ループで巻き戻って見えないよう 1 秒前後余らせてある。

  hook_gauge.mp4     19.0s  充電ゲージが100%到達→寿命バーが削れていく（hook cut0-1）
  graph_decay.mp4    21.5s  100%放置 vs 20〜80%運用 の容量グラフ（ch2 cut15-16）
  toggle_80.mp4       7.5s  スマホ設定のトグルON→80%で充電停止（ch2 cut19）
  care_checklist.mp4  7.5s  電池ケア3項目がスタンプされていく（ch3 cut24）

出力: assets/clips/<name>.mp4（無音・台本の video: で全画面埋め込み）
実行: PYTHONPATH=. python3 scripts/gen_infographics.py
"""

import math
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
GREEN = (86, 216, 148)
AMBER = (255, 190, 80)
RED = (255, 100, 80)
GRAY = (150, 158, 175)
CARD = (24, 34, 54)

_cfg = Config.load()
_font_path = _cfg.find_pillow_font()


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(_font_path, size, index=0)


def ease(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def overshoot(x: float) -> float:
    """0→1 を少し行き過ぎてから戻る（スタンプ感）。"""
    x = max(0.0, min(1.0, x))
    c = 1.70158
    x -= 1
    return 1 + (c + 1) * x ** 3 + c * x ** 2


def ctext(d: ImageDraw.ImageDraw, cx: float, y: float, s: str,
          f: ImageFont.FreeTypeFont, fill) -> None:
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


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
    tmp = Path(tempfile.mkdtemp(prefix=f"info_{name}_"))
    for fi in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw_frame(ImageDraw.Draw(img, "RGBA"), fi / FPS)
        img.save(tmp / f"{fi:04d}.png")
    encode(tmp, Path(f"assets/clips/{name}.mp4"))


# ------------------------------------------------------------------
# 1) hook_gauge — 100%到達で寿命バーが削れていく
#    hook cut0 (8.82s) = 充電が進む / cut1 (9.13s) = 寿命が削れる
# ------------------------------------------------------------------
FULL_AT = 8.82


def hook_gauge(d: ImageDraw.ImageDraw, t: float) -> None:
    x0, y0, x1, y1 = 560, 380, 1360, 700
    pct = 100 * ease(t / FULL_AT) if t < FULL_AT else 100
    full = t >= FULL_AT

    # 本体
    d.rounded_rectangle([x0, y0, x1, y1], radius=40, outline=INK, width=8)
    d.rounded_rectangle([x1 + 8, (y0 + y1) / 2 - 55, x1 + 46, (y0 + y1) / 2 + 55],
                        radius=14, fill=INK)
    # 中身（80%を超えると琥珀→満タンで赤く脈動）
    if pct < 80:
        col = GREEN
    elif not full:
        col = AMBER
    else:
        pulse = 0.5 + 0.5 * math.sin((t - FULL_AT) * 5)
        col = tuple(int(RED[i] * (0.85 + 0.15 * pulse)) for i in range(3))
    fx = x0 + 20 + (x1 - x0 - 40) * pct / 100
    if pct > 1:
        d.rounded_rectangle([x0 + 20, y0 + 20, fx, y1 - 20], radius=24, fill=col)
    # 80%の目盛り
    mx = x0 + 20 + (x1 - x0 - 40) * 0.8
    d.line([mx, y0 - 26, mx, y0 - 6], fill=GRAY, width=5)
    d.text((mx - 34, y0 - 78), "80%", font=font(40), fill=GRAY)

    # %カウンタ（電池の中・縁取り付き。下部はテロップ用に空けておく）
    f_pct = font(130)
    s_pct = f"{int(pct)}%"
    d.text(((x0 + x1) / 2 - d.textlength(s_pct, font=f_pct) / 2,
            (y0 + y1) / 2 - 75), s_pct, font=f_pct, fill=INK,
           stroke_width=6, stroke_fill=(10, 14, 24))

    # 満タン到達フラッシュ
    if full and t - FULL_AT < 0.5:
        a = int(200 * (1 - (t - FULL_AT) / 0.5))
        d.rounded_rectangle([x0 - 14, y0 - 14, x1 + 60, y1 + 14], radius=48,
                            outline=(255, 255, 255, a), width=10)

    # 寿命バー（満タン後に右から削れていく）。テロップと重ならないよう画面上部
    bx0, bx1, by0, by1 = 560, 1360, 160, 208
    d.text((bx0, by0 - 64), "電池寿命", font=font(44), fill=INK)
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=20, fill=(30, 40, 60))
    life = 1.0 if not full else 1.0 - 0.35 * ease((t - FULL_AT) / 8.0)
    lx = bx0 + (bx1 - bx0) * life
    lcol = GREEN if not full else tuple(
        int(GREEN[i] + (RED[i] - GREEN[i]) * (1 - life) / 0.35) for i in range(3))
    d.rounded_rectangle([bx0, by0, lx, by1], radius=20, fill=lcol)
    if full:  # 削れている先端の火花
        for k in range(3):
            ph = (t * 7 + k * 2.1) % 1.0
            d.ellipse([lx - 4 + 26 * ph, by0 - 10 - 22 * ph,
                       lx + 6 + 26 * ph, by0 - 22 * ph],
                      fill=(255, 170, 90, int(220 * (1 - ph))))


# ------------------------------------------------------------------
# 2) graph_decay — 放置実験の容量グラフ
#    ch2 cut15 (12.21s) = 赤線 / cut16 (8.12s) = 緑線＋差のバッジ
# ------------------------------------------------------------------
G_SPLIT = 12.21
PX0, PX1, PY0, PY1 = 360, 1700, 260, 900   # プロット領域
VLO, VHI = 60.0, 102.0                      # y軸の値域


def _ypix(v: float) -> float:
    return PY0 + (VHI - v) / (VHI - VLO) * (PY1 - PY0)


def _curve_red(u: float) -> float:   # 100%のまま放置 → 70%まで低下
    return 100 - 30 * (u ** 0.85)


def _curve_green(u: float) -> float:  # 20〜80%で運用 → 92%を維持
    return 100 - 8 * (u ** 0.9)


def _draw_curve(d, fn, prog: float, col, width=7) -> tuple:
    pts = []
    steps = 120
    for i in range(int(steps * prog) + 1):
        u = i / steps
        pts.append((PX0 + (PX1 - PX0) * u, _ypix(fn(u))))
    if len(pts) >= 2:
        d.line(pts, fill=col, width=width, joint="curve")
    return pts[-1] if pts else (PX0, _ypix(100))


def graph_decay(d: ImageDraw.ImageDraw, t: float) -> None:
    # 軸とグリッド
    for v in (100, 90, 80, 70):
        y = _ypix(v)
        d.line([PX0, y, PX1, y], fill=(40, 52, 76), width=2)
        d.text((PX0 - 96, y - 22), f"{v}%", font=font(34), fill=GRAY)
    d.line([PX0, PY0 - 20, PX0, PY1], fill=GRAY, width=4)
    d.line([PX0, PY1, PX1 + 10, PY1], fill=GRAY, width=4)
    d.text((PX0, PY0 - 68), "残り容量のイメージ", font=font(38), fill=INK)
    d.text((PX1 - 330, PY1 + 26), "時間がたつほど →", font=font(36), fill=GRAY)

    # 赤線: 100%のまま放置
    rp = ease((t - 1.0) / (G_SPLIT - 2.0))
    if rp > 0:
        tip = _draw_curve(d, _curve_red, rp, RED)
        d.ellipse([tip[0] - 12, tip[1] - 12, tip[0] + 12, tip[1] + 12], fill=RED)
        if rp > 0.35:
            d.text((tip[0] - 320, tip[1] - 78), "100%のまま保管",
                   font=font(42), fill=RED)
    # 緑線: 20〜80%で運用
    gp = ease((t - G_SPLIT - 0.3) / 4.5)
    if gp > 0:
        tip = _draw_curve(d, _curve_green, gp, GREEN)
        d.ellipse([tip[0] - 12, tip[1] - 12, tip[0] + 12, tip[1] + 12], fill=GREEN)
        if gp > 0.35:
            d.text((tip[0] - 330, tip[1] - 80), "20〜80%で運用",
                   font=font(42), fill=GREEN)
    # 差のバッジ
    bp = overshoot((t - G_SPLIT - 5.2) / 0.4)
    if bp > 0:
        bw, bh = 560 * bp, 120 * bp
        cx, cy = 1280, 520
        d.rounded_rectangle([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2],
                            radius=26 * bp, fill=(58, 44, 12),
                            outline=AMBER, width=max(1, int(5 * bp)))
        if bp > 0.6:
            ctext(d, cx, cy - 34, "減りかたに数倍の差", font(56), AMBER)
    d.text((PX1 - 620, H - 60), "※研究報告の傾向を単純化したイメージ",
           font=font(28), fill=(110, 118, 134))


# ------------------------------------------------------------------
# 3) toggle_80 — 設定トグルON→80%で充電が止まる
#    ch2 cut19 (6.97s)
# ------------------------------------------------------------------
def _toggle(d, x, y, on: float) -> None:
    """トグルスイッチ。on は 0(オフ)〜1(オン) の補間。"""
    track = tuple(int((70, 80, 96)[i] + (GREEN[i] - (70, 80, 96)[i]) * on)
                  for i in range(3))
    d.rounded_rectangle([x, y, x + 108, y + 56], radius=28, fill=track)
    kx = x + 8 + 52 * on
    d.ellipse([kx, y + 6, kx + 44, y + 50], fill=(255, 255, 255))


def toggle_80(d: ImageDraw.ImageDraw, t: float) -> None:
    a = ease(t / 0.5)
    dy = 40 * (1 - a)  # 登場で少し浮き上がる
    px0, py0, px1, py1 = 660, 120 + dy, 1260, 960 + dy
    d.rounded_rectangle([px0, py0, px1, py1], radius=56, fill=(26, 32, 44),
                        outline=(90, 98, 114), width=6)
    sx0, sy0, sx1, sy1 = px0 + 26, py0 + 54, px1 - 26, py1 - 26
    d.rounded_rectangle([sx0, sy0, sx1, sy1], radius=34, fill=(14, 18, 28))
    d.rounded_rectangle([(px0 + px1) / 2 - 70, py0 + 18, (px0 + px1) / 2 + 70,
                         py0 + 36], radius=9, fill=(8, 10, 16))
    ctext(d, (sx0 + sx1) / 2, sy0 + 28, "設定", font(40), INK)

    rows = [("充電上限", "iPhone", 1.5), ("いたわり充電", "Android", 2.9)]
    for i, (label, sub, at) in enumerate(rows):
        ry = sy0 + 110 + i * 150
        d.rounded_rectangle([sx0 + 22, ry, sx1 - 22, ry + 124], radius=22,
                            fill=CARD)
        d.text((sx0 + 48, ry + 20), label, font=font(42), fill=INK)
        d.text((sx0 + 48, ry + 74), sub, font=font(30), fill=GRAY)
        _toggle(d, sx1 - 160, ry + 34, ease((t - at) / 0.3))

    # バッテリーバー: トグルON後に55%→80%で停止
    gy = sy0 + 470
    d.text((sx0 + 48, gy - 58), "バッテリー", font=font(34), fill=GRAY)
    d.rounded_rectangle([sx0 + 48, gy, sx1 - 48, gy + 56], radius=18,
                        fill=(30, 40, 60))
    pct = 55 + 25 * ease((t - 3.6) / 1.8)
    gx = sx0 + 48 + (sx1 - sx0 - 96) * pct / 100
    d.rounded_rectangle([sx0 + 48, gy, gx, gy + 56], radius=18, fill=GREEN)
    ctext(d, (sx0 + sx1) / 2, gy + 72, f"{int(pct)}%", font(48), INK)

    # 80%で停止 → チェックが押される
    sp = overshoot((t - 5.7) / 0.35)
    if sp > 0:
        cx, cy, r = (sx0 + sx1) / 2, gy + 230, 62 * sp
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN)
        if sp > 0.5:
            lw = max(6, int(10 * sp))
            d.line([cx - 26, cy + 2, cx - 8, cy + 22], fill=(255, 255, 255),
                   width=lw)
            d.line([cx - 8, cy + 22, cx + 30, cy - 20], fill=(255, 255, 255),
                   width=lw)
        if sp > 0.8:
            ctext(d, cx, cy + 84, "80%で自動ストップ", font(36), GREEN)


# ------------------------------------------------------------------
# 4) care_checklist — 電池ケア3項目がスタンプされる
#    ch3 cut24 (6.84s)
# ------------------------------------------------------------------
CARE_ITEMS = [
    ("高温を避ける", "車内・直射日光はNG", 0.7),
    ("ながら重いゲームを控える", "充電中は電池が熱くなる", 2.3),
    ("充電上限・最適化充電をオン", "設定はこれ1回だけ", 3.9),
]


def care_checklist(d: ImageDraw.ImageDraw, t: float) -> None:
    ctext(d, W / 2, 150, "今日からできる電池ケア", font(64), INK)
    d.line([W / 2 - 300, 240, W / 2 + 300, 240], fill=ACCENT, width=6)
    for i, (label, sub, at) in enumerate(CARE_ITEMS):
        p = ease((t - at) / 0.35)
        if p <= 0:
            continue
        y = 330 + i * 190
        ox = -60 * (1 - p)  # 左からスッと入る
        a = int(255 * p)
        d.rounded_rectangle([460 + ox, y, 1460 + ox, y + 150], radius=26,
                            fill=(*CARD, a))
        d.text((640 + ox, y + 26), f"{i + 1}. {label}", font=font(48),
               fill=(*INK, a))
        d.text((640 + ox, y + 92), sub, font=font(32), fill=(*GRAY, a))
        # チェックスタンプ
        sp = overshoot((t - at - 0.55) / 0.3)
        if sp > 0:
            cx, cy, r = 545 + ox, y + 75, 44 * sp
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN)
            if sp > 0.5:
                lw = max(5, int(9 * sp))
                d.line([cx - 18, cy + 2, cx - 5, cy + 16], fill=(255, 255, 255),
                       width=lw)
                d.line([cx - 5, cy + 16, cx + 22, cy - 14], fill=(255, 255, 255),
                       width=lw)


def main() -> None:
    render("hook_gauge", 19.0, hook_gauge)
    render("graph_decay", 21.5, graph_decay)
    render("toggle_80", 7.5, toggle_80)
    render("care_checklist", 7.5, care_checklist)


if __name__ == "__main__":
    main()
