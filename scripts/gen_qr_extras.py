#!/usr/bin/env python3
"""qr-code プロジェクト用のアニメクリップを生成する。

  qr_ticket.mp4   34.0s  チケットのQRにシミ→スキャン成功（冒頭茶番）
  qr_anatomy.mp4  75.0s  QRコード解剖（0/1→バーコード比較→目玉→回転→比率→余白）
  qr_repair.mp4   39.3s  誤り訂正（予備データ→シミ復元→2度目→レベルと30%）
  go_to_qr.mp4    20.5s  碁盤の白黒→QRコードへモーフ（着想シーン）
  era_1994.mp4    15.0s  時代カード: 1994 QRコード誕生
  era_open.mp4    26.0s  時代カード: 特許の無料開放

フェーズ境界は timing.json のカット実測に同期（コメントの秒数）。
QRの模様は qrcode ライブラリで「ふしぎ研究所」を実際に符号化した本物。

実行: PYTHONPATH=. python3 scripts/gen_qr_extras.py
"""

import math
import random
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ytf.config import Config, ffmpeg_bin  # noqa: E402

import qrcode  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

W, H, FPS = 1920, 1080, 30
BG = (8, 12, 22)
INK = (235, 242, 252)
ACCENT = (58, 160, 255)
AMBER = (255, 190, 80)
GREEN = (86, 216, 148)
ZUNDA = (110, 190, 90)
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


# ---- 本物のQR行列（「ふしぎ研究所」をレベルHで符号化）----
_q = qrcode.QRCode(version=3, error_correction=qrcode.constants.ERROR_CORRECT_H,
                   border=0)
_q.add_data("ふしぎ研究所")
_q.make(fit=True)
M = _q.modules
N = len(M)


def is_finder(r: int, c: int) -> bool:
    return (r < 7 and c < 7) or (r < 7 and c >= N - 7) or (r >= N - 7 and c < 7)


def draw_qr(d, x0, y0, px, fg=(20, 24, 32), bgc=(255, 255, 255),
            finder_fg=None, quiet=3, data_tint=None, parity_cols=False,
            alpha=255):
    """QRを描く。quiet=余白モジュール数。"""
    size = (N + quiet * 2) * px
    d.rounded_rectangle([x0, y0, x0 + size, y0 + size], radius=px * 2,
                        fill=(*bgc, alpha))
    ox, oy = x0 + quiet * px, y0 + quiet * px
    for r in range(N):
        for c in range(N):
            if not M[r][c]:
                continue
            col = fg
            if finder_fg and is_finder(r, c):
                col = finder_fg
            elif data_tint and not is_finder(r, c):
                col = data_tint
            if parity_cols and not is_finder(r, c) and c >= int(N * 0.72):
                col = (196, 138, 32)  # 予備データ領域（琥珀）
            d.rectangle([ox + c * px, oy + r * px,
                         ox + (c + 1) * px - 1, oy + (r + 1) * px - 1],
                        fill=(*col, alpha))
    return size


def qr_image(px, quiet=3, **kw) -> Image.Image:
    size = (N + quiet * 2) * px
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw_qr(ImageDraw.Draw(img, "RGBA"), 0, 0, px, quiet=quiet, **kw)
    return img


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
    tmp = Path(tempfile.mkdtemp(prefix=f"qr_{name}_"))
    for fi in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw_frame(img, ImageDraw.Draw(img, "RGBA"), fi / FPS)
        img.save(tmp / f"{fi:04d}.png")
    encode(tmp, Path(f"assets/clips/{name}.mp4"))


# ------------------------------------------------------------------
# 1) qr_ticket — チケットのQRにシミ→読み取り成功（茶番）
#    シミ=2カット目頭(7.93) / 成功=5カット目頭(26.09) / DUR=34.0
# ------------------------------------------------------------------
STAIN_T, OK_T = 7.93, 26.09
_stain_blobs = [(0.30, 0.62, 150, 110), (0.52, 0.78, 110, 84),
                (0.18, 0.84, 90, 66), (0.44, 0.50, 76, 58)]


def _draw_stain(d, qx, qy, qsize, k):
    for (fx, fy, rw, rh) in _stain_blobs:
        rw, rh = rw * k, rh * k
        cx, cy = qx + qsize * fx, qy + qsize * fy
        d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh],
                  fill=(96, 150, 70, 235))
        d.ellipse([cx - rw * .5, cy - rh * .5, cx + rw * .6, cy + rh * .5],
                  fill=(120, 175, 88, 235))


