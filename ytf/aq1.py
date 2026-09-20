"""AquesTalk1（棒読みちゃん同梱DLL）用の読み変換と音声合成。

■ なぜ別モジュールなのか
AquesTalkPlayer（Mac期に使っていた公式プレイヤー）は漢字かな交じり文を
そのまま受け取り、内部の形態素解析でアクセントを付けていた。対して
棒読みちゃん同梱の AquesTalk1 DLL は**音声記号列（カタカナ）しか受け付けない**。
つまり「漢字→カタカナ」を自前で用意しないと合成自体ができない。

■ 数詞を自前で読む理由（2026-09-20 に実測して決めた）
「アラビア数字→漢数字に直して pykakasi に渡す」案を先に試したが、複合数詞で
壊れることが分かったので棄却した:

    21日   → ニジュウツイタチ   （二十一日 の末尾に 一日=ついたち を適用）
    25日   → ニジュウイツカ
    1894年 → センパチヒャク…    （八百=はっぴゃく にならない）
    1952年 → センキュウヒャクイソジネン

そのため数詞は下の num_to_kana()/count_to_kana() で明示的に読む。
漢字語そのものは pykakasi が十分優秀だった（織機→ショッキ、鋳物→イモノ、
金型→カナガタ、六月十日→ロクガツトウカ が全て正解）ので、そちらは任せる。

■ 処理順
    1. 読み台帳（assets/readings_common.yaml + projects/<slug>/readings.yaml）
    2. 数詞＋助数詞 → カタカナ
    3. 残りを pykakasi でカタカナ化
    4. AquesTalk1 が受け付けない文字を落とす
1〜2 の出力はカタカナなので、3 の pykakasi は素通りする。
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

from .config import Config, ffmpeg_bin

SAMPLE_RATE = 24000

# 32bit ブリッジ（scripts/aquestalk1.ps1）を叩くための 32bit PowerShell。
# 同梱DLLが32bit専用で、本体Python(64bit)からは直接呼べないため必要。
WOW64_POWERSHELL = r"C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe"

# 棒読みちゃんの声質番号と同じ並び（exe内のラベル順から確認・2026-09-20）
#   1:女性1 2:女性2 3:男性1 4:男性2 5:中性 6:ロボット 7:機械1 8:機械2
# フォルダ名との対応はexeに文字列として持っておらず確定できなかったため、
# 基本周波数の実測（f1/f2/m1/m2 を基準に中間帯を探す）で imd1 を中性と判断した。
# 耳で選び直す場合は channel.yaml の aquestalk1_voice に別のフォルダ名を書く。
VOICES = ("f1", "f2", "m1", "m2", "r1", "dvd", "jgr", "imd1")
DEFAULT_VOICE = "imd1"

_ONES =["", "イチ", "ニ", "サン", "ヨン", "ゴ", "ロク", "ナナ", "ハチ", "キュウ"]
# 百の位・千の位は音便が起きる（三百=サンビャク、六百=ロッピャク、八百=ハッピャク…）
_HYAKU = ["", "ヒャク", "ニヒャク", "サンビャク", "ヨンヒャク", "ゴヒャク",
          "ロッピャク", "ナナヒャク", "ハッピャク", "キュウヒャク"]
_SEN = ["", "セン", "ニセン", "サンゼン", "ヨンセン", "ゴセン",
        "ロクセン", "ナナセン", "ハッセン", "キュウセン"]


def _under_10000(n: int) -> str:
    """1〜9999 をカタカナで読む。"""
    out = ""
    out += _SEN[n // 1000]
    n %= 1000
    out += _HYAKU[n // 100]
    n %= 100
    if n // 10:
        out += ("" if n // 10 == 1 else _ONES[n // 10]) + "ジュウ"
    n %= 10
    return out + _ONES[n]


def num_to_kana(n: int) -> str:
    """整数をカタカナの読みにする（助数詞なしの素の数）。"""
    if n == 0:
        return "ゼロ"
    units = [(10 ** 12, "チョウ"), (10 ** 8, "オク"), (10 ** 4, "マン")]
    out = ""
    for base, name in units:
        q, n = divmod(n, base)
        if q:
            out += num_to_kana(q) + name
    if n:
        out += _under_10000(n)
    return out


# 月は 4=シ / 7=シチ / 9=ク と決まっている（ヨン・ナナ・キュウとは読まない）
_GATSU = ["", "イチ", "ニ", "サン", "シ", "ゴ", "ロク", "シチ", "ハチ", "ク",
          "ジュウ", "ジュウイチ", "ジュウニ"]

# 日は1〜10と14・20・24が不規則。それ以外は「数＋ニチ」だが、
# 一の位の 4→ヨッカ系 / 7→シチ / 9→ク を取り違えやすい
_NICHI_IRREG = {
    1: "ツイタチ", 2: "フツカ", 3: "ミッカ", 4: "ヨッカ", 5: "イツカ",
    6: "ムイカ", 7: "ナノカ", 8: "ヨウカ", 9: "ココノカ", 10: "トオカ",
    14: "ジュウヨッカ", 20: "ハツカ", 24: "ニジュウヨッカ",
}
_NICHI_ONES = ["", "イチ", "ニ", "サン", "ヨ", "ゴ", "ロク", "シチ", "ハチ", "ク"]


def count_to_kana(n: int, counter: str) -> str | None:
    """助数詞つきの数を読む。対応していない助数詞なら None。"""
    if counter == "年":
        return _year(n)
    if counter == "月":
        return _GATSU[n] + "ガツ" if 1 <= n <= 12 else None
    if counter == "日":
        if n in _NICHI_IRREG:
            return _NICHI_IRREG[n]
        if 1 <= n <= 31:
            tens, ones = divmod(n, 10)
            head = ("" if tens == 1 else _ONES[tens]) + "ジュウ" if tens else ""
            return head + _NICHI_ONES[ones] + "ニチ"
        return None
    return None


def _year(n: int) -> str:
    """西暦の読み。一の位が4のときだけ ヨ になる（1894年=…キュウジュウヨネン）。"""
    if n % 10 == 4:
        return num_to_kana(n - 4) + "ヨネン"
    return num_to_kana(n) + "ネン"


# 数字の直後に来たら読みを変える助数詞（連濁するもの）
_RENDAKU = {"型": "ガタ", "本": "ホン", "杯": "ハイ", "匹": "ヒキ"}

_NUM_RE = re.compile(r"([0-9０-９]+)\s*(年|月|日|型)?")


def _convert_numbers(text: str) -> str:
    """アラビア数字（＋助数詞）をカタカナの読みに置き換える。"""
    def rep(m: re.Match) -> str:
        raw = m.group(1).translate(str.maketrans("０１２３４５６７８９", "0123456789"))
        n = int(raw)
        counter = m.group(2)
        if counter:
            kana = count_to_kana(n, counter)
            if kana:
                return kana
            if counter in _RENDAKU:
                return num_to_kana(n) + _RENDAKU[counter]
            return num_to_kana(n) + counter
        return num_to_kana(n)
    return _NUM_RE.sub(rep, text)


def to_katakana(s: str) -> str:
    """ひらがな→カタカナ。"""
    return "".join(chr(ord(c) + 0x60) if "ぁ" <= c <= "ゖ" else c for c in s)


def load_ledger(cfg: Config, proj=None) -> list[tuple[str, str]]:
    """読み台帳を (表記, カタカナ読み) の長い順で返す。

    既存の検査系（scripts/check_readings.py）と同じ2ファイルを読む。
    ここだけ別の台帳を持つと、検査を通ったのに合成が違う読みになる。
    """
    import yaml

    entries: list = []
    if proj is not None:
        p = Path(proj.root) / "readings.yaml"
        if p.exists():
            entries += yaml.safe_load(p.read_text(encoding="utf-8")) or []
    common = cfg.root / "assets" / "readings_common.yaml"
    if common.exists():
        entries += yaml.safe_load(common.read_text(encoding="utf-8")) or []
    out = []
    for e in entries:
        if isinstance(e, dict) and e.get("surface") and e.get("reading"):
            out.append((str(e["surface"]), to_katakana(str(e["reading"]))))
    # 長い表記を先に当てる（「豊田喜一郎」を「豊田」で潰さない）
    out.sort(key=lambda x: -len(x[0]))
    return out


# AquesTalk1 が受け付けない文字の言い換え（2026-09-20 に全カタカナを実機総当たりして確認）。
# 未対応の字が1つでも混じると合成ごと失敗する（エラーコード105）ので、
# 手前で必ず潰す。実際「鋳物づくり」の ヅ で1行だけ落ちた。
_SUBST = {
    "ヂ": "ジ", "ヅ": "ズ",   # 現代語では発音が同じなので置換して問題ない
    "ヵ": "カ", "ヶ": "ケ",
    "ヰ": "イ", "ヱ": "エ", "ヲ": "オ",
    "！": "。",              # 全角！も未対応。間として読ませる
}

# ヴは1字ずつ潰すと「ヴァ→ブァ」になって不自然なので、拗音の組みごと直す
_VU = [("ヴァ", "バ"), ("ヴィ", "ビ"), ("ヴェ", "ベ"), ("ヴォ", "ボ"),
       ("ヴュ", "ビュ"), ("ヴ", "ブ")]

# AquesTalk1 の音声記号列で意味を持つ文字だけ残す。
# 「、」「。」は無音の間になる。'（アクセント）はこちらでは付けない
_KEEP = re.compile(r"[ァ-ンー、。？]")


def to_koe(text: str, ledger: list[tuple[str, str]] | None = None) -> str:
    """漢字かな交じり文を AquesTalk1 の音声記号列（カタカナ）にする。"""
    import pykakasi

    s = text.replace(" ", "").replace("\u3000", "")
    for surface, reading in (ledger or []):
        s = s.replace(surface, reading)
    s = _convert_numbers(s)
    kks = pykakasi.kakasi()
    s = "".join(x["kana"] for x in kks.convert(s))
    s = to_katakana(s)
    # 未対応字の言い換えは、取りこぼし用のフィルタより先に当てる。
    # 逆順にすると ヴ や ヶ が置換されずに消えて、読みが変わってしまう
    for a, b in _VU:
        s = s.replace(a, b)
    s = s.translate(str.maketrans(_SUBST))
    s = "".join(_KEEP.findall(s))
    return s


def synthe(cfg: Config, koe: str, voice: str, speed: float) -> bytes:
    """音声記号列をWAV(24kHz mono 16bit)に合成する。

    DLLの出力は 8kHz mono。パイプライン標準の24kHzへ上げ、話速は
    AquesTalk1 側にパラメータがないので atempo（ピッチ保持）で合わせる。
    """
    if sys.platform != "win32":
        raise SystemExit(
            "engine: aquestalk1 は Windows 専用です（同梱DLLが32bit Windows版のため）。\n"
            "  macOS では channel.yaml の該当キャラを engine: voicevox などに変えてください。")
    if voice not in VOICES:
        raise SystemExit(
            f"aquestalk1_voice が不正です: {voice}\n"
            f"  指定できるのは {', '.join(VOICES)} です")

    dll = cfg.root / "tools" / "BouyomiChan" / "AquesTalk" / voice / "AquesTalk.dll"
    if not dll.exists():
        raise SystemExit(
            f"AquesTalk1 のDLLがありません: {dll}\n"
            "  棒読みちゃん(BouyomiChan.zip)を tools/BouyomiChan/ に展開してください。\n"
            "  入手: https://chi.usamimi.info/Program/Application/BouyomiChan/")
    bridge = cfg.root / "scripts" / "aquestalk1.ps1"
    if not Path(WOW64_POWERSHELL).exists():
        raise SystemExit(f"32bit PowerShell が見つかりません: {WOW64_POWERSHELL}")

    with tempfile.TemporaryDirectory() as td:
        txt = Path(td) / "koe.txt"
        # 引数ではなくファイルで渡す。引数経由はコードページ次第でカタカナが化ける
        txt.write_text(koe, encoding="utf-8")
        raw = Path(td) / "raw.wav"
        r = subprocess.run(
            [WOW64_POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", str(bridge), "-Dll", str(dll),
             "-TextFile", str(txt), "-Out", str(raw)],
            capture_output=True, text=True, timeout=120)
        if not raw.exists() or raw.stat().st_size == 0:
            raise SystemExit(
                f"AquesTalk1 合成に失敗（声={voice}）: {koe[:40]}\n  {r.stdout.strip()}")
        out = Path(td) / "out.wav"
        af = f"atempo={speed}" if abs(speed - 1.0) > 1e-3 else "anull"
        subprocess.run(
            [ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error",
             "-i", str(raw), "-af", af,
             "-ar", str(SAMPLE_RATE), "-ac", "1", "-sample_fmt", "s16", str(out)],
            check=True, capture_output=True)
        return out.read_bytes()
