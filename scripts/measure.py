#!/usr/bin/env python3
"""施策の効果を、動画ごとの「初週の数字」で測る（2026-10-11〜）。

調査（docs/再生を伸ばす調査_2026-10-11.md）で打った施策
（冒頭の作り直し・終了画面・題名とサムネの新しい型・A/B テスト）が効いたかを、
新しく公開する回の初週と、旧型の回の基準（analytics/baseline_2026-10-11.csv）で比べる。

■ データの出どころ
- YouTube Reporting API（2026-10-11 に有効化・ジョブ作成）
  - channel_reach_basic_a1 ... 動画×日の「インプレッション」と「クリック率」。
    Analytics API には無い指標で、これまでは Studio を開いて読むしかなかった
  - channel_basic_a3 ......... 再生・総再生時間・登録
  - channel_end_screens_a1 ... 終了画面の表示とクリック（施策2）
  - channel_traffic_source_a3  流入元（ホーム・関連動画・終了画面・再生リスト）
  レポートは YouTube 側で毎日作られ、ジョブを作った日以降の分が溜まる。
  **約60日で消えるので、少なくとも月1回は pull して手元に落とす**
- YouTube Analytics API ... 30秒時点の残存率（audienceWatchRatio）
- A/B テストの途中経過（案ごとの総再生時間の割合）は API が無い。Studio の「テストレポートを表示」で読む

■ 日付
Reporting API の日付は太平洋時間。10:00 JST 公開は前日 18:00 PT なので、PT の公開日（0日目）は6時間しかない。
「初日」= PT の 0〜1日目、「初週」= 0〜7日目 として数える。

実行:
  python scripts/measure.py setup    # ジョブを作る（済み。足りない種類だけ作る）
  python scripts/measure.py pull     # 新しいレポートを analytics/reports/ に落とす
  python scripts/measure.py report   # docs/施策の効果.md を作り直す
  python scripts/measure.py          # pull → report
"""

from __future__ import annotations

import csv
import json
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

REPORT_DIR = ROOT / "analytics" / "reports"
BASELINE = ROOT / "analytics" / "baseline_2026-10-11.csv"
OUT = ROOT / "docs" / "施策の効果.md"
JOBS = {
    "channel_reach_basic_a1": "インプレッションとクリック率",
    "channel_basic_a3": "再生・総再生時間・登録",
    "channel_end_screens_a1": "終了画面",
    "channel_traffic_source_a3": "流入元",
}
JST = timezone(timedelta(hours=9))


def _pt(dt: datetime) -> datetime:
    """UTC の時刻を太平洋時間にする。Windows の Python には tz データが無く（tzdata 未導入）、
    venv に足すより夏時間の規則を書く方が軽い: 3月第2日曜 2:00 〜 11月第1日曜 2:00 が UTC-7、他は UTC-8"""
    y = dt.year
    mar = datetime(y, 3, 8 + (6 - datetime(y, 3, 8).weekday()) % 7, 10, tzinfo=timezone.utc)   # 2:00 PST
    nov = datetime(y, 11, 1 + (6 - datetime(y, 11, 1).weekday()) % 7, 9, tzinfo=timezone.utc)  # 2:00 PDT
    off = -7 if mar <= dt.astimezone(timezone.utc) < nov else -8
    return dt.astimezone(timezone(timedelta(hours=off)))
# 施策の区切り（公開日・JST）
NEW_INTRO = date(2026, 9, 30)     # 冒頭の作り直し（山場の先出し・テンポ）
TRACK_FROM = date(2026, 10, 8)    # A/B テストを付けた最初の回。ここから初週を記録する


def reporting():
    from googleapiclient.discovery import build
    from upload_youtube import credentials
    return build("youtubereporting", "v1", credentials=credentials(False), cache_discovery=False)


def cmd_setup() -> None:
    rp = reporting()
    have = {j["reportTypeId"]: j for j in rp.jobs().list().execute().get("jobs", [])}
    for t, label in JOBS.items():
        if t in have:
            print(f"あり  {t}（{label}） 作成 {have[t]['createTime'][:10]}")
            continue
        j = rp.jobs().create(body={"reportTypeId": t, "name": t}).execute()
        print(f"作成  {t}（{label}） {j['id']}")


def cmd_pull() -> None:
    from google.auth.transport.requests import AuthorizedSession
    from upload_youtube import credentials
    rp = reporting()
    sess = AuthorizedSession(credentials(False))
    jobs = rp.jobs().list().execute().get("jobs", [])
    new = 0
    for j in jobs:
        t = j["reportTypeId"]
        if t not in JOBS:
            continue
        d = REPORT_DIR / t
        d.mkdir(parents=True, exist_ok=True)
        tok = None
        while True:
            r = rp.jobs().reports().list(jobId=j["id"], pageToken=tok).execute()
            for rep in r.get("reports", []):
                f = d / f"{rep['startTime'][:10]}_{rep['id']}.csv"
                if f.exists():
                    continue
                resp = sess.get(rep["downloadUrl"])
                resp.raise_for_status()
                f.write_bytes(resp.content)
                new += 1
            tok = r.get("nextPageToken")
            if not tok:
                break
    print(f"新しいレポート {new} 件 → {REPORT_DIR.relative_to(ROOT)}")


