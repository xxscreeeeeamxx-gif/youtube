"""ブラウザで台本を微修正するローカル編集画面。

    ytf edit <slug>

で 127.0.0.1 にサーバを立ち上げ、ブラウザからセリフ・読み（reading）・
テロップ・スライド・画像/動画・motion を編集して script.yaml に保存する。
プレビューは本番と同じ合成関数（Composer）で描画するので見た目がそのまま確認できる。
VOICEVOX が起動していれば、選択中のカットだけ音声を試聴できる。
"""

from __future__ import annotations

import base64
import json
import os
import re
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path

import yaml

from .config import Config, Project
from .schema import Cut, Script, split_reading


def _save_script(proj: Project, script: Script) -> None:
    """既存ファイル冒頭のコメント行を残したまま script.yaml を上書きする。"""
    path = proj.script_path
    header = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("#"):
                header.append(line)
            else:
                break
        # 保存前バックアップ（1世代）
        path.with_suffix(".yaml.bak").write_text(
            path.read_text(encoding="utf-8"), encoding="utf-8")
    body = yaml.safe_dump(script.model_dump(exclude_none=True),
                          allow_unicode=True, sort_keys=False, width=200)
    path.write_text("\n".join(header) + ("\n" if header else "") + body,
                    encoding="utf-8")


# ビルド（エンコード）の進行状況（サーバ内で共有）
BUILD_STATE: dict = {"running": False, "done": False, "error": "", "line": ""}


def _audio_lists(cfg: Config) -> dict:
    def names(kind: str) -> list[str]:
        d = cfg.root / "assets" / kind
        return sorted(p.name for p in d.glob("*.mp3")) if d.exists() else []
    return {
        "se": names("se"),
        "bgm": names("bgm"),
        "bgm_current": Path(cfg.get("video", "bgm", "file", default="") or "").name,
        "bgm_volume": cfg.get("video", "bgm", "volume_db", default=-20),
        "se_volume": cfg.get("video", "se_volume_db", default=-3),
    }


def _set_bgm(cfg: Config, body: dict) -> None:
    """channel.yaml の bgm.file / 音量を、コメントを保ったまま行単位で書き換える。"""
    import re as _re
    path = cfg.root / "channel.yaml"
    text = path.read_text(encoding="utf-8")
    if "file" in body:
        val = f"assets/bgm/{body['file']}" if body["file"] else "null"
        text = _re.sub(r"(?m)^(\s*file:).*$",
                       lambda m: f"{m.group(1)} {val}", text, count=1)
    if "bgm_volume" in body:
        text = _re.sub(r"(?m)^(\s*volume_db:).*$",
                       lambda m: f"{m.group(1)} {int(body['bgm_volume'])}", text, count=1)
    if "se_volume" in body:
        text = _re.sub(r"(?m)^(\s*se_volume_db:).*$",
                       lambda m: f"{m.group(1)} {int(body['se_volume'])}", text, count=1)
    path.write_text(text, encoding="utf-8")


def _start_build(cfg: Config, proj: Project) -> dict:
    import subprocess
    import threading

    if BUILD_STATE["running"]:
        return {"ok": False, "error": "already running"}
    BUILD_STATE.update(running=True, done=False, error="", line="開始…")

    def worker():
        try:
            p = subprocess.Popen(
                [sys.executable, "-m", "ytf.cli", "make", proj.root.name],
                cwd=str(cfg.root), stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, bufsize=1,
                env={**os.environ, "PYTHONPATH": str(cfg.root)},
            )
            for line in p.stdout:
                line = line.strip()
                if line and "Warning" not in line and "warnings.warn" not in line:
                    BUILD_STATE["line"] = line
            p.wait()
            if p.returncode == 0:
                BUILD_STATE.update(done=True, line="完了")
            else:
                BUILD_STATE.update(error=BUILD_STATE.get("line", "失敗"))
        except Exception as e:  # noqa: BLE001
            BUILD_STATE["error"] = str(e)
        finally:
            BUILD_STATE["running"] = False

    threading.Thread(target=worker, daemon=True).start()
    return {"ok": True}