def qr_ticket(img, d, t):
    # チケット本体
    tx0, ty0, tx1, ty1 = 300, 260, 1620, 830
    d.rounded_rectangle([tx0 + 10, ty0 + 14, tx1 + 10, ty1 + 14],
                        radius=30, fill=(0, 0, 0, 90))
    d.rounded_rectangle([tx0, ty0, tx1, ty1], radius=30, fill=(248, 248, 244))
    d.rounded_rectangle([tx0, ty0, tx1, ty0 + 92], radius=30,
                        fill=(34, 40, 58))
    d.rectangle([tx0, ty0 + 50, tx1, ty0 + 92], fill=(34, 40, 58))
    d.text((tx0 + 36, ty0 + 22), "LIVE TICKET", font=font(44), fill=INK)
    ctext(d, tx0 + 300, ty0 + 150, "推しのライブ FINAL", font(52), (30, 34, 44))
    ctext(d, tx0 + 300, ty0 + 240, "本日 18:00 開演", font(40), (90, 96, 110))
    ctext(d, tx0 + 300, ty0 + 320, "入場口で QR をかざしてください",
          font(30), (120, 126, 140))
    d.line([tx0 + 640, ty0 + 120, tx0 + 640, ty1 - 30], fill=(200, 200, 200),
           width=3)
    # QR（右側）
    px = 12
    qsize = (N + 6) * px
    qx, qy = tx1 - qsize - 60, (ty0 + ty1) // 2 - qsize // 2 + 40
    draw_qr(d, qx, qy, px)

    # シミ（2カット目頭でボトッと落ちる）
    if t >= STAIN_T:
        _draw_stain(d, qx, qy, qsize, min(1.0, (t - STAIN_T) / 0.35))

    # スキャン成功（5カット目頭）
    if t >= OK_T:
        k = (t - OK_T)
        if k < 0.8:  # 青いスキャンラインが上下に走る
            yy = qy + qsize * (0.5 - 0.5 * math.cos(k / 0.8 * math.tau))
            d.rectangle([qx - 14, yy - 3, qx + qsize + 14, yy + 3],
                        fill=(*ACCENT, 230))
        else:
            r = 64 * min(1.0, (k - 0.8) / 0.25)
            cx, cy = qx + qsize / 2, qy + qsize / 2
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*GREEN, 240))
            if r > 40:
                d.line([cx - 26, cy + 2, cx - 8, cy + 22], fill=(255, 255, 255),
                       width=10)
                d.line([cx - 8, cy + 22, cx + 30, cy - 20], fill=(255, 255, 255),
                       width=10)
            ctext(d, W / 2, ty1 + 60, "読み取り成功", font(56), GREEN)
            d.rounded_rectangle([tx0 - 8, ty0 - 8, tx1 + 8, ty1 + 8], radius=34,
                                outline=(*GREEN, 230), width=8)


# ------------------------------------------------------------------
# 2) qr_anatomy — QR解剖ツアー（6フェーズ・75秒）
# ------------------------------------------------------------------
A1, A2, A3, A4, A5, A6 = 7.63, 25.5, 37.53, 52.04, 57.97, 65.93
_rng_bits = random.Random(7)
_bits = "".join(_rng_bits.choice("01") for _ in range(160))


def _caption(d, s, col=INK):
    ctext(d, W / 2, 150, s, font(60), col)


