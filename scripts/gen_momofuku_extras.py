#!/usr/bin/env python3
"""momofuku プロジェクト用のアニメクリップを生成する。

  era_m1957/1958/1966/1971/1972  時代カード（黒背景+年号+ひと言）
  mf_fail.mp4       22.4s  失敗モンタージュ7フェーズ（白黒調・3段オチ）
  mf_ana.mp4        16.8s  麺の穴図解4フェーズ（スポンジ穴→お湯浸透→3分→まとめ）
  mf_gyakusama.mp4  14.6s  逆さま充填3フェーズ（落とすと割れる→かぶせる→固定）
  mf_asama.mp4      20.0s  雪の中継5フェーズ（山→TV10日間→凍る弁当→湯気→全国へ）
  mf_timer3.mp4     18.2s  3分タイマー4フェーズ（注ぐ→染みる→残り1分→完成）

フェーズ境界は timing.json のカット実測に同期（コメントの秒数）。
実行: PYTHONPATH=. python3 scripts/gen_momofuku_extras.py
"""

import math
import sys
import subprocess
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
CUPW = (246, 242, 232)

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
    # ドラマモードは吹き出しがy120〜に出るため、見出しはその上の帯(y70)に置く
    ctext(d, W / 2, 60, s, font(54), col)


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
    tmp = Path(tempfile.mkdtemp(prefix=f"mf_{name}_"))
    for fi in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw_frame(ImageDraw.Draw(img, "RGBA"), fi / FPS)
        img.save(tmp / f"{fi:04d}.png")
    encode(tmp, Path(f"assets/clips/{name}.mp4"))


# ---------------------------------------------------------------- 時代カード
ERAS = [("1957", "すべてを失う"), ("1958", "チキンラーメン誕生"),
        ("1966", "どんぶりのない国へ"), ("1971", "カップヌードル誕生"),
        ("1972", "雪の中継"), ("2005", "宇宙へ")]


def make_era(idx: int, year: str, title: str, sub: str):
    def draw(d, t):
        a = ease(t / 0.8)
        # 年表バー（下部ではなく上寄せ: 立ち絵と吹き出しを避けた中央帯に配置）
        yf = font(230)
        col = (int(INK[0] * a), int(INK[1] * a), int(INK[2] * a))
        ctext(d, W / 2, 300, year, yf, col)
        if t > 0.7:
            b = ease((t - 0.7) / 0.6)
            ctext(d, W / 2, 590, title, font(96),
                  (int(AMBER[0] * b), int(AMBER[1] * b), int(AMBER[2] * b)))
        if sub and t > 1.3:
            b = ease((t - 1.3) / 0.6)
            ctext(d, W / 2, 730, sub, font(54),
                  (int(GRAY[0] * b), int(GRAY[1] * b), int(GRAY[2] * b)))
        # 年表ドット
        bar_y = 880
        x0, x1 = 360, W - 360
        d.line([x0, bar_y, x1, bar_y], fill=(60, 70, 90), width=6)
        for i, (y_, _) in enumerate(ERAS):
            x = x0 + (x1 - x0) * i / (len(ERAS) - 1)
            on = i == idx
            r = 16 if on else 10
            d.ellipse([x - r, bar_y - r, x + r, bar_y + r],
                      fill=AMBER if on else (80, 90, 110))
            if on:
                pulse = 1 + 0.2 * math.sin(t * 4)
                pr = int(24 * pulse)
                d.ellipse([x - pr, bar_y - pr, x + pr, bar_y + pr],
                          outline=AMBER, width=3)
    return draw


