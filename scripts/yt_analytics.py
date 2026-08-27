#!/usr/bin/env python3
"""YouTube Analytics API で視聴データを読む（投稿の判断材料をとる）。

■ できること / できないこと
できる: 日別の再生数、動画ごとの維持率、曜日の偏り、流入経路
できない: **時間帯（何時に見られたか）**。Analytics API にその次元が無い。
  Studio の「視聴者が YouTube にアクセスしている時間帯」だけが情報源で、
  チャンネルが小さいうちは「データ不足」で表示されない（2026-08-27 時点がそれ）

認証は upload_youtube.py と共通のトークンを使う。スコープを増やしたので、
このスクリプトを初めて使うときは auth をやり直す必要がある:
  rm .youtube_token.json && python3 scripts/upload_youtube.py auth

実行:
  python3 scripts/yt_analytics.py videos          # 動画ごとの成績一覧
  python3 scripts/yt_analytics.py daily <slugかvideoId>  # 日別の推移
  python3 scripts/yt_analytics.py dow             # 曜日別の再生
  python3 scripts/yt_analytics.py sources <slugかvideoId>  # 流入経路
"""

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from upload_youtube import service, _fail  # noqa: E402

WEEK = ["月", "火", "水", "木", "金", "土", "日"]


def analytics():
    from googleapiclient.discovery import build
    from upload_youtube import credentials
    return build("youtubeAnalytics", "v2", credentials=credentials(False),
                 cache_discovery=False)


def query(ya, start, end, metrics, dimensions=None, filters=None, sort=None,
          max_results=None):
    kw = dict(ids="channel==MINE", startDate=start, endDate=end, metrics=metrics)
    if dimensions:
        kw["dimensions"] = dimensions
    if filters:
        kw["filters"] = filters
    if sort:
        kw["sort"] = sort
    if max_results:
        kw["maxResults"] = max_results
    return ya.reports().query(**kw).execute()


def all_videos(yt):
    """公開・非公開すべての動画を、公開が古い順に返す。"""
    ch = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]
    up = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, tok = [], None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=up,
                                    maxResults=50, pageToken=tok).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        tok = r.get("nextPageToken")
        if not tok:
            break
    vs = yt.videos().list(part="snippet,statistics,status,contentDetails",
                          id=",".join(ids)).execute()["items"]
    vs.sort(key=lambda v: v["snippet"]["publishedAt"])
    return vs


def resolve_video(yt, key: str) -> tuple:
    """slug・日本語フォルダ名・タイトルの一部・動画IDのどれでも動画を引く。"""
    if len(key) == 11 and "/" not in key:
        r = yt.videos().list(part="snippet", id=key).execute()["items"]
        if r:
            return key, r[0]["snippet"]["title"], r[0]["snippet"]["publishedAt"][:10]
    # プロジェクト側に控えた動画IDを見る
    try:
        from ytf.config import Config, find_project_dir
        proj = find_project_dir(Config.load().root, key)
        if proj is not None:
            f = proj / "out" / "youtube_video_id.txt"
            if f.exists():
                return resolve_video(yt, f.read_text(encoding="utf-8").strip())
    except Exception:
        pass
    for v in all_videos(yt):
        if key in v["snippet"]["title"]:
            return v["id"], v["snippet"]["title"], v["snippet"]["publishedAt"][:10]
    _fail(f"動画が見つかりません: {key}")


def _bar(n, top, width=34):
    return "█" * max(0, round(width * n / top)) if top else ""


# ---------------------------------------------------------------- 動画ごと
def cmd_videos(args) -> int:
    yt = service()
    ya = analytics()
    vs = all_videos(yt)
    end = date.today().isoformat()
    print(f"{'#':<3}{'公開日':<12}{'再生':>6}{'平均視聴':>8}{'維持率':>7}"
          f"{'高評価率':>8}  タイトル")
    for n, v in enumerate(vs, 1):
        if v["status"]["privacyStatus"] != "public":
            continue
        vid = v["id"]
        pub = v["snippet"]["publishedAt"][:10]
        r = query(ya, pub, end,
                  "views,averageViewDuration,averageViewPercentage",
                  filters=f"video=={vid}")
        row = (r.get("rows") or [[0, 0, 0]])[0]
        views, avg_s, avg_pct = int(row[0]), int(row[1]), float(row[2])
        likes = int(v["statistics"].get("likeCount", 0))
        lr = 100 * likes / views if views else 0
        print(f"{n:<3}{pub:<12}{views:>6}{avg_s//60:>5}分{avg_s%60:02d}秒"
              f"{avg_pct:>6.1f}%{lr:>7.1f}%  {v['snippet']['title'][:34]}")
    return 0


