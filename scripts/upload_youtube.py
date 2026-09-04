#!/usr/bin/env python3
"""YouTube Data API v3 で動画を投稿する（タイトル・説明文・タグ・サムネ・再生リストまで）。

■ なぜこれが要るか
ブラウザ経由の投稿は不可能だった（2026-08-24 に判明）。拡張機能のファイル送信は
10MB上限で動画は700MB超、ファイル選択ダイアログは macOS 側の管轄でブラウザから
触れない。API なら HTTP でファイルをそのまま送れるので、全部自動になる。

■ 初回だけ必要な準備（本人の作業）
  1. https://console.cloud.google.com/ でプロジェクトを作る
  2. 「YouTube Data API v3」を有効化する
  3. OAuth 同意画面を作る（外部／テストユーザーに自分のGmailを追加）
  4. 認証情報 → OAuth クライアント ID → 種類は「デスクトップアプリ」
  5. JSON をダウンロードし、リポジトリ直下に client_secret.json として置く
  6. `python3 scripts/upload_youtube.py auth` を実行し、開いたブラウザで承認する
     （パスワードはこちらでは扱わない。承認は本人が1回押すだけ）

■ 投稿
  python3 scripts/upload_youtube.py upload <slug>                 # 非公開で上げる
  python3 scripts/upload_youtube.py upload <slug> --privacy public
  python3 scripts/upload_youtube.py upload <slug> --publish-at 2026-09-01T19:00:00+09:00

既定は **非公開（private）**。公開は `--privacy public` を明示したときだけ行う。
予約投稿は private のまま publishAt を付ける（YouTube の仕様）。

■ 割り当て
動画1本の投稿は 1600 ユニット、既定の1日枠は 10000 ユニット。1日6本までが目安。
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROOT = Path(__file__).resolve().parent.parent
CLIENT_SECRET = ROOT / "client_secret.json"
TOKEN = ROOT / ".youtube_token.json"

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube",
          # 視聴データの読み取り（yt_analytics.py が使う）。スコープを増やすと
          # 既存のトークンは無効になるので、追加したら auth をやり直すこと
          "https://www.googleapis.com/auth/yt-analytics.readonly"]
# 投稿先を取り違えないための保険。Studio が別チャンネルで開いていて
# 危うく他人のチャンネルに投げかけた実績があるので、名前で照合してから送る
EXPECT_CHANNEL = "日常研究所"
CATEGORY_EDUCATION = "27"          # 教育
MAX_TITLE = 100
MAX_DESC = 5000
MAX_TAGS_CHARS = 480               # YouTube のタグ欄は合計500文字まで


def _fail(msg: str) -> "None":
    print(f"‼ {msg}")
    raise SystemExit(1)


def credentials(interactive: bool = True):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        # **リフレッシュトークンは7日で失効する**（Google Cloud の公開ステータスが
        # 「テスト」のあいだ）。ここで例外を投げると auth まで落ちて再認証できなくなるので、
        # 失敗したら取得済みトークンを捨てて同意フローからやり直す
        from google.auth.exceptions import RefreshError
        try:
            creds.refresh(Request())
            TOKEN.write_text(creds.to_json(), encoding="utf-8")
            return creds
        except RefreshError as e:
            print(f"⚠ トークンが失効しています（{e.args[0] if e.args else e}）。再認証します。")
            creds = None
    if not interactive:
        _fail("未認証です。先に `python3 scripts/upload_youtube.py auth` を実行してください")
    if not CLIENT_SECRET.exists():
        _fail(f"{CLIENT_SECRET.name} がありません。"
              "Google Cloud Console で OAuth クライアントID（デスクトップアプリ）を作り、"
              "JSON をリポジトリ直下に client_secret.json として置いてください")
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent",
                                  authorization_prompt_message=
                                  "ブラウザで承認してください: {url}")
    TOKEN.write_text(creds.to_json(), encoding="utf-8")
    TOKEN.chmod(0o600)
    return creds


def service(interactive: bool = False):
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=credentials(interactive),
                 cache_discovery=False)


def whoami(yt) -> dict:
    r = yt.channels().list(part="snippet,statistics", mine=True).execute()
    items = r.get("items") or []
    if not items:
        _fail("このアカウントにチャンネルがありません")
    return items[0]


def check_channel(yt, expect: str) -> dict:
    ch = whoami(yt)
    title = ch["snippet"]["title"]
    if expect and title != expect:
        _fail(f"投稿先が違います。認証されているのは「{title}」です（期待: 「{expect}」）。\n"
              f"   {TOKEN.name} を削除して auth をやり直し、承認画面で「{expect}」を選んでください")
    subs = ch.get("statistics", {}).get("subscriberCount", "?")
    print(f"投稿先: {title}（登録者 {subs}）")
    return ch


# ---------------------------------------------------------------- メタデータ
def metadata(slug: str):
    """gen_youtube_meta と同じ組み立てを使う（説明文の正は script.yaml の summary）。"""
    from ytf.config import Config, find_project_dir
    from scripts.gen_youtube_meta import build_entry

    proj = find_project_dir(Config.load().root, slug)
    if proj is None:
        _fail(f"プロジェクトが見つかりません: {slug}")
    entry = build_entry(_slug_of(proj), proj)
    if not entry:
        _fail(f"メタデータを組み立てられません（out/metadata.txt が要ります）: {proj}")
    title, description, tag_line = entry
    tags = [t for t in tag_line.split(",") if t]
    # 合計文字数の上限に収まるところで切る（越えると API が丸ごと弾く）
    kept, total = [], 0
    for t in tags:
        if total + len(t) + 1 > MAX_TAGS_CHARS:
            break
        kept.append(t)
        total += len(t) + 1
    if len(kept) < len(tags):
        print(f"（タグを {len(tags)}→{len(kept)} 件に切りました。合計500文字の上限のため）")
    if len(title) > MAX_TITLE:
        _fail(f"タイトルが{len(title)}文字です（上限{MAX_TITLE}）: {title}")
    if len(description) > MAX_DESC:
        _fail(f"説明文が{len(description)}文字です（上限{MAX_DESC}）")
    return proj, title, description, kept


def _slug_of(proj: Path) -> str:
    import yaml
    return yaml.safe_load((proj / "script.yaml").read_text(encoding="utf-8"))["meta"]["slug"]


# ---------------------------------------------------------------- 投稿
def upload(args) -> int:
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    proj, title, description, tags = metadata(args.slug)
    video = proj / "out" / "video.mp4"
    thumb = proj / "out" / "thumbnail.png"
    if not video.exists():
        _fail(f"動画がありません: {video}")
    size_mb = video.stat().st_size / 1024 / 1024

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": args.category,
            "defaultLanguage": "ja",
            "defaultAudioLanguage": "ja",
        },
        "status": {
            "privacyStatus": args.privacy,
            "selfDeclaredMadeForKids": False,
            "license": "youtube",
            "embeddable": True,
        },
    }
    if args.publish_at:
        # 予約投稿は private のまま publishAt を付ける（YouTube の仕様）
        body["status"]["privacyStatus"] = "private"
        body["status"]["publishAt"] = args.publish_at

    print(f"\n■ 投稿内容")
    print(f"  ファイル : {video}（{size_mb:.0f} MB）")
    print(f"  タイトル : {title}")
    print(f"  公開設定 : {body['status']['privacyStatus']}"
          + (f" / 予約 {args.publish_at}" if args.publish_at else ""))
    print(f"  タグ     : {len(tags)}件")
    print(f"  サムネ   : {'あり' if thumb.exists() else 'なし'}")
    print(f"  説明文   : {len(description)}文字\n")
    if args.dry_run:
        print("--dry-run のため送信しません。")
        print("-" * 60)
        print(description)
        print("-" * 60)
        return 0

    yt = service(interactive=False)
    check_channel(yt, args.channel)

    media = MediaFileUpload(str(video), chunksize=8 * 1024 * 1024,
                            resumable=True, mimetype="video/mp4")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)

    vid, tries = None, 0
    while vid is None:
        try:
            status, response = req.next_chunk()
            if status:
                print(f"\r  送信中… {int(status.progress() * 100):3d}%", end="", flush=True)
            if response:
                vid = response["id"]
        except HttpError as e:
            # 5xx は再送すれば通ることが多い。再開可能アップロードなので続きから送れる
            if e.resp.status in (500, 502, 503, 504) and tries < 6:
                tries += 1
                wait = 2 ** tries
                print(f"\n  一時エラー {e.resp.status}。{wait}秒後に再送（{tries}/6）")
                time.sleep(wait)
                continue
            raise
    print(f"\r  送信中… 100%")
    url = f"https://youtu.be/{vid}"
    print(f"✓ 投稿しました: {url}")

    if thumb.exists() and not args.no_thumbnail:
        # サムネの上限は2MB。越えても動画自体は上がっているので、ここでは落とさない
        if thumb.stat().st_size > 2 * 1024 * 1024:
            print(f"‼ サムネが{thumb.stat().st_size/1024/1024:.1f}MBで上限2MBを超えます。"
                  "設定を飛ばしました（Studio から手で設定してください）")
        else:
            from googleapiclient.http import MediaFileUpload as MFU
            yt.thumbnails().set(videoId=vid, media_body=MFU(str(thumb))).execute()
            print("✓ サムネイルを設定しました")

    if args.playlist:
        pid = resolve_playlist(yt, args.playlist)
        yt.playlistItems().insert(part="snippet", body={"snippet": {
            "playlistId": pid,
            "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
        print(f"✓ 再生リストに追加しました（{args.playlist}）")

    (proj / "out" / "youtube_video_id.txt").write_text(vid + "\n", encoding="utf-8")
    print(f"\n動画ID を out/youtube_video_id.txt に控えました。")
    if body["status"]["privacyStatus"] == "private" and not args.publish_at:
        print("いまは非公開です。中身を見てから Studio で公開に切り替えてください。")
    return 0


def cmd_schedule(args) -> int:
    """すでに上げてある動画に、あとから公開予約を付ける（または公開に切り替える）。

    videos.update は指定した part を**丸ごと差し替える**ので、
    いまの status を読んでから publishAt だけ足して送り返す。
    読まずに送ると made-for-kids やライセンスの設定が消える
    """
    yt = service()
    check_channel(yt, args.channel)
    vid = args.video
    if len(vid) != 11:
        from ytf.config import Config, find_project_dir
        proj = find_project_dir(Config.load().root, vid)
        f = proj / "out" / "youtube_video_id.txt" if proj else None
        if not (f and f.exists()):
            _fail(f"動画IDが分かりません: {args.video}")
        vid = f.read_text(encoding="utf-8").strip()
    items = yt.videos().list(part="snippet,status", id=vid).execute().get("items")
    if not items:
        _fail(f"動画が見つかりません: {vid}")
    v = items[0]
    st = dict(v["status"])
    for k in ("uploadStatus", "privacyStatus", "license", "embeddable",
              "publicStatsViewable", "selfDeclaredMadeForKids"):
        st.setdefault(k, v["status"].get(k))
    st.pop("uploadStatus", None)
    st.pop("rejectionReason", None)
    st.pop("failureReason", None)
    if args.publish_at:
        st["privacyStatus"] = "private"     # 予約は private のままでないと効かない
        st["publishAt"] = args.publish_at
    else:
        st["privacyStatus"] = args.privacy
        st.pop("publishAt", None)
    print(f"  {v['snippet']['title'][:44]}")
    print(f"  {v['status']['privacyStatus']} → {st['privacyStatus']}"
          + (f" / 予約 {args.publish_at}" if args.publish_at else ""))
    if args.dry_run:
        print("--dry-run のため送信しません。")
        return 0
    yt.videos().update(part="status", body={"id": vid, "status": st}).execute()
    print(f"✓ 更新しました: https://youtu.be/{vid}")
    return 0


def cmd_thumbnail(args) -> int:
    """投稿済みの動画のサムネイルだけを差し替える。

    サムネは公開後も何度でも変えられる。CTR は Studio に前後で出るので、
    **新作を待たずに、母数のある既存動画1本で型の検証ができる**
    （2026-09-02 に CTR 0.8〜1.3% と判明したのを受けて追加）。
    """
    from googleapiclient.http import MediaFileUpload
    from ytf.config import Config, find_project_dir
    yt = service()
    check_channel(yt, args.channel)
    proj = find_project_dir(Config.load().root, args.video)
    if proj is None:
        _fail(f"プロジェクトが見つかりません: {args.video}")
    vid_file = proj / "out" / "youtube_video_id.txt"
    if not vid_file.exists():
        _fail(f"動画IDの控えがありません: {vid_file}")
    vid = vid_file.read_text(encoding="utf-8").strip()
    thumb = Path(args.file) if args.file else (proj / "out" / "thumbnail.png")
    if not thumb.exists():
        _fail(f"サムネがありません: {thumb}")
    mb = thumb.stat().st_size / 1024 / 1024
    if mb > 2:
        _fail(f"サムネが{mb:.1f}MBで上限2MBを超えます")
    v = yt.videos().list(part="snippet", id=vid).execute()["items"][0]
    print(f"  {v['snippet']['title'][:44]}")
    print(f"  {thumb}（{mb*1024:.0f} KB）")
    if args.dry_run:
        print("--dry-run のため送信しません。")
        return 0
    yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb))).execute()
    print(f"✓ 差し替えました: https://youtu.be/{vid}")
    return 0


def _channel_videos(yt):
    """自分のチャンネルの全動画を {videoId: title} で返す。"""
    ch = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]
    up = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    out, tok = {}, None
    while True:
        r = yt.playlistItems().list(part="snippet", playlistId=up,
                                    maxResults=50, pageToken=tok).execute()
        for it in r["items"]:
            out[it["snippet"]["resourceId"]["videoId"]] = it["snippet"]["title"]
        tok = r.get("nextPageToken")
        if not tok:
            return out


def cmd_thumbnail_all(args) -> int:
    """全動画のサムネを一括で差し替える。

    動画IDの控え（out/youtube_video_id.txt）が無い初期の動画は、
    gen_youtube_meta.TITLES の題名でチャンネル上の動画と突き合わせて特定し、
    見つかったら控えを書き戻す（次回から突き合わせ不要になる）。
    """
    import sys as _s
    from googleapiclient.http import MediaFileUpload
    _s.path.insert(0, str(ROOT / "scripts"))
    from gen_youtube_meta import TITLES
    from ytf.config import Config
    root = Config.load().root
    yt = service()
    check_channel(yt, args.channel)
    live = _channel_videos(yt)
    by_title = {t: v for v, t in live.items()}

    jobs, missing = [], []
    for sy in sorted(root.glob("projects/*/*/*/script.yaml")):
        proj = sy.parent
        thumb = proj / "out" / "thumbnail.png"
        if not thumb.exists():
            continue
        import re
        m = re.search(r'^\s*slug:\s*"?([\w-]+)"?', sy.read_text(encoding="utf-8"), re.M)
        slug = m.group(1) if m else proj.name
        idf = proj / "out" / "youtube_video_id.txt"
        vid = idf.read_text(encoding="utf-8").strip() if idf.exists() else None
        if not vid:
            vid = by_title.get(TITLES.get(slug, ""))
            if vid:
                idf.write_text(vid, encoding="utf-8")   # 次回から突き合わせ不要
        if vid and vid in live:
            jobs.append((slug, vid, thumb, live[vid]))
        else:
            missing.append(slug)

    print(f"対象 {len(jobs)} 本" + (f" / 特定できず {len(missing)} 本: {', '.join(missing)}"
                                     if missing else ""))
    if args.dry_run:
        for slug, vid, thumb, title in jobs:
            print(f"  - {slug:<20}{title[:40]}")
        print(f"差し替え予定: {len(jobs)}/{len(jobs)} 本")
        return 0

    # **サムネ差し替えには専用のレート制限がある**（uploadRateLimitExceeded）。
    # 2026-09-05 の実測では連続10本で 429 になった。Retry-After は返ってこないので、
    # 済んだ分を控えに残しながら待って再試行する（同じ動画に投げ直して枠を潰さない）
    import json as _j
    import time as _t
    state = ROOT / ".thumb_synced.json"
    done = set(_j.loads(state.read_text(encoding="utf-8"))) if state.exists() else set()
    todo = [x for x in jobs if x[0] not in done and
            x[2].stat().st_size / 1024 / 1024 <= 2]
    print(f"済み {len(done)} 本 / これから {len(todo)} 本")
    wait, waited = args.wait, 0
    while todo and waited <= args.max_wait:
        stalled = False
        for job in list(todo):
            slug, vid, thumb, title = job
            try:
                yt.thumbnails().set(videoId=vid,
                                    media_body=MediaFileUpload(str(thumb))).execute()
                done.add(slug)
                todo.remove(job)
                state.write_text(_j.dumps(sorted(done), ensure_ascii=False),
                                 encoding="utf-8")
                print(f"  ✓ {slug:<20}{title[:40]}", flush=True)
                _t.sleep(args.gap)
            except Exception as e:
                if "uploadRateLimitExceeded" in str(e) or "429" in str(e):
                    print(f"  … レート制限。{wait//60}分待ちます（残り {len(todo)} 本）",
                          flush=True)
                    stalled = True
                    break
                print(f"  ✗ {slug:<20}{str(e)[:70]}", flush=True)
                todo.remove(job)
        if not todo:
            break
        if stalled:
            _t.sleep(wait)
            waited += wait
            wait = min(int(wait * 1.5), 3600)
    print(f"差し替え完了: {len(done)} 本" + (f" / 残り {len(todo)} 本" if todo else ""))
    return 0


def resolve_playlist(yt, name_or_id: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_-]{18,}", name_or_id):
        return name_or_id
    tok = None
    while True:
        r = yt.playlists().list(part="snippet", mine=True, maxResults=50,
                                pageToken=tok).execute()
        for it in r.get("items", []):
            if it["snippet"]["title"] == name_or_id:
                return it["id"]
        tok = r.get("nextPageToken")
        if not tok:
            break
    _fail(f"再生リストが見つかりません: {name_or_id}")


# ---------------------------------------------------------------- 補助
def cmd_auth(args) -> int:
    yt = service(interactive=True)
    ch = whoami(yt)
    print(f"✓ 認証しました: {ch['snippet']['title']}"
          f"（登録者 {ch.get('statistics', {}).get('subscriberCount', '?')}）")
    if ch["snippet"]["title"] != EXPECT_CHANNEL:
        print(f"‼ 期待していたチャンネル「{EXPECT_CHANNEL}」ではありません。"
              f"{TOKEN.name} を消してやり直し、承認画面で切り替えてください")
        return 1
    print(f"（{TOKEN.name} に保存しました。次からは承認不要です）")
    return 0


def cmd_playlists(args) -> int:
    yt = service()
    tok = None
    while True:
        r = yt.playlists().list(part="snippet,contentDetails", mine=True,
                                maxResults=50, pageToken=tok).execute()
        for it in r.get("items", []):
            print(f"  {it['id']}  {it['contentDetails']['itemCount']:3d}本  "
                  f"{it['snippet']['title']}")
        tok = r.get("nextPageToken")
        if not tok:
            return 0


def cmd_quota(args) -> int:
    """残り枠は API から取れないので、消費の目安だけ出す。"""
    print("投稿1本=1600ユニット / 既定の1日枠=10000ユニット → 1日6本まで")
    print("使用量は Google Cloud Console の「APIとサービス」→「割り当て」で見られます")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="YouTubeへ投稿する")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("auth", help="初回の認証（ブラウザで承認）")
    a.set_defaults(func=cmd_auth)

    u = sub.add_parser("upload", help="動画を投稿する")
    u.add_argument("slug", help="slug または日本語フォルダ名")
    u.add_argument("--privacy", default="private",
                   choices=["private", "unlisted", "public"],
                   help="既定は private。公開は明示したときだけ")
    u.add_argument("--publish-at", help="予約投稿の日時 例 2026-09-01T19:00:00+09:00")
    u.add_argument("--playlist", help="追加する再生リスト（名前かID）")
    u.add_argument("--category", default=CATEGORY_EDUCATION, help="既定 27（教育）")
    u.add_argument("--channel", default=EXPECT_CHANNEL,
                   help="投稿先チャンネル名の照合。空文字で照合しない")
    u.add_argument("--no-thumbnail", action="store_true")
    u.add_argument("--dry-run", action="store_true", help="送らずに内容だけ出す")
    u.set_defaults(func=upload)

    sc = sub.add_parser("schedule", help="投稿済みの動画に公開予約を付ける／公開に切り替える")
    sc.add_argument("video", help="slug・日本語フォルダ名・動画ID")
    sc.add_argument("--publish-at", help="予約日時 例 2026-09-01T19:00:00+09:00")
    sc.add_argument("--privacy", default="public",
                    choices=["private", "unlisted", "public"],
                    help="--publish-at を付けないときの公開設定")
    sc.add_argument("--channel", default=EXPECT_CHANNEL)
    sc.add_argument("--dry-run", action="store_true")
    sc.set_defaults(func=cmd_schedule)

    tb = sub.add_parser("thumbnail", help="投稿済み動画のサムネを差し替える")
    tb.add_argument("video", help="slug・日本語フォルダ名")
    tb.add_argument("--file", help="使う画像（既定は out/thumbnail.png）")
    tb.add_argument("--channel", default=EXPECT_CHANNEL)
    tb.add_argument("--dry-run", action="store_true")
    tb.set_defaults(func=cmd_thumbnail)

    ta = sub.add_parser("thumbnail-all", help="全動画のサムネを一括で差し替える")
    ta.add_argument("--channel", default=EXPECT_CHANNEL)
    ta.add_argument("--dry-run", action="store_true")
    ta.add_argument("--gap", type=float, default=4.0, help="1本ごとの間隔（秒）")
    ta.add_argument("--wait", type=int, default=900, help="レート制限時の初回待ち（秒）")
    ta.add_argument("--max-wait", type=int, default=6 * 3600, help="待ちの合計上限（秒）")
    ta.set_defaults(func=cmd_thumbnail_all)

    p = sub.add_parser("playlists", help="再生リストの一覧")
    p.set_defaults(func=cmd_playlists)

    q = sub.add_parser("quota", help="割り当ての目安")
    q.set_defaults(func=cmd_quota)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
