#!/usr/bin/env python3
"""再現ドラマ台本の型チェック（2026-10-01 のユーザー指摘をまとめて機械で拾う）。

使い方: PYTHONPATH=. python scripts/lint_drama.py <slug> [--timing]
  --timing  audio/timing.json があれば SE の間隔（30秒以内の連続）も見る

見ること（SKILL.md の決まりに対応）:
  - 字数（セリフ42字・ナレ52字）と、1文の読点は1個まで
  - 情報の言い切り（伝えられています・とされます・らしい・と言われています・そうよ）
  - 意味が二通りに取れる否定の条件文（〜なければ。／〜ないと。で終わる）と「〜はね、」
  - ずんだもんの「のだ」の割合（3割前後）
  - SE: 同じ SE は2回まで・ちゃんちゃん(oti)は2回まで・1シーン1個・bubu 禁止・合計15〜20個
  - つむぎ: 劇中（ずんだもんに名札がある場面）では役（名札）がある時だけ
  - BGM: 使用禁止の曲／現代の解説の章に暗い曲
  - 尺の見込み（1文字 0.151 秒）
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

from ytf.config import Config, Project  # noqa: E402

# 伝聞の「そう」は終止形に付く（付いてた・そうよ）。様態の「そう」（落ちそう・なりそう）は拾わない
HEDGE = re.compile(r"伝えられて|とされ(ます|てい|る)|(?<!すば)らしい|と言われて|といわれて|"
                   r"[たるいだ]そう(よ|です|だ|ね)|といいます")
AMBIG = re.compile(r"(なければ|ないと)[。、！？]?$")
BANNED_BGM = {"mystery", "ambient", "warm", "beat"}
DARK_BGM = {"kinakusai", "serious", "223am", "curious"}
SEC_PER_CHAR = 0.151


def plain(t: str) -> str:
    return re.sub(r"\[([^|\]]+)\|[^\]]+\]", r"\1", t)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cfg = Config.load()
    proj = Project.resolve(cfg, sys.argv[1])
    script = proj.load_script()
    warn: list[str] = []

    cuts = [(sc, c) for sc in script.scenes for c in sc.cuts]
    se_count: Counter = Counter()
    for sc in script.scenes:
        tags = {x.who: (getattr(x, "tag", "") or "") for x in (sc.stage or [])}
        drama = bool(tags.get("zundamon"))
        ses = [c.se for c in sc.cuts if c.se]
        if len(ses) > 1:
            warn.append(f"SE: {sc.id} に {len(ses)} 個（1シーン1個まで）: {ses}")
        if sc.bgm in BANNED_BGM:
            warn.append(f"BGM: {sc.id} の {sc.bgm} は使用禁止")
        speakers = {c.speaker for c in sc.cuts}
        if not drama and "tsumugi" in speakers and sc.bgm in DARK_BGM:
            warn.append(f"BGM: 現代の解説 {sc.id} に暗い曲 {sc.bgm}")
        if drama and "tsumugi" in speakers and not tags.get("tsumugi"):
            warn.append(f"配役: 劇中 {sc.id} で役の無いつむぎが喋っている")
        for c in sc.cuts:
            t = plain(c.text)
            narr = c.speaker == "reimu"
            lim = 52 if narr else 42
            if len(t) > lim:
                warn.append(f"字数: {sc.id} [{c.speaker}] {len(t)}字 > {lim}: {t}")
            for sent in re.split(r"[。！？!?]", t):
                if sent.count("、") > 1:
                    warn.append(f"読点: {sc.id} [{c.speaker}] 1文に{sent.count('、')}個: {t}")
                    break
            if HEDGE.search(t):
                warn.append(f"言い切り: {sc.id} [{c.speaker}] {t}")
            if AMBIG.search(t.rstrip("」")):
                warn.append(f"否定の条件文: {sc.id} [{c.speaker}] {t}")
            if "はね、" in t:
                warn.append(f"はね: {sc.id} [{c.speaker}] {t}（羽根に化ける）")
            if c.se:
                se_count[c.se] += 1
    for name, n in se_count.items():
        lim = 2
        if n > lim:
            warn.append(f"SE: {name} が {n} 回（同じ SE は2回まで）")
    if se_count.get("bubu"):
        warn.append("SE: bubu は使わない")
    total_se = sum(se_count.values())

    if "--timing" in sys.argv and proj.timing_path.exists():
        tm = json.load(open(proj.timing_path, encoding="utf-8"))
        prev = None
        for (sc, c), x in zip(cuts, tm):
            if c.se:
                if prev is not None and x["start"] - prev[0] < 30:
                    warn.append(f"SE間隔: {prev[1]} → {c.se} が {x['start'] - prev[0]:.0f} 秒（{sc.id}）")
                prev = (x["start"], c.se)

    z = [c for _, c in cuts if c.speaker == "zundamon"]
    noda = 100 * sum("のだ" in c.text for c in z) / max(1, len(z))
    chars = sum(len(plain(c.text)) for _, c in cuts)
    narr_ratio = 100 * sum(c.speaker == "reimu" for _, c in cuts) / max(1, len(cuts))
    print(f"{script.meta.slug}: {len(cuts)}カット / {chars}字（見込み {chars * SEC_PER_CHAR / 60:.1f} 分）/ "
          f"のだ {noda:.0f}% / ナレ {narr_ratio:.0f}% / SE {total_se}個 {dict(se_count)}")
    if not 24 <= noda <= 36:
        warn.append(f"のだ: {noda:.0f}%（3割前後に）")
    if not 15 <= total_se <= 22:
        warn.append(f"SE: 合計 {total_se} 個（15〜20個に）")
    for w in warn:
        print("  ⚠", w)
    print(f"指摘 {len(warn)} 件")
    return 1 if warn else 0


if __name__ == "__main__":
    raise SystemExit(main())
