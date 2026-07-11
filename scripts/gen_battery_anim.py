#!/usr/bin/env python3
"""リチウムイオン電池の仕組みアニメを生成する。

  フェーズ1 (0-CHARGE_END): 充電 — イオンが右(正極)から左(負極)へ押し込まれる
  フェーズ2 (CHARGE_END-DUR): 満充電 — 左にぎゅうぎゅう詰めで振動、プレートが熱を帯びる

尺は battery-80 の該当2カット（timing.json 実測 8.7s + 11.7s）に合わせ、
ループで巻き戻って見えないよう1秒余らせてある。台本側は video_speed 無指定（等速）。

出力: assets/clips/battery_anim.mp4（無音・台本の video: で全画面埋め込み）
実行: PYTHONPATH=. python3 scripts/gen_battery_anim.py
"""

import math
import random
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ytf.config import Config, ffmpeg_bin  # noqa: E402

from PIL import Image, ImageDraw, ImageFilter, ImageFont  # noqa: E402

W, H, FPS, DUR = 1920, 1080, 30, 21.5
CHARGE_END = 8.7          # 充電フェーズの終わり（＝1カット目の長さ）
ACCENT = (58, 160, 255)
ION = (120, 210, 255)
HOT = (255, 120, 70)
INK = (235, 242, 252)

# 電極の位置
LX0, LX1 = 180, 360        # 負極（左）
RX0, RX1 = W - 360, W - 180  # 正極（右）
TOP, BOT = 260, H - 160


def ease(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def main() -> None:
    cfg = Config.load()
    font_path = cfg.find_pillow_font()
    f_big = ImageFont.truetype(font_path, 72, index=0)
    f_mid = ImageFont.truetype(font_path, 52, index=0)
    f_ion = ImageFont.truetype(font_path, 34, index=0)

    rng = random.Random(11)
    # イオン: 充電で右側から左のスロットへ移動する
    ions = []
    cols, rows = 4, 5
    for i in range(cols * rows):
        r, c = divmod(i, cols)
        # 左電極内の最終スロット
        dst = (LX1 + 60 + c * 90, TOP + 90 + r * 130)
        # 出発位置（右側の電解液〜正極）
        src = (rng.uniform(RX0 - 500, RX0 - 40), rng.uniform(TOP + 60, BOT - 60))
        delay = rng.uniform(0.0, CHARGE_END - 3.4)
        ions.append((src, dst, delay))

    n = int(DUR * FPS)
    tmp = Path(tempfile.mkdtemp(prefix="batanim_"))

    for fi in range(n):
        t = fi / FPS
        img = Image.new("RGB", (W, H), (8, 12, 22))
        d = ImageDraw.Draw(img, "RGBA")

        # 電解液（中央の淡い帯）
        d.rounded_rectangle([LX1 + 10, TOP, RX0 - 10, BOT], radius=24,
                            fill=(20, 34, 58, 255))

        charge = min(1.0, t / CHARGE_END)          # 充電の進行度
        full = t >= CHARGE_END                      # 満充電フェーズ
        heat = ease((t - CHARGE_END) / 1.2) if full else 0.0

        # 電極（満充電で左が熱を帯びる）
        lcol = tuple(int(60 + (HOT[k] - 60) * heat * 0.55) for k in range(3))
        d.rounded_rectangle([LX0, TOP, LX1, BOT], radius=18, fill=(*lcol, 255),
                            outline=(*ACCENT, 255), width=4)
        d.rounded_rectangle([RX0, TOP, RX1, BOT], radius=18, fill=(46, 52, 66, 255),
                            outline=(150, 158, 175, 255), width=4)
        d.text((LX0 + 40, BOT + 24), "負極", font=f_mid, fill=INK)
        d.text((RX0 + 40, BOT + 24), "正極", font=f_mid, fill=INK)

        # 見出し
        if not full:
            head = "充電 = イオンを片側に押し込む"
        else:
            head = "満タン = ぎゅうぎゅう詰めのまま"
        # 左上の章見出しタブと重ならないよう、少し下げて中央に置く
        tw = d.textlength(head, font=f_big)
        d.text(((W - tw) / 2, 150), head, font=f_big,
               fill=INK if not full else (255, 190, 160))

        # 充電の矢印（フェーズ1のみ・脈動）
        if not full:
            ax = W / 2 + 80 * math.sin(t * 3)
            d.line([ax + 180, H / 2, ax - 180, H / 2], fill=(*ACCENT, 230), width=14)
            d.polygon([(ax - 240, H / 2), (ax - 180, H / 2 - 34),
                       (ax - 180, H / 2 + 34)], fill=(*ACCENT, 230))

        # イオン
        for (src, dst, delay) in ions:
            k = ease((t - delay) / 3.0)
            x = src[0] + (dst[0] - src[0]) * k
            y = src[1] + (dst[1] - src[1]) * k
            if full:  # 満員で震える
                x += rng.uniform(-1, 1) * 5 * heat
                y += rng.uniform(-1, 1) * 5 * heat
            rr = 34
            core = ION if not full else tuple(
                int(ION[j] + (HOT[j] - ION[j]) * heat * 0.5) for j in range(3))
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(*core, 255),
                      outline=(255, 255, 255, 200), width=3)
            d.text((x - 11, y - 22), "＋", font=f_ion, fill=(10, 20, 34))

        # 満充電の警告テキスト
        if full and heat > 0.5:
            warn = "高い電圧がかかり続ける = 劣化が進む"
            tw = d.textlength(warn, font=f_mid)
            a = int(255 * min(1.0, (heat - 0.5) * 2.5))
            d.text(((W - tw) / 2, BOT + 90), warn, font=f_mid,
                   fill=(255, 150, 110, a))

        img.save(tmp / f"{fi:03d}.png")

    out = Path("assets/clips/battery_anim.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error",
         "-framerate", str(FPS), "-i", str(tmp / "%03d.png"),
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