# ---------------------------------------------------------------- 麺の束
def _noodle_block(d, cx, cy, w=380, h=200, col=NOODLE, broken=False, tilt=0.0):
    """波線の麺塊。broken でヒビ、tilt で傾き表現（簡易）。"""
    import random
    rnd = random.Random(7)
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                        radius=40, fill=col)
    dk = tuple(int(c * 0.82) for c in col)
    for i in range(9):
        y = cy - h / 2 + 20 + i * (h - 40) / 8 + tilt * (i - 4)
        pts = []
        for j in range(24):
            x = cx - w / 2 + 16 + j * (w - 32) / 23
            pts.append((x, y + 6 * math.sin(j * 1.1 + i)))
        d.line(pts, fill=dk, width=5)
    if broken:
        d.line([cx - 30, cy - h / 2 - 8, cx + 10, cy + h / 2 + 8],
               fill=(40, 44, 54), width=10)
        d.line([cx + 60, cy - h / 2 - 8, cx + 90, cy + h / 2 + 8],
               fill=(40, 44, 54), width=7)


def _batsu(d, cx, cy, size=70, t=1.0):
    a = ease(t)
    s = size * a
    for dx in (-1, 1):
        d.line([cx - s * dx, cy - s, cx + s * dx, cy + s], fill=RED, width=18)


# ---------------------------------------------------------------- 失敗モンタージュ
# 境界(実測): [0, 3.72, 6.34, 8.64, 12.2, 16.32, 19.02] / DUR 22.4
F_P = [0.0, 3.72, 6.34, 8.64, 12.2, 16.32, 19.02]
F_DUR = 22.4


def draw_fail(d, t):
    g = (168, 172, 182)  # 白黒調
    gd = (120, 124, 134)
    if t < F_P[1]:
        # P0 タイトル（立ち絵の頭より上の帯に収める）
        a = ease(t / 0.8)
        ctext(d, W / 2, 180, "失敗の記録",
              font(120), tuple(int(c * a) for c in g))
        if t > 1.0:
            b = ease((t - 1.0) / 0.6)
            ctext(d, W / 2, 330, "1957 - 1958　研究小屋にて",
                  font(48), tuple(int(c * b) for c in gd))
    elif t < F_P[2]:
        # P1 スープ練り込み
        lt = t - F_P[1]
        _caption(d, "その1　麺にスープを練り込む", g)
        _noodle_block(d, W / 2, 560, col=g)
        # スープの渦
        for i in range(3):
            ang = lt * 2 + i * 2.1
            x = W / 2 + 250 * math.cos(ang)
            y = 560 + 90 * math.sin(ang)
            d.ellipse([x - 28, y - 28, x + 28, y + 28], outline=gd, width=6)
    elif t < F_P[3]:
        # P2 ぼろぼろ
        lt = t - F_P[2]
        _caption(d, "→ 麺がぼろぼろに切れた", g)
        _noodle_block(d, W / 2, 560, col=gd, broken=True)
        _batsu(d, W / 2, 560, 90, lt / 0.5)
    elif t < F_P[4]:
        # P3 天日干し
        lt = t - F_P[3]
        _caption(d, "その2　天日で干す", g)
        # 太陽
        sx, sy = W / 2, 380
        d.ellipse([sx - 80, sy - 80, sx + 80, sy + 80], outline=g, width=10)
        for i in range(8):
            ang = i * math.pi / 4 + lt * 0.5
            d.line([sx + 110 * math.cos(ang), sy + 110 * math.sin(ang),
                    sx + 150 * math.cos(ang), sy + 150 * math.sin(ang)],
                   fill=g, width=8)
        _noodle_block(d, W / 2, 680, col=g)
    elif t < F_P[5]:
        # P4 10分かかる
        lt = t - F_P[4]
        _caption(d, "→ 戻すのに10分。麺は硬いまま", g)
        # 時計
        cx, cy, r = W / 2, 560, 150
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=g, width=12)
        ang = -math.pi / 2 + min(lt / 2.5, 1.0) * 2 * math.pi
        d.line([cx, cy, cx + (r - 40) * math.cos(ang),
                cy + (r - 40) * math.sin(ang)], fill=g, width=10)
        ctext(d, cx, cy + r + 40, "10分", font(72), g)
        _batsu(d, cx + 300, cy, 70, (lt - 2.0) / 0.5 if lt > 2.0 else 0)
    elif t < F_P[6]:
        # P5 3回目の意気込み
        lt = t - F_P[5]
        _caption(d, "その3　保存テスト", g)
        _noodle_block(d, W / 2, 560, col=g)
        d.rounded_rectangle([W / 2 - 260, 420, W / 2 + 260, 720],
                            radius=24, outline=g, width=8)
        ctext(d, W / 2, 740, "数日間、置いてみる", font(50), gd)
    else:
        # P6 カビ
        lt = t - F_P[6]
        _caption(d, "→ カビが生えた", g)
        _noodle_block(d, W / 2, 560, col=gd)
        import random
        rnd = random.Random(3)
        n = int(min(lt / 1.2, 1.0) * 26)
        for i in range(n):
            x = W / 2 - 170 + rnd.random() * 340
            y = 480 + rnd.random() * 160
            r = 8 + rnd.random() * 14
            d.ellipse([x - r, y - r, x + r, y + r], fill=(96, 128, 96))
        _batsu(d, W / 2, 560, 110, (lt - 1.2) / 0.5 if lt > 1.2 else 0)