# ---------------------------------------------------------------- 日別
def cmd_daily(args) -> int:
    yt = service()
    ya = analytics()
    vid, title, pub = resolve_video(yt, args.video)
    end = date.today().isoformat()
    r = query(ya, pub, end, "views,estimatedMinutesWatched",
              dimensions="day", filters=f"video=={vid}", sort="day")
    rows = r.get("rows") or []
    if not rows:
        print("データがありません")
        return 0
    top = max(x[1] for x in rows)
    total = sum(x[1] for x in rows)
    print(f"{title}\n公開 {pub} / 合計 {total} 回\n")
    for d, views, mins in rows:
        wd = WEEK[date.fromisoformat(d).weekday()]
        print(f"  {d}({wd}) {views:>5} {_bar(views, top)}")
    # 直近7日と、その前7日を比べて「まだ伸びているか」を見る
    if len(rows) >= 14:
        last7 = sum(x[1] for x in rows[-7:])
        prev7 = sum(x[1] for x in rows[-14:-7])
        first7 = sum(x[1] for x in rows[:7])
        print(f"\n  最初の7日 {first7} 回")
        print(f"  その前の7日 {prev7} 回 → 直近7日 {last7} 回", end="")
        if prev7:
            print(f"（{100*last7/prev7-100:+.0f}%）")
        else:
            print()
        share = 100 * last7 / total if total else 0
        print(f"  直近7日が全体の {share:.0f}%", end="  ")
        print("→ まだ伸びている" if share > 20 else
              "→ 初速で稼いで落ち着いた形" if first7 > last7 * 3 else "→ ゆるやかに継続")
    return 0


# ---------------------------------------------------------------- 曜日
def cmd_dow(args) -> int:
    ya = analytics()
    end = date.today()
    start = end - timedelta(days=args.days)
    r = query(ya, start.isoformat(), end.isoformat(), "views",
              dimensions="day", sort="day")
    rows = r.get("rows") or []
    if not rows:
        print("データがありません")
        return 0
    agg = {i: [0, 0] for i in range(7)}
    for d, views in rows:
        w = date.fromisoformat(d).weekday()
        agg[w][0] += views
        agg[w][1] += 1
    print(f"曜日別の再生（{start} 〜 {end} の {len(rows)} 日ぶん）\n")
    avgs = {w: (v[0] / v[1] if v[1] else 0) for w, v in agg.items()}
    top = max(avgs.values()) or 1
    for w in range(7):
        print(f"  {WEEK[w]}  1日平均 {avgs[w]:>6.1f} 回  {_bar(avgs[w], top)}")
    print("\n※ これは「視聴された曜日」であって「投稿すべき曜日」ではない。"
          "\n  本数が少ないうちは、公開直後の山がそのまま曜日の偏りに見える点に注意")
    return 0


# ---------------------------------------------------------------- 流入経路
def cmd_sources(args) -> int:
    yt = service()
    ya = analytics()
    vid, title, pub = resolve_video(yt, args.video)
    r = query(ya, pub, date.today().isoformat(), "views",
              dimensions="insightTrafficSourceType",
              filters=f"video=={vid}", sort="-views")
    rows = r.get("rows") or []
    total = sum(x[1] for x in rows) or 1
    names = {"YT_SEARCH": "YouTube検索", "SUGGESTED_VIDEO": "関連動画",
             "BROWSE": "ブラウジング機能（ホーム等）", "EXT_URL": "外部サイト",
             "NOTIFICATION": "通知", "PLAYLIST": "再生リスト",
             "CHANNEL": "チャンネルページ", "NO_LINK_OTHER": "直接・不明",
             "SUBSCRIBER": "登録チャンネル欄", "YT_CHANNEL": "チャンネルページ"}
    print(f"{title}\n流入経路（公開〜現在 / 合計 {total} 回）\n")
    for src, views in rows:
        print(f"  {names.get(src, src):<24}{views:>6} 回  {100*views/total:>5.1f}%")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="視聴データを読む")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("videos", help="動画ごとの成績一覧")
    v.set_defaults(func=cmd_videos)
    d = sub.add_parser("daily", help="日別の推移")
    d.add_argument("video", help="slug・タイトルの一部・動画ID")
    d.set_defaults(func=cmd_daily)
    w = sub.add_parser("dow", help="曜日別の再生")
    w.add_argument("--days", type=int, default=28)
    w.set_defaults(func=cmd_dow)
    s = sub.add_parser("sources", help="流入経路")
    s.add_argument("video", help="slug・タイトルの一部・動画ID")
    s.set_defaults(func=cmd_sources)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
