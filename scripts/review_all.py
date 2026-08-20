#!/usr/bin/env python3
"""未アップロード動画の一括レビュー。

これまでユーザー指摘で出た失敗の型を、機械で拾えるだけ拾う。
出力は「要目視」の候補であって、確定した不具合ではない。全件を人が判定すること。

実行: PYTHONPATH=. python3 scripts/review_all.py [slug...]
"""
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROOT = Path(__file__).resolve().parent.parent
NARR = "reimu"


def vis(t: str) -> str:
    """[表示|よみ] を表示側だけにする。"""
    return re.sub(r"\[([^|\]]+)\|[^\]]+\]", r"\1", t or "")


# 動画の外を指す言い回し（1本で完結させる方針に反する）
META = ["この動画", "今回の動画", "前回の", "前回は", "の回で", "コーナー",
        "本日は", "再現ドラマでお送り", "主演"]
FURI = ["ここが今日いちばん", "ここからがすごい", "ここからが面白い", "一番面白いところ",
        "必見", "刮目"]
# 説明文で伏せるべき語（オチ・死・到達点）
SPOIL = ["亡くなり", "死去", "遺志", "最期", "永眠", "他界"]
# 相手の発言に反応する型のミーム。自分の直前発言に使うと破綻する
REACT = ["それな", "その発想はなかった", "完全に一致", "情報量が多"]


def review(slug: str) -> list:
    from ytf.config import Config, find_project_dir
    root = find_project_dir(Config.load().root, slug)
    y = yaml.safe_load((root / "script.yaml").read_text())
    meta = y.get("meta") or {}
    cuts = [(s["id"], c) for s in y["scenes"] for c in s["cuts"]]
    out = []

    # ① 吹き出し・ナレ帯の字数（ドラマのみ。解説は吹き出しを使わないので対象外）
    if meta.get("mode") == "drama":
        for i, (sid, c) in enumerate(cuts):
            t = vis(c.get("text") or "")
            lim = 52 if c.get("speaker") == NARR else 42
            if len(t) > lim:
                out.append(("字数超過", f"{sid}/cut{i} {len(t)}字(上限{lim}): {t[:44]}"))

    # ② 舞台にいないキャラの発話
    for s in y["scenes"]:
        on = {m["who"] for m in (s.get("stage") or [])} | {NARR}
        if not s.get("stage"):
            continue
        for j, c in enumerate(s["cuts"]):
            if c.get("speaker") not in on:
                out.append(("舞台に不在", f"{s['id']}/cut{j} [{c.get('speaker')}]"))

    # ③ 同じ言い回しが近くで繰り返される
    seen = {}
    for i, (sid, c) in enumerate(cuts):
        t = vis(c.get("text") or "")
        for n in (10, 9, 8):
            for k in range(len(t) - n + 1):
                frag = t[k:k + n]
                if not re.search(r"[一-龥ァ-ヶ]", frag):
                    continue
                if frag in seen and 0 < i - seen[frag][0] <= 3:
                    out.append(("近接重複",
                                f"cut{seen[frag][0]}とcut{i}（{i-seen[frag][0]}カット差）"
                                f"「{frag}」"))
                seen[frag] = (i, sid)
            break

    # ④ メタ発言・前振り・過去回参照
    for i, (sid, c) in enumerate(cuts):
        t = vis(c.get("text") or "")
        for w in META:
            if w in t:
                out.append(("メタ発言", f"{sid}/cut{i}「{w}」: {t[:40]}"))
        for w in FURI:
            if w in t:
                out.append(("前振り", f"{sid}/cut{i}「{w}」: {t[:40]}"))

    # ⑤ 反応型ミームを自分の直前発言に使っていないか
    for i, (sid, c) in enumerate(cuts):
        t = vis(c.get("text") or "")
        for w in REACT:
            if w in t and i > 0 and cuts[i - 1][1].get("speaker") == c.get("speaker"):
                out.append(("自分の発言に反応",
                            f"{sid}/cut{i}「{w}」前も同じ話者: {t[:40]}"))

    # ⑥ 説明文のネタバレ
    summ = meta.get("summary") or ""
    for w in SPOIL:
        if w in summ:
            out.append(("説明文でネタバレ", f"「{w}」: {summ[:50]}"))
    if len(summ) > 210:
        out.append(("説明文が長い", f"{len(summ)}字（150〜200字が目安）"))

    # ⑦ 尺の一致
    v, a = root / "out" / "video.mp4", root / "audio" / "narration.wav"
    if v.exists() and a.exists():
        import subprocess
        fp = str(ROOT / "tools" / "ffprobe")

        def dur(p):
            r = subprocess.run([fp, "-v", "error", "-show_entries", "format=duration",
                                "-of", "csv=p=0", str(p)], capture_output=True, text=True)
            return float(r.stdout.strip() or 0)
        if abs(dur(v) - dur(a)) > 2:
            out.append(("尺が不一致", f"video {dur(v)/60:.1f}分 / audio {dur(a)/60:.1f}分"))

    return out


def main():
    from ytf.config import Config
    cfg = Config.load()
    slugs = sys.argv[1:]
    if not slugs:
        slugs = []
        for sp in sorted((cfg.root / "projects" / "未アップロード").rglob("script.yaml")):
            s = (yaml.safe_load(sp.read_text()).get("meta") or {}).get("slug")
            if s:
                slugs.append(s)
    total = 0
    for slug in slugs:
        issues = review(slug)
        total += len(issues)
        mark = "○" if not issues else f"{len(issues)}件"
        print(f"■ {slug:20} {mark}")
        for kind, msg in issues:
            print(f"    [{kind}] {msg}")
    print(f"\n要目視 合計 {total} 件")


if __name__ == "__main__":
    main()