def qr_anatomy(img, d, t):
    px = 15
    qsize = (N + 6) * px
    cx0, cy0 = W // 2 - qsize // 2, 300

    if t < A1:  # P0: QRが現れる
        k = ease(t / 0.6)
        _caption(d, "この模様の正体は？")
        draw_qr(d, cx0, cy0 + 30 * (1 - k), px, alpha=int(255 * k))
        return
    if t < A2:  # P1: 文字→0/1→マス
        _caption(d, "文字を 0 と 1 に変えて、白黒のマスで並べる")
        # 左: 変換の流れ
        lx = 220
        d.rounded_rectangle([lx, 320, lx + 480, 430], radius=18, fill=(24, 34, 54))
        ctext(d, lx + 240, 348, "ふしぎ研究所", font(48), INK)
        ay = 470
        d.polygon([(lx + 240 - 22, ay), (lx + 240 + 22, ay), (lx + 240, ay + 34)],
                  fill=(*ACCENT, 255))
        nshow = int(min(1.0, (t - A1) / 3.0) * 96)
        f_b = font(30)
        for i in range(nshow):
            r, c = divmod(i, 16)
            col = ACCENT if _bits[i] == "1" else GRAY
            d.text((lx + 60 + c * 24, 540 + r * 40), _bits[i], font=f_b, fill=col)
        # 右: QR（データ部が青く脈動）
        pulse = 0.5 + 0.5 * math.sin(t * 2.4)
        tint = tuple(int(20 + (ACCENT[i] - 20) * 0.5 * pulse) for i in range(3))
        draw_qr(d, W - 220 - qsize, cy0, px, data_tint=tint)
        return
    if t < A3:  # P2: バーコードとの比較
        _caption(d, "バーコードは横だけ、QRは縦と横")
        # 左: バーコード
        bx, by, bw, bh = 240, 380, 520, 280
        d.rounded_rectangle([bx - 30, by - 30, bx + bw + 30, by + bh + 30],
                            radius=16, fill=(248, 248, 244))
        rb = random.Random(3)
        xx = bx
        while xx < bx + bw:
            w_ = rb.choice((6, 6, 10, 14, 18))
            if rb.random() < 0.55:
                d.rectangle([xx, by, xx + w_, by + bh], fill=(20, 24, 32))
            xx += w_ + rb.choice((5, 8, 11))
        ar_y = by + bh + 70
        d.line([bx, ar_y, bx + bw, ar_y], fill=(*AMBER, 255), width=8)
        d.polygon([(bx + bw + 26, ar_y), (bx + bw - 6, ar_y - 16),
                   (bx + bw - 6, ar_y + 16)], fill=(*AMBER, 255))
        ctext(d, bx + bw / 2, ar_y + 26, "横方向だけ", font(36), AMBER)
        # 右: QR + 縦横矢印
        qx = W - 260 - qsize
        draw_qr(d, qx, 340, 13)
        qs2 = (N + 6) * 13
        d.line([qx - 40, 340, qx - 40, 340 + qs2], fill=(*ACCENT, 255), width=8)
        d.polygon([(qx - 40, 340 + qs2 + 26), (qx - 56, 340 + qs2 - 6),
                   (qx - 24, 340 + qs2 - 6)], fill=(*ACCENT, 255))
        d.line([qx, 340 + qs2 + 40, qx + qs2, 340 + qs2 + 40],
               fill=(*ACCENT, 255), width=8)
        d.polygon([(qx + qs2 + 26, 340 + qs2 + 40), (qx + qs2 - 6, 340 + qs2 + 24),
                   (qx + qs2 - 6, 340 + qs2 + 56)], fill=(*ACCENT, 255))
        ctext(d, qx + qs2 / 2, 340 + qs2 + 66, "縦と横の両方", font(36), ACCENT)
        return
    if t < A4:  # P3: 位置検出パターン
        _caption(d, "三隅の目玉 = 位置検出パターン")
        draw_qr(d, cx0, cy0, px, finder_fg=(226, 132, 22))
        blink = 0.5 + 0.5 * math.sin(t * 3.2)
        ox, oy = cx0 + 3 * px, cy0 + 3 * px
        fs = 7 * px
        for (fx, fy) in ((0, 0), ((N - 7) * px, 0), (0, (N - 7) * px)):
            d.rectangle([ox + fx - 8, oy + fy - 8, ox + fx + fs + 8, oy + fy + fs + 8],
                        outline=(*AMBER, int(120 + 130 * blink)), width=6)
        # ロックオン枠
        k = ease((t - A3) / 0.8)
        pad = 60 * (1 - k) + 24
        for (x, y, dx, dy) in ((cx0 - pad, cy0 - pad, 1, 1),
                               (cx0 + qsize + pad, cy0 - pad, -1, 1),
                               (cx0 - pad, cy0 + qsize + pad, 1, -1),
                               (cx0 + qsize + pad, cy0 + qsize + pad, -1, -1)):
            d.line([x, y, x + 46 * dx, y], fill=(*ACCENT, 255), width=8)
            d.line([x, y, x, y + 46 * dy], fill=(*ACCENT, 255), width=8)
        return
    if t < A5:  # P4: 回転しても読める
        _caption(d, "斜めでも逆さまでも、一瞬で見つかる")
        ang = 360 * ease((t - A4) / (A5 - A4))
        qi = qr_image(11, finder_fg=(226, 132, 22))
        qi = qi.rotate(ang, expand=True, resample=Image.BICUBIC)
        img.paste(qi, (W // 2 - qi.width // 2, 620 - qi.height // 2), qi)
        return
    if t < A6:  # P5: 1:1:3:1:1 の比率
        _caption(d, "白黒の比率は、どこを通っても 1:1:3:1:1")
        draw_qr(d, 220, 330, 11, finder_fg=(226, 132, 22))
        qs2 = (N + 6) * 11
        yy = 330 + (3 + 3.5) * 11
        d.line([220, yy, 220 + qs2, yy], fill=(*RED, 220), width=5)
        # 右: 比率バー
        bx, by, u, bh = 900, 480, 92, 120
        segs = [(1, True), (1, False), (3, True), (1, False), (1, True)]
        xx = bx
        for (n_, black) in segs:
            w_ = n_ * u
            d.rectangle([xx, by, xx + w_, by + bh],
                        fill=(20, 24, 32) if black else (245, 245, 245),
                        outline=(120, 126, 140), width=2)
            lab = str(n_)
            ctext(d, xx + w_ / 2, by + bh + 18, lab, font(44),
                  AMBER if n_ == 3 else INK)
            xx += w_
        ctext(d, bx + 3.5 * u, by - 74, "黒 : 白 : 黒 : 白 : 黒", font(38), GRAY)
        return
    # P6: 余白（クワイエットゾーン）
    _caption(d, "周りの余白まで含めて、QRコード")
    blink = 0.5 + 0.5 * math.sin(t * 2.8)
    qx, qy = cx0, cy0
    d.rounded_rectangle([qx - 6, qy - 6, qx + qsize + 6, qy + qsize + 6],
                        radius=18, fill=(*AMBER, int(60 + 70 * blink)))
    draw_qr(d, qx, qy, px)
    inner = 3 * px
    d.rectangle([qx + inner, qy + inner, qx + qsize - inner, qy + qsize - inner],
                outline=(*AMBER, 255), width=4)
    ctext(d, W / 2, cy0 + qsize + 26, "この余白がないと読めないことがある",
          font(36), AMBER)


# ------------------------------------------------------------------
# 3) qr_repair — 誤り訂正（39.3秒）
#    R1=11.2 シミ→復元 / R1B=19.65 二度目 / R2=29.31 レベルと30%
# ------------------------------------------------------------------
R1, R1B, R2 = 11.2, 19.65, 29.31


def _repair_seq(d, qx, qy, qsize, t0, t, blobs, label_y):
    """シミ→スキャン→復元の一連。t0からの経過で進行。"""
    k = t - t0
    if k < 0:
        return
    # シミ
    for i, (fx, fy, rw, rh) in enumerate(blobs):
        kk = min(1.0, max(0.0, (k - i * 0.12) / 0.3))
        if kk <= 0:
            continue
        cx, cy = qx + qsize * fx, qy + qsize * fy
        d.ellipse([cx - rw * kk, cy - rh * kk, cx + rw * kk, cy + rh * kk],
                  fill=(96, 150, 70, 235))
    if k > 1.2:  # 復元中バー
        p = min(1.0, (k - 1.2) / 1.6)
        bx, bw = qx - 20, qsize + 40
        d.rounded_rectangle([bx, label_y, bx + bw, label_y + 18], radius=9,
                            fill=(30, 40, 60))
        d.rounded_rectangle([bx, label_y, bx + bw * p, label_y + 18], radius=9,
                            fill=(*ACCENT, 255))
    if k > 2.8:  # 復元完了: シミの上にマスを描き直す
        for (fx, fy, rw, rh) in blobs:
            cx, cy = qx + qsize * fx, qy + qsize * fy
            d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh],
                      fill=(96, 150, 70, 70))
        px = qsize // (N + 6)
        draw_qr(d, qx, qy, px, alpha=235)
        kk = min(1.0, (k - 2.8) / 0.3)
        r = 54 * kk
        cx, cy = qx + qsize / 2, qy + qsize / 2
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*GREEN, 235))
        if kk > 0.6:
            d.line([cx - 22, cy + 2, cx - 6, cy + 18], fill=(255, 255, 255), width=9)
            d.line([cx - 6, cy + 18, cx + 26, cy - 16], fill=(255, 255, 255), width=9)