def _rows(kind: str):
    for f in sorted((REPORT_DIR / kind).glob("*.csv")):
        with f.open(encoding="utf-8") as fh:
            yield from csv.DictReader(fh)


def _pt_date(s: str) -> date:
    return date(int(s[:4]), int(s[4:6]), int(s[6:8]))


def _load_reports():
    """動画ID → PT日付 → 指標。同じ日が2つのレポートに入っていたら後のもので上書きされないよう、
    レポートファイル単位ではなく行単位で足す（再発行分は同じ startTime 名で重複しない）。"""
    reach = defaultdict(lambda: defaultdict(lambda: [0, 0.0]))      # impr, clicks
    for r in _rows("channel_reach_basic_a1"):
        imp = int(r.get("video_thumbnail_impressions") or 0)
        ctr = float(r.get("video_thumbnail_impressions_ctr") or 0)
        cell = reach[r["video_id"]][_pt_date(r["date"])]
        cell[0] += imp
        cell[1] += imp * ctr
    basic = defaultdict(lambda: defaultdict(lambda: [0, 0.0, 0]))   # views, minutes, subs
    for r in _rows("channel_basic_a3"):
        cell = basic[r["video_id"]][_pt_date(r["date"])]
        cell[0] += int(r.get("views") or 0)
        cell[1] += float(r.get("watch_time_minutes") or 0)
        cell[2] += int(r.get("subscribers_gained") or 0) - int(r.get("subscribers_lost") or 0)
    ends = defaultdict(lambda: defaultdict(lambda: [0, 0]))         # impr, clicks
    for r in _rows("channel_end_screens_a1"):
        cell = ends[r["video_id"]][_pt_date(r["date"])]
        cell[0] += int(r.get("end_screen_element_impressions") or 0)
        cell[1] += int(r.get("end_screen_element_clicks") or 0)
    return reach, basic, ends


def _window(per_day: dict, pub: date, lo: int, hi: int, width: int):
    tot = [0] * width
    for d, cell in per_day.items():
        k = (d - pub).days
        if lo <= k <= hi:
            for i in range(width):
                tot[i] += cell[i]
    return tot


def _retention30(ya, vid: str, pub: str, dur: int):
    from yt_analytics import query
    if not dur:
        return None
    try:
        r = query(ya, pub, date.today().isoformat(), "audienceWatchRatio",
                  dimensions="elapsedVideoTimeRatio", filters=f"video=={vid}",
                  sort="elapsedVideoTimeRatio")
    except Exception:
        return None
    rows = r.get("rows") or []
    if not rows:
        return None
    base = rows[0][1] or 1.0
    best = min(rows, key=lambda x: abs(x[0] - 30 / dur))
    return 100 * best[1] / base


def _mmss(sec: float) -> str:
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}"


