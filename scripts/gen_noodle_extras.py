#!/usr/bin/env python3
"""cup-noodle プロジェクト用のアニメクリップを生成する。

  cup_timer.mp4      26.0s  3分タイマー茶番（30秒で開けてバリバリ→3分と比較）
  noodle_pore.mp4    47.0s  麺の穴5フェーズ（生麺→揚げ→穴→お湯染み込み→3分ゲージ）
  cup_structure.mp4  20.5s  中間保持構造（麺の宙づりと3つの機能）
  era_1958/1971/2005 各カード 安藤百福の年表

フェーズ境界は timing.json のカット実測に同期（コメントの秒数）。
実行: PYTHONPATH=. python3 scripts/gen_noodle_extras.py
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
NOODLE = (238, 210, 140)
NOODLE_DK = (206, 172, 96)
BROTH = (244, 170, 90)

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
    tmp = Path(tempfile.mkdtemp(prefix=f"cn_{name}_"))
    for fi in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw_frame(ImageDraw.Draw(img, "RGBA"), fi / FPS)
        img.save(tmp / f"{fi:04d}.png")
    encode(tmp, Path(f"assets/clips/{name}.mp4"))


def _cup(d, cx, cy, w_top=280, w_bot=210, h=340, lid=0.0):
    """カップ（台形）。lid=フタの開き具合0〜1。"""
    d.polygon([(cx - w_top / 2, cy - h / 2), (cx + w_top / 2, cy - h / 2),
               (cx + w_bot / 2, cy + h / 2), (cx - w_bot / 2, cy + h / 2)],
              fill=(246, 243, 236))
    d.rectangle([cx - w_top / 2, cy - h / 2 + h * 0.42, cx + w_top / 2 - (w_top - w_bot) * 0.42 / 2,
                 cy - h / 2 + h * 0.62], fill=(212, 60, 60))
    ctext(d, cx, cy - h * 0.04, "NOODLE", font(38), (250, 246, 240))
    # フタ
    if lid < 0.99:
        ang = -lid * 1.2
        lx = cx - w_top / 2
        d.ellipse([cx - w_top / 2 - 8, cy - h / 2 - 16, cx + w_top / 2 + 8, cy - h / 2 + 16],
                  fill=(232, 228, 218), outline=(150, 146, 138), width=3)
    else:
        d.ellipse([cx + w_top / 2 - 40, cy - h / 2 - 120, cx + w_top / 2 + 120, cy - h / 2 - 40],
                  fill=(232, 228, 218), outline=(150, 146, 138), width=3)


def _crunchy(d, cx, cy, scale=1.0, col=NOODLE_DK):
    """バリバリ麺（ジグザグ線）。"""
    rr = random.Random(3)
    for i in range(6):
        y = cy - 50 * scale + i * 20 * scale
        pts = []
        for j in range(9):
            pts.append((cx - 120 * scale + j * 30 * scale,
                        y + (8 if j % 2 else -8) * scale + rr.uniform(-3, 3)))
        d.line(pts, fill=col, width=int(7 * scale), joint="curve")


def _wavy(d, cx, cy, scale=1.0, t=0.0):
    """ふっくら麺（なめらか波）。"""
    for i in range(6):
        y = cy - 50 * scale + i * 20 * scale
        pts = []
        for j in range(25):
            x = cx - 120 * scale + j * 10 * scale
            pts.append((x, y + math.sin(j / 3 + i + t) * 7 * scale))
        d.line(pts, fill=NOODLE, width=int(7 * scale), joint="curve")


# ------------------------------------------------------------------
# 1) cup_timer — 3分待てない茶番（開封=6.74 / バリバリ=13.99 / 比較=19.09）
# ------------------------------------------------------------------
T_OPEN, T_CRUNCH, T_COMPARE = 6.74, 13.99, 19.09


def cup_timer(d, t):
    if t < T_CRUNCH:
        opened = t >= T_OPEN
        _caption(d, "待ち時間 3:00" if not opened else "我慢の限界（経過 0:30）",
                 INK if not opened else RED)
        _cup(d, W / 2 - 200, 560, lid=1.0 if opened else 0.0)
        # 湯気
        if not opened:
            for i in range(3):
                x = W / 2 - 240 + i * 40
                yy = 330 - (t * 40 + i * 25) % 90
                d.ellipse([x, yy, x + 16, yy + 16], fill=(220, 224, 232, 90))
        # タイマー
        el = min(t * (30 / T_OPEN), 30) if not opened else 30
        mm, ss = divmod(int(el), 60)
        d.rounded_rectangle([W / 2 + 60, 420, W / 2 + 560, 700], radius=28, fill=(24, 34, 54))
        ctext(d, W / 2 + 310, 452, "経過時間", font(36), GRAY)
        ctext(d, W / 2 + 310, 510, f"{mm}:{ss:02d}", font(130),
              INK if not opened else RED)
        if opened:
            blink = (int(t * 2) % 2) == 0
            if blink:
                ctext(d, W / 2 + 310, 720, "まだ2分30秒あります", font(34), RED)
        return
    if t < T_COMPARE:
        _caption(d, "30秒の麺", RED)
        d.rounded_rectangle([W / 2 - 320, 380, W / 2 + 320, 800], radius=28, fill=(24, 34, 54))
        _crunchy(d, W / 2, 560, 1.6)
        ctext(d, W / 2, 700, "バリバリ（芯まで硬い）", font(44), RED)
        return
    # 比較
    _caption(d, "30秒 と 3分、同じ麺")
    for i, (label, col, good) in enumerate((("30秒", RED, False), ("3分", GREEN, True))):
        cx = W / 2 + (i * 2 - 1) * 400
        d.rounded_rectangle([cx - 320, 340, cx + 320, 820], radius=28, fill=(24, 34, 54))
        ctext(d, cx, 372, label, font(52), col)
        if good:
            _wavy(d, cx, 580, 1.5, t)
            ctext(d, cx, 730, "ふっくら もちもち", font(40), GREEN)
        else:
            _crunchy(d, cx, 580, 1.5)
            ctext(d, cx, 730, "バリバリ", font(40), RED)


# ------------------------------------------------------------------
# 2) noodle_pore — 麺の穴5フェーズ（47秒）
#    揚げ=9.75 / 穴=17.06 / 染み込み=30.14 / 3分ゲージ=37.64
# ------------------------------------------------------------------
N_FRY, N_PORE, N_SOAK, N_TIMER = 9.75, 17.06, 30.14, 37.64
_pores = [(random.Random(i * 3 + 1).uniform(-1, 1), random.Random(i * 7 + 2).uniform(-1, 1))
          for i in range(60)]


def _slab(d, fill=NOODLE):
    d.rounded_rectangle([560, 340, 1360, 760], radius=48, fill=fill,
                        outline=NOODLE_DK, width=6)


def noodle_pore(d, t):
    if t < N_FRY:
        _caption(d, "生の麺は、水分たっぷり")
        _slab(d)
        for (px_, py_) in _pores[:24]:
            x, y = 960 + px_ * 340, 550 + py_ * 160
            d.ellipse([x - 16, y - 22, x + 16, y + 22], fill=(90, 170, 240, 220))
        ctext(d, 960, 800, "麺の断面（イメージ）", font(34), GRAY)
        return
    if t < N_PORE:
        _caption(d, "揚げる = 水分が蒸気になって弾け飛ぶ")
        # 油
        oy = 700
        d.rectangle([460, oy, 1460, 860], fill=(230, 168, 60, 220))
        rb = random.Random(int(t * 8))
        for _ in range(14):
            x = rb.uniform(480, 1440)
            y = rb.uniform(oy + 8, 840)
            r = rb.uniform(4, 12)
            d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 230, 170), width=3)
        _slab(d)
        # 蒸気が飛び出す
        k = (t - N_FRY)
        for i, (px_, py_) in enumerate(_pores[:24]):
            kk = (k * 0.8 + i * 0.13) % 1.6
            x = 960 + px_ * 340
            y = 550 + py_ * 160 - kk * 260
            a = max(0, int(230 * (1 - kk / 1.6)))
            d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(235, 238, 245, a))
        return
    if t < N_SOAK:
        _caption(d, "水分の跡に、無数の小さな穴が残る")
        _slab(d, fill=NOODLE_DK)
        for (px_, py_) in _pores:
            x, y = 960 + px_ * 350, 550 + py_ * 170
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(60, 44, 24))
        ctext(d, 960, 800, "乾いてカチカチ = 長持ちする保存食", font(36), GRAY)
        return
    if t < N_TIMER:
        _caption(d, "お湯が穴に染み込んで、ふっくら戻る")
        _slab(d)
        k = ease((t - N_SOAK) / 5.5)
        n_fill = int(len(_pores) * k)
        for i, (px_, py_) in enumerate(_pores):
            x, y = 960 + px_ * 350, 550 + py_ * 170
            col = (244, 150, 70) if i < n_fill else (60, 44, 24)
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=col)
        # 上からお湯
        d.rectangle([930, 220, 990, 340], fill=(120, 190, 250, 200))
        return
    # 3分ゲージ
    _caption(d, "3分 = お湯が芯まで届く時間")
    k = ease((t - N_TIMER) / 6.0)
    # 断面円（表面→芯へ染みる）
    cx, cy, R = 660, 570, 210
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=NOODLE_DK)
    rr = R * (1 - 0.9 * k)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(244, 150, 70))
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=NOODLE_DK)
    ctext(d, cx, cy + R + 26, "表面 → 芯へ", font(36), GRAY)
    # タイマー
    mm, ss = divmod(int(180 * k), 60)
    d.rounded_rectangle([1060, 430, 1560, 710], radius=28, fill=(24, 34, 54))
    ctext(d, 1310, 462, "染み込み時間", font(36), GRAY)
    ctext(d, 1310, 520, f"{mm}:{ss:02d}", font(130), GREEN if k >= 1.0 else INK)


# ------------------------------------------------------------------
# 3) cup_structure — 中間保持（機能表示=11.8 / DUR 20.5）
# ------------------------------------------------------------------
C_FUNC = 11.8


def cup_structure(d, t):
    _caption(d, "麺はカップの中で、宙づり" if t < C_FUNC else "宙づりの3つの仕事")
    # カップ断面
    cx = W // 2
    top_w, bot_w, cy0, cy1 = 560, 420, 300, 860
    d.line([cx - top_w / 2, cy0, cx - bot_w / 2, cy1], fill=INK, width=8)
    d.line([cx + top_w / 2, cy0, cx + bot_w / 2, cy1], fill=INK, width=8)
    d.line([cx - bot_w / 2, cy1, cx + bot_w / 2, cy1], fill=INK, width=8)
    # 麺ブロック（中間）
    ny = 620 + 6 * math.sin(t * 1.6)
    d.rounded_rectangle([cx - 230, ny - 90, cx + 230, ny + 90], radius=24, fill=NOODLE)
    rrng = random.Random(4)
    for _ in range(40):
        x = rrng.uniform(cx - 210, cx + 210)
        y = rrng.uniform(ny - 74, ny + 74)
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=NOODLE_DK)
    # 具（上）
    for i, col in enumerate(((222, 120, 110), (120, 190, 120), (240, 214, 120))):
        d.ellipse([cx - 130 + i * 110, ny - 140, cx - 80 + i * 110, ny - 96], fill=col)
    # 下の空間ラベル
    d.text((cx + bot_w / 2 + 36, 760), "下は空間", font=font(40), fill=ACCENT)
    d.line([cx + bot_w / 2 + 24, 780, cx + 120, 800], fill=(*ACCENT, 200), width=4)
    if t >= C_FUNC:
        k = t - C_FUNC
        feats = [("お湯が全体に回る", GREEN), ("落としても麺が割れない", AMBER),
                 ("麺がカップを支える柱になる", ACCENT)]
        for i, (s, col) in enumerate(feats):
            kk = ease((k - i * 1.6) / 0.5)
            if kk <= 0:
                continue
            d.rounded_rectangle([200, 330 + i * 150, 200 + 470 * kk, 430 + i * 150],
                                radius=20, fill=(24, 34, 54, int(255 * kk)))
            if kk > 0.7:
                d.text((230, 358 + i * 150), s, font=font(38), fill=col)


# ------------------------------------------------------------------
# 3.5) salt_gauge — 塩分ゲージ（目標比較=10.22 / スープを残す=19.88 / DUR 31.7）
#      1杯 約5g / 目標 男7.5g・女6.5g / スープを残すと2〜3割減
# ------------------------------------------------------------------
S_TARGET, S_LEAVE = 10.22, 19.88
S_MAX = 8.0  # ゲージ上限（g）


def _bar(d, x, y, w, h, frac, col, label, grams, f_label, f_val):
    d.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=(24, 34, 54))
    if frac > 0:
        bw = max(36, w * min(frac, 1.0))
        d.rounded_rectangle([x, y, x + bw, y + h], radius=18, fill=col)
    d.text((x, y - 54), label, font=f_label, fill=INK)
    d.text((x + w + 28, y + h / 2 - 26), grams, font=f_val, fill=col)


def salt_gauge(d, t):
    f_label, f_val = font(40), font(46)
    x, w, h = 360, 900, 76
    if t < S_TARGET:
        _caption(d, "カップ麺1杯の塩分")
        k = ease(t / 2.5)
        g = 5.0 * k
        _bar(d, x, 480, w, h, g / S_MAX, RED, "カップ麺 1杯", f"{g:.1f}g", f_label, f_val)
        if k >= 1.0:
            ctext(d, W / 2, 640, "およそ5g（スープまで飲んだ場合・推計）", font(36), GRAY)
        return
    if t < S_LEAVE:
        _caption(d, "1日の目標量と比べると……")
        _bar(d, x, 340, w, h, 5.0 / S_MAX, RED, "カップ麺 1杯", "5.0g", f_label, f_val)
        k1 = ease((t - S_TARGET) / 0.8)
        if k1 > 0:
            _bar(d, x, 540, w, h, 7.5 / S_MAX * k1, GRAY, "1日の目標（男性）",
                 "7.5g未満", f_label, f_val)
        k2 = ease((t - S_TARGET - 0.8) / 0.8)
        if k2 > 0:
            _bar(d, x, 740, w, h, 6.5 / S_MAX * k2, GRAY, "1日の目標（女性）",
                 "6.5g未満", f_label, f_val)
        if k2 >= 1.0:
            ctext(d, W / 2, 900, "1杯で1日分の7割前後", font(44), AMBER)
        return
    # スープを残す
    _caption(d, "スープを残すだけで")
    k = ease((t - S_LEAVE) / 2.0)
    g = 5.0 - 1.4 * k  # 約3割減
    col = GREEN if k >= 1.0 else RED
    _bar(d, x, 420, w, h, g / S_MAX, col, "麺と具だけ食べる", f"{g:.1f}g", f_label, f_val)
    kk = ease((t - S_LEAVE - 2.2) / 0.6)
    if kk > 0:
        d.rounded_rectangle([x, 640, x + 640 * kk, 750], radius=20,
                            fill=(24, 44, 34, int(255 * kk)))
        if kk > 0.7:
            d.text((x + 34, 668), "塩分を2〜3割カットできると言われている",
                   font=font(38), fill=GREEN)
    ctext(d, W / 2, 900, "本当の注意点は、添加物より塩分", font(40), GRAY)


# ------------------------------------------------------------------
# 4) 時代カード（安藤百福の年表バー付き）
# ------------------------------------------------------------------
ERAS = ["1958 チキンラーメン", "1966 渡米", "1971 カップヌードル", "2005 宇宙へ"]


def _silhouette(d, cx, cy, scale, col):
    r = int(58 * scale)
    d.ellipse([cx - r, cy - r * 2.1, cx + r, cy - 0.1 * r], fill=col)
    d.pieslice([cx - r * 2, cy - r * 0.2, cx + r * 2, cy + r * 2.6],
               start=180, end=360, fill=col)


def make_era(idx, year, title, persons, sub):
    def draw(d, t):
        k = ease(t / 0.5)
        f_year = font(150)
        yw = d.textlength(year, font=f_year)
        d.text(((W - yw) / 2, 120 - 40 * (1 - k)), year, font=f_year,
               fill=(*AMBER, int(255 * k)))
        k2 = ease((t - 0.35) / 0.4)
        if k2 > 0:
            ctext(d, W / 2, 320, title, font(72), (*INK, int(255 * k2)))
        k3 = ease((t - 0.7) / 0.4)
        if k3 > 0:
            ctext(d, W / 2, 430, sub, font(42), (*GRAY, int(255 * k3)))
        for i, (name, role) in enumerate(persons):
            kp = ease((t - 0.9 - i * 0.25) / 0.4)
            if kp <= 0:
                continue
            cx = W / 2 + (i - (len(persons) - 1) / 2) * 420
            cy = 700 + 14 * math.sin(t * 1.4 + i)
            _silhouette(d, cx, cy, kp, (46, 66, 100, int(255 * kp)))
            ctext(d, cx, 770, name, font(46), (*INK, int(255 * kp)))
            ctext(d, cx, 828, role, font(30), (*GRAY, int(255 * kp)))
        bx0, bx1, by = 560, 1360, 952
        d.line([bx0, by, bx1, by], fill=(50, 64, 92), width=6)
        prog = ease((t - 0.4) / 1.2)
        d.line([bx0, by, bx0 + (bx1 - bx0) * prog * idx / (len(ERAS) - 1), by],
               fill=(*ACCENT, 255), width=6)
        f_tick = font(24)
        for i, e in enumerate(ERAS):
            x = bx0 + (bx1 - bx0) * i / (len(ERAS) - 1)
            cur = i == idx
            r = 13 + (5 * (0.5 + 0.5 * math.sin(t * 3)) if cur else 0)
            col = AMBER if cur else ((150, 158, 175) if i < idx else (60, 72, 98))
            d.ellipse([x - r, by - r, x + r, by + r], fill=col)
            d.text((x - d.textlength(e, font=f_tick) / 2, by + 22), e,
                   font=f_tick, fill=INK if cur else GRAY)
    return draw


CLIPS = {
    "cup_timer": (26.0, lambda: cup_timer),
    "noodle_pore": (47.0, lambda: noodle_pore),
    "cup_structure": (20.5, lambda: cup_structure),
    "salt_gauge": (31.7, lambda: salt_gauge),
}


def main() -> None:
    # 引数でクリップ名を渡すとそれだけ再生成する（例: salt_gauge）
    if len(sys.argv) > 1:
        for name in sys.argv[1:]:
            dur, fn = CLIPS[name]
            render(name, dur, fn())
        return
    render("cup_timer", 26.0, cup_timer)
    render("salt_gauge", 31.7, salt_gauge)
    render("noodle_pore", 47.0, noodle_pore)
    render("cup_structure", 20.5, cup_structure)
    render("era_1958", 24.0, make_era(
        0, "1958", "チキンラーメン、誕生", [("安藤百福", "48歳の再出発")],
        "裏庭の小屋から生まれた、お湯で戻る麺"))
    render("era_1971", 21.5, make_era(
        2, "1971", "カップヌードル、誕生", [("安藤百福", "どんぶりのない国で着想")],
        "カップがどんぶりになればいい"))
    render("era_2005", 14.5, make_era(
        3, "2005", "宇宙へ", [("安藤百福", "91歳")],
        "宇宙食ラーメンを開発、生涯現役"))


if __name__ == "__main__":
    main()
