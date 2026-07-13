#!/usr/bin/env python3
"""auto-door プロジェクト用のアニメクリップを生成する。

  door_skit.mp4    21.5s  茶番: 手を振ってもジャンプしても開かない→おじさんは開く
  door_sensor.mp4  50.2s  センサーの仕組み（赤外線シャワー→反射一定→変化→全部同じ→補助センサー）
  door_ignore.mp4  43.5s  無視される理由（黒い服→静止=背景→真横=エリア外）
  heron_door.mp4   31.8s  ヘロンの神殿の扉（火→空気膨張→水移動→滑車で開く）
  era_1956.mp4     17.5s  国産マット式の時代カード

フェーズ境界は timing.json のカット実測に同期（コメントの秒数）。
実行: PYTHONPATH=. python3 scripts/gen_door_extras.py [クリップ名...]
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
IR = (255, 120, 90)      # 赤外線
DOOR = (120, 180, 230)   # ガラス扉
FRAME = (60, 76, 104)

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
    tmp = Path(tempfile.mkdtemp(prefix=f"ad_{name}_"))
    for fi in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw_frame(ImageDraw.Draw(img, "RGBA"), fi / FPS)
        img.save(tmp / f"{fi:04d}.png")
    encode(tmp, Path(f"assets/clips/{name}.mp4"))


def _door(d, cx, open_k=0.0, w=560, h=520, top=300):
    """正面から見た自動ドア。open_k=0閉 1全開。センサー箱つき。"""
    d.rectangle([cx - w / 2 - 26, top - 90, cx + w / 2 + 26, top], fill=FRAME)
    d.rounded_rectangle([cx - 70, top - 74, cx + 70, top - 18], radius=10,
                        fill=(16, 20, 30), outline=(90, 110, 140), width=3)
    ctext(d, cx, top - 68, "センサー", font(26), GRAY)
    d.rectangle([cx - w / 2 - 26, top, cx - w / 2, top + h], fill=FRAME)
    d.rectangle([cx + w / 2, top, cx + w / 2 + 26, top + h], fill=FRAME)
    slide = (w / 2) * open_k
    # 左扉・右扉
    for sgn in (-1, 1):
        x0 = cx + sgn * slide - (w / 4) + (0 if sgn < 0 else 0)
        lx = cx - w / 2 + (slide if sgn > 0 else 0)
        if sgn < 0:
            x0, x1 = cx - w / 2 - slide, cx - slide
        else:
            x0, x1 = cx + slide, cx + w / 2 + slide
        d.rectangle([max(x0, cx - w / 2 - 26), top + 6,
                     min(x1, cx + w / 2 + 26), top + h],
                    fill=(*DOOR, 70), outline=DOOR, width=4)
    d.rectangle([cx - w / 2 - 26, top + h, cx + w / 2 + 26, top + h + 14], fill=FRAME)


def _person(d, cx, cy, scale=1.0, col=(220, 226, 238), arms_up=False):
    r = int(30 * scale)
    d.ellipse([cx - r, cy - 150 * scale, cx + r, cy - 150 * scale + 2 * r], fill=col)
    d.rounded_rectangle([cx - 36 * scale, cy - 88 * scale, cx + 36 * scale, cy + 40 * scale],
                        radius=int(24 * scale), fill=col)
    if arms_up:
        d.line([cx - 30 * scale, cy - 70 * scale, cx - 66 * scale, cy - 130 * scale],
               fill=col, width=int(16 * scale))
        d.line([cx + 30 * scale, cy - 70 * scale, cx + 66 * scale, cy - 130 * scale],
               fill=col, width=int(16 * scale))
    d.line([cx - 16 * scale, cy + 40 * scale, cx - 16 * scale, cy + 110 * scale],
           fill=col, width=int(16 * scale))
    d.line([cx + 16 * scale, cy + 40 * scale, cx + 16 * scale, cy + 110 * scale],
           fill=col, width=int(16 * scale))


# ------------------------------------------------------------------
# 1) door_skit — 茶番（手振り/ジャンプ=5.46 / おじさん=13.71 / DUR 21.5）
# ------------------------------------------------------------------
S_WAVE, S_OJISAN = 5.46, 13.71
ZUNDA = (140, 200, 120)  # ずんだもん風カラー


def door_skit(d, t):
    cx = W / 2
    if t < S_WAVE:
        _caption(d, "目の前にいるのに、開かない")
        _door(d, cx, 0.0)
        _person(d, cx - 420, 660, col=ZUNDA)
        for i in range(3):
            a = int(200 * (0.4 + 0.6 * ((t * 2 + i * 0.3) % 1)))
            ctext(d, cx - 420, 380 - i * 8, "…", font(60), (200, 210, 225, a))
        return
    if t < S_OJISAN:
        _caption(d, "手を振っても、跳んでも、開かない")
        _door(d, cx, 0.0)
        hop = abs(math.sin(t * 4)) * 60
        _person(d, cx - 420, 660 - hop, col=ZUNDA, arms_up=True)
        ctext(d, cx - 420, 350, "バサバサ", font(38), GRAY)
        return
    _caption(d, "後ろのおじさんには、スッと開く")
    k = ease((t - S_OJISAN) / 1.2)
    _door(d, cx, k)
    _person(d, cx - 470, 660, col=ZUNDA)
    ojx = cx - 260 + ease((t - S_OJISAN) / 2.5) * 240
    _person(d, ojx, 660, col=(225, 210, 180))
    if k >= 1.0:
        # 人物と重ならないよう扉上部のガラス面に出す
        ctext(d, cx, 345, "ウェルカム", font(40), GREEN)
        ctext(d, cx - 470, 380, "なんでなのだ…", font(36), RED)


# ------------------------------------------------------------------
# 2) door_sensor — 仕組み（反射一定=8.37 / 変化=16.57 / (Z=25.66) /
#    全部同じ=30.22 / 補助=38.88 / DUR 50.2）
# ------------------------------------------------------------------
D_SAME, D_CHANGE, D_WORLD, D_GUARD = 8.37, 16.57, 30.22, 38.88


def _ir_shower(d, sx, sy, spread, ln, on=1.0, n=7):
    for i in range(n):
        a = -spread / 2 + spread * i / (n - 1)
        ex = sx + ln * math.sin(a)
        ey = sy + ln * math.cos(a)
        d.line([sx, sy, ex, ey], fill=(*IR, int(150 * on)), width=5)


def door_sensor(d, t):
    cx = W / 2
    if t < D_SAME:
        _caption(d, "上の箱から、赤外線のシャワー")
        _door(d, cx, 0.0)
        k = ease(t / 1.0)
        _ir_shower(d, cx, 236, 1.1, 590 * k)
        d.ellipse([cx - 330, 790, cx + 330, 850], outline=IR, width=6)
        ctext(d, cx, 866, "床の検知エリア", font(32), GRAY)
        return
    if t < D_CHANGE:
        _caption(d, "誰もいなければ、跳ね返りはいつも同じ")
        _door(d, cx - 300, 0.0, w=420, h=420, top=340)
        _ir_shower(d, cx - 300, 276, 0.9, 480)
        # 上向きの反射
        for i in range(4):
            x = cx - 430 + i * 90
            kk = ((t * 0.8 + i * 0.25) % 1.0)
            d.line([x, 800 - kk * 200, x, 800 - kk * 200 - 40], fill=(*IR, 160), width=4)
        # 一定グラフ
        d.rounded_rectangle([1180, 420, 1720, 720], radius=20, fill=(24, 34, 54))
        ctext(d, 1450, 448, "反射の量", font(34), GRAY)
        y = 600 + 4 * math.sin(t * 3)
        d.line([1220, y, 1680, y], fill=GREEN, width=8)
        ctext(d, 1450, 640, "ずっと一定 = 誰もいない", font(30), GREEN)
        return
    if t < D_WORLD:
        _caption(d, "人が入ると「変化」→ 開く")
        k = ease((t - D_CHANGE) / 2.0)
        _door(d, cx - 300, ease((t - D_CHANGE - 1.2) / 0.8), w=420, h=420, top=340)
        _ir_shower(d, cx - 300, 276, 0.9, 480)
        px = cx - 720 + k * 260
        _person(d, px, 700, 0.9)
        d.rounded_rectangle([1180, 420, 1720, 720], radius=20, fill=(24, 34, 54))
        ctext(d, 1450, 448, "反射の量", font(34), GRAY)
        pts = [(1220 + i * 20, 600) for i in range(12)]
        kk = ease((t - D_CHANGE - 0.8) / 0.8)
        for i in range(12, 24):
            x = 1220 + i * 20
            y = 600 - kk * (70 + 20 * math.sin(i)) if i > 14 else 600
            pts.append((x, y))
        d.line(pts, fill=AMBER, width=8, joint="curve")
        if kk > 0.6:
            ctext(d, 1450, 640, "変化を検知 → OPEN", font(30), AMBER)
        return
    if t < D_GUARD:
        _caption(d, "ドアの目には、全部おなじ「変化」")
        items = [("人", GREEN), ("台車", ACCENT), ("買い物袋", AMBER)]
        for i, (s, col) in enumerate(items):
            kk = ease((t - D_WORLD - i * 0.5) / 0.5)
            if kk <= 0:
                continue
            x = 480 + i * 480
            d.rounded_rectangle([x - 170, 430, x + 170, 640], radius=24,
                                fill=(24, 34, 54, int(255 * kk)))
            if kk > 0.5:
                ctext(d, x, 470, s, font(52), col)
                ctext(d, x, 560, "= 反射の変化", font(34), GRAY)
        ctext(d, W / 2, 760, "誰であるかは、見ていない", font(44), GRAY)
        return
    _caption(d, "開いたら、見張り係にバトンタッチ")
    _door(d, cx, 1.0)
    # 補助センサーのビーム（ドア間）
    blink = 0.5 + 0.5 * math.sin(t * 4)
    for y in (420, 520, 620):
        d.line([cx - 250, y, cx + 250, y], fill=(*GREEN, int(120 + 100 * blink)), width=5)
    _person(d, cx, 660, 0.95)
    ctext(d, cx, 880, "人がいる間は、絶対に閉めない", font(38), GREEN)


# ------------------------------------------------------------------
# 3) door_ignore — 無視される理由（黒服=6.63 / 静止=22.23 / 真横=31.44 / DUR 43.5）
# ------------------------------------------------------------------
G_BLACK, G_STILL, G_SIDE = 6.63, 22.23, 31.44
REASONS = ["黒い服", "動かない", "真横から", "環境"]


def door_ignore(d, t):
    cx = W / 2
    if t < G_BLACK:
        _caption(d, "無視される、4つの定番")
        for i, s in enumerate(REASONS):
            kk = ease((t - i * 0.5) / 0.5)
            if kk <= 0:
                continue
            x = 330 + i * 420
            d.rounded_rectangle([x - 170, 440, x + 170, 640], radius=24,
                                fill=(24, 34, 54, int(255 * kk)))
            if kk > 0.5:
                ctext(d, x, 480, f"その{i + 1}", font(30), GRAY)
                ctext(d, x, 530, s, font(48), AMBER)
        return
    if t < G_STILL:
        _caption(d, "黒は赤外線を吸い込む")
        _door(d, cx - 300, 0.0, w=420, h=420, top=340)
        _ir_shower(d, cx - 300, 276, 0.9, 480)
        _person(d, cx - 340, 700, 0.9, col=(30, 32, 40))
        # 吸収表現: 反射矢印が出ない×
        d.line([cx - 90, 560, cx - 30, 500], fill=RED, width=10)
        d.line([cx - 90, 500, cx - 30, 560], fill=RED, width=10)
        d.rounded_rectangle([1180, 430, 1730, 700], radius=20, fill=(24, 34, 54))
        ctext(d, 1455, 460, "跳ね返り", font(34), GRAY)
        y0 = 560
        d.line([1220, y0, 1450, y0], fill=GREEN, width=8)
        kk = ease((t - G_BLACK - 0.8) / 0.8)
        d.line([1450, y0, 1450 + 230 * kk, y0 + 60 * kk], fill=RED, width=8)
        if kk > 0.7:
            ctext(d, 1455, 640, "弱すぎて「無人」扱い", font(30), RED)
        return
    if t < G_SIDE:
        _caption(d, "止まった人は「背景」になる")
        _door(d, cx - 300, 0.0, w=420, h=420, top=340)
        _ir_shower(d, cx - 300, 276, 0.9, 480)
        k = ease((t - G_STILL) / 6.0)
        col = tuple(int(220 - (220 - 60) * k) for _ in range(3))
        _person(d, cx - 340, 700, 0.9, col=(col[0], col[1] + 6, col[2] + 22))
        d.rounded_rectangle([1180, 470, 1730, 660], radius=20, fill=(24, 34, 54))
        ctext(d, 1455, 500, "センサーの判定", font(32), GRAY)
        label = "人がいる…？" if k < 0.5 else "＝ 床や壁と同じ"
        ctext(d, 1455, 560, label, font(40), AMBER if k < 0.5 else GRAY)
        return
    _caption(d, "真横からだと、エリアの外")
    _door(d, cx, 0.0, w=460, h=430, top=330)
    d.ellipse([cx - 300, 780, cx + 300, 850], outline=IR, width=6)
    ctext(d, cx, 866, "検知エリア", font(30), GRAY)
    k = ((t - G_SIDE) / 3.5) % 1.0
    px = cx - 760 + k * 660
    _person(d, px, 740, 0.85)
    d.line([cx - 740, 820, cx - 340, 820], fill=(120, 140, 170), width=4)
    d.polygon([(cx - 350, 808), (cx - 320, 820), (cx - 350, 832)], fill=(120, 140, 170))
    if px < cx - 320:
        ctext(d, px, 520, "まだ見えていない", font(32), RED)


# ------------------------------------------------------------------
# 4) heron_door — 神殿の扉（膨張=3.96 / 水移動=13.84 / 開く=24.18 / DUR 31.8）
# ------------------------------------------------------------------
H_FIRE, H_WATER, H_OPEN = 3.96, 13.84, 24.18
STONE = (196, 186, 160)
STONE_DK = (150, 140, 116)


def heron_door(d, t):
    fire_k = ease((t - H_FIRE + 1.0) / 1.0) if t >= H_FIRE - 1.0 else 0.0
    water_k = ease((t - H_WATER) / 6.0) if t >= H_WATER else 0.0
    open_k = ease((t - H_OPEN) / 4.0) if t >= H_OPEN else 0.0
    if t < H_FIRE:
        _caption(d, "神殿の扉の、地下の仕掛け")
    elif t < H_WATER:
        _caption(d, "火が空気を膨らませる")
    elif t < H_OPEN:
        _caption(d, "押された水が、バケツへ")
    else:
        _caption(d, "重くなったバケツが、扉を引き開ける")
    # 地面
    gy = 620
    d.rectangle([0, gy, W, gy + 8], fill=STONE_DK)
    # 神殿（左）: 柱と扉
    tx = 560
    d.rectangle([tx - 300, 300, tx + 300, 356], fill=STONE)   # 屋根梁
    d.polygon([(tx - 330, 300), (tx, 226), (tx + 330, 300)], fill=STONE)
    for px_ in (tx - 260, tx + 260):
        d.rectangle([px_ - 28, 356, px_ + 28, gy], fill=STONE)
    # 扉（2枚を左右に開く表現）
    dw = 150
    slide = open_k * 110
    for sgn in (-1, 1):
        x0 = tx + sgn * (10 + slide)
        d.rectangle([min(x0, x0 + sgn * dw), 386, max(x0, x0 + sgn * dw), gy],
                    fill=(96, 70, 44), outline=(60, 42, 26), width=4)
    if open_k > 0.9:
        ctext(d, tx, 410, "ゴゴゴ…", font(34), AMBER)
    # 祭壇（右）と火
    ax = 1330
    d.rectangle([ax - 90, gy - 130, ax + 90, gy], fill=STONE_DK)
    ctext(d, ax, gy - 170, "祭壇", font(30), GRAY)
    if fire_k > 0:
        rr = random.Random(int(t * 12))
        for _ in range(6):
            fx = ax + rr.uniform(-40, 40)
            fh = rr.uniform(40, 90) * fire_k
            d.polygon([(fx - 14, gy - 130), (fx + 14, gy - 130), (fx, gy - 130 - fh)],
                      fill=(255, 150 + int(60 * rr.random()), 60, 230))
    # 地下装置
    uy = gy + 40
    # 空気室（祭壇の下）
    d.rounded_rectangle([ax - 100, uy, ax + 100, uy + 150], radius=14,
                        outline=ACCENT, width=5)
    if fire_k > 0:
        r = 20 + 26 * fire_k
        for i in range(3):
            ang = t * 2 + i * 2.1
            bx_ = ax + math.cos(ang) * 30
            by_ = uy + 75 + math.sin(ang) * 30
            d.ellipse([bx_ - r / 2, by_ - r / 2, bx_ + r / 2, by_ + r / 2],
                      outline=(255, 160, 120), width=3)
        ctext(d, ax, uy + 160, "空気が膨張", font(28), (255, 160, 120))
    # 水容器（中央）と水
    wx = 1000
    d.rounded_rectangle([wx - 110, uy, wx + 110, uy + 200], radius=14,
                        outline=ACCENT, width=5)
    lvl = 150 - 110 * water_k
    d.rectangle([wx - 104, uy + 200 - lvl, wx + 104, uy + 194], fill=(80, 150, 230, 200))
    # 接続管
    d.line([ax - 100, uy + 60, wx + 110, uy + 60], fill=ACCENT, width=6)
    # 水→バケツの管
    bx_ = 780
    d.line([wx - 110, uy + 170, bx_ + 60, uy + 170], fill=ACCENT, width=6)
    if 0 < water_k < 1:
        for i in range(3):
            kk = ((t * 0.7 + i * 0.33) % 1.0)
            px_ = wx - 110 - kk * (wx - 110 - bx_ - 60)
            d.ellipse([px_ - 8, uy + 162, px_ + 8, uy + 178], fill=(120, 190, 250))
    # バケツ（ロープで滑車→扉）
    by_ = uy + 60 + 120 * water_k
    d.polygon([(bx_ - 60, by_), (bx_ + 60, by_), (bx_ + 42, by_ + 90), (bx_ - 42, by_ + 90)],
              outline=(210, 200, 170), width=5)
    wl = 80 * water_k
    if wl > 4:
        d.polygon([(bx_ - 52, by_ + 84 - wl), (bx_ + 52, by_ + 84 - wl),
                   (bx_ + 42, by_ + 88), (bx_ - 42, by_ + 88)], fill=(80, 150, 230, 200))
    # 滑車とロープ
    py_ = gy + 30
    d.ellipse([bx_ - 18, py_ - 18, bx_ + 18, py_ + 18], outline=(210, 200, 170), width=5)
    d.line([bx_, py_, bx_, by_], fill=(210, 200, 170), width=4)
    d.line([bx_ - 18, py_, tx + 10 + slide, gy - 10], fill=(210, 200, 170), width=4)
    if t >= H_OPEN + 6.0:
        ctext(d, W / 2, 880, "火を消せば、逆に動いて閉まる", font(38), GRAY)


# ------------------------------------------------------------------
# 5) 時代カード
# ------------------------------------------------------------------
ERAS = ["約2000年前 ヘロンの扉", "1956 国産マット式", "現代 センサー式"]


def _silhouette(d, cx, cy, scale, col):
    r = int(58 * scale)
    d.ellipse([cx - r, cy - r * 2.1, cx + r, cy - 0.1 * r], fill=col)
    d.pieslice([cx - r * 2, cy - r * 0.2, cx + r * 2, cy + r * 2.6],
               start=180, end=360, fill=col)


def era_1956(d, t):
    k = ease(t / 0.5)
    f_year = font(150)
    yw = d.textlength("1956", font=f_year)
    d.text(((W - yw) / 2, 120 - 40 * (1 - k)), "1956", font=f_year,
           fill=(*AMBER, int(255 * k)))
    k2 = ease((t - 0.35) / 0.4)
    if k2 > 0:
        ctext(d, W / 2, 320, "国産初の自動ドア、登場", font(72), (*INK, int(255 * k2)))
    k3 = ease((t - 0.7) / 0.4)
    if k3 > 0:
        ctext(d, W / 2, 430, "センサーではなく、マットを踏むと開いた時代",
              font(42), (*GRAY, int(255 * k3)))
    # マット式ピクトグラム
    kp = ease((t - 0.9) / 0.5)
    if kp > 0:
        cx, cy = W / 2, 740
        d.polygon([(cx - 220, cy + 40), (cx + 220, cy + 40), (cx + 170, cy + 90),
                   (cx - 170, cy + 90)], outline=AMBER, width=6)
        ctext(d, cx, cy + 104, "マット（踏むと開く）", font(30), AMBER)
        _person(d, cx, cy - 60, 0.85, col=(46, 66, 100))
    bx0, bx1, by = 560, 952, 952
    bx1 = 1360
    d.line([bx0, by, bx1, by], fill=(50, 64, 92), width=6)
    prog = ease((t - 0.4) / 1.2)
    d.line([bx0, by, bx0 + (bx1 - bx0) * prog * 1 / 2, by], fill=(*ACCENT, 255), width=6)
    f_tick = font(24)
    for i, e in enumerate(ERAS):
        x = bx0 + (bx1 - bx0) * i / 2
        cur = i == 1
        r = 13 + (5 * (0.5 + 0.5 * math.sin(t * 3)) if cur else 0)
        col = AMBER if cur else ((150, 158, 175) if i < 1 else (60, 72, 98))
        d.ellipse([x - r, by - r, x + r, by + r], fill=col)
        d.text((x - d.textlength(e, font=f_tick) / 2, by + 22), e,
               font=f_tick, fill=INK if cur else GRAY)


CLIPS = {
    "door_skit": (21.5, lambda: door_skit),
    "door_sensor": (50.2, lambda: door_sensor),
    "door_ignore": (43.5, lambda: door_ignore),
    "heron_door": (31.8, lambda: heron_door),
    "era_1956": (17.5, lambda: era_1956),
}


def main() -> None:
    names = sys.argv[1:] or list(CLIPS)
    for name in names:
        dur, fn = CLIPS[name]
        render(name, dur, fn())


if __name__ == "__main__":
    main()
