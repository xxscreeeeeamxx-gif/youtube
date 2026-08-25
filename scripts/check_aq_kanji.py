#!/usr/bin/env python3
"""ゆっくりナレの漢字語を、実音で読み確認する（AquesTalkの盲点をふさぐ）。

■ なぜ必要か
AquesTalk は text をそのまま読むが moras を返さないため、VOICEVOX 側で使っている
モーラ照合が使えない。代わりに使っていた whisper 照合には穴があって、
whisper は言語モデルを持つので、たとえば「きんがた」と発音されても
文脈から「金型」と書き起こしてしまい、誤読が一致率に出てこない。
（2026-08-25 にユーザー指摘。「金型」がナレで誤読されていたのを検査が素通りした）

■ やり方
同じ文を「漢字のまま」と「想定した読みのかなに置換」の2通りで単体合成し、
波形を突き合わせる。読みが一致していれば2つはほぼ同じ音になり、
違っていればはっきり差が出る。聴かずに機械で判定できる。

実行:
  PYTHONPATH=. python3 scripts/check_aq_kanji.py <slug>            # 台帳の語を全部
  PYTHONPATH=. python3 scripts/check_aq_kanji.py <slug> 金型 鋼    # 語を指定
"""

import re
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402
import yaml  # noqa: E402

from ytf.config import Config, find_project_dir  # noqa: E402
from ytf.voice import aquestalk_synthe  # noqa: E402

TAG = re.compile(r"\[([^|\]]+)\|([^\]]+)\]")


def disp(t: str) -> str:
    """画面に出る表示テキスト（タグを表示側に開く）。"""
    return TAG.sub(lambda m: m.group(1), t)


def spoken_of(t: str) -> str:
    """実際に AquesTalk へ渡る文（タグを読み側に開く）。"""
    return TAG.sub(lambda m: m.group(2), t)
# 両エンジンが同じ誤読をしがちで、モーラ照合では捕まらない語。
# 見つけるたびにここへ足す（漢字, 正しい読み）
SUSPECT = [
    # 読みが一つに決まる語だけを置く。ここに入れた語は差が出たら誤読と断じてよい
    ("金型", "かながた"), ("鋼", "はがね"), ("深絞り", "ふかしぼり"),
    ("生糸", "きいと"), ("行方", "ゆくえ"), ("木綿", "もめん"),
    ("為替", "かわせ"), ]
# 文脈で読みが変わる語。自動で白黒は付けられないので、出てきたら人が判断する。
# 例: 市場=いちば/しじょう、上手=じょうず/うわて、三重=みえ/さんじゅう
AMBIGUOUS = ["市場", "上手", "下手", "大手", "三重", "十分", "一寸",
             "水面", "風車", "問屋"]


def _wav(data: bytes) -> np.ndarray:
    import io
    with wave.open(io.BytesIO(data)) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return a.astype(np.float32) / 32768.0


def _env(a: np.ndarray, n: int = 400) -> np.ndarray:
    """粗い振幅包絡。長さをそろえて比較できるようにする。"""
    if len(a) < n:
        a = np.pad(a, (0, n - len(a)))
    e = np.abs(a)
    idx = np.linspace(0, len(e), n + 1).astype(int)
    v = np.array([e[idx[i]:idx[i + 1]].mean() if idx[i + 1] > idx[i] else 0.0
                  for i in range(n)])
    return v / (v.max() + 1e-9)


def compare(cfg, kanji_line: str, kana_line: str, preset: str, speed: float):
    a = _wav(aquestalk_synthe(cfg, kanji_line, preset, speed))
    b = _wav(aquestalk_synthe(cfg, kana_line, preset, speed))
    dur_a, dur_b = len(a) / 24000, len(b) / 24000
    d = float(np.abs(_env(a) - _env(b)).mean())
    return d, dur_a, dur_b


def main(slug: str, words: list[str]) -> int:
    cfg = Config.load()
    proj = find_project_dir(cfg.root, slug)
    script = yaml.safe_load((proj / "script.yaml").read_text(encoding="utf-8"))
    narrator = script["meta"].get("narrator") or "reimu"
    ch = cfg.character(narrator) or {}
    preset = ch.get("aquestalk_preset", "れいむ")
    speed = float(ch.get("speed_scale", 1.3))

    pairs = [(k, y) for k, y in SUSPECT if not words or k in words]
    if words:
        known = {k for k, _ in SUSPECT}
        for w in words:
            if w not in known:
                print(f"（{w} は SUSPECT に未登録。読みを足してから実行してください）")

    narr = [c for s in script["scenes"] for c in s["cuts"]
            if c["speaker"] == narrator]
    problems = []
    for kanji, yomi in pairs:
        # 表示ではなく「実際に合成へ渡される文」を見る。voice.py は AquesTalk へ
        # split_reading の spoken 側（[表示|よみ]をよみに置換した文）を渡す
        hits = [c for c in narr if kanji in disp(c["text"])]
        if not hits:
            continue
        for c in hits:
            line = spoken_of(c["text"])          # 実際に喋る文
            kana_line = disp(c["text"]).replace(kanji, yomi)   # 期待する読み
            d, da, db = compare(cfg, line, kana_line, preset, speed)
            ok = d < 0.055
            mark = "OK " if ok else "‼ "
            print(f"{mark}「{kanji}」→ 期待 {yomi} / 差 {d:.4f} "
                  f"（漢字 {da:.2f}s / かな {db:.2f}s）")
            print(f"    {line[:46]}")
            if not ok:
                problems.append((kanji, yomi, line))
    narr_text = " ".join(disp(c["text"]) for c in narr)
    amb = [w for w in AMBIGUOUS if w in narr_text]
    if amb:
        print(f"（要人手判定: {' '.join(amb)} が出てきます。"
              f"文脈で読みが変わるので、実音を聴いて判断すること）")
    if not pairs:
        print("この台本のナレに、読みが一つに決まる要注意語は出てきません")
    print()
    if problems:
        print(f"‼ 誤読の疑い {len(problems)} 件。読みタグではなく言い換えで直すこと")
        for k, y, ln in problems:
            print(f"  - 「{k}」（正: {y}）: {ln[:44]}")
        return 1
    print("OK: ナレの要注意語はすべて想定どおりの音でした")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("使い方: check_aq_kanji.py <slug> [語 ...]")
    sys.exit(main(sys.argv[1], sys.argv[2:]))
