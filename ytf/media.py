"""フリー素材の検索・ダウンロード。

- Wikimedia Commons: APIキー不要。歴史画像・絵画・図版・写真に強い。
  ライセンスはPD/CC系で様々なので credits.txt を必ず確認すること
  （CC BY系は概要欄にクレジット表記が必要）。
- Pexels: 環境変数 PEXELS_API_KEY（無料登録）があれば写真と動画クリップも
  検索できる。Pexelsライセンスはクレジット不要で商用可。

使い方:
    ytf media "中世 銀行"            # 画像を media/ にダウンロード
    ytf media "skating rink" --video # 動画クリップ（Pexels、要APIキー）
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import requests

from .config import Config

UA = {"User-Agent": "yt-factory/0.1 (personal video pipeline)"}


def _slug(query: str) -> str:
    s = re.sub(r"[^\w\-]+", "-", query, flags=re.UNICODE).strip("-")
    return s[:40] or "query"


def _download(url: str, dest: Path) -> bool:
    import time

    for attempt in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=60)
            if r.status_code == 429:  # レート制限: 待って再試行
                time.sleep(3 * (attempt + 1))
                continue
            r.raise_for_status()
            dest.write_bytes(r.content)
            time.sleep(1)  # 連続ダウンロードのマナー
            return True
        except requests.RequestException as e:
            print(f"  取得失敗: {url} ({e})")
            return False
    print(f"  取得失敗（レート制限）: {url}")
    return False


def search_wikimedia(query: str, n: int) -> list[dict]:
    """Wikimedia Commons の画像検索。thumb（小）と url（挿入用の大）を返す。"""
    r = requests.get(
        "https://commons.wikimedia.org/w/api.php",
        params={
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {query}",
            "gsrnamespace": 6,
            "gsrlimit": n,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "iiurlwidth": 480,
        },
        headers=UA,
        timeout=30,
    )
    r.raise_for_status()
    pages = (r.json().get("query") or {}).get("pages") or {}
    out = []
    for p in pages.values():
        info = (p.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}

        def m(key: str) -> str:
            return re.sub(r"<[^>]+>", "", str((meta.get(key) or {}).get("value", ""))).strip()

        thumb = info.get("thumburl")
        original = info.get("url")
        if not thumb or not original:
            continue
        # 挿入用はオリジナルを使う（サムネ生成サービスは不安定なため確実な原本を取得）
        out.append({
            "url": original,
            "thumb": thumb,
            "type": "image",
            "title": p.get("title", "").replace("File:", ""),
            "license": m("LicenseShortName") or "不明",
            "author": m("Artist") or "不明",
            "page": info.get("descriptionurl", ""),
            "source": "Wikimedia Commons",
        })
    return out


def search_pexels(query: str, n: int, video: bool) -> list[dict]:
    """Pexels の写真/動画検索（要 PEXELS_API_KEY）。"""
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        return []
    headers = {"Authorization": key, **UA}
    if video:
        r = requests.get("https://api.pexels.com/videos/search",
                         params={"query": query, "per_page": n},
                         headers=headers, timeout=30)
        r.raise_for_status()
        out = []
        for v in r.json().get("videos", []):
            files = sorted(v.get("video_files", []),
                           key=lambda f: abs((f.get("height") or 0) - 1080))
            if not files:
                continue
            out.append({
                "url": files[0]["link"],
                "thumb": v.get("image", ""),
                "type": "video",
                "title": f"pexels_video_{v['id']}.mp4",
                "license": "Pexels License（クレジット不要・商用可）",
                "author": v.get("user", {}).get("name", "不明"),
                "page": v.get("url", ""),
                "source": "Pexels",
            })
        return out
    r = requests.get("https://api.pexels.com/v1/search",
                     params={"query": query, "per_page": n},
                     headers=headers, timeout=30)
    r.raise_for_status()
    return [{
        "url": p["src"]["large2x"],
        "thumb": p["src"]["medium"],
        "type": "image",
        "title": f"pexels_{p['id']}.jpg",
        "license": "Pexels License（クレジット不要・商用可）",
        "author": p.get("photographer", "不明"),
        "page": p.get("url", ""),
        "source": "Pexels",
    } for p in r.json().get("photos", [])]


def search_all(cfg: Config, query: str, n: int, video: bool) -> list[dict]:
    """編集画面用: Wikimedia + Pexels を集約して検索する（DLはしない）。"""
    if video:
        return search_pexels(query, n, video=True)
    results: list[dict] = []
    try:
        results += search_wikimedia(query, n)
    except requests.RequestException as e:
        print(f"Wikimedia検索に失敗: {e}")
    results += search_pexels(query, max(2, n // 2), video=False)
    return results


def insert_media(cfg: Config, item: dict, kind: str) -> dict:
    """素材を1件ダウンロードして所定の場所に配置し、台本へ書く値を返す。

    kind: "background"（フル画面背景）/ "image"（カード内画像）/ "video"（カード内動画）
    """
    import hashlib

    url = item["url"]
    key = hashlib.sha1(url.encode()).hexdigest()[:8]
    src_ext = Path(url.split("?")[0]).suffix.lower()

    if kind == "background":
        ext = src_ext if src_ext in (".jpg", ".jpeg", ".png") else ".jpg"
        name = f"m_{key}"
        dest = cfg.root / "assets" / "backgrounds" / f"{name}{ext}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not _download(url, dest):
            raise RuntimeError("素材のダウンロードに失敗しました")
        ret = {"kind": "background", "value": name}
    else:
        ext = src_ext or (".mp4" if kind == "video" else ".jpg")
        rel = f"media/_editor/m_{key}{ext}"
        dest = cfg.root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not _download(url, dest):
            raise RuntimeError("素材のダウンロードに失敗しました")
        ret = {"kind": kind, "value": rel}

    # ライセンス・作者を1ファイルに集約記録（公開前の確認用）
    credits = cfg.root / "media" / "credits.txt"
    credits.parent.mkdir(parents=True, exist_ok=True)
    line = (f"{dest.relative_to(cfg.root)}\t{item.get('source', '')}\t"
            f"{item.get('license', '')}\t{item.get('author', '')}\t{item.get('page', '')}")
    prev = credits.read_text(encoding="utf-8") if credits.exists() else ""
    credits.write_text(prev + line + "\n", encoding="utf-8")
    ret["license"] = item.get("license", "")
    return ret


def run_media(cfg: Config, query: str, n: int, video: bool, dest: str | None) -> None:
    out_dir = Path(dest) if dest else cfg.root / "media" / _slug(query)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = search_all(cfg, query, n, video)
    if video and not results:
        raise SystemExit(
            "動画素材の検索には Pexels のAPIキーが必要です（無料）。\n"
            "  1. https://www.pexels.com/api/ でキーを取得\n"
            "  2. export PEXELS_API_KEY=<キー> を設定して再実行"
        )

    if not results:
        raise SystemExit("見つかりませんでした。クエリを変えてみてください（英語も有効）。")

    credits = out_dir / "credits.txt"
    lines = [credits.read_text(encoding="utf-8")] if credits.exists() else []
    got = 0
    for i, item in enumerate(results):
        ext = Path(item["title"]).suffix or (".mp4" if video else ".jpg")
        name = f"{_slug(query)}_{i:02d}{ext}"
        if _download(item["url"], out_dir / name):
            got += 1
            print(f"  {name}  [{item['source']}] {item['license']}")
            lines.append(f"{name}\t{item['source']}\t{item['license']}\t"
                         f"{item['author']}\t{item['page']}")
    credits.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\n{got} 件 -> {out_dir}")
    print(f"ライセンス・作者の一覧: {credits}")
    print("使い方: 良いものを選んで台本のカットに image:（画像）/ video:（動画）で指定")
    if any("CC BY" in r["license"] for r in results):
        print("⚠ CC BY系の素材を使う場合は、概要欄に作者クレジットの追記が必要です")