def cmd_report() -> None:
    from upload_youtube import service
    from yt_analytics import all_videos, analytics, _dur_seconds
    yt, ya = service(), analytics()
    reach, basic, ends = _load_reports()
    ab = {v["video_id"]: v for v in json.loads((ROOT / "scripts" / "ab_variants.json").read_text(encoding="utf-8"))}
    today_pt = _pt(datetime.now(timezone.utc)).date()

    vids = []
    for v in all_videos(yt):
        st = v["status"]
        when = st.get("publishAt") if st.get("privacyStatus") != "public" else v["snippet"]["publishedAt"]
        if st.get("privacyStatus") != "public" and not st.get("publishAt"):
            continue                                   # 非公開で予約も無い（旧版など）
        t = datetime.fromisoformat((when or v["snippet"]["publishedAt"]).replace("Z", "+00:00"))
        vids.append(dict(id=v["id"], title=v["snippet"]["title"], pub_jst=t.astimezone(JST).date(),
                         pub_pt=_pt(t).date(), dur=_dur_seconds(v["contentDetails"]["duration"]),
                         public=st.get("privacyStatus") == "public"))

    lines = ["# 施策の効果（自動生成: scripts/measure.py report）", "",
             f"更新: {datetime.now(JST):%Y-%m-%d %H:%M} JST。施策と比べ方は scripts/measure.py の先頭を参照。",
             "Reporting API のレポートは1〜2日遅れで届く。経過日数は太平洋時間の公開日から数える。", ""]

    # ---- 新しく公開した回（A/B テスト以降）
    lines += ["## 新しい回の初週（2026-10-08 公開〜）", "",
              "| 公開 | 動画 | 型 | 経過 | 初日の表示 | 初日CTR | 初週の表示 | 初週CTR | 初週の再生 | 平均視聴 | 30秒残存 | 終了画面クリック | 登録 |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    cohort = defaultdict(list)
    vids.sort(key=lambda v: v["pub_jst"])
    for v in vids:
        if v["pub_jst"] < TRACK_FROM:
            continue
        name = v["title"].split("】")[0].lstrip("【") if v["title"].startswith("【") else v["title"][:14]
        kind = "A/B" if v["id"] in ab else "新型"
        age = (today_pt - v["pub_pt"]).days
        if not v["public"]:
            lines.append(f"| {v['pub_jst']:%m/%d} | {name} | {kind} | 公開前 | | | | | | | | | |")
            continue
        i1 = _window(reach.get(v["id"], {}), v["pub_pt"], 0, 1, 2)
        i7 = _window(reach.get(v["id"], {}), v["pub_pt"], 0, 7, 2)
        b7 = _window(basic.get(v["id"], {}), v["pub_pt"], 0, 7, 3)
        e7 = _window(ends.get(v["id"], {}), v["pub_pt"], 0, 7, 2)
        r30 = _retention30(ya, v["id"], v["pub_jst"].isoformat(), v["dur"])
        ctr1 = f"{100 * i1[1] / i1[0]:.1f}%" if i1[0] else ""
        ctr7 = f"{100 * i7[1] / i7[0]:.1f}%" if i7[0] else ""
        avd = _mmss(60 * b7[1] / b7[0]) if b7[0] else ""
        lines.append(f"| {v['pub_jst']:%m/%d} | {name} | {kind} | {age}日 | {i1[0] or ''} | {ctr1} | "
                     f"{i7[0] or ''} | {ctr7} | {b7[0] or ''} | {avd} | "
                     f"{f'{r30:.0f}%' if r30 is not None else ''} | {e7[1] if e7[0] else ''} | {b7[2] or ''} |")
        if age >= 8 and i7[0]:
            cohort[kind].append((i7[0], 100 * i7[1] / i7[0], r30))
    lines.append("")

    # ---- 基準（旧型）
    base = []
    with BASELINE.open(encoding="utf-8") as fh:
        rows = [ln for ln in fh if not ln.startswith("#")]
    for r in csv.DictReader(rows):
        base.append(r)
    by_name = {}
    for v in vids:
        if v["title"].startswith("【"):
            by_name[v["title"].split("】")[0].lstrip("【")] = v
    groups = defaultdict(list)
    for r in base:
        v = by_name.get(r["name"])
        if not v or (date.today() - v["pub_jst"]).days < 8:
            continue                                    # 初週（0〜7日目）が終わっていない回は基準に入れない
        g = "旧型（〜9/29）" if v["pub_jst"] < NEW_INTRO else "新しい冒頭（9/30〜10/7）"
        if v["pub_jst"] >= TRACK_FROM:
            continue
        r30 = _retention30(ya, v["id"], v["pub_jst"].isoformat(), v["dur"])
        groups[g].append((int(r["impressions"]), float(r["ctr"]), r30))

    def summary(label, xs):
        if not xs:
            return f"| {label} | 0本 | | | |"
        imp = statistics.median(x[0] for x in xs)
        ctr = statistics.median(x[1] for x in xs)
        rs = [x[2] for x in xs if x[2] is not None]
        r30 = f"{statistics.median(rs):.0f}%" if rs else ""
        return f"| {label} | {len(xs)}本 | {imp:,.0f} | {ctr:.1f}% | {r30} |"

    lines += ["## 比べる（中央値）", "",
              "基準は Studio の全期間の値（インプレッションは公開後ほぼ1週間で止まるので初週とみなせる）。",
              "新しい回は初週（0〜7日目）が終わったものだけ数える。", "",
              "| まとまり | 本数 | 初週の表示 | CTR | 30秒残存 |", "|---|---|---|---|---|"]
    for g in ("旧型（〜9/29）", "新しい冒頭（9/30〜10/7）"):
        lines.append(summary(g, groups.get(g, [])))
    lines.append(summary("A/B テスト中（10/8〜10/22）", cohort.get("A/B", [])))
    lines.append(summary("新しい型（10/23〜）", cohort.get("新型", [])))
    lines += ["", "A/B テストの案ごとの途中経過は API が無いので、PUBLISH.md「A/B テストの記録」に Studio から写す。", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("書き出し:", OUT.relative_to(ROOT))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "setup":
        cmd_setup()
    elif cmd == "pull":
        cmd_pull()
    elif cmd == "report":
        cmd_report()
    else:
        cmd_pull()
        cmd_report()