def qr_repair(img, d, t):
    px = 13
    qsize = (N + 6) * px
    qx, qy = W // 2 - qsize // 2, 300

    if t < R1:  # P0: 本文＋予備データ
        _caption(d, "本文と一緒に、復元用の予備データを書き込む")
        draw_qr(d, qx, qy, px, parity_cols=True)
        # 凡例
        ly = qy + qsize + 40
        d.rectangle([W / 2 - 330, ly, W / 2 - 290, ly + 40], fill=(20, 24, 32))
        d.text((W / 2 - 274, ly), "本文のデータ", font=font(36), fill=INK)
        d.rectangle([W / 2 + 60, ly, W / 2 + 100, ly + 40], fill=(196, 138, 32))
        d.text((W / 2 + 116, ly), "復元用の予備", font=font(36), fill=AMBER)
        return
    _caption(d, "欠けても、残りと予備データから計算で復元")
    draw_qr(d, qx, qy, px, parity_cols=True)
    if t < R2:
        _repair_seq(d, qx, qy, qsize, R1 + 0.3, min(t, R1B),
                    [(0.28, 0.6, 130, 100), (0.5, 0.76, 96, 70)], qy + qsize + 46)
        if t >= R1B:
            _repair_seq(d, qx, qy, qsize, R1B + 0.3, t,
                        [(0.74, 0.3, 110, 90), (0.6, 0.16, 80, 60)], qy + qsize + 46)
        return
    # P2: 復元レベル4段階（statの30%が上に重なるため見出しは出さない）
    levels = [("L", 7), ("M", 15), ("Q", 25), ("H", 30)]
    bx, bw, gap = 330, 260, 60
    for i, (name, pct) in enumerate(levels):
        x = bx + i * (bw + gap)
        hmax = 330
        hh = hmax * pct / 30 * ease((t - R2 - i * 0.15) / 0.5)
        y1 = 800
        hot = name == "H"
        col = AMBER if hot else (60, 90, 130)
        d.rounded_rectangle([x, y1 - hh, x + bw, y1], radius=16, fill=(*col, 255))
        ctext(d, x + bw / 2, y1 + 20, f"レベル{name}", font(40), INK if hot else GRAY)
        if t - R2 > 0.8 + i * 0.15:
            ctext(d, x + bw / 2, y1 - hh - 60, f"{pct}%", font(48),
                  AMBER if hot else GRAY)
    if t - R2 > 2.2:
        blink = 0.5 + 0.5 * math.sin(t * 3)
        x = bx + 3 * (bw + gap)
        d.rounded_rectangle([x - 10, 800 - 330 - 90, x + bw + 10, 810], radius=20,
                            outline=(*AMBER, int(140 + 110 * blink)), width=6)


