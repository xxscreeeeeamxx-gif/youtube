#!/usr/bin/env python3
"""ゆっくりナレ（AquesTalk1）に実際に渡る音声記号列を全行出して目視させる。

■ なぜ実音比較（check_aq_kanji.py）ではなくこれなのか
旧 AquesTalkPlayer は漢字かな交じり文を内部で形態素解析していたので、
どう読まれるかは合成してみないと分からなかった。だから「漢字版」と「想定した
かな版」を単体合成して波形を比べる、という回りくどい検査が要った。

AquesTalk1 はカタカナしか受け付けないので、**読みを決めているのは ytf/aq1.py**。
つまり合成前に確定していて、そのまま読める。漢字版とかな版を比べても、
どちらも同じ aq1.to_koe() を通るので必ず一致し、検査として意味を成さない。

そこで実音比較はやめて、変換結果そのものを全行並べる。誤読があれば
カタカナの時点で目に見える（「金型」がカナガタと出ていれば正しいと分かる）。

■ 何を ‼ で止めるか
`reading:` の無いナレ行のうち、漢字を含むもの。読みが pykakasi 任せになっていて
誰も確認していない状態を指す。SKILL.md の「ナレーターは全行 reading: でひらがな必須」
を機械で担保する。

実行:
  PYTHONPATH=. python scripts/check_aq1_koe.py <slug>
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml  # noqa: E402

from ytf import aq1  # noqa: E402
from ytf.config import Config, find_project_dir  # noqa: E402
from ytf.schema import split_reading  # noqa: E402

KANJI = re.compile(r"[一-鿿]")


def main(slug: str) -> int:
    cfg = Config.load()
    root = find_project_dir(cfg.root, slug)
    if root is None:
        print(f"‼ プロジェクトが見つかりません: {slug}")
        return 1
    script = yaml.safe_load((root / "script.yaml").read_text(encoding="utf-8"))
    meta = script.get("meta") or {}
    narrator = meta.get("narrator") or "reimu"
    ch = cfg.character(narrator) or {}
    if ch.get("engine") != "aquestalk1":
        print(f"ナレの音声記号列: engine が aquestalk1 ではないのでスキップ"
              f"（{narrator}={ch.get('engine')}）")
        return 0

    class _P:
        pass
    p = _P()
    p.root = root
    ledger = aq1.load_ledger(cfg, p)

    cuts = [c for sc in (script.get("scenes") or [])
            for c in (sc.get("cuts") or []) if c.get("speaker") == narrator]
    if not cuts:
        print("ナレの音声記号列: ナレーション行がありません")
        return 0

    missing = []
    print(f"ナレの音声記号列: {len(cuts)}行（声={ch.get('aquestalk1_voice', aq1.DEFAULT_VOICE)}）")
    for i, c in enumerate(cuts, 1):
        text = c.get("text") or ""
        reading = c.get("reading")
        spoken = reading if reading else split_reading(text)[1]
        koe = aq1.to_koe(spoken, ledger)
        src = "reading" if reading else "text"
        print(f"  {i:3d} [{src}] {text[:34]}")
        print(f"      → {koe}")
        if not reading and KANJI.search(text):
            missing.append((i, text))

    if missing:
        print(f"‼ reading: の無い漢字入りナレ行が {len(missing)} 件。"
              f"読みが pykakasi 任せで未確認です")
        for i, t in missing[:10]:
            print(f"   {i:3d} {t[:40]}")
        return 1
    print("  （全行に reading: あり）")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python scripts/check_aq1_koe.py <slug>")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
