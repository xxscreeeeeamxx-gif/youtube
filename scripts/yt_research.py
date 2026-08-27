#!/usr/bin/env python3
"""同ジャンルの他チャンネルを調べる（尺・再生数の相場を知るため）。

■ なぜ必要か
自チャンネルの維持率だけを見ていると「短くすべきか」を判断できない。
2026-08-27 に自チャンネル4本の維持率だけを見て「17〜20分に短くすべき」と
結論しかけたが、市場を調べたら**長いほうが同等以上**で、逆だった。
n=4 の内部データより、同ジャンルの数百本のほうが尺の判断材料になる。

■ 読み方の注意
- 検索順（order=viewCount）はチャンネル規模に引っ張られる。
  尺の効果を見たいときは **同じチャンネルの中で** 短い側と長い側を比べる（channel サブコマンド）
- 総集編・総まとめは尺そのものが商品なので、単発ものと混ぜない

実行:
  python3 scripts/yt_research.py search "ずんだもん 解説 誕生" "ゆっくり解説 開発秘話"
  python3 scripts/yt_research.py channel "世界まる見えずんだもん"
"""

import argparse
import re
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from upload_youtube import service, _fail  # noqa: E402

ISO = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")


def dur(iso: str) -> int:
    m = ISO.fullmatch(iso or "")
    if not m:
        return 0
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s


def hms(sec: int) -> str:
    return f"{sec//60:>3}分{sec%60:02d}"


def fetch(yt, ids):
    out = []
    for i in range(0, len(ids), 50):
        out += yt.videos().list(part="snippet,statistics,contentDetails",
                                id=",".join(ids[i:i + 50])).execute()["items"]
    return out


def cmd_search(args) -> int:
    yt = service()
    seen = {}
    for q in args.queries:
        r = yt.search().list(part="snippet", q=q, type="video",
                             maxResults=args.per_query, order="viewCount",
                             regionCode="JP", relevanceLanguage="ja",
                             publishedAfter=f"{args.since}-01-01T00:00:00Z").execute()
        for it in r.get("items", []):
            seen[it["id"]["videoId"]] = True
    rows = []
    for v in fetch(yt, list(seen)):
        d = dur(v["contentDetails"]["duration"])
        if d < args.min_sec:
            continue
        rows.append((int(v["statistics"].get("viewCount", 0)), d,
                     v["snippet"]["channelTitle"], v["snippet"]["title"]))
    rows.sort(reverse=True)
    print(f"候補 {len(seen)} 本 / {args.min_sec//60}分以上に絞って {len(rows)} 本\n")
    print(f"{'再生':>9}{'尺':>9}  {'チャンネル':<22} タイトル")
    for vc, d, ch, ti in rows[:args.top]:
        print(f"{vc:>9,}{hms(d):>9}  {ch[:20]:<22}{ti[:44]}")
    ds = [d for _, d, _, _ in rows]
    if ds:
        print(f"\n尺の中央値 {st.median(ds)/60:.0f}分 / 平均 {st.mean(ds)/60:.0f}分")
    return 0


def cmd_channel(args) -> int:
    """同じチャンネルの中で、短い側と長い側の再生を比べる（規模の影響を消す）。"""
    yt = service()
    r = yt.search().list(part="snippet", q=args.name, type="channel",
                         maxResults=5).execute()
    cid = next((it["snippet"]["channelId"] for it in r.get("items", [])
                if args.name in it["snippet"]["title"]), None)
    if not cid:
        cid = (r.get("items") or [{}])[0].get("snippet", {}).get("channelId")
    if not cid:
        _fail(f"チャンネルが見つかりません: {args.name}")
    ch = yt.channels().list(part="snippet,statistics,contentDetails",
                            id=cid).execute()["items"][0]
    up = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, tok = [], None
    while len(ids) < args.limit:
        p = yt.playlistItems().list(part="contentDetails", playlistId=up,
                                    maxResults=50, pageToken=tok).execute()
        ids += [i["contentDetails"]["videoId"] for i in p["items"]]
        tok = p.get("nextPageToken")
        if not tok:
            break
    rows = [(int(v["statistics"].get("viewCount", 0)),
             dur(v["contentDetails"]["duration"]), v["snippet"]["title"])
            for v in fetch(yt, ids[:args.limit])]
    rows = [x for x in rows if x[1] >= args.min_sec]
    if not rows:
        print("対象がありません")
        return 0
    ds = [d for _, d, _ in rows]
    med = st.median(ds)
    short = [v for v, d, _ in rows if d < med]
    long_ = [v for v, d, _ in rows if d >= med]
    subs = int(ch["statistics"].get("subscriberCount", 0))
    print(f"===== {ch['snippet']['title']}（登録 {subs:,} / {len(rows)}本）=====")
    print(f"  尺の中央値 {med/60:.0f}分（{min(ds)//60}〜{max(ds)//60}分）")
    if short and long_:
        a, b = st.median(short), st.median(long_)
        print(f"  中央値より短い {len(short):>3}本 → 再生の中央値 {a:>9,.0f}")
        print(f"  中央値より長い {len(long_):>3}本 → 再生の中央値 {b:>9,.0f}"
              f"（{100*b/a-100:+.0f}%）")
    rows.sort(reverse=True)
    print("  上位10本:")
    for v, d, t in rows[:10]:
        print(f"    {v:>9,}  {hms(d)}  {t[:42]}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="同ジャンルの相場を調べる")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="検索して尺と再生の一覧を出す")
    s.add_argument("queries", nargs="+")
    s.add_argument("--per-query", type=int, default=25)
    s.add_argument("--since", default="2024")
    s.add_argument("--min-sec", type=int, default=240)
    s.add_argument("--top", type=int, default=30)
    s.set_defaults(func=cmd_search)
    c = sub.add_parser("channel", help="1チャンネル内で尺と再生の関係を見る")
    c.add_argument("name")
    c.add_argument("--limit", type=int, default=100)
    c.add_argument("--min-sec", type=int, default=240)
    c.set_defaults(func=cmd_channel)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