# ------------------------------------------------------------------
# 4) go_to_qr — 碁盤の白黒がQRに変わる（20.5秒）
#    G1=5.78 ひらめき→モーフ / G2=13.97 QR完成
# ------------------------------------------------------------------
G1, G2 = 5.78, 13.97
_rg = random.Random(19)
_LINES = 13
_stones = []
for _i in range(26):
    _stones.append((_rg.randrange(1, _LINES - 1), _rg.randrange(1, _LINES - 1),
                    _rg.random() < 0.5, _rg.uniform(0, 4.6)))


def _board_scene(t) -> Image.Image:
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    bs = 660
    bx, by = W // 2 - bs // 2, 300
    d.rounded_rectangle([bx - 30, by - 30, bx + bs + 30, by + bs + 30],
                        radius=16, fill=(172, 132, 84))
    step = bs / (_LINES - 1)
    for i in range(_LINES):
        d.line([bx, by + i * step, bx + bs, by + i * step], fill=(84, 60, 34), width=3)
        d.line([bx + i * step, by, bx + i * step, by + bs], fill=(84, 60, 34), width=3)
    morph = ease((t - G1) / 2.2)  # 石→四角
    for (r, c, black, delay) in _stones:
        k = ease((t - delay) / 0.3)
        if k <= 0:
            continue
        cx, cy = bx + c * step, by + r * step
        rad = step * 0.46 * k
        corner = rad * (1 - morph)  # 角丸→四角
        col = (24, 26, 30) if black else (245, 245, 242)
        d.rounded_rectangle([cx - rad, cy - rad, cx + rad, cy + rad],
                            radius=max(1, corner), fill=col,
                            outline=(70, 72, 78) if not black else None, width=2)
    return im