# ---------------------------------------------------------------- 麺の穴図解
# 境界(実測): [0, 3.56, 7.86, 11.67] / DUR 16.8
A_P = [0.0, 3.56, 7.86, 11.67]
A_DUR = 16.8

_pores = []
import random as _rnd_mod
_r = _rnd_mod.Random(11)
for _ in range(60):
    ang = _r.random() * 2 * math.pi
    rad = _r.random() ** 0.5
    _pores.append((ang, rad, 8 + _r.random() * 16))


def _men_cross(d, cx, cy, R, fill=NOODLE, pore_col=(150, 120, 60), wet=0.0):
    """麺の断面（円）とスポンジ状の穴。wet 0→1 で外から水分が染みる。"""
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=fill, outline=NOODLE_DK, width=8)
    if wet > 0:
        # 外周から染みる（リング）
        depth = wet * R
        for i in range(int(depth)):
            a = 90 - int(70 * i / max(depth, 1))
            rr = R - i
            if rr <= 0:
                break
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                      outline=(BROTH[0], BROTH[1], BROTH[2], a), width=2)
    for ang, rad, pr in _pores:
        px = cx + math.cos(ang) * rad * (R - 24)
        py = cy + math.sin(ang) * rad * (R - 24)
        # 濡れた穴は色が変わる
        soaked = wet > 0 and rad > 1.0 - wet
        col = BROTH if soaked else pore_col
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=col)


