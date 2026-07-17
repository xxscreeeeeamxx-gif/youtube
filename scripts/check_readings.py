#!/usr/bin/env python3
"""固有名詞の読み間違いを機械的に検出する（読み台帳ベース）。

使い方:
  PYTHONPATH=. python3 scripts/check_readings.py <slug>

仕組み:
  projects/<slug>/readings.yaml に「この動画に出る固有名詞と正しい読み」を列挙しておく。
  本スクリプトは2段階で検査する:

  1) 静的検査（台本だけで可能）
     - 台帳の surface が台本のセリフに現れたら、
       ・ナレーター（AquesTalk。辞書が効かない）→ [表示|よみ] タグ必須
       ・VOICEVOX話者 → タグ or dictionary.yaml のエントリが必須
  2) 音声後検査（timing.json があれば）
     - VOICEVOXカットは moras に台帳の読み（カタカナ）が含まれるか実測で確認

  ※台帳に無い固有名詞は検出できない。台本を書いたら人名・地名・社名・専門語を
    必ず台帳に足すこと（SKILL.mdの手順に組み込み済み）。

readings.yaml の形式:
  - {surface: 仁子, reading: まさこ}
  - {surface: 東洋莫大小, reading: とうようめりやす}
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml  # noqa: E402

from ytf.config import Config, Project  # noqa: E402
from ytf.schema import READING_RE  # noqa: E402

KATA = str.maketrans(
    "ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとど"
    "なにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔ",
    "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトド"
    "ナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴ",
)


O_COL = set("オコソトノホモヨロヲゴゾドボポォョウ")
E_COL = set("エケセテネヘメレゲゼデベペェ")


def to_kata(s: str) -> str:
    return unicodedata.normalize("NFKC", s).translate(KATA)


def canon(s: str) -> str:
    """長音の表記ゆれを吸収（トウヨウ↔トオヨオ、セイ↔セエ）。

    VOICEVOXのmorasは長音を発音どおり（オ段+オ、エ段+エ）で返すため、
    仮名書きの読みと比較する前に両方をこの形へ寄せる。
    """
    out = []
    for ch in to_kata(s):
        if ch == "ウ" and out and out[-1] in O_COL:
            ch = "オ"
        elif ch == "イ" and out and out[-1] in E_COL:
            ch = "エ"
        out.append(ch)
    return "".join(out)


def main(slug: str) -> int:
    cfg = Config.load()
    proj = Project.resolve(cfg, slug)
    ledger_path = proj.root / "readings.yaml"
    if not ledger_path.exists():
        print(f"NG: 読み台帳がありません: {ledger_path}")
        print("    人名・地名・社名・専門語を {surface, reading} で列挙してください")
        return 1
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8")) or []
    common = cfg.root / "assets" / "readings_common.yaml"
    if common.exists():
        ledger += yaml.safe_load(common.read_text(encoding="utf-8")) or []
    ledger = [e for e in ledger if e.get("surface") and e.get("reading")]
    script = proj.load_script()
    narrator = getattr(script.meta, "narrator", "")

    # dictionary.yaml（VOICEVOXのユーザー辞書）に載っている表記
    dict_surfaces = set()
    dict_path = cfg.root / "dictionary.yaml"
    if dict_path.exists():
        for e in yaml.safe_load(dict_path.read_text(encoding="utf-8")) or []:
            if isinstance(e, dict) and e.get("surface"):
                dict_surfaces.add(unicodedata.normalize("NFKC", e["surface"]))

    def speaker_engine(sp: str) -> str:
        try:
            return cfg.character(sp).get("engine", "voicevox")
        except SystemExit:
            return "voicevox"  # モブは register_mobs 前なので voicevox 扱い

    problems = []

    # ---- 1) 静的検査 ----
    for scene in script.scenes:
        for cut in scene.cuts:
            text = cut.text
            spoken_src = cut.reading if cut.reading else text
            # ナレーター(AquesTalk)は漢字変換の誤読を構造的に防ぐため全行ひらがな必須
            if speaker_engine(cut.speaker) == "aquestalk" and not cut.reading:
                problems.append(
                    f"reading必須(ナレーターは全行ひらがな指定): "
                    f"{scene.id}: {text[:30]}")
                continue
            for e in ledger:
                surf = e["surface"]
                if surf not in re.sub(READING_RE, lambda m: "", text) and surf not in text:
                    continue
                # タグ済みの出現を除いた「裸の表記」を数える
                naked = READING_RE.sub(lambda m: "\x00" * len(m.group(0)), spoken_src)
                if surf not in naked:
                    continue  # 全出現がタグ済み or reading: で上書き済み
                eng = speaker_engine(cut.speaker)
                if eng == "aquestalk":
                    problems.append(
                        f"タグ必須(ナレーター): 「{surf}」 in "
                        f"{scene.id}/{cut.speaker}: {text[:28]}")
                elif unicodedata.normalize("NFKC", surf) not in dict_surfaces:
                    problems.append(
                        f"タグか辞書が必要: 「{surf}」 in "
                        f"{scene.id}/{cut.speaker}: {text[:28]}")

    # ---- 2) 音声後検査（moras 実測） ----
    timing_path = proj.timing_path
    if timing_path.exists():
        timings = json.loads(timing_path.read_text(encoding="utf-8"))
        cuts_flat = [c for sc in script.scenes for c in sc.cuts]
        for ct, cut in zip(timings, cuts_flat):
            if not ct.get("moras"):
                continue
            kana = canon("".join(m[0] for m in ct["moras"]))
            disp = ct["display_text"]
            for e in ledger:
                if e["surface"] not in disp:
                    continue
                expect = canon(e["reading"])
                if expect not in kana:
                    problems.append(
                        f"実測不一致: 「{e['surface']}」読み「{e['reading']}」が "
                        f"moras に無い idx{ct['index']}: {disp[:24]} → {kana[:40]}")
    else:
        print("(timing.json 未生成のため実測検査はスキップ。voice 後に再実行)")

    # ---- 3) 多読み漢字の警告（自動列挙→制作者がモーラを通読して確認する） ----
    ambiguous = ["金", "空", "方", "日", "年", "何", "声", "札", "人", "話",
                 "同じ", "辛", "上手", "下手", "人気", "一行", "一見"]
    if timing_path.exists():
        warned = 0
        for ct, cut in zip(timings, cuts_flat):
            disp = ct["display_text"]
            hits = []
            for w in ambiguous:
                if len(w) == 1:
                    if re.search(rf"(?<![一-龥]){w}(?![一-龥])", disp):
                        hits.append(w)
                elif w in disp:
                    hits.append(w)
            if hits:
                kana = (canon("".join(m[0] for m in ct["moras"]))
                        if ct.get("moras") else "(ナレーター: whisperで確認)")
                print(f"要通読 idx{ct['index']} [{'/'.join(hits)}] "
                      f"{disp[:26]} → {kana[:44]}")
                warned += 1
        if warned:
            print(f"↑ 多読み漢字 {warned} 件。読みが正しいか上のカナを通読して確認すること")

    if problems:
        print(f"NG: {len(problems)} 件")
        for p in problems:
            print(" -", p)
        return 1
    print(f"OK: 台帳 {len(ledger)} 語 × 全カットで問題なし")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: check_readings.py <slug>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
