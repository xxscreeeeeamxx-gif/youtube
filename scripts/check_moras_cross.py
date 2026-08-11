#!/usr/bin/env python3
"""VOICEVOXの実読み（timing.jsonのmoras）を、独立エンジン(pykakasi)と全カット突き合わせる。

「予想した語だけ照合する」方式の穴を塞ぐための全数検査。
漢字を含む語ごとに、pykakasiの読みがVOICEVOXのモーラ列に含まれるかを確認し、
不一致を全件列挙する。不一致=誤読とは限らない（pykakasi側が誤ることもある）ので、
出力の全件を人間/エージェントが判定し、本物の誤読はタグ修正+readings_common追加する。

両エンジンが同じ誤読をする語（例: 三重=ミエ）はここでは捕まらないため、
そういう語は見つけ次第 assets/readings_common.yaml と辞書に登録して構造的に防ぐ。

使い方: PYTHONPATH=. python3 scripts/check_moras_cross.py <slug>
        PYTHONPATH=. python3 scripts/check_moras_cross.py --all   # 全プロジェクト走査
"""

import json
import re
import sys
from pathlib import Path

import pykakasi

_kks = pykakasi.kakasi()

_SMALL = {"ャ", "ュ", "ョ", "ァ", "ィ", "ゥ", "ェ", "ォ", "ヮ"}
_ROW_VOWEL = {}
for _v, _chars in {
    "ア": "アカサタナハマヤラワガザダバパャァヮ",
    "イ": "イキシチニヒミリギジヂビピィ",
    "ウ": "ウクスツヌフムユルグズヅブプュゥヴ",
    "エ": "エケセテネヘメレゲゼデベペェ",
    "オ": "オコソトノホモヨロヲゴゾドボポョォ",
}.items():
    for _c in _chars:
        _ROW_VOWEL[_c] = _v


def _norm_base(kana: str) -> str:
    kana = kana.replace("ヂ", "ジ").replace("ヅ", "ズ").replace("ヲ", "オ")
    out = []
    for ch in kana:
        if ch == "ー" and out:
            out.append(_ROW_VOWEL.get(out[-1], out[-1]))
        else:
            out.append(ch)
    return "".join(out)


def norms(kana: str):
    """正規化の2形（長音置換のみ / +オウ→オオ・エイ→エエ）を返す。

    オウ→オオ変換は語境界をまたぐと誤変換になる（例: ソノ+ウラ→ソノオラ）ため、
    変換なし形とのどちらかで一致すればOKとする。
    """
    base = _norm_base(kana)
    fused = re.sub(r"([オコソトノホモヨロゴゾドボポョ])ウ", r"\1オ", base)
    fused = re.sub(r"([エケセテネヘメレゲゼデベペェ])イ", r"\1エ", fused)
    return base, fused


# 文脈で読みが確定する言い回し（ALTの許容読みでは見逃せるため個別に照合する）。
# 例: 「方」は方式=ホオ / 次の方=カタ。ALTに両方入れると誤読を拾えない
# (正規表現, 期待読み)。「その方針/方向/方式」等に誤反応しないよう後続を除外する
_NOT_KATA = r"(?![針向式法面々々位角言便])"
CONTEXT = [
    (r"次の方" + _NOT_KATA, "ツギノカタ"),
    (r"あの方" + _NOT_KATA, "アノカタ"),
    (r"この方" + _NOT_KATA, "コノカタ"),
    (r"その方" + _NOT_KATA, "ソノカタ"),
    (r"どの方" + _NOT_KATA, "ドノカタ"),
    (r"一人の方" + _NOT_KATA, "ヒトリノカタ"),
    (r"女の方" + _NOT_KATA, "オンナノカタ"),
    (r"男の方" + _NOT_KATA, "オトコノカタ"),
    (r"何人", "ナンニン"), (r"何回", "ナンカイ"), (r"何度", "ナンド"),
    (r"今日は", "キョオワ"), (r"明日は", "アシタワ"),
]