def draw_ana(d, t):
    cx, cy, R = W / 2, 560, 260
    if t < A_P[1]:
        # P0 スポンジみたいに穴だらけ
        a = ease(t / 0.6)
        _caption(d, "揚げた麺の断面は、穴だらけ")
        _men_cross(d, cx, cy, R)
        if t > 1.2:
            n = int(ease((t - 1.2) / 1.2) * 12)
            for ang, rad, pr in _pores[:n]:
                px = cx + math.cos(ang) * rad * (R - 24)
                py = cy + math.sin(ang) * rad * (R - 24)
                d.ellipse([px - pr - 8, py - pr - 8, px + pr + 8, py + pr + 8],
                          outline=ACCENT, width=4)
    elif t < A_P[2]:
        # P1 お湯が穴を通って芯まで
        lt = t - A_P[1]
        _caption(d, "お湯は穴を通って、麺の芯まで届く")
        wet = min(lt / 3.6, 1.0)
        _men_cross(d, cx, cy, R, wet=wet)
        # お湯の矢印
        for i in range(4):
            ang = i * math.pi / 2 + 0.6
            x0 = cx + math.cos(ang) * (R + 120)
            y0 = cy + math.sin(ang) * (R + 120)
            x1 = cx + math.cos(ang) * (R + 30)
            y1 = cy + math.sin(ang) * (R + 30)
            d.line([x0, y0, x1, y1], fill=ACCENT, width=10)
            # 矢頭
            ah = 18
            d.polygon([(x1, y1),
                       (x1 + ah * math.cos(ang + 2.6), y1 + ah * math.sin(ang + 2.6)),
                       (x1 + ah * math.cos(ang - 2.6), y1 + ah * math.sin(ang - 2.6))],
                      fill=ACCENT)
    elif t < A_P[3]:
        # P2 3分ゲージ
        lt = t - A_P[2]
        _caption(d, "だから、お湯だけで3分")
        _men_cross(d, cx, cy - 40, 220, wet=1.0)
        gx0, gx1, gy = 480, W - 480, 900
        d.rounded_rectangle([gx0, gy - 26, gx1, gy + 26], radius=26,
                            outline=GRAY, width=5)
        p = min(lt / 3.0, 1.0)
        d.rounded_rectangle([gx0 + 6, gy - 20, gx0 + 6 + (gx1 - gx0 - 12) * p, gy + 20],
                            radius=20, fill=GREEN)
        ctext(d, W / 2, gy - 110, f"{p*3:.1f}分", font(64), GREEN)
    else:
        # P3 まとめ
        lt = t - A_P[3]
        _caption(d, "3分 ＝ 穴にお湯が染み込む時間")
        _men_cross(d, cx, cy, R, wet=1.0)
        if lt > 0.6:
            b = ease((lt - 0.6) / 0.6)
            ctext(d, W / 2, 900, "穴の発明が、時間の発明だった",
                  font(60), tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 逆さま充填
# 境界(実測): [0, 3.75, 8.0] / DUR 14.6
G_P = [0.0, 3.75, 8.0]
G_DUR = 14.6


def _cup(d, cx, cy, w=300, h=340, up=True):
    """カップ台形。up=False で逆さま。"""
    tw, bw = (w, w * 0.72) if up else (w * 0.72, w)
    pts = [(cx - tw / 2, cy - h / 2), (cx + tw / 2, cy - h / 2),
           (cx + bw / 2, cy + h / 2), (cx - bw / 2, cy + h / 2)]
    d.polygon(pts, fill=CUPW, outline=(90, 96, 110))
    d.line([pts[0], pts[1]] if up else [pts[3], pts[2]], fill=RED, width=14)


def draw_gyakusama(d, t):
    if t < G_P[1]:
        # P0 上から落とすと割れる
        lt = t - G_P[0]
        _caption(d, "上から入れると、斜めになって割れる")
        _cup(d, 560, 640)
        drop = ease(min(lt / 1.2, 1.0))
        ny = 300 + drop * 280
        _noodle_block(d, 560 + 40 * drop, ny, w=240, h=150,
                      broken=drop >= 1.0, tilt=10 * drop)
        if lt > 1.5:
            _batsu(d, 560, 560, 80, (lt - 1.5) / 0.5)
        # 説明側
        ctext(d, 1360, 560, "高速ラインでは", font(52), GRAY)
        ctext(d, 1360, 640, "麺が暴れる", font(52), GRAY)
    elif t < G_P[2]:
        # P1 逆さまにかぶせる
        lt = t - G_P[1]
        _caption(d, "発想の逆転　麺にカップをかぶせる")
        _noodle_block(d, 560, 700, w=240, h=150)
        drop = ease(min(lt / 1.6, 1.0))
        cy = 260 + drop * 300
        _cup(d, 560, cy, up=False)
        if drop >= 1.0:
            ctext(d, 1360, 600, "逆さま充填", font(72), AMBER)
    else:
        # P2 中間保持で固定
        lt = t - G_P[2]
        _caption(d, "麺はカップの中間で固定される")
        cx = W / 2
        _cup(d, cx, 580, w=340, h=400)
        # 中間保持の麺
        _noodle_block(d, cx, 560, w=250, h=150)
        # 支え線
        d.line([cx - 170, 660, cx - 125, 640], fill=GRAY, width=6)
        d.line([cx + 170, 660, cx + 125, 640], fill=GRAY, width=6)
        if lt > 1.0:
            b = ease((lt - 1.0) / 0.6)
            col = tuple(int(GREEN[i] * b) for i in range(3))
            ctext(d, cx, 880, "輸送で割れない・お湯が下にも回る", font(54), col)


# ---------------------------------------------------------------- 雪の中継
# 境界(実測): [0, 5.27, 8.03, 10.45, 15.04] / DUR 20.0
S_P = [0.0, 5.27, 8.03, 10.45, 15.04]
S_DUR = 20.0

_snow = [( _r.random(), _r.random(), 0.4 + _r.random()) for _ in range(140)]


def _snowfall(d, t, area=(0, 0, W, H)):
    x0, y0, x1, y1 = area
    for sx, sy, spd in _snow:
        y = (y0 + (sy * (y1 - y0) + t * 60 * spd)) % (y1 - y0) + y0
        x = x0 + sx * (x1 - x0) + 20 * math.sin(t * spd + sy * 9)
        r = 3 + spd * 3
        d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 228, 240, 190))