def go_to_qr(img, d, t):
    if t < G1:
        _caption(d, "お昼休みの囲碁")
        img.paste(_board_scene(t), (0, 0), _board_scene(t))
        return
    if t < G2:
        _caption(d, "白黒の並びなら、縦と横に情報を詰め込める")
        # ひらめきフラッシュ
        fk = max(0.0, 1 - (t - G1) / 0.5)
        board = _board_scene(t)
        cross = ease((t - G1 - 1.8) / 2.6)  # 碁盤→QRクロスフェード
        img.paste(board, (0, 0), board)
        if cross > 0:
            qi = qr_image(15, finder_fg=(226, 132, 22))
            qi.putalpha(qi.split()[3].point(lambda a: int(a * cross)))
            img.paste(qi, (W // 2 - qi.width // 2, 300), qi)
        if fk > 0:
            ov = Image.new("RGBA", (W, H), (255, 250, 220, int(200 * fk)))
            img.paste(ov, (0, 0), ov)
        return
    _caption(d, "碁盤から生まれた、面で持つコード")
    qi = qr_image(15, finder_fg=(226, 132, 22))
    img.paste(qi, (W // 2 - qi.width // 2, 300), qi)
    blink = 0.5 + 0.5 * math.sin(t * 3)
    qx = W // 2 - qi.width // 2
    d.rectangle([qx - 12, 300 - 12, qx + qi.width + 12, 300 + qi.height + 12],
                outline=(*AMBER, int(110 + 130 * blink)), width=5)


# ------------------------------------------------------------------
# 5) 時代カード（QR史の年表バー付き）
# ------------------------------------------------------------------
ERAS = ["現場の悲鳴", "囲碁のひらめき", "1994 誕生", "特許開放", "世界標準"]


def _silhouette(d, cx, cy, scale, col):
    r = int(58 * scale)
    d.ellipse([cx - r, cy - r * 2.1, cx + r, cy - 0.1 * r], fill=col)
    d.pieslice([cx - r * 2, cy - r * 0.2, cx + r * 2, cy + r * 2.6],
               start=180, end=360, fill=col)


def make_era(idx, year, title, persons, sub):
    def draw(img, d, t):
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
        n = len(persons)
        for i, (name, role) in enumerate(persons):
            kp = ease((t - 0.9 - i * 0.25) / 0.4)
            if kp <= 0:
                continue
            cx = W / 2 + (i - (n - 1) / 2) * 420
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


# ------------------------------------------------------------------
# 6) era_dev — 開発者紹介カード（原昌宏さんの写真入り・CC0/qargo氏撮影）
#    span3=17.9s → DUR 19.5
# ------------------------------------------------------------------
_hara = None


def _hara_img():
    global _hara
    if _hara is None:
        ph = Image.open("assets/images/hara_qargo.jpg").convert("RGB")
        hgt = 720
        ph = ph.resize((int(ph.width * hgt / ph.height), hgt), Image.LANCZOS)
        mask = Image.new("L", ph.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, ph.width, ph.height],
                                               radius=28, fill=255)
        ph.putalpha(mask)
        _hara = ph
    return _hara


def era_dev(img, d, t):
    k = ease(t / 0.5)
    f_year = font(140)
    d.text((260, 130 - 40 * (1 - k)), "1990s", font=f_year,
           fill=(*AMBER, int(255 * k)))
    k2 = ease((t - 0.35) / 0.4)
    if k2 > 0:
        d.text((266, 330), "原昌宏", font=font(84), fill=(*INK, int(255 * k2)))
        d.text((270, 450), "DENSO の技術者", font=font(46),
               fill=(*GRAY, int(255 * k2)))
    k3 = ease((t - 0.8) / 0.4)
    if k3 > 0:
        for i, line in enumerate(["読み取りやすさへの執念と", "わずか2人の開発チーム"]):
            d.text((270, 560 + i * 64), line, font=font(40),
                   fill=(*INK, int(255 * k3)))
    # 写真（右側・ふわっと登場）
    kp = ease((t - 0.5) / 0.6)
    if kp > 0:
        ph = _hara_img().copy()
        ph.putalpha(ph.split()[3].point(lambda a: int(a * kp)))
        px_, py_ = 1170, 140 + int(20 * (1 - kp))
        img.paste(ph, (px_, py_), ph)
        d.text((px_ + 6, 140 + 720 + 12), "写真: qargo（CC0 / Wikimedia Commons）",
               font=font(24), fill=(110, 118, 134))
    # 年表バー
    bx0, bx1, by = 560, 1360, 1008
    d.line([bx0, by, bx1, by], fill=(50, 64, 92), width=6)
    f_tick = font(24)
    for i, e in enumerate(ERAS):
        x = bx0 + (bx1 - bx0) * i / (len(ERAS) - 1)
        cur = i == 0
        r = 13 + (5 * (0.5 + 0.5 * math.sin(t * 3)) if cur else 0)
        col = AMBER if cur else (60, 72, 98)
        d.ellipse([x - r, by - r, x + r, by + r], fill=col)
        d.text((x - d.textlength(e, font=f_tick) / 2, by + 20), e,
               font=f_tick, fill=INK if cur else GRAY)


# ------------------------------------------------------------------
# 7) green_qr — 全緑QRは読めない→濃い緑なら読める（3章の後日談ネタ）
#    FAIL=10.56（つむぎの指摘の頭）/ OK=34.76（作り直すのだ の頭）/ DUR 41.5
# ------------------------------------------------------------------
GFAIL, GOK = 10.56, 34.76


def green_qr(img, d, t):
    px = 13
    qsize = (N + 6) * px
    qx, qy = W // 2 - qsize // 2, 280

    if t < GOK:
        # 全部ずんだ色（低コントラスト）
        _caption(d, "ずんだ色QR、爆誕" if t < GFAIL else "明暗の差がないと、機械には見えない")
        draw_qr(d, qx, qy, px, fg=(122, 186, 108), bgc=(158, 208, 146))
        if t < GFAIL:
            # スキャンを試みる
            k = (t - 6.0)
            if 0 < k < 1.6:
                yy = qy + qsize * (0.5 - 0.5 * math.cos(k / 1.6 * math.tau))
                d.rectangle([qx - 14, yy - 3, qx + qsize + 14, yy + 3],
                            fill=(*ACCENT, 230))
        else:
            blink = (int(t * 1.6) % 2) == 0
            if blink:
                cx, cy = qx + qsize / 2, qy + qsize / 2
                r = 58
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*RED, 235))
                d.line([cx - 22, cy - 22, cx + 22, cy + 22], fill=(255, 255, 255), width=10)
                d.line([cx - 22, cy + 22, cx + 22, cy - 22], fill=(255, 255, 255), width=10)
            ctext(d, W / 2, qy + qsize + 30, "読み取れません", font(48), RED)
        return
    # 濃いずんだ色 × 白 → 成功
    _caption(d, "濃いずんだ色 × 白なら、読める")
    draw_qr(d, qx, qy, px, fg=(26, 92, 44), bgc=(252, 252, 250))
    k = t - GOK - 1.2
    if 0 < k < 0.8:
        yy = qy + qsize * (0.5 - 0.5 * math.cos(k / 0.8 * math.tau))
        d.rectangle([qx - 14, yy - 3, qx + qsize + 14, yy + 3], fill=(*ACCENT, 230))
    if k >= 0.8:
        kk = min(1.0, (k - 0.8) / 0.25)
        r = 58 * kk
        cx, cy = qx + qsize / 2, qy + qsize / 2
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*GREEN, 240))
        if kk > 0.6:
            d.line([cx - 22, cy + 2, cx - 6, cy + 18], fill=(255, 255, 255), width=9)
            d.line([cx - 6, cy + 18, cx + 26, cy - 16], fill=(255, 255, 255), width=9)
        ctext(d, W / 2, qy + qsize + 30, "読み取り成功", font(48), GREEN)


def main() -> None:
    render("qr_ticket", 34.0, qr_ticket)
    render("qr_anatomy", 75.0, qr_anatomy)
    render("qr_repair", 39.3, qr_repair)
    render("go_to_qr", 20.5, go_to_qr)
    render("era_1994", 15.0, make_era(
        2, "1994", "QRコード、誕生", [("原昌宏", "DENSO")],
        "名前の由来は Quick Response ＝ 素早い応答"))
    render("era_open", 26.0, make_era(
        3, "無料開放", "特許の権利を行使しないと宣言", [("DENSO", "1994〜")],
        "誰でも無料で使える、世界の共通インフラへ"))
    render("era_dev", 19.5, era_dev)
    render("green_qr", 41.5, green_qr)


if __name__ == "__main__":
    main()
