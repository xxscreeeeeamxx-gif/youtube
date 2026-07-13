#!/usr/bin/env python3
"""flash-memory 追加章用: compare_media.mp4（記憶媒体の比較・80.6秒）を生成する。

フェーズ境界は timing.json のカット実測に同期:
  HDD=7.25 / (磁気=17.59 / 衝撃=30.96) / SSD=36.57 / (仲間=49.26) / 光=55.5 / テープ=68.27
実行: PYTHONPATH=. python3 scripts/gen_flash_compare.py
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


D_HDD, D_MAG, D_SHOCK, D_SSD, D_MATE, D_DISC, D_TAPE = 7.25, 17.59, 30.96, 36.57, 49.26, 55.5, 68.27
DUR = 80.6


def _hdd_icon(d, cx, cy, s=1.0, t=0.0):
    r = 90 * s
    d.rounded_rectangle([cx - r * 1.3, cy - r * 1.1, cx + r * 1.3, cy + r * 1.1],
                        radius=14, outline=GRAY, width=5)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 52, 76), outline=ACCENT, width=4)
    d.ellipse([cx - r * 0.2, cy - r * 0.2, cx + r * 0.2, cy + r * 0.2], fill=GRAY)
    ang = t * 6
    d.line([cx + r * 0.2 * math.cos(ang), cy + r * 0.2 * math.sin(ang),
            cx + r * 0.95 * math.cos(ang), cy + r * 0.95 * math.sin(ang)],
           fill=(90, 110, 140), width=3)
    # ヘッドアーム
    ax, ay = cx + r * 1.15, cy + r * 0.9
    hx = cx + r * 0.45 * math.cos(t * 0.9)
    hy = cy + r * 0.45 * math.sin(t * 0.9) * 0.4 - r * 0.2
    d.line([ax, ay, hx, hy], fill=AMBER, width=int(8 * s))
    d.ellipse([hx - 8 * s, hy - 8 * s, hx + 8 * s, hy + 8 * s], fill=AMBER)


def _ssd_icon(d, cx, cy, s=1.0, open_k=0.0):
    w, h = 190 * s, 120 * s
    d.rounded_rectangle([cx - w, cy - h, cx + w, cy + h], radius=14,
                        fill=(30, 42, 60), outline=GREEN, width=5)
    if open_k > 0:
        # 中のフラッシュチップ（檻）
        for i in range(3):
            for j in range(2):
                kk = ease(open_k * 3 - (i + j))
                if kk <= 0:
                    continue
                x = cx - w * 0.62 + i * w * 0.62
                y = cy - h * 0.42 + j * h * 0.84
                d.rounded_rectangle([x - 44 * s * kk, y - 30 * s * kk,
                                     x + 44 * s * kk, y + 30 * s * kk],
                                    radius=6, fill=(20, 60, 46), outline=(120, 200, 160), width=3)
    elif s > 0.2:
        ctext(d, cx, cy - 24 * s, "SSD", font(max(int(44 * s), 8)), GREEN)


def _disc_icon(d, cx, cy, s=1.0):
    r = 95 * s
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(56, 66, 96), outline=(170, 190, 230), width=4)
    d.ellipse([cx - r * 0.25, cy - r * 0.25, cx + r * 0.25, cy + r * 0.25], fill=BG)
    for i in range(3):
        rr = r * (0.45 + i * 0.16)
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], start=200, end=320,
              fill=(190, 210, 250), width=2)


def _tape_icon(d, cx, cy, s=1.0, t=0.0):
    w, h = 150 * s, 95 * s
    d.rounded_rectangle([cx - w, cy - h, cx + w, cy + h], radius=12,
                        fill=(46, 40, 30), outline=AMBER, width=4)
    for sgn in (-1, 1):
        rx = cx + sgn * w * 0.45
        r = 38 * s
        d.ellipse([rx - r, cy - r, rx + r, cy + r], fill=(24, 20, 14), outline=(210, 190, 140), width=4)
        ang = t * 3 * sgn
        for k in range(3):
            a = ang + k * 2.09
            d.line([rx, cy, rx + r * 0.8 * math.cos(a), cy + r * 0.8 * math.sin(a)],
                   fill=(150, 134, 96), width=3)


def _sd_icon(d, cx, cy, s=1.0):
    w, h = 62 * s, 82 * s
    d.polygon([(cx - w, cy - h), (cx + w * 0.5, cy - h), (cx + w, cy - h * 0.5),
               (cx + w, cy + h), (cx - w, cy + h)], fill=(50, 60, 86), outline=ACCENT)
    if s > 0.2:
        ctext(d, cx, cy + h * 0.1, "SD", font(max(int(34 * s), 8)), INK)


def compare_media(d, t):
    if t < D_HDD:
        _caption(d, "記憶装置の代表選手たち")
        # 右端は立ち絵と重なるので1450まで
        items = [("HDD", 340), ("SSD", 630), ("SDカード", 920), ("DVD", 1180), ("磁気テープ", 1440)]
        for i, (name, x) in enumerate(items):
            kk = ease((t - 0.6 - i * 0.5) / 0.5)
            if kk <= 0:
                continue
            y = 560
            if name == "HDD":
                _hdd_icon(d, x, y, 0.8 * kk, t)
            elif name == "SSD":
                _ssd_icon(d, x, y, 0.7 * kk)
            elif name == "SDカード":
                _sd_icon(d, x, y, 1.1 * kk)
            elif name == "DVD":
                _disc_icon(d, x, y, 0.9 * kk)
            else:
                _tape_icon(d, x, y, 0.8 * kk, t)
            if kk > 0.7:
                ctext(d, x, 700, name, font(34), GRAY)
        if t > 3.6:
            ctext(d, W / 2, 820, "違いは「覚え方」", font(44), AMBER)
        return
    if t < D_SSD:
        if t < D_MAG:
            _caption(d, "HDD = 回る円盤に、磁石で書く")
        elif t < D_SHOCK:
            _caption(d, "大容量で安い。でも部品が動く")
        else:
            _caption(d, "動く部品 = 衝撃が大敵")
        # 大きなHDD断面
        cx, cy, r = 760, 590, 240
        d.rounded_rectangle([cx - r * 1.35, cy - r * 1.15, cx + r * 1.35, cy + r * 1.15],
                            radius=20, outline=GRAY, width=6)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 52, 76), outline=ACCENT, width=6)
        d.ellipse([cx - r * 0.18, cy - r * 0.18, cx + r * 0.18, cy + r * 0.18], fill=GRAY)
        # 回転の目印
        ang = t * 5
        for k in range(2):
            a = ang + k * math.pi
            d.line([cx + r * 0.2 * math.cos(a), cy + r * 0.2 * math.sin(a),
                    cx + r * 0.93 * math.cos(a), cy + r * 0.93 * math.sin(a)],
                   fill=(80, 100, 132), width=4)
        # 磁気ビット（N/S）
        if t >= D_MAG:
            rr = r * 0.7
            for i in range(10):
                a = -0.9 + i * 0.2
                x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
                col = RED if i % 2 else ACCENT
                ctext(d, x, y - 16, "N" if i % 2 else "S", font(30), col)
        # ヘッドアーム
        ax, ay = cx + r * 1.25, cy + r
        hx = cx + r * 0.5 * math.cos(t * 0.8)
        hy = cy + r * 0.4 * math.sin(t * 0.8) * 0.4 - r * 0.25
        d.line([ax, ay, hx, hy], fill=AMBER, width=12)
        d.ellipse([hx - 12, hy - 12, hx + 12, hy + 12], fill=AMBER)
        d.text((cx + r * 0.9, cy - r * 1.05), "読み書きヘッド", font=font(28), fill=AMBER)
        # 特性パネル
        feats = [("磁石の向きで 0 と 1", ACCENT, D_MAG),
                 ("大容量・安い", GREEN, D_MAG + 4.0),
                 ("衝撃に弱い / 速さは負ける", RED, D_SHOCK)]
        for i, (s_, col, t0) in enumerate(feats):
            kk = ease((t - t0) / 0.5)
            if kk <= 0:
                continue
            d.rounded_rectangle([1310, 400 + i * 130, 1310 + 480 * kk, 500 + i * 130],
                                radius=16, fill=(24, 34, 54, int(255 * kk)))
            if kk > 0.7:
                d.text((1340, 428 + i * 130), s_, font=font(34), fill=col)
        return
    if t < D_DISC:
        _caption(d, "SSDの中身は、フラッシュメモリ")
        open_k = ease((t - D_SSD - 1.0) / 1.5)
        _ssd_icon(d, 700, 560, 1.5, open_k=open_k)
        if open_k > 0.8:
            ctext(d, 700, 780, "中は電子の檻がぎっしり", font(36), GREEN)
        if t >= D_MATE:
            k = t - D_MATE
            mates = ["USBメモリ", "SDカード", "スマホの保存領域"]
            for i, s_ in enumerate(mates):
                kk = ease((k - i * 0.5) / 0.5)
                if kk <= 0:
                    continue
                d.rounded_rectangle([1230, 420 + i * 120, 1230 + 440 * kk, 510 + i * 120],
                                    radius=16, fill=(20, 60, 46, int(255 * kk)))
                if kk > 0.7:
                    d.text((1260, 444 + i * 120), s_, font=font(34), fill=(120, 200, 160))
            if k > 2.2:
                ctext(d, 1450, 800, "みんな同じ「檻」の仲間", font(34), GREEN)
        return
    if t < D_TAPE:
        _caption(d, "DVD・ブルーレイ = デコボコを光で読む")
        _disc_icon(d, 640, 580, 2.2)
        # レーザー
        blink = 0.6 + 0.4 * math.sin(t * 6)
        d.line([640, 920, 640 + 150, 580 + 60], fill=(255, 80, 80, int(255 * blink)), width=8)
        d.polygon([(600, 920), (680, 920), (640, 960)], fill=(90, 100, 130))
        # ピット拡大
        d.ellipse([1150, 430, 1650, 760], outline=ACCENT, width=8)
        rr = random.Random(5)
        for i in range(6):
            y = 480 + i * 45
            x = 1200
            while x < 1600:
                ln = rr.uniform(18, 60)
                if rr.random() > 0.4:
                    d.rounded_rectangle([x, y, min(x + ln, 1600), y + 18], radius=9,
                                        fill=(170, 190, 230))
                x += ln + 14
        ctext(d, 1400, 790, "表面の凹凸 = 0 と 1", font(32), ACCENT)
        return
    _caption(d, "磁気テープ = 骨董品どころか、現役")
    _tape_icon(d, 620, 560, 2.0, t)
    kk = ease((t - D_TAPE - 1.0) / 0.6)
    if kk > 0:
        d.rounded_rectangle([1150, 400, 1150 + 560 * kk, 640], radius=20,
                            fill=(24, 34, 54, int(255 * kk)))
        if kk > 0.7:
            d.text((1190, 430), "安い・長持ち", font=font(40), fill=AMBER)
            d.text((1190, 500), "企業や研究所の保管用で", font=font(32), fill=INK)
            d.text((1190, 550), "いまも現役と言われる", font=font(32), fill=INK)
    if t > D_TAPE + 5.0:
        ctext(d, W / 2, 880, "適材適所で、世界の記憶は守られている", font(38), GRAY)


def main() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="fc_compare_"))
    for fi in range(int(DUR * FPS)):
        img = Image.new("RGB", (W, H), BG)
        compare_media(ImageDraw.Draw(img, "RGBA"), fi / FPS)
        img.save(tmp / f"{fi:04d}.png")
    out = Path("assets/clips/compare_media.mp4")
    r = subprocess.run(
        [ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error",
         "-framerate", str(FPS), "-i", str(tmp / "%04d.png"),
         "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", str(out)],
        capture_output=True, text=True)
    for p in tmp.glob("*.png"):
        p.unlink()
    tmp.rmdir()
    if r.returncode != 0:
        raise SystemExit(f"エンコード失敗: {r.stderr[-400:]}")
    print(f"生成完了: {out}")


if __name__ == "__main__":
    main()
