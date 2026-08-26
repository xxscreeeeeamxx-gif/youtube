#!/usr/bin/env python3
"""系統の違う3つの辞書に読ませ、割れた「語」だけを自動で拾う。

■ なぜ必要か
これまでの検査は「怪しいと思った語」を人が挙げる方式だったので、
思いつかなかった語は永久に取りこぼした（ユーザー指摘 2026-08-26）。
語を指定せずに、**辞書どうしを戦わせて割れた場所だけを拾う**方式に変える。

■ なぜ3つなのか
誤読は辞書の系統ごとに出る。VOICEVOX(OpenJTalk) は IPAdic 系なので、
同じ系統の辞書とだけ比べても同じ間違いをして一致してしまう。系統を散らす:

  - janome    … IPAdic 系（VOICEVOX と同じ系統。VOICEVOX の癖を代弁する）
  - pykakasi  … KAKASI 系（独自の漢和辞書）
  - SudachiPy … UniDic/Sudachi 系

3つが割れた語は、読みが一意でない場所。そこだけを人が見ればよい。
語を一つも指定せずに 金型・他の・破れる・細ければ・詰んで・その方・深絞り を検出できた。

■ 残る穴
辞書が3つとも同じ間違いをする語。ほぼネットミーム語に限られる
（「メンタル鋼」は3辞書とも コウ。正しくは はがね）。ミームは
meme-repertoire.md という有限の一覧があるので、漢字を含むミーム語は
assets/readings_common.yaml に登録して潰す。

実行:
  PYTHONPATH=. python3 scripts/check_readings_vote.py <slug>
  PYTHONPATH=. python3 scripts/check_readings_vote.py --all
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import jaconv  # noqa: E402
import yaml  # noqa: E402

TAG = re.compile(r"\[([^|\]]+)\|([^\]]+)\]")
KANJI = re.compile(r"[一-鿿々]")
JOIN = re.compile(r"[一-鿿々0-9０-９]")   # これに挟まれた語は複合語の一部
KANA_ONLY = re.compile(r"[^ァ-ヶー]")
# 1モーラの語は連濁・音便のノイズが多く、実読に埋もれた別語とも当たる。
# 2モーラ以上に絞ると偽陽性が実用域まで落ちる（八木・荷馬車は2モーラ以上）
MIN_MORA = 2
O_COL = set("オコソトノホモヨロヲゴゾドボポョ")
E_COL = set("エケセテネヘメレゲゼデベペ")
VOICED = str.maketrans("ガギグゲゴザジズゼゾダヂヅデドバビブベボ",
                       "カキクケコサシスセソタチツテトハヒフヘホ")
# canon() は長音のゆれを吸収するために「オ段+ウ」を「オ段+オ」に寄せる。
# その副作用で、文の中に置かれた語は語頭の ウ/イ が変わってしまう
# （「の受け売り」→ ノオケウリ。単独の ウケウリ と字面が合わなくなる）。
# 語が文中にあるか調べるときだけ、ウ/オ・イ/エ を同一視して照合する
LOOSE = str.maketrans("ウイ", "オエ")

_sud = _jt = _kks = _mode = None


def _engines():
    global _sud, _jt, _kks, _mode
    if _sud is None:
        from sudachipy import dictionary, tokenizer
        from janome.tokenizer import Tokenizer as JT
        import pykakasi
        _sud = dictionary.Dictionary(dict="core").create()
        _mode = tokenizer.Tokenizer.SplitMode.C
        _jt = JT()
        _kks = pykakasi.kakasi()


def canon(s: str) -> str:
    """長音・四つ仮名のゆれを吸収し、カナ以外を落とす。"""
    out = []
    for ch in jaconv.hira2kata(s).replace("ヅ", "ズ").replace("ヂ", "ジ"):
        if ch == "ウ" and out and out[-1] in O_COL:
            ch = "オ"
        elif ch == "イ" and out and out[-1] in E_COL:
            ch = "エ"
        out.append(ch)
    return KANA_ONLY.sub("", "".join(out))


def words_janome(t):
    _engines()
    return [(tok.surface, tok.reading) for tok in _jt.tokenize(t)
            if tok.reading and tok.reading != "*"]


def words_sudachi(t):
    _engines()
    return [(m.surface(), m.reading_form()) for m in _sud.tokenize(t, _mode)
            if m.reading_form()]


def words_kakasi(t):
    _engines()
    return [(r["orig"], r["kana"]) for r in _kks.convert(t) if r.get("kana")]


def spoken_of(t):
    return TAG.sub(lambda m: m.group(2), t)


def disp_of(t):
    return TAG.sub(lambda m: m.group(1), t)


def word_votes(text: str):
    """漢字を含む語ごとに、3系統の読みを集める。表層が一致する語だけ比べる。

    返り値は (割れた語, 全会一致の語)。全会一致も返すのは、辞書どうしの
    不一致だけを見ていると **辞書が3つとも正しくて VOICEVOX だけが間違えた語**
    を取りこぼすため（八木=ハチボク・荷馬車=ニウマシャ・通って=カヨッテ の実例。
    2026-08-26、光ファイバー回で3件が多数決検査をすり抜けた）。
    """
    maps = {}
    for name, fn in (("IPAdic", words_janome), ("KAKASI", words_kakasi),
                     ("Sudachi", words_sudachi)):
        d = defaultdict(set)
        for surf, yomi in fn(text):
            if KANJI.search(surf):
                d[surf].add(canon(yomi))
        maps[name] = d
    common = set(maps["IPAdic"]) & set(maps["KAKASI"]) & set(maps["Sudachi"])
    split, agreed = {}, {}
    for surf in common:
        votes = {n: sorted(maps[n][surf]) for n in maps}
        flat = [v[0] for v in votes.values() if v]
        if len(set(flat)) > 1:
            split[surf] = votes
        elif flat and len(set().union(*(set(v) for v in votes.values()))) == 1:
            # 3辞書が1つの読みしか出さなかった語。ここが割れないということは
            # 読みが一意なので、実読がそれと違えば誤読と断じてよい
            agreed[surf] = flat[0]
    return split, agreed


def _standalone(text: str, surf: str) -> bool:
    """その語が、前後を漢字・数字に挟まれていない位置に現れるか。"""
    for m in re.finditer(re.escape(surf), text):
        before = text[m.start() - 1] if m.start() else ""
        after = text[m.end()] if m.end() < len(text) else ""
        if not JOIN.match(before or " ") and not JOIN.match(after or " "):
            return True
    return False


def check(slug: str) -> list:
    from ytf.config import Config, find_project_dir
    cfg = Config.load()
    proj = find_project_dir(cfg.root, slug)
    if proj is None:
        raise SystemExit(f"プロジェクトが見つかりません: {slug}")
    script = yaml.safe_load((proj / "script.yaml").read_text(encoding="utf-8"))
    tp = proj / "audio" / "timing.json"
    timings = json.loads(tp.read_text(encoding="utf-8")) if tp.exists() else []
    narrator = script["meta"].get("narrator") or ""
    cuts = [c for s in script["scenes"] for c in s["cuts"]]

    found = []
    for i, cut in enumerate(cuts):
        text = spoken_of(cut["text"])
        if not KANJI.search(text):
            continue
        split, agreed = word_votes(text)
        is_narr = cut["speaker"] == narrator
        # 複合語の断片を飛ばすのは **ナレだけ**。ナレは「その語をかなに置換した文」を
        # 合成して聴き比べるので、「2005年7月」から「月」だけ抜くと置換文が別物になり
        # 比較にならない。セリフは実読カナと突き合わせるだけなので、複合語の中にあっても
        # 判定できる。ここを一律に除外していたため「八木先生」の八木＝ハチボクを
        # 取りこぼした（2026-08-26）
        if is_narr:
            split = {w: v for w, v in split.items() if _standalone(text, w)}
            agreed = {w: y for w, y in agreed.items() if _standalone(text, w)}
        actual = None
        if not is_narr and i < len(timings) and timings[i].get("moras"):
            actual = canon("".join(m[0] for m in timings[i]["moras"]))

        def present(y, act=None):
            act = actual if act is None else act
            for tr in (LOOSE, None):
                a, b = (act.translate(tr), y.translate(tr)) if tr else (act, y)
                if b in a or b.translate(VOICED) in a.translate(VOICED):
                    return True
            return False

        # ① 3辞書が全会一致なのに VOICEVOX がそう読んでいない語
        if actual is not None:
            for surf, yomi in sorted(agreed.items()):
                if len(yomi) < MIN_MORA or present(yomi):
                    continue
                found.append({"idx": i, "speaker": cut["speaker"], "narr": False,
                              "text": disp_of(cut["text"]), "surf": surf,
                              "votes": {"3辞書とも": [yomi]}, "actual": actual,
                              "verdict": f"‼ 3辞書とも {yomi} なのに実読に無い"})
        # ② 辞書どうしが割れた語
        for surf, votes in split.items():
            cand = [v[0] for v in votes.values() if v]
            major = max(set(cand), key=cand.count)
            n_major = cand.count(major)
            verdict = None
            if actual is not None:
                # 実読の中にどの候補が含まれるか。連濁で頭が濁ることがあるので許す
                hits = [y for y in set(cand) if present(y)]
                if len(hits) == 1 and hits[0] == major and n_major >= 2:
                    continue                     # 多数派どおりに読めている
                verdict = ("実読が少数派の読み" if hits and hits[0] != major
                           else "実読がどの候補とも合わない" if not hits
                           else "辞書が割れている")
            else:
                verdict = "ナレ・辞書が割れている"
            found.append({"idx": i, "speaker": cut["speaker"], "narr": is_narr,
                          "text": disp_of(cut["text"]), "surf": surf,
                          "votes": votes, "actual": actual, "verdict": verdict})
    return found


def verify_narration(cfg, script, hits: list) -> None:
    """ナレの割れた語を、多数決の読みを仮説にして実音で判定する。

    同じ文を「そのまま」と「その語だけ多数派の読みに置換」で単体合成し、
    振幅包絡を比べる。合っていれば差はほぼ 0、違えば大きく開く。
    仮説を人が用意する必要がないのがこの方式の要点。
    """
    import numpy as np
    from ytf.voice import aquestalk_synthe
    narr_cuts = [c for s_ in script["scenes"] for c in s_["cuts"]]
    ch = cfg.character(script["meta"].get("narrator") or "reimu") or {}
    preset = ch.get("aquestalk_preset", "れいむ")
    speed = float(ch.get("speed_scale", 1.3))

    def env(a, n=400):
        e = np.abs(a)
        if len(e) < n:
            e = np.pad(e, (0, n - len(e)))
        idx = np.linspace(0, len(e), n + 1).astype(int)
        v = np.array([e[idx[i]:idx[i+1]].mean() if idx[i+1] > idx[i] else 0.0
                      for i in range(n)])
        return v / (v.max() + 1e-9)

    def wav(b):
        import io as _io, wave
        with wave.open(_io.BytesIO(b)) as w:
            return np.frombuffer(w.readframes(w.getnframes()),
                                 dtype=np.int16).astype(np.float32) / 32768.0

    cache = {}

    def synth(t):
        if t not in cache:
            cache[t] = env(wav(aquestalk_synthe(cfg, t, preset, speed)))
        return cache[t]

    for h in hits:
        if not h["narr"]:
            continue
        line = spoken_of(narr_cuts[h["idx"]]["text"])
        cand = sorted(set(v[0] for v in h["votes"].values() if v))
        # 候補ごとに「その読みに置換した文」を作り、実音がどれに近いかで決める。
        # 多数派とだけ比べると、かな置換そのものが解析を乱した分（交絡）を
        # 誤読と取り違える。全候補を同じ条件で置換すれば、その分は打ち消える
        try:
            base = synth(line)
            dists = {y: float(np.abs(base - synth(
                line.replace(h["surf"], jaconv.kata2hira(y), 1))).mean())
                for y in cand}
        except Exception as e:
            h["audio"] = f"（合成できず: {e}）"
            continue
        best = min(dists, key=dists.get)
        detail = " / ".join(f"{y}:{d:.3f}" for y, d in sorted(dists.items(),
                                                             key=lambda kv: kv[1]))
        cand_counts = [v[0] for v in h["votes"].values() if v]
        major = max(set(cand_counts), key=cand_counts.count)
        h["audio"] = (f"実音は {best} に最も近い（{detail}）"
                      + ("" if best == major else "  ‼ 多数派と違う"))


def report(slug: str) -> int:
    hits = check(slug)
    if not hits:
        print(f"OK {slug}: 辞書3系統で読みが割れる語なし")
        return 0
    if any(h["narr"] for h in hits):
        from ytf.config import Config, find_project_dir
        cfg = Config.load()
        proj = find_project_dir(cfg.root, slug)
        script = yaml.safe_load((proj / "script.yaml").read_text(encoding="utf-8"))
        verify_narration(cfg, script, hits)
    seen = {}
    for h in hits:
        seen.setdefault(h["surf"], []).append(h)
    print(f"‼ {slug}: 読みが割れる語 {len(seen)} 種 / {len(hits)} 箇所")
    for surf, group in sorted(seen.items(), key=lambda kv: -len(kv[1])):
        v = group[0]["votes"]
        line = " / ".join(f"{n}={','.join(y)}" for n, y in v.items())
        print(f"\n  「{surf}」 {line}")
        for h in group[:3]:
            tag = "ナレ" if h["narr"] else h["speaker"]
            act = f" 実読={h['actual'][:40]}" if h["actual"] else ""
            print(f"    idx{h['idx']} [{tag}] {h['verdict']}")
            print(f"      {h['text'][:50]}{act}")
            if h.get("audio"):
                print(f"      {h['audio']}")
        if len(group) > 3:
            print(f"    …ほか {len(group)-3} 箇所")
    return len(seen)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        raise SystemExit("使い方: check_readings_vote.py <slug> | --all")
    if args[0] == "--all":
        import glob
        total = 0
        for f in sorted(glob.glob("projects/**/script.yaml", recursive=True)):
            d = yaml.safe_load(Path(f).read_text(encoding="utf-8"))
            if d:
                total += report(d["meta"]["slug"])
                print()
        raise SystemExit(1 if total else 0)
    raise SystemExit(1 if report(args[0]) else 0)
