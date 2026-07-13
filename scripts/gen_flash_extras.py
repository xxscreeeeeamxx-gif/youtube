#!/usr/bin/env python3
"""flash-memory プロジェクト用のアニメクリップを生成する。

  usb_alive.mp4   15.5s  洗濯後のUSBを挿す→認識→写真全部無事✓（茶番の回収）
  flash_cell.mp4  55.6s  電子の檻4フェーズ（構造/壁→書き込みトンネル→0と1→一括消去=フラッシュ）
  era_1980.mp4    28.0s  時代カード: 1980 舛岡富士雄・電子の檻の発明
  era_1987.mp4    19.0s  時代カード: 1987 NAND型の誕生
  era_2006.mp4    23.0s  時代カード: 2006 発明の対価・和解

フェーズ境界は timing.json のカット実測に同期（コメントの秒数）。
実行: PYTHONPATH=. python3 scripts/gen_flash_extras.py
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
CARD = (24, 34, 54)
ELECTRON = (120, 210, 255)

_cfg = Config.load()
_font_path = _cfg.find_pillow_font()


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(_font_path, size, index=0)


def ease(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def ctext(d, cx, y, s, f, fill):
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
    tmp = Path(tempfile.mkdtemp(prefix=f"fm_{name}_"))
    for fi in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw_frame(ImageDraw.Draw(img, "RGBA"), fi / FPS)
        img.save(tmp / f"{fi:04d}.png")
    encode(tmp, Path(f"assets/clips/{name}.mp4"))


def _caption(d, s, col=INK):
    ctext(d, W / 2, 150, s, font(60), col)


def _check(d, cx, cy, r, col=GREEN):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*col, 240))
    lw = max(6, int(r / 6))
    d.line([cx - r * 0.4, cy + r * 0.05, cx - r * 0.1, cy + r * 0.35],
           fill=(255, 255, 255), width=lw)
    d.line([cx - r * 0.1, cy + r * 0.35, cx + r * 0.45, cy - r * 0.3],
           fill=(255, 255, 255), width=lw)


# ------------------------------------------------------------------
# 1) usb_alive — USB認識→写真サムネ全部無事（成功✓は開始1.4秒）
# ------------------------------------------------------------------
_rng = random.Random(5)
_thumbs = [( (200, 235, 200), (150, 200, 120) ), ((200, 215, 245), (120, 160, 220)),
           ((245, 220, 200), (220, 170, 120)), ((235, 205, 235), (190, 130, 200)),
           ((215, 235, 240), (130, 190, 210)), ((240, 235, 205), (210, 190, 110))]


def usb_alive(d, t):
    # ウィンドウ
    wx0, wy0, wx1, wy1 = 360, 200, 1560, 900
    d.rounded_rectangle([wx0 + 8, wy0 + 12, wx1 + 8, wy1 + 12], radius=24, fill=(0, 0, 0, 90))
    d.rounded_rectangle([wx0, wy0, wx1, wy1], radius=24, fill=(244, 246, 250))
    d.rounded_rectangle([wx0, wy0, wx1, wy0 + 72], radius=24, fill=(34, 40, 58))
    d.rectangle([wx0, wy0 + 40, wx1, wy0 + 72], fill=(34, 40, 58))
    d.text((wx0 + 28, wy0 + 18), "USBドライブ (E:)", font=font(34), fill=INK)
    if t < 0.9:
        # 認識中スピナー
        ctext(d, W / 2, 500, "ドライブを認識しています…", font(44), (90, 96, 110))
        cx, cy, r = W / 2, 660, 42
        a0 = (t * 300) % 360
        d.arc([cx - r, cy - r, cx + r, cy + r], start=a0, end=a0 + 260,
              fill=(120, 180, 255), width=10)
        return
    # 写真サムネイルが次々出る
    for i, (light, dark) in enumerate(_thumbs * 2):
        k = ease((t - 0.9 - i * 0.08) / 0.25)
        if k <= 0:
            continue
        r_, c_ = divmod(i, 4)
        x = wx0 + 70 + c_ * 290
        y = wy0 + 120 + r_ * 230
        wgt, hgt = 250 * k, 180 * k
        cx_, cy_ = x + 125, y + 100
        d.rounded_rectangle([cx_ - wgt / 2, cy_ - hgt / 2, cx_ + wgt / 2, cy_ + hgt / 2],
                            radius=12, fill=light)
        # 山と太陽の適当な写真アイコン
        if k > 0.7:
            d.ellipse([cx_ + wgt * 0.15, cy_ - hgt * 0.32, cx_ + wgt * 0.33, cy_ - hgt * 0.1],
                      fill=(250, 210, 90))
            d.polygon([(cx_ - wgt * 0.42, cy_ + hgt * 0.42), (cx_ - wgt * 0.05, cy_ - hgt * 0.15),
                       (cx_ + wgt * 0.3, cy_ + hgt * 0.42)], fill=dark)
    if t > 2.0:
        k = min(1.0, (t - 2.0) / 0.25)
        _check(d, W / 2, 550, 84 * k)
        if k >= 1.0:
            ctext(d, W / 2, 950, "写真はすべて無事です", font(52), GREEN)


# ------------------------------------------------------------------
# 2) flash_cell — 電子の檻（4フェーズ・55.6秒）
#    壁強調=8.56 / 書き込み=23.22 / 0と1=37.88 / 一括消去=46.23
# ------------------------------------------------------------------
F_WALL, F_WRITE, F_READ, F_ERASE = 8.56, 23.22, 37.88, 46.23
CX, CY = W // 2, 520          # 檻の中心
CW, CH = 460, 300             # 檻の大きさ
WALLPAD = 46                  # 壁の厚み
_els = [(random.Random(9).uniform(-1, 1), random.Random(i * 7 + 1).uniform(-0.8, 0.8),
         random.Random(i * 13 + 2).uniform(0, math.tau)) for i in range(8)]


def _electron(d, x, y, r=26, col=ELECTRON, alpha=255):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(*col, alpha),
              outline=(255, 255, 255, min(200, alpha)), width=3)
    d.line([x - r * 0.4, y, x + r * 0.4, y], fill=(10, 20, 34, alpha), width=5)


def _cage(d, heat_wall=0.0):
    # 絶縁体の壁（外枠）
    wall_col = tuple(int((88, 96, 120)[i] + (AMBER[i] - (88, 96, 120)[i]) * heat_wall)
                     for i in range(3))
    d.rounded_rectangle([CX - CW / 2 - WALLPAD, CY - CH / 2 - WALLPAD,
                         CX + CW / 2 + WALLPAD, CY + CH / 2 + WALLPAD],
                        radius=34, fill=(*wall_col, 255))
    # 檻の内側
    d.rounded_rectangle([CX - CW / 2, CY - CH / 2, CX + CW / 2, CY + CH / 2],
                        radius=22, fill=(16, 24, 42))


def _electron_pool(d, t, gone: float = 0.0):
    """下部の電子だまり。gone=1で空。"""
    by = 900
    for i in range(6):
        if i / 6.0 < gone:
            continue
        x = CX - 300 + i * 120
        y = by + 10 * math.sin(t * 1.5 + i)
        _electron(d, x, y, 24)


def flash_cell(d, t):
    if t < F_WRITE:
        # P0: 構造（8.56から壁を強調）
        hl = 0.5 + 0.5 * math.sin(t * 3) if t >= F_WALL else 0.0
        _caption(d, "1マス = 電子の檻" if t < F_WALL else "檻の周りは、電気を通さない壁")
        _cage(d, heat_wall=0.35 * hl)
        ctext(d, CX, CY - 24, "電子の檻", font(48), (90, 110, 150))
        # 壁ラベル
        lbl_col = AMBER if t >= F_WALL else GRAY
        d.line([CX + CW / 2 + WALLPAD + 10, CY, CX + CW / 2 + WALLPAD + 90, CY],
               fill=(*lbl_col, 255), width=5)
        d.text((CX + CW / 2 + WALLPAD + 104, CY - 26), "絶縁体の壁", font=font(42), fill=lbl_col)
        _electron_pool(d, t)
        ctext(d, CX, 968, "電子", font(34), GRAY)
        return
    if t < F_READ:
        # P1: 書き込み（トンネル効果で壁を通って檻へ）
        _caption(d, "書き込み = 高い電圧で、電子が壁をすり抜ける")
        _cage(d)
        ctext(d, CX - 320, 220, "", font(40), INK)
        # 高電圧表示
        blink = 0.6 + 0.4 * math.sin(t * 5)
        d.text((CX - CW / 2 - 320, CY - 30), "⚡ 高電圧", font=font(46),
               fill=(255, 214, 90, int(255 * blink)))
        # 電子が上昇して壁を抜ける
        n_in = 0
        for i, (ox, oy, ph) in enumerate(_els[:6]):
            k = ease((t - F_WRITE - 0.6 - i * 1.1) / 1.6)
            if k <= 0:
                x = CX - 300 + i * 120
                _electron(d, x, 900 + 10 * math.sin(t * 1.5 + i), 24)
                continue
            # 軌道: だまり→壁の下辺→檻の中
            sx = CX - 300 + i * 120
            tx = CX + ox * (CW / 2 - 60)
            ty = CY + oy * (CH / 2 - 60)
            x = sx + (tx - sx) * k
            y = 900 + (ty - 900) * k
            # 壁の帯内では半透明（すり抜け表現）
            wall_y0 = CY + CH / 2
            wall_y1 = CY + CH / 2 + WALLPAD
            alpha = 120 if wall_y0 < y < wall_y1 + 20 else 255
            _electron(d, x, y, 24, alpha=alpha)
            if k >= 1.0:
                n_in += 1
        _electron_pool(d, t, gone=min(1.0, (t - F_WRITE) / 8.0))
        return
    if t < F_ERASE:
        # P2: 保持と読み取り（電源OFFでも残る・0と1）
        _caption(d, "電源を切っても、電子は檻の中 = これが記憶")
        _cage(d)
        for i, (ox, oy, ph) in enumerate(_els[:6]):
            x = CX + ox * (CW / 2 - 60) + 3 * math.sin(t * 2 + ph)
            y = CY + oy * (CH / 2 - 60) + 3 * math.cos(t * 1.7 + ph)
            _electron(d, x, y, 24)
        # 電源OFFバッジ
        d.rounded_rectangle([180, 470, 470, 570], radius=20, fill=(40, 46, 60))
        ctext(d, 325, 496, "電源 OFF", font(46), (200, 120, 110))
        # 右: 0/1 ミニセル
        for j, (has, lbl) in enumerate(((True, "= 1"), (False, "= 0"))):
            mx, my = 1560, 380 + j * 260
            d.rounded_rectangle([mx - 90, my - 70, mx + 90, my + 70], radius=16,
                                fill=(88, 96, 120))
            d.rounded_rectangle([mx - 64, my - 46, mx + 64, my + 46], radius=10,
                                fill=(16, 24, 42))
            if has:
                _electron(d, mx, my, 20)
            d.text((mx + 108, my - 28), lbl, font=font(52), fill=INK)
        return
    # P3: 一括消去 = フラッシュ
    k = t - F_ERASE
    _caption(d, "消去は、一斉に引き抜いて一瞬 = フラッシュ", (255, 224, 130))
    _cage(d)
    for i, (ox, oy, ph) in enumerate(_els[:6]):
        kk = ease((k - 0.4 - i * 0.06) / 0.7)
        sx = CX + ox * (CW / 2 - 60)
        sy = CY + oy * (CH / 2 - 60)
        x = sx
        y = sy + (900 - sy) * kk
        alpha = 120 if CY + CH / 2 < y < CY + CH / 2 + WALLPAD + 20 else 255
        _electron(d, x, y, 24, alpha=alpha)
    # 白いフラッシュ（0.4〜0.7秒）
    if 0.35 < k < 0.75:
        a = int(230 * (1 - abs(k - 0.55) / 0.2))
        d.rectangle([0, 0, W, H], fill=(255, 255, 245, max(0, a)))
    if k > 1.6:
        kk = min(1.0, (k - 1.6) / 0.3)
        ctext(d, CX, CY - 30, "空っぽ = 消去完了", font(46), (*GRAY, int(255 * kk)))


# ------------------------------------------------------------------
# 3) 時代カード（フラッシュメモリ史の年表バー付き）
# ------------------------------------------------------------------
ERAS = ["1980 発明", "1984 世界へ", "1987 NAND", "2004 提訴", "2006 和解"]


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


def main() -> None:
    render("usb_alive", 15.5, usb_alive)
    render("flash_cell", 55.6, flash_cell)
    render("era_1980", 28.0, make_era(
        0, "1980", "電子の檻を発明", [("舛岡富士雄", "東芝の技術者")],
        "電源なしで記憶するメモリの特許を出願"))
    render("era_1987", 19.0, make_era(
        2, "1987", "NAND型、誕生", [("舛岡富士雄", "改良を続けた")],
        "安く、大容量に。今のUSBメモリの原型"))
    render("era_2006", 23.0, make_era(
        4, "2006", "発明の対価を求めて", [("舛岡富士雄", "東北大学 教授")],
        "2004年に提訴、2006年に和解が成立"))


if __name__ == "__main__":
    main()