def _mountain(d, x0, y0, x1, y1):
    d.polygon([(x0, y1), ((x0 + x1) * 0.45, y0), (x1 * 0.8, y1)],
              fill=(52, 62, 82))
    d.polygon([(x0 + (x1 - x0) * 0.35, y1), ((x0 + x1) * 0.7, y0 + 60), (x1, y1)],
              fill=(40, 48, 66))
    # 冠雪
    d.polygon([((x0 + x1) * 0.45 - 70, y0 + 90), ((x0 + x1) * 0.45, y0),
               ((x0 + x1) * 0.45 + 70, y0 + 90)], fill=(210, 220, 235))


def draw_asama(d, t):
    if t < S_P[1]:
        # P0 雪山（静か）
        _mountain(d, 200, 320, W - 200, 820)
        _snowfall(d, t)
        _caption(d, "1972年2月　極寒の山", GRAY)
    elif t < S_P[2]:
        # P1 テレビ中継10日間
        lt = t - S_P[1]
        tvx0, tvy0, tvx1, tvy1 = 560, 300, W - 560, 800
        d.rounded_rectangle([tvx0 - 40, tvy0 - 40, tvx1 + 40, tvy1 + 40],
                            radius=36, fill=(30, 34, 44), outline=(70, 76, 90), width=8)
        _mountain(d, tvx0, tvy0 + 60, tvx1, tvy1 - 20)
        _snowfall(d, t, (tvx0, tvy0, tvx1, tvy1))
        d.ellipse([tvx0 + 24, tvy0 + 20, tvx0 + 52, tvy0 + 48], fill=RED)
        d.text((tvx0 + 64, tvy0 + 16), "生中継", font=font(40), fill=INK)
        days = int(min(lt / 2.0, 1.0) * 10)
        ctext(d, W / 2, 880, f"中継は {days}日間 続いた", font(56), INK)
    elif t < S_P[3]:
        # P2 凍る弁当
        _caption(d, "弁当が凍って食べられない", INK)
        bx, by = W / 2, 580
        d.rounded_rectangle([bx - 220, by - 120, bx + 220, by + 120],
                            radius=20, fill=(120, 130, 150), outline=GRAY, width=6)
        for i in range(3):
            d.rounded_rectangle([bx - 190 + i * 135, by - 80, bx - 80 + i * 135, by + 80],
                                radius=12, fill=(160, 170, 190))
        # 氷の結晶マーク
        for i, (ix, iy) in enumerate(((bx - 250, by - 160), (bx + 240, by - 130),
                                      (bx + 20, by + 170))):
            for a6 in range(6):
                ang = a6 * math.pi / 3
                d.line([ix, iy, ix + 30 * math.cos(ang), iy + 30 * math.sin(ang)],
                       fill=(180, 220, 250), width=5)
        _snowfall(d, t)
    elif t < S_P[4]:
        # P3 カップと湯気
        lt = t - S_P[3]
        _caption(d, "お湯を注ぐだけの一杯が、そこにあった", INK)
        cx = W / 2
        _cup(d, cx, 640, w=280, h=320)
        # 湯気
        for i in range(3):
            ph = lt * 1.6 + i * 2.0
            pts = []
            for j in range(14):
                yy = 470 - j * 16
                pts.append((cx - 60 + i * 60 + 26 * math.sin(ph + j * 0.5), yy))
            d.line(pts, fill=(230, 236, 246, 170), width=10)
        _snowfall(d, t)
    else:
        # P4 全国のテレビへ
        lt = t - S_P[4]
        _caption(d, "湯気は、全国のお茶の間に届いた", INK)
        n = int(min(lt / 2.2, 1.0) * 9)
        for i in range(9):
            gx = 560 + (i % 3) * 300
            gy = 330 + (i // 3) * 220
            on = i < n
            d.rounded_rectangle([gx, gy, gx + 240, gy + 170], radius=16,
                                fill=(40, 46, 58) if not on else (56, 66, 84),
                                outline=(80, 88, 104), width=4)
            if on:
                _cup(d, gx + 120, gy + 100, w=70, h=80)
                d.line([gx + 105, gy + 45, gx + 112, gy + 20], fill=INK, width=4)
                d.line([gx + 135, gy + 45, gx + 128, gy + 20], fill=INK, width=4)


# ---------------------------------------------------------------- 3分タイマー
# 境界(実測): [0, 4.15, 9.13] / DUR 13.5（両脇の立ち絵を避け、全要素をx800〜1120に集約）
T_P = [0.0, 4.15, 9.13]
T_DUR = 13.5
T_END = 12.0   # ここで0:00に到達


def _timer(d, cx, cy, R, remain, total=180.0):
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=GRAY, width=10)
    frac = 1.0 - remain / total
    d.arc([cx - R + 14, cy - R + 14, cx + R - 14, cy + R - 14],
          start=-90, end=-90 + 360 * frac, fill=GREEN, width=18)
    mm, ss = int(remain) // 60, int(remain) % 60
    ctext(d, cx, cy - 60, f"{mm}:{ss:02d}", font(110), INK)