# pykakasi側が単独では読みを外しやすい汎用語の代替読み（これらが実読に居れば不一致としない）
ALT = {
    "人": ["ヒト", "ジン", "ニン"], "入": ["ハイ", "イ", "ニュウ"], "何": ["ナニ", "ナン"],
    "上": ["ウエ", "ジョオ", "ジョウ", "アゲ", "ノボ", "カミ"], "下": ["シタ", "サ", "クダ", "オ"],
    "日": ["ヒ", "ニチ", "ビ", "カ", "ジツ"], "方": ["ホオ", "ホウ", "カタ"],
    "間": ["アイダ", "マ", "カン", "ゲン"], "後": ["アト", "ゴ", "ノチ", "ウシ"],
    "前": ["マエ", "ゼン"], "中": ["ナカ", "チュウ", "ジュウ"], "大": ["オオ", "ダイ", "タイ"],
    "小": ["チイ", "コ", "ショオ", "ショウ"], "出": ["デ", "ダ", "シュツ"],
    "来": ["キ", "ク", "コ", "ライ"], "行": ["イ", "オコナ", "コオ", "ギョオ", "ユ"],
    "分": ["ワ", "フン", "ブン", "プン"], "手": ["テ", "シュ"], "物": ["モノ", "ブツ", "モツ"],
    "米": ["コメ", "ベエ", "マイ"], "間接": ["カンセツ"], "側": ["ガワ", "ソバ", "カワ"],
    # pykakasiが単独で外しやすい追加分（VOICEVOXが正しいのに flag される定番）
    "的": ["マト", "テキ"], "印": ["シルシ", "イン"], "君": ["キミ", "クン"],
    "音": ["オト", "ネ", "オン"], "浅": ["アサ", "セン"], "用": ["ヨオ", "モチ"],
    "今日": ["キョオ", "コンニチ"], "明日": ["アシタ", "アス"], "今": ["イマ", "コン"],
    "私": ["ワタシ", "シ"], "僕": ["ボク"], "家": ["イエ", "ウチ", "カ", "ケ"],
    "町": ["マチ", "チョオ"], "街": ["マチ", "ガイ"], "所": ["トコロ", "ショ", "ジョ"],
    "先": ["サキ", "セン", "サッキ"], "元": ["モト", "ゲン", "ガン"],
    "点": ["テン", "ポチ"], "数": ["カズ", "スウ", "ス"], "頭": ["アタマ", "トオ", "ズ"],
    "顔": ["カオ", "ガン"], "声": ["コエ", "ゴエ", "セエ"], "話": ["ハナシ", "ワ", "バナシ"],
    "形": ["カタチ", "ケエ", "ガタ", "ケイ"], "場": ["バ", "ジョオ"],
    "気": ["キ", "ケ"], "本": ["ホン", "モト", "ボン", "ポン"],
    "皆": ["ミナ", "ミンナ", "カイ"], "娘": ["ムスメ"], "床": ["ユカ", "トコ"],
    "縁": ["エン", "フチ", "ヘリ"], "傷": ["キズ", "ショオ"], "薬": ["クスリ", "ヤク"],
    "湯": ["ユ", "トオ"], "酒": ["サケ", "シュ", "ザケ"], "面": ["メン", "ツラ", "オモ"],
    "種": ["タネ", "シュ"], "率": ["リツ", "ヒキ"], "立": ["タ", "ダ", "リツ", "リュウ"],
}


def seg_ok(orig: str, exp_kana: str, mstrs) -> bool:
    for exp in norms(exp_kana):
        if any(exp in m for m in mstrs):
            return True
    for alt in ALT.get(orig, []):
        for a in norms(alt):
            if any(a in m for m in mstrs):
                return True
    # 送りがな付き（例: 入っ）は語幹1字のALTも見る
    stem = orig[0]
    if stem != orig:
        for alt in ALT.get(stem, []):
            for a in norms(alt):
                if any(a in m for m in mstrs):
                    return True
    return False


def strip_tags(text: str) -> str:
    return re.sub(r"\[([^|]+)\|[^\]]+\]", r"\1", text)


def check_slug(slug: str) -> int:
    from ytf.config import Config, find_project_dir
    d = find_project_dir(Config.load().root, slug)
    tj = (d / "audio" / "timing.json") if d else Path("nonexistent")
    if not tj.exists():
        print(f"({slug}: timing.json なし・スキップ)")
        return 0
    cuts = json.loads(tj.read_text())
    hits = 0
    for i, c in enumerate(cuts):
        moras = c.get("moras") or []
        if not moras:
            continue  # ナレーター行(かな強制)は対象外
        raw = "".join(x[0] for x in moras)
        mstrs = norms(raw)
        text = strip_tags(c.get("display_text", ""))
        # 文脈で読みが確定する言い回しを先に照合（ALTの許容読みでは拾えないため）
        for pattern, expect in CONTEXT:
            if not re.search(pattern, text):
                continue
            if not any(expect in m for m in mstrs):
                hits += 1
                print(f"‼ {slug} idx{i} 「{re.search(pattern, text).group(0)}」は {expect} のはず")
                print(f"   text: {c.get('display_text','')[:42]}")
                print(f"   実読: {mstrs[0][:60]}")
        for seg in _kks.convert(text):
            orig = seg["orig"]
            if not re.search(r"[一-鿿]", orig):
                continue  # 漢字を含む語だけ照合
            if len(seg["kana"]) < 2:
                continue
            if not seg_ok(orig, seg["kana"], mstrs):
                hits += 1
                exp0 = norms(seg["kana"])[0]
                print(f"‼ {slug} idx{i} [{orig}] 期待:{exp0}")
                print(f"   text: {c.get('display_text','')[:42]}")
                print(f"   実読: {mstrs[0][:60]}")
    return hits


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "--all":
        total = 0
        from ytf.config import Config, iter_projects
        for p in iter_projects(Config.load().root):
            if (p / "audio" / "timing.json").exists():
                total += check_slug(p.name)
        print(f"\n不一致 合計 {total} 件（全件を目視判定すること）")
    else:
        n = check_slug(sys.argv[1])
        print(f"\n不一致 {n} 件（全件を目視判定すること）")
