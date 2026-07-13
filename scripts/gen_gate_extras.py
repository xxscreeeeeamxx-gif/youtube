#!/usr/bin/env python3
"""ticket-gate プロジェクト用のアニメクリップを生成する。

  gate_try.mp4      23.5s  茶番: 切符をどの向きで入れても通れる実験
  gate_anatomy.mp4  51.5s  改札機の断面解剖（磁気面→搬送→反転→読み書きパンチ印字）
  ic_tap.mp4        46.5s  ICタッチ（コイルとチップ→電磁誘導→0.2秒の4仕事→13度）
  era_1967/2001/2007       自動改札史の時代カード

フェーズ境界は timing.json のカット実測に同期（コメントの秒数）。
実行: PYTHONPATH=. python3 scripts/gen_gate_extras.py [クリップ名...]
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
TICKET = (240, 236, 224)   # 切符おもて
TICKET_BK = (52, 50, 54)   # 切符うら（磁気面）
GATE = (30, 42, 66)

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
    tmp = Path(tempfile.mkdtemp(prefix=f"tg_{name}_"))
    for fi in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw_frame(ImageDraw.Draw(img, "RGBA"), fi / FPS)
        img.save(tmp / f"{fi:04d}.png")
    encode(tmp, Path(f"assets/clips/{name}.mp4"))


def _ticket(d, cx, cy, w=170, h=100, back=False, upside=False, rot=0.0):
    """切符1枚。rot はY軸回転風の横縮み（-1..1 → 裏返り演出）。"""
    ww = w * abs(math.cos(rot)) if rot else w
    face_back = back if not rot else (math.cos(rot) < 0) ^ back
    col = TICKET_BK if face_back else TICKET
    d.rounded_rectangle([cx - ww / 2, cy - h / 2, cx + ww / 2, cy + h / 2],
                        radius=10, fill=col, outline=(120, 120, 130), width=3)
    if ww < 24:
        return
    if face_back:
        # 磁気面のバー
        for i in range(4):
            y = cy - h / 2 + 22 + i * 18
            d.line([cx - ww / 2 + 14, y, cx + ww / 2 - 14, y],
                   fill=(90, 88, 96), width=6)
    else:
        f = font(int(26 * ww / w)) if ww > 60 else None
        if f:
            s = "きっぷ"
            if upside:
                # 逆さは文字を下側に反転配置した風に（簡易表現）
                d.text((cx - d.textlength(s, font=f) / 2, cy + h / 2 - 40), s,
                       font=f, fill=(180, 60, 40))
            else:
                d.text((cx - d.textlength(s, font=f) / 2, cy - h / 2 + 12), s,
                       font=f, fill=(180, 60, 40))
            d.line([cx - ww / 2 + 12, cy + (h * -0.1 if upside else h * 0.16),
                    cx + ww / 2 - 12, cy + (h * -0.1 if upside else h * 0.16)],
                   fill=(200, 130, 60), width=5)


# ------------------------------------------------------------------
# 1) gate_try — 茶番（逆さ連打=7.67 / 断面ネタバレ=15.61 / DUR 23.5）
# ------------------------------------------------------------------
T_RAPID, T_REVEAL = 7.67, 15.61


def _gate_box(d, x, y, w=560, h=300):
    d.rounded_rectangle([x, y, x + w, y + h], radius=26, fill=GATE,
                        outline=(70, 92, 130), width=4)
    # 投入口
    d.rounded_rectangle([x + 40, y + 60, x + 190, y + 96], radius=10,
                        fill=(12, 16, 26), outline=AMBER, width=4)
    ctext(d, x + 115, y + 106, "入れる", font(26), GRAY)


def _ok(d, cx, cy, k):
    r = 70 * k
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GREEN, width=14)


def gate_try(d, t):
    if t < T_REVEAL:
        attempts = [("裏向き", True, False), ("逆さ", False, True), ("裏向き＋逆さ", True, True)]
        if t < T_RAPID:
            idx, t0, dur = 0, 0.0, T_RAPID
        elif t < T_RAPID + (T_REVEAL - T_RAPID) / 2:
            idx, t0, dur = 1, T_RAPID, (T_REVEAL - T_RAPID) / 2
        else:
            idx, t0, dur = 2, T_RAPID + (T_REVEAL - T_RAPID) / 2, (T_REVEAL - T_RAPID) / 2
        label, back, ups = attempts[idx]
        _caption(d, f"実験{idx + 1}: {label}で入れる")
        gx, gy = W / 2 - 40, 430
        _gate_box(d, gx, gy)
        k = ease((t - t0) / (dur * 0.45))
        tx = (gx - 300) + k * 320
        if k < 1.0:
            _ticket(d, tx, gy + 78, back=back, upside=ups)
        else:
            k2 = ease((t - t0 - dur * 0.45) / 0.5)
            _ok(d, gx + 280, gy + 150, k2)
            if k2 >= 1.0:
                ctext(d, gx + 280, gy + 240, "通れた", font(44), GREEN)
        # 実験の進捗
        for i, (s, _, _) in enumerate(attempts):
            done = i < idx or (i == idx and k >= 1.0)
            col = GREEN if done else (60, 72, 98)
            d.ellipse([560 + i * 300, 290, 588 + i * 300, 318], fill=col)
            d.text((600 + i * 300, 288), s, font=font(30),
                   fill=INK if done else GRAY)
        return
    # 断面ネタバレ
    _caption(d, "箱の中で、直されている")
    bx, by, bw, bh = 360, 430, 1200, 300
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=26,
                        outline=(70, 92, 130), width=4)
    d.line([bx + 30, by + 190, bx + bw - 30, by + 190], fill=(70, 92, 130), width=6)
    k = ((t - T_REVEAL) / 4.0) % 1.0
    tx = bx + 80 + k * (bw - 200)
    rot = min(max((k - 0.35) / 0.3, 0), 1) * math.pi
    _ticket(d, tx, by + 130, back=True, rot=rot)
    for x_, s in ((bx + 320, "整列"), (bx + 620, "反転"), (bx + 920, "読み取り")):
        d.text((x_, by + 220), s, font=font(34), fill=ACCENT)
    ctext(d, W / 2, 800, "どの向きでも、走りながら表向きに直る", font(40), GRAY)


# ------------------------------------------------------------------
# 2) gate_anatomy — 解剖（データ=9.26 / 搬送=17.22 / 反転=24.51〜39.52 /
#    読み書き=39.52 / DUR 51.5）
# ------------------------------------------------------------------
A_DATA, A_RUN, A_FLIP, A_RW = 9.26, 17.22, 24.51, 39.52


def gate_anatomy(d, t):
    if t < A_RUN:
        # 磁気面クローズアップ
        _caption(d, "裏の黒は、磁石の粉（酸化鉄）" if t < A_DATA else "磁気で書かれた、切符の中身")
        cx, cy, w, h = W / 2, 560, 900, 520
        d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                            radius=24, fill=TICKET_BK, outline=(110, 108, 118), width=5)
        rr = random.Random(7)
        for i in range(6):
            y = cy - h / 2 + 70 + i * 72
            seg = 0
            x = cx - w / 2 + 60
            while x < cx + w / 2 - 60:
                ln = rr.uniform(30, 110)
                on = rr.random() > 0.35
                if on:
                    d.line([x, y, min(x + ln, cx + w / 2 - 60), y],
                           fill=(150, 148, 160), width=10)
                x += ln + 18
                seg += 1
        if t >= A_DATA:
            k = ease((t - A_DATA) / 0.8)
            for i, (s, col) in enumerate((("乗車駅", ACCENT), ("日付", GREEN), ("金額", AMBER))):
                kk = ease((t - A_DATA - i * 0.9) / 0.5)
                if kk <= 0:
                    continue
                x = cx - 330 + i * 330
                d.rounded_rectangle([x - 120, 260, x + 120, 330], radius=16,
                                    fill=(24, 34, 54, int(255 * kk)))
                if kk > 0.6:
                    ctext(d, x, 274, s, font(40), col)
                d.line([x, 330, x, 380 + i * 40], fill=(*col, int(200 * kk)), width=4)
        return
    # 機内断面
    bx, by, bw, bh = 200, 420, 1520, 330
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=26,
                        outline=(70, 92, 130), width=4)
    belty = by + 200
    d.line([bx + 30, belty, bx + bw - 30, belty], fill=(70, 92, 130), width=6)
    for i in range(10):
        x = bx + 90 + i * 150
        d.ellipse([x - 16, belty - 16, x + 16, belty + 16],
                  outline=(70, 92, 130), width=5)
    d.rounded_rectangle([bx - 10, belty - 60, bx + 60, belty + 20], radius=8,
                        fill=(12, 16, 26), outline=AMBER, width=3)
    stations = [("整列", bx + 330), ("反転", bx + 560), ("読む", bx + 810),
                ("書く", bx + 980), ("パンチ", bx + 1150), ("印字", bx + 1320)]
    if t < A_FLIP:
        _caption(d, "投入した瞬間、機内を猛スピードで走る")
        k = ((t - A_RUN) / 2.2) % 1.0
        tx = bx + 100 + k * (bw - 240)
        _ticket(d, tx, belty - 60, back=False, w=130, h=76)
        for i in range(3):
            d.line([tx - 90 - i * 26, belty - 80 + i * 14, tx - 130 - i * 26,
                    belty - 80 + i * 14], fill=(120, 150, 190), width=5)
        for s, x_ in stations:
            d.text((x_ - 30, by + bh - 76), s, font=font(28), fill=GRAY)
        return
    if t < A_RW:
        _caption(d, "ベルトの速度差で、走りながら裏返る")
        # 速度差の矢印と被るので、このフェーズは「反転」だけ表示
        d.text((bx + 530, by + bh - 76), "反転", font=font(34), fill=ACCENT)
        k = ((t - A_FLIP) / 3.2) % 1.0
        tx = bx + 200 + k * 900
        rot = min(max((k - 0.3) / 0.4, 0), 1) * math.pi
        _ticket(d, tx, belty - 60, back=True, rot=rot, w=130, h=76)
        # 速度差矢印
        d.line([bx + 470, belty - 120, bx + 690, belty - 120], fill=(*AMBER, 220), width=8)
        d.polygon([(bx + 690, belty - 132), (bx + 720, belty - 120), (bx + 690, belty - 108)], fill=AMBER)
        d.text((bx + 470, belty - 176), "上ベルト: ゆっくり", font=font(26), fill=AMBER)
        d.line([bx + 470, belty + 44, bx + 760, belty + 44], fill=(*GREEN, 220), width=8)
        d.polygon([(bx + 760, belty + 32), (bx + 790, belty + 44), (bx + 760, belty + 56)], fill=GREEN)
        d.text((bx + 810, belty + 26), "下ベルト: 速い", font=font(26), fill=GREEN)
        return
    _caption(d, "読んで、書いて、穴をあけて、印字して排出")
    k = ((t - A_RW) / 3.4) % 1.0
    tx = bx + 700 + k * (bw - 800)
    _ticket(d, tx, belty - 60, back=False, w=130, h=76)
    for i, (s, x_) in enumerate(stations):
        active = i >= 2 and abs(tx - x_) < 90
        col = GREEN if active else (ACCENT if i >= 2 else GRAY)
        d.text((x_ - 30, by + bh - 76), s, font=font(28), fill=col)
        if i >= 2:
            d.rounded_rectangle([x_ - 46, belty - 150, x_ + 46, belty - 106],
                                radius=8, fill=(24, 34, 54),
                                outline=GREEN if active else (70, 92, 130), width=3)
    ctext(d, W / 2, 800, "ここまで全部で、1秒かからないと言われている", font(40), GRAY)


# ------------------------------------------------------------------
# 3) ic_tap — IC（コイル=8.09 / 0.2秒=18.14 / 13度=34.25 / DUR 46.5）
# ------------------------------------------------------------------
I_COIL, I_TIME, I_ANGLE = 8.09, 18.14, 34.25


def _card(d, cx, cy, w=760, h=460, glow=0.0):
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                        radius=30, fill=(20, 60, 46), outline=(90, 160, 130), width=5)
    # コイル（3重）
    for i in range(3):
        m = 46 + i * 26
        col = (120 + int(120 * glow), 210, 160) if glow else (98, 170, 134)
        d.rounded_rectangle([cx - w / 2 + m, cy - h / 2 + m,
                             cx + w / 2 - m, cy + h / 2 - m],
                            radius=20, outline=col, width=8)
    # チップ
    chip = (255, 220, 120) if glow else (190, 170, 110)
    d.rounded_rectangle([cx - 60, cy - 46, cx + 60, cy + 46], radius=10, fill=chip)
    d.text((cx - 44, cy - 20), "IC", font=font(40), fill=(60, 50, 20))


def ic_tap(d, t):
    if t < I_COIL:
        _caption(d, "カードの中身は、コイルとチップだけ")
        _card(d, W / 2, 560)
        # 電池なし
        d.rounded_rectangle([1460, 420, 1700, 520], radius=16, outline=GRAY, width=6)
        d.rectangle([1700, 445, 1724, 495], fill=GRAY)
        d.line([1450, 400, 1710, 540], fill=RED, width=14)
        ctext(d, 1580, 550, "電池なし", font(36), RED)
        return
    if t < I_TIME:
        _caption(d, "改札の電波を、コイルが電気に変える")
        # 下からリーダーの電波
        d.rounded_rectangle([660, 860, 1260, 960], radius=18, fill=GATE,
                            outline=(70, 92, 130), width=4)
        ctext(d, 960, 888, "読み取り部", font(34), GRAY)
        k = (t - I_COIL)
        for i in range(3):
            kk = ((k * 0.9 + i * 0.33) % 1.0)
            r = 60 + kk * 260
            a = int(220 * (1 - kk))
            d.arc([960 - r, 850 - r, 960 + r, 850 + r], start=220, end=320,
                  fill=(120, 190, 250, a), width=10)
        glow = 0.5 + 0.5 * math.sin(t * 5)
        _card(d, W / 2, 520, glow=glow)
        # 稲妻マーク（フォント絵文字は豆腐になるので多角形で描く）
        bx_, by_ = 1330, 400
        d.polygon([(bx_ + 26, by_), (bx_, by_ + 34), (bx_ + 18, by_ + 34),
                   (bx_ + 8, by_ + 64), (bx_ + 40, by_ + 24), (bx_ + 22, by_ + 24)],
                  fill=AMBER)
        d.text((1390, 420), "その場で発電", font=font(40), fill=AMBER)
        return
    if t < I_ANGLE:
        _caption(d, "0.2秒の中身は、4つの仕事")
        jobs = [("残高確認", ACCENT), ("運賃計算", GREEN), ("書き込み", AMBER), ("ゲート判断", RED)]
        k = ease((t - I_TIME) / 5.0)
        bx, bw = 340, 1240
        d.rounded_rectangle([bx, 700, bx + bw, 780], radius=20, fill=(24, 34, 54))
        for i, (s, col) in enumerate(jobs):
            x0 = bx + bw * i / 4
            fill_k = min(max(k * 4 - i, 0), 1)
            if fill_k > 0:
                d.rounded_rectangle([x0 + 4, 706, x0 + 4 + (bw / 4 - 8) * fill_k, 774],
                                    radius=14, fill=col)
            d.text((x0 + 30, 620), s, font=font(34),
                   fill=col if fill_k > 0.5 else GRAY)
        sec = 0.2 * min(k, 1.0)
        ctext(d, W / 2, 830, f"{sec:.2f} 秒", font(90), INK if k < 1 else GREEN)
        _card(d, W / 2, 380, w=560, h=330, glow=1.0 if k < 1 else 0.3)
        return
    _caption(d, "読み取り部の傾きは、実験で選ばれた13度")
    # 側面図
    px, py = 760, 760
    ang = math.radians(13)
    L = 560
    x2, y2 = px + L * math.cos(ang), py - L * math.sin(ang)
    d.line([px - 80, py, px + 700, py], fill=(70, 92, 130), width=6)  # 水平線
    d.line([px, py, x2, y2], fill=ACCENT, width=14)
    k = ease((t - I_ANGLE) / 1.2)
    d.arc([px - 180, py - 180, px + 180, py + 180], start=-13 * k, end=0,
          fill=AMBER, width=10)
    d.text((px + 240, py - 90), f"{int(13 * k)}°", font=font(72), fill=AMBER)
    # カードが乗る
    kk = ease((t - I_ANGLE - 1.0) / 0.8)
    if kk > 0:
        mx, my = (px + x2) / 2, (py + y2) / 2 - 40 - (1 - kk) * 160
        card_w, card_h = 300, 40
        dx, dy = math.cos(ang), -math.sin(ang)
        nx, ny = math.sin(ang), math.cos(ang)
        pts = []
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            pts.append((mx + sx * dx * card_w / 2 + sy * nx * card_h / 2 * -1,
                        my + sx * dy * card_w / 2 + sy * ny * card_h / 2 * -1))
        d.polygon(pts, fill=(60, 140, 105), outline=(120, 200, 160))
    ctext(d, W / 2, 940, "叩かず「置く」と、いちばん読みやすい", font(40), GRAY)


# ------------------------------------------------------------------
# 4) 時代カード
# ------------------------------------------------------------------
ERAS = ["1967 北千里駅", "2001 Suica", "2007 IEEE認定"]


def _silhouette(d, cx, cy, scale, col):
    r = int(58 * scale)
    d.ellipse([cx - r, cy - r * 2.1, cx + r, cy - 0.1 * r], fill=col)
    d.pieslice([cx - r * 2, cy - r * 0.2, cx + r * 2, cy + r * 2.6],
               start=180, end=360, fill=col)


def make_era(idx, year, title, persons, sub, medal=False):
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
        if medal:
            kp = ease((t - 0.9) / 0.5)
            if kp > 0:
                cx, cy = W / 2, 690
                r = 120 * kp
                d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=AMBER, width=12)
                d.ellipse([cx - r * 0.72, cy - r * 0.72, cx + r * 0.72, cy + r * 0.72],
                          outline=(120, 100, 50), width=4)
                if kp > 0.8:
                    ctext(d, cx, cy - 40, "IEEE", font(54), AMBER)
                    ctext(d, cx, cy + 16, "MILESTONE", font(28), GRAY)
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


CLIPS = {
    "gate_try": (23.5, lambda: gate_try),
    "gate_anatomy": (51.5, lambda: gate_anatomy),
    "ic_tap": (46.5, lambda: ic_tap),
    "era_1967": (10.8, lambda: make_era(
        0, "1967", "世界初の自動改札機", [("立石電機と大学・鉄道の技術者たち", "現・オムロン")],
        "大阪・阪急北千里駅に誕生")),
    "era_2001": (15.0, lambda: make_era(
        1, "2001", "Suica、登場", [("JR東日本の開発者たち", "タッチ&ゴーを実現")],
        "切符からカードへ、改札の世代交代")),
    "era_2007": (16.8, lambda: make_era(
        2, "2007", "IEEEマイルストーン認定", [],
        "エジソンの電球と並ぶ、電気技術の偉業リストへ", medal=True)),
}


def main() -> None:
    names = sys.argv[1:] or list(CLIPS)
    for name in names:
        dur, fn = CLIPS[name]
        render(name, dur, fn())


if __name__ == "__main__":
    main()
