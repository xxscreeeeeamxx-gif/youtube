#!/usr/bin/env python3
"""リチウムイオン電池の仕組みアニメ 掛け合い版（4フェーズ・battery-80-duoの解説に同期）を生成する。

  P0 構造:   2つの電極（正極/負極）と電解液、イオンは正極側で待機
  P1 充電:   イオンが電気の力で負極側へ押し込まれていく
  P2 放電:   イオンが正極側へ戻り、その流れが電気になる（稲妻マーク）
  P3 満タン: 負極側にぎゅうぎゅう詰めのまま高電圧 → 発熱・劣化警告

フェーズ境界は battery-80-duo の該当カット実測（timing.json）に合わせる。
ループで巻き戻って見えないよう DUR は span 合計より 1 秒ほど長くする。

出力: assets/clips/battery_anim_duo.mp4（無音・台本の video: で全画面埋め込み）
実行: PYTHONPATH=. python3 scripts/gen_battery_anim_duo.py
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

# ---- フェーズ境界（秒）: battery-80-duo chapter1 のカット実測に合わせる ----
P1S = 15.30   # 充電開始（充電というのは… の頭）
P2S = 25.98   # 放電開始（そうだよ。スマホを使うときは… の頭）
P3S = 34.87   # 満タン開始（なるほどなのだ。じゃあ満タンは… の頭）
WARN_T = 48.69  # 劣化警告テキスト（満タンの間は…高い電圧… の頭）
DUR = 57.5    # 全体尺（span合計 56.4 + 余白。ループで巻き戻さないため）

ACCENT = (58, 160, 255)
ION = (120, 210, 255)
HOT = (255, 120, 70)
INK = (235, 242, 252)
GRAY = (150, 158, 175)
YELLOW = (255, 214, 90)

# 電極の位置（立ち絵が画面下部の左右に立つため、内側に寄せてある）
LX0, LX1 = 340, 520          # 負極（左）
RX0, RX1 = W - 520, W - 340  # 正極（右）
TOP, BOT = 260, H - 160


def ease(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def lerp(a, b, k):
    return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)


def main() -> None:
    cfg = Config.load()
    font_path = cfg.find_pillow_font()
    f_big = ImageFont.truetype(font_path, 72, index=0)
    f_mid = ImageFont.truetype(font_path, 52, index=0)
    f_sub = ImageFont.truetype(font_path, 38, index=0)
    f_ion = ImageFont.truetype(font_path, 34, index=0)
    f_sign = ImageFont.truetype(font_path, 64, index=0)

    rng = random.Random(11)
    cols, rows = 4, 5
    ions = []
    for i in range(cols * rows):
        r, c = divmod(i, cols)
        left = (LX1 + 60 + c * 90, TOP + 90 + r * 130)       # 負極側の定位置
        right = (rng.uniform(RX0 - 420, RX0 - 50),            # 正極側の待機位置
                 rng.uniform(TOP + 70, BOT - 70))
        d1 = rng.uniform(0.0, (P2S - P1S) * 0.45)             # 充電の出発遅れ
        d2 = rng.uniform(0.0, (P3S - P2S) * 0.35)             # 放電の出発遅れ
        d3 = rng.uniform(0.0, 2.0)                            # 再充電の出発遅れ
        wob = rng.uniform(0, math.tau)                        # 待機中の揺らぎ位相
        ions.append((left, right, d1, d2, d3, wob))

    def ion_pos(ion, t: float):
        left, right, d1, d2, d3, wob = ion
        if t < P1S:      # P0: 正極側で待機（ゆるく揺れる）
            return (right[0] + 10 * math.sin(t * 0.9 + wob),
                    right[1] + 8 * math.sin(t * 1.3 + wob * 2))
        if t < P2S:      # P1: 負極へ移動
            k = ease((t - P1S - d1) / 3.2)
            return lerp(right, left, k)
        if t < P3S:      # P2: 正極へ戻る
            k = ease((t - P2S - d2) / 3.0)
            return lerp(left, right, k)
        # P3: 負極へ素早く再集合 → 満員でぎゅうぎゅう
        k = ease((t - P3S - d3 * 0.4) / 1.8)
        x, y = lerp(right, left, k)
        if k >= 1.0:
            heat = ease((t - P3S - 3.0) / 1.5)
            x += rng.uniform(-1, 1) * 5 * heat
            y += rng.uniform(-1, 1) * 5 * heat
        return (x, y)

    n = int(DUR * FPS)
    tmp = Path(tempfile.mkdtemp(prefix="batanim_"))

    for fi in range(n):
        t = fi / FPS
        img = Image.new("RGB", (W, H), (8, 12, 22))
        d = ImageDraw.Draw(img, "RGBA")

        # 電解液（中央の淡い帯）
        d.rounded_rectangle([LX1 + 10, TOP, RX0 - 10, BOT], radius=24,
                            fill=(20, 34, 58, 255))

        full = t >= P3S
        heat = ease((t - P3S - 3.0) / 1.5) if full else 0.0

        # 電極（満タンで負極が熱を帯びる）
        lcol = tuple(int(60 + (HOT[k] - 60) * heat * 0.55) for k in range(3))
        d.rounded_rectangle([LX0, TOP, LX1, BOT], radius=18, fill=(*lcol, 255),
                            outline=(*ACCENT, 255), width=4)
        d.rounded_rectangle([RX0, TOP, RX1, BOT], radius=18, fill=(46, 52, 66, 255),
                            outline=(150, 158, 175, 255), width=4)
        # 極板ラベルは縦書きで板の中に（画面下部は立ち絵と重なるため）
        for x0, x1, mark, label in ((LX0, LX1, "−", "負極"), (RX0, RX1, "＋", "正極")):
            cx = (x0 + x1) / 2
            d.text((cx - 18, TOP + 14), mark, font=f_sign, fill=INK)
            for k, chz in enumerate(label):
                d.text((cx - 26, (TOP + BOT) / 2 - 70 + k * 62), chz,
                       font=f_mid, fill=INK)

        # フェーズごとの見出し（左上の章見出しタブと重ならないよう y=150）
        if t < P1S:
            head, hcol = "電池の中は 2つの部屋", INK
        elif t < P2S:
            head, hcol = "充電 = イオンを負極に押し込む", INK
        elif t < P3S:
            head, hcol = "使うとき = イオンが戻る流れが電気", INK
        else:
            head, hcol = "満タン = ぎゅうぎゅう詰めのまま", (255, 190, 160)
        tw = d.textlength(head, font=f_big)
        d.text(((W - tw) / 2, 150), head, font=f_big, fill=hcol)

        # P0: 電解液ラベル
        if t < P1S:
            lbl = "電解液（イオンが移動できる液体）"
            tw = d.textlength(lbl, font=f_sub)
            d.text(((W - tw) / 2, BOT - 70), lbl, font=f_sub, fill=GRAY)

        # P1/P2: 移動方向の矢印（脈動）
        if P1S <= t < P2S or P2S <= t < P3S:
            charging = t < P2S
            ax = W / 2 + 80 * math.sin(t * 3)
            if charging:
                d.line([ax + 180, H / 2, ax - 180, H / 2], fill=(*ACCENT, 230), width=14)
                d.polygon([(ax - 240, H / 2), (ax - 180, H / 2 - 34),
                           (ax - 180, H / 2 + 34)], fill=(*ACCENT, 230))
            else:
                d.line([ax - 180, H / 2, ax + 180, H / 2], fill=(*YELLOW, 230), width=14)
                d.polygon([(ax + 240, H / 2), (ax + 180, H / 2 - 34),
                           (ax + 180, H / 2 + 34)], fill=(*YELLOW, 230))

        # P2: 電気が流れている表現（稲妻マーク）
        if P2S <= t < P3S:
            blink = 0.6 + 0.4 * math.sin(t * 6)
            bx, by = W / 2, TOP + 120
            bolt = [(bx - 18, by), (bx + 6, by), (bx - 8, by + 44),
                    (bx + 22, by + 44), (bx - 22, by + 116),
                    (bx - 2, by + 56), (bx - 26, by + 56)]
            d.polygon(bolt, fill=(255, 214, 90, int(255 * blink)))
            lbl = "電気が流れる"
            d.text((bx + 44, by + 30), lbl, font=f_sub,
                   fill=(255, 224, 130, int(255 * blink)))

        # イオン
        for ion in ions:
            x, y = ion_pos(ion, t)
            rr = 34
            core = ION if not full else tuple(
                int(ION[j] + (HOT[j] - ION[j]) * heat * 0.5) for j in range(3))
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(*core, 255),
                      outline=(255, 255, 255, 200), width=3)
            d.text((x - 11, y - 22), "＋", font=f_ion, fill=(10, 20, 34))

        # P3: 劣化警告（高い電圧の説明カットに合わせて表示）
        if t >= WARN_T:
            warn = "高い電圧がかかり続ける = 劣化が進む"
            tw = d.textlength(warn, font=f_mid)
            a = int(255 * min(1.0, (t - WARN_T) / 0.5))
            d.text(((W - tw) / 2, BOT + 90), warn, font=f_mid,
                   fill=(255, 150, 110, a))

        img.save(tmp / f"{fi:04d}.png")

    out = Path("assets/clips/battery_anim_duo.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
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
        raise SystemExit(f"エンコード失敗: {r.stderr[-500:]}")
    print(f"生成完了: {out}")


if __name__ == "__main__":
    main()
