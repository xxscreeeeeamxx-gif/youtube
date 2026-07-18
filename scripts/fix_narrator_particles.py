#!/usr/bin/env python3
"""ナレーター(AquesTalk)の reading: 内の助詞 は/へ を わ/え に機械修正する。

AquesTalkはひらがなを字面どおり読むため、助詞の「は」「へ」はそのままだと
ハ・ヘ と発音される。表示テキストをVOICEVOXの形態素解析にかけ、ワ/エ になる
位置に対応する reading の は/へ を わ/え へ置換して script.yaml を書き換える。

使い方: PYTHONPATH=. python3 scripts/fix_narrator_particles.py <slug>
"""

import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

from scripts.check_readings import canon, to_kata  # noqa: E402
from ytf.config import Config, Project  # noqa: E402
from ytf.schema import READING_RE  # noqa: E402
from ytf.voice import ensure_engine  # noqa: E402


def norm_char(ch: str, prev: str) -> str:
    """canon相当の1文字正規化（ー展開・ヲ→オ・ヅ→ズ・ヂ→ジ）。"""
    if ch == "ヲ":
        return "オ"
    if ch == "ヅ":
        return "ズ"
    if ch == "ヂ":
        return "ジ"
    if ch == "ー" and prev:
        for group, v in (
            ("オコソトノホモヨロヲゴゾドボポォョウ", "オ"),
            ("エケセテネヘメレゲゼデベペェ", "エ"),
            ("アカサタナハマヤラワガザダバパァャヮ", "ア"),
            ("イキシチニヒミリギジヂビピィ", "イ"),
            ("ウクスツヌフムユルグズヅブプゥュヴ", "ウ"),
        ):
            if prev in group:
                return v
    return ch


def normalize(kana: str) -> str:
    kana = canon(kana)
    out = []
    for ch in kana:
        out.append(norm_char(ch, out[-1] if out else ""))
    return "".join(out)


def main(slug: str) -> int:
    cfg = Config.load()
    proj = Project.resolve(cfg, slug)
    script = proj.load_script()
    client = ensure_engine(cfg)
    path = proj.root / "script.yaml"
    src = path.read_text(encoding="utf-8")
    total = 0

    for sc in script.scenes:
        for cut in sc.cuts:
            try:
                if cfg.character(cut.speaker).get("engine") != "aquestalk":
                    continue
            except SystemExit:
                continue
            if not cut.reading:
                continue
            disp = READING_RE.sub(lambda m: m.group(2), cut.text)
            q = requests.post(f"{client.base}/audio_query",
                              params={"text": disp, "speaker": 13}, timeout=30)
            q.raise_for_status()
            vv = normalize("".join(m.get("text", "")
                                   for ph in q.json()["accent_phrases"]
                                   for m in ph.get("moras", [])))
            # reading のかな位置（元文字列インデックス）を保持して正規化
            kata = to_kata(cut.reading)
            kana_chars, pos = [], []
            for i, ch in enumerate(kata):
                if "ァ" <= ch <= "ヶ" or ch == "ー":
                    kana_chars.append(ch)
                    pos.append(i)
            rd = normalize("".join(kana_chars))
            fixes = []  # 元reading内インデックス → 新文字
            for op, a0, a1, b0, b1 in difflib.SequenceMatcher(
                    None, rd, vv).get_opcodes():
                if op != "replace" or (a1 - a0) != (b1 - b0):
                    continue
                for k in range(a1 - a0):
                    r_ch, v_ch = rd[a0 + k], vv[b0 + k]
                    orig_i = pos[a0 + k]
                    orig_ch = cut.reading[orig_i]
                    if r_ch == "ハ" and v_ch == "ワ" and orig_ch == "は":
                        fixes.append((orig_i, "わ"))
                    elif r_ch == "ヘ" and v_ch == "エ" and orig_ch == "へ":
                        fixes.append((orig_i, "え"))
            if not fixes:
                continue
            new_reading = list(cut.reading)
            for i, ch in fixes:
                new_reading[i] = ch
            new_reading = "".join(new_reading)
            old_line = f'reading: "{cut.reading}"'
            new_line = f'reading: "{new_reading}"'
            if src.count(old_line) < 1:
                print(f"  !! 行が見つからない: {sc.id}: {cut.reading[:24]}")
                continue
            src = src.replace(old_line, new_line, 1)
            total += len(fixes)
            print(f"  {sc.id}: {len(fixes)}箇所 {cut.text[:22]}")

    path.write_text(src, encoding="utf-8")
    print(f"修正合計 {total} 箇所 -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
