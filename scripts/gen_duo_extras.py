#!/usr/bin/env python3
"""battery-80-duo の茶番・開発秘話用クリップを生成する。

  batt_dead.mp4   19.5s  推し配信画面→電池1%→ブラックアウト（冒頭茶番）
  era_1970.mp4    19.0s  時代カード: エクソン／ウィッティンガム
  era_1980.mp4    27.0s  時代カード: グッドイナフ＋水島公一・電圧2倍
  era_1985.mp4    25.6s  時代カード: 吉野彰・燃えない電池
  era_1991.mp4    13.5s  時代カード: ソニー世界初の商用化
  era_2019.mp4    21.0s  時代カード: ノーベル化学賞

尺は timing.json のカット実測 + 約1秒（ループで巻き戻さないため）。
batt_dead のブラックアウトは2カット目の頭（6.48s）に同期。
時代カードは下部に共通の年表バー（立ち絵と重ならない中央寄せ）。

実行: PYTHONPATH=. python3 scripts/gen_duo_extras.py
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
    tmp = Path(tempfile.mkdtemp(prefix=f"duo_{name}_"))
    for fi in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw_frame(ImageDraw.Draw(img, "RGBA"), fi / FPS)
        img.save(tmp / f"{fi:04d}.png")
    encode(tmp, Path(f"assets/clips/{name}.mp4"))


# ------------------------------------------------------------------
# 1) batt_dead — 推し配信画面→電池切れ（ブラックアウトは2カット目の頭）
# ------------------------------------------------------------------
DEAD_AT = 6.48


def batt_dead(d: ImageDraw.ImageDraw, t: float) -> None:
    if t >= DEAD_AT:
        # ブラックアウト: 空の電池アイコンが点滅
        blink = (int(t * 1.4) % 2) == 0
        if blink:
            x0, y0, x1, y1 = 860, 480, 1060, 570
            d.rounded_rectangle([x0, y0, x1, y1], radius=14, outline=(160, 60, 50), width=7)
            d.rounded_rectangle([x1 + 6, y0 + 28, x1 + 22, y1 - 28], radius=5, fill=(160, 60, 50))
            ctext(d, W / 2, 620, "充電してください", font(40), (150, 70, 60))
        return
    # 配信待機画面
    d.rounded_rectangle([360, 130, 1560, 950], radius=36, fill=(16, 22, 36))
    d.rounded_rectangle([360, 130, 1560, 260], radius=36, fill=(22, 30, 48))
    d.ellipse([404, 160, 474, 230], fill=(90, 200, 120))
    d.text((500, 172), "ずんだの推しチャンネル", font=font(42), fill=INK)
    d.rounded_rectangle([1330, 168, 1520, 224], radius=28, fill=(220, 60, 70))
    ctext(d, 1425, 178, "LIVE", font(34), (255, 255, 255))
    ctext(d, W / 2, 480, "推しの生配信 まもなく開始", font(64), INK)
    # ローディングスピナー
    cx, cy, r = W / 2, 680, 46
    a0 = (t * 260) % 360
    d.arc([cx - r, cy - r, cx + r, cy + r], start=a0, end=a0 + 260,
          fill=(120, 180, 255), width=10)
    # 右上の電池残量が急降下（30%→1%）
    pct = max(1, int(30 - 29 * ease(t / (DEAD_AT - 0.6))))
    col = RED if pct < 15 else AMBER
    bx, by = 1650, 60
    d.rounded_rectangle([bx, by, bx + 120, by + 54], radius=10, outline=INK, width=4)
    d.rounded_rectangle([bx + 124, by + 16, bx + 136, by + 38], radius=3, fill=INK)
    d.rounded_rectangle([bx + 6, by + 6, bx + 6 + 108 * pct / 100, by + 48], radius=6, fill=col)
    d.text((bx - 110, by + 8), f"{pct}%", font=font(40), fill=col)


# ------------------------------------------------------------------
# 2) 時代カード（共通の年表バー付き）
# ------------------------------------------------------------------
ERAS = ["1970s", "1980", "1985", "1991", "2019"]


def _silhouette(d, cx, cy, scale, col):
    """人物シルエット（頭＋肩）。"""
    r = int(58 * scale)
    d.ellipse([cx - r, cy - r * 2.1, cx + r, cy - 0.1 * r], fill=col)
    d.pieslice([cx - r * 2, cy - r * 0.2, cx + r * 2, cy + r * 2.6],
               start=180, end=360, fill=col)


def make_era(idx: int, year: str, title: str, persons: list, sub: str):
    def draw(d: ImageDraw.ImageDraw, t: float) -> None:
        # 年号（スライドイン）
        k = ease(t / 0.5)
        f_year = font(150)
        yw = d.textlength(year, font=f_year)
        d.text(((W - yw) / 2, 120 - 40 * (1 - k)), year, font=f_year,
               fill=(*AMBER, int(255 * k)))
        # タイトル
        k2 = ease((t - 0.35) / 0.4)
        if k2 > 0:
            ctext(d, W / 2, 320, title, font(72), (*INK, int(255 * k2)))
        # サブテキスト
        k3 = ease((t - 0.7) / 0.4)
        if k3 > 0:
            ctext(d, W / 2, 430, sub, font(42), (*GRAY, int(255 * k3)))
        # 人物シルエット＋名前
        n = len(persons)
        for i, (name, role) in enumerate(persons):
            kp = ease((t - 0.9 - i * 0.25) / 0.4)
            if kp <= 0:
                continue
            cx = W / 2 + (i - (n - 1) / 2) * 420
            cy = 700 + 14 * math.sin(t * 1.4 + i)  # ゆっくり浮遊
            col = (46, 66, 100, int(255 * kp))
            _silhouette(d, cx, cy, kp, col)
            ctext(d, cx, 770, name, font(46), (*INK, int(255 * kp)))
            ctext(d, cx, 828, role, font(30), (*GRAY, int(255 * kp)))
        # 年表バー（下部中央・立ち絵を避ける）
        bx0, bx1, by = 560, 1360, 952
        d.line([bx0, by, bx1, by], fill=(50, 64, 92), width=6)
        prog = ease((t - 0.4) / 1.2)
        d.line([bx0, by, bx0 + (bx1 - bx0) * prog * idx / (len(ERAS) - 1), by],
               fill=(*ACCENT, 255), width=6)
        f_tick = font(26)
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
    render("batt_dead", 19.5, batt_dead)
    render("era_1970", 19.0, make_era(
        0, "1970年代", "充電できるリチウム電池、誕生",
        [("ウィッティンガム", "石油会社エクソン")], "オイルショックが生んだ研究"))
    render("era_1980", 27.0, make_era(
        1, "1980", "電圧が2倍になった",
        [("グッドイナフ", "オックスフォード大学"), ("水島公一", "東芝から留学")],
        "コバルト酸リチウムの発見"))
    render("era_1985", 25.6, make_era(
        2, "1985", "燃えない電池の完成",
        [("吉野彰", "旭化成")], "イオンを炭素の隙間にしまう"))
    render("era_1991", 13.5, make_era(
        3, "1991", "世界初の商用化",
        [("ソニー", "日本")], "ビデオカメラから、世界へ"))
    render("era_2019", 21.0, make_era(
        4, "2019", "ノーベル化学賞",
        [("ウィッティンガム", ""), ("グッドイナフ", "97歳・史上最高齢"), ("吉野彰", "")],
        "充電できる世界を作った"))


if __name__ == "__main__":
    main()