def _render_preview(cfg: Config, proj: Project, payload: dict) -> bytes:
    """1カットぶんのフレームを合成してPNGで返す（本番と同じ描画）。"""
    from .compose import Composer

    cut = Cut.model_validate(payload.get("cut") or {})
    scene = payload.get("scene") or {}
    composer = Composer(cfg, proj, vertical=bool(payload.get("vertical")))
    img = composer.compose_cut(
        background=scene.get("background") or "default",
        header=scene.get("title") or "",
        chars=[],
        slide=cut.slide,
        image=cut.image,
        video_card=bool(cut.video and cut.slide is None and not cut.video_full),
        telops=cut.telops,
    )
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _filmstrip(cfg: Config, proj: Project, width: int = 300) -> list[dict]:
    """全カットの縮小プレビューを合成し、フィルムストリップ用の一覧を返す。"""
    from .compose import Composer

    script = proj.load_script()
    composer = Composer(cfg, proj)
    strip = []
    for si, scene in enumerate(script.scenes):
        for ci, cut in enumerate(scene.cuts):
            img = composer.compose_cut(
                background=scene.background,
                header=scene.title,
                chars=[],
                slide=cut.slide,
                image=cut.image,
                video_card=bool(cut.video and cut.slide is None and not cut.video_full),
                telops=cut.telops,
            ).convert("RGB")
            img.thumbnail((width, width * 9 // 16))
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=72)
            tags = []
            if cut.telops:
                tags.append("T")
            if cut.slide:
                tags.append("S")
            if cut.video:
                tags.append("動")
            elif cut.image:
                tags.append("画")
            strip.append({
                "si": si, "ci": ci,
                "scene": scene.title or scene.id,
                "text": cut.text[:28],
                "tags": tags,
                "img": "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(),
            })
    return strip


def _synthesize_cut(cfg: Config, payload: dict) -> bytes:
    """選択カットのセリフをVOICEVOXで合成してWAVを返す（試聴用）。"""
    from .voice import VoicevoxClient, load_dictionary, style_for

    client = VoicevoxClient(cfg.get("voicevox", "url",
                                    default="http://127.0.0.1:50021"))
    if not client.ping():
        raise ConnectionError("VOICEVOXが起動していません")
    client.sync_dictionary(load_dictionary(cfg))
    text = payload.get("reading") or split_reading(payload.get("text", ""))[1]
    style_id, speed, pitch, intonation = style_for(
        cfg, payload.get("speaker", ""), payload.get("emotion", "normal"))
    return client.synthesize(text, style_id, speed, pitch, intonation)


def make_handler(cfg: Config, proj: Project):
    html_path = Path(__file__).parent / "editor.html"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # 静かに
            pass

        def _send(self, code: int, body: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code: int, obj: dict) -> None:
            self._send(code, json.dumps(obj, ensure_ascii=False).encode(),
                       "application/json; charset=utf-8")

        def _body(self) -> dict:
            n = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(n) or b"{}")

        def do_GET(self):
            if self.path == "/" or self.path.startswith("/index"):
                self._send(200, html_path.read_bytes(),
                           "text/html; charset=utf-8")
            elif self.path == "/api/script":
                script = proj.load_script()
                self._json(200, {"name": proj.root.name,
                                 "script": script.model_dump()})
            elif self.path.startswith("/api/filmstrip"):
                from urllib.parse import parse_qs, urlparse
                q = parse_qs(urlparse(self.path).query)
                w = max(160, min(1280, int((q.get("w") or ["300"])[0])))
                try:
                    self._json(200, {"cuts": _filmstrip(cfg, proj, width=w)})
                except (SystemExit, Exception) as e:  # noqa: BLE001
                    self._json(400, {"error": str(e)})
            elif self.path.startswith("/api/video"):
                self._serve_video(proj.root / "out" / "video.mp4")
            elif self.path == "/api/audiolist":
                self._json(200, _audio_lists(cfg))
            elif self.path.startswith("/api/se/") or self.path.startswith("/api/bgm/"):
                kind = "se" if "/se/" in self.path else "bgm"
                name = self.path.rsplit("/", 1)[-1].split("?")[0]
                self._serve_audio(cfg.root / "assets" / kind / name)
            elif self.path == "/api/build/status":
                self._json(200, dict(BUILD_STATE))
            else:
                self._send(404, b"not found", "text/plain")

        def _serve_audio(self, path: Path) -> None:
            if not path.exists() or ".." in path.name:
                self._json(404, {"error": "not found"})
                return
            self._send(200, path.read_bytes(), "audio/mpeg")

        def _serve_video(self, path: Path) -> None:
            if not path.exists():
                self._json(404, {"error": "まだビルドされていません（ytf make <slug>）"})
                return
            size = path.stat().st_size
            rng = self.headers.get("Range")
            m = re.match(r"bytes=(\d+)-(\d*)", rng or "")
            with open(path, "rb") as f:
                if m:  # シーク対応（206 Partial Content）
                    start = int(m.group(1))
                    end = int(m.group(2)) if m.group(2) else size - 1
                    end = min(end, size - 1)
                    length = end - start + 1
                    self.send_response(206)
                    self.send_header("Content-Type", "video/mp4")
                    self.send_header("Accept-Ranges", "bytes")
                    self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                    self.send_header("Content-Length", str(length))
                    self.end_headers()
                    f.seek(start)
                    self.wfile.write(f.read(length))
                else:
                    self.send_response(200)
                    self.send_header("Content-Type", "video/mp4")
                    self.send_header("Accept-Ranges", "bytes")
                    self.send_header("Content-Length", str(size))
                    self.end_headers()
                    self.wfile.write(f.read())

        def do_POST(self):
            try:
                if self.path == "/api/save":
                    script = Script.model_validate(self._body().get("script"))
                    _save_script(proj, script)
                    self._json(200, {"ok": True})
                elif self.path == "/api/preview":
                    png = _render_preview(cfg, proj, self._body())
                    self._send(200, png, "image/png")
                elif self.path == "/api/tts":
                    wav = _synthesize_cut(cfg, self._body())
                    self._send(200, wav, "audio/wav")
                elif self.path == "/api/media/search":
                    from .media import pexels_key, search_all
                    b = self._body()
                    results = search_all(cfg, b.get("query", ""),
                                         int(b.get("count", 12)), bool(b.get("video")))
                    self._json(200, {"results": results,
                                     "pexels": bool(pexels_key(cfg))})
                elif self.path == "/api/media/insert":
                    from .media import insert_media
                    b = self._body()
                    self._json(200, insert_media(cfg, b.get("item") or {},
                                                 b.get("kind", "image")))
                elif self.path == "/api/bgm/set":
                    _set_bgm(cfg, self._body())
                    self._json(200, {"ok": True})
                elif self.path == "/api/build":
                    self._json(200, _start_build(cfg, proj))
                else:
                    self._send(404, b"not found", "text/plain")
            except ConnectionError as e:
                self._json(503, {"ok": False, "error": str(e)})
            except (SystemExit, Exception) as e:  # noqa: BLE001
                self._json(400, {"ok": False, "error": str(e)})

    return Handler


def run_editor(cfg: Config, proj: Project, port: int = 8765,
               open_browser: bool = True) -> None:
    srv = ThreadingHTTPServer(("127.0.0.1", port), make_handler(cfg, proj))
    url = f"http://127.0.0.1:{port}/"
    print(f"編集画面: {url}")
    print("保存すると script.yaml に反映されます（.bak に1世代バックアップ）。"
          "終了は Ctrl+C")
    if open_browser:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n終了しました")