def draw_timer3(d, t):
    cx = W / 2 + 60   # 左の立ち絵(ずんだもん)を避けて少し右へ
    caps = ["今日は、ちゃんと3分待つ", "48歳の再出発が詰まった3分",
            "待った分だけ、お湯が届く"]
    ph = 0 if t < T_P[1] else (1 if t < T_P[2] else 2)
    _caption(d, caps[ph])
    remain = max(180.0 * (1 - t / T_END), 0.0)
    _timer(d, cx, 560, 230, remain)
    # 麺のもどりゲージ（タイマー下）
    gx0, gx1, gy = cx - 160, cx + 160, 880
    d.rounded_rectangle([gx0, gy - 20, gx1, gy + 20], radius=20,
                        outline=GRAY, width=4)
    p = 1 - remain / 180.0
    d.rounded_rectangle([gx0 + 5, gy - 15, gx0 + 5 + (gx1 - gx0 - 10) * p, gy + 15],
                        radius=15, fill=BROTH)
    ctext(d, cx, gy - 76, "麺のもどり", font(38), GRAY)
    if remain <= 0:
        # 完成の湯気
        for i in range(3):
            phw = t * 1.8 + i * 2.1
            pts = []
            for j in range(10):
                yy = 300 - j * 14
                pts.append((cx - 70 + i * 70 + 20 * math.sin(phw + j * 0.5), yy))
            d.line(pts, fill=(230, 236, 246, 180), width=9)


# ---------------------------------------------------------------- main
if __name__ == "__main__":
    # 時代カード（各カット実測+1s）
    render("era_m1957", 6.4, make_era(0, "1957", "すべてを失う", "安藤百福、47歳"))
    render("era_m1958", 6.3, make_era(1, "1958", "チキンラーメン誕生",
                                      "8月25日発売・35円"))
    render("era_m1966", 7.3, make_era(2, "1966", "どんぶりのない国へ", "単身、アメリカ"))
    render("era_m1971", 6.1, make_era(3, "1971", "カップヌードル誕生",
                                      "9月18日発売・100円"))
    render("era_m1972", 6.2, make_era(4, "1972", "雪の中継", ""))
    render("mf_fail", F_DUR, draw_fail)
    render("mf_ana", A_DUR, draw_ana)
    render("mf_gyakusama", G_DUR, draw_gyakusama)
    render("mf_asama", S_DUR, draw_asama)
    render("mf_timer3", T_DUR, draw_timer3)
