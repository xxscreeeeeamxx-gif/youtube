"""channel.yaml のロードとプロジェクトディレクトリの解決。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .schema import Script


def find_repo_root(start: Path | None = None) -> Path:
    p = (start or Path.cwd()).resolve()
    for cand in [p, *p.parents]:
        if (cand / "channel.yaml").exists():
            return cand
    raise SystemExit("channel.yaml が見つかりません。リポジトリ直下で実行してください。")


class Config:
    def __init__(self, root: Path, data: dict[str, Any]):
        self.root = root
        self.data = data

    @classmethod
    def load(cls, start: Path | None = None) -> "Config":
        root = find_repo_root(start)
        with open(root / "channel.yaml", encoding="utf-8") as f:
            return cls(root, yaml.safe_load(f))

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def get(self, *keys: str, default: Any = None) -> Any:
        cur: Any = self.data
        for k in keys:
            if not isinstance(cur, dict) or k not in cur:
                return default
            cur = cur[k]
        return cur

    @property
    def characters(self) -> dict[str, dict]:
        return self.data["characters"]

    def character(self, key: str) -> dict:
        try:
            return self.characters[key]
        except KeyError:
            raise SystemExit(
                f"台本の speaker '{key}' が channel.yaml の characters に存在しません"
            )

    def find_pillow_font(self) -> str:
        for p in self.get("fonts", "paths", default=[]):
            if Path(p).exists():
                return p
        raise SystemExit(
            "日本語フォントが見つかりません。channel.yaml の fonts.paths に"
            "存在するフォントファイルを追加してください。"
        )


def find_project_dir(root: Path, name: str) -> Path | None:
    """projects/ 以下から name に一致するプロジェクトを探す。

    一致の優先順位: フォルダ名の完全一致 → script.yaml の meta.slug 一致。
    「アップロード済み/」のような中間フォルダが何段あってもよい。
    """
    base = root / "projects"
    if not base.is_dir():
        return None
    cands = sorted(base.rglob("script.yaml"))
    import re as _re

    def _bare(n: str) -> str:
        return _re.sub(r"^\d+_", "", n)   # 制作順の番号プレフィックスを外す

    for sp in cands:
        if sp.parent.name == name or _bare(sp.parent.name) == _bare(name):
            return sp.parent
    import yaml as _yaml
    for sp in cands:
        try:
            # encoding を省くと Windows では cp932 で開かれ、日本語の script.yaml が
            # UnicodeDecodeError になる。それが except で握り潰され「プロジェクトが
            # 見つかりません」に化けていた（2026-09-20 Windows移行時に判明）
            meta = (_yaml.safe_load(sp.read_text(encoding="utf-8")) or {}).get("meta", {})
        except Exception:
            continue
        if meta.get("slug") == name:
            return sp.parent
    return None


UPLOADED_DIR = "アップロード済み"


def is_uploaded(path) -> bool:
    """公開済みプロジェクトか（一括処理の対象外にする）。"""
    from pathlib import Path as _P
    return UPLOADED_DIR in _P(path).parts


def iter_projects(root: Path):
    """projects/ 以下の全プロジェクトディレクトリを列挙する。"""
    base = root / "projects"
    if not base.is_dir():
        return []
    return sorted({sp.parent for sp in base.rglob("script.yaml")})


@dataclass
class Project:
    """projects/<slug>/ 以下の作業ディレクトリ。"""

    root: Path  # プロジェクトディレクトリ

    @classmethod
    def resolve(cls, cfg: Config, name: str) -> "Project":
        """slug・フォルダ名・パスのいずれからでもプロジェクトを見つける。

        projects/ 以下は「アップロード済み/未アップロード」などで階層を切って
        よい（フォルダ名は日本語可）。script.yaml の meta.slug でも引ける。
        """
        p = Path(name)
        if p.exists() and (p / "script.yaml").exists():
            return cls(p.resolve())
        found = find_project_dir(cfg.root, name)
        if found is None:
            raise SystemExit(f"プロジェクトが見つかりません: {name}")
        return cls(found.resolve())

    @property
    def script_path(self) -> Path:
        return self.root / "script.yaml"

    @property
    def audio_dir(self) -> Path:
        return self._ensure(self.root / "audio")

    @property
    def frames_dir(self) -> Path:
        return self._ensure(self.root / "frames")

    @property
    def out_dir(self) -> Path:
        return self._ensure(self.root / "out")

    @property
    def llm_dir(self) -> Path:
        return self._ensure(self.root / "llm")

    @property
    def timing_path(self) -> Path:
        return self.root / "audio" / "timing.json"

    def _ensure(self, p: Path) -> Path:
        p.mkdir(parents=True, exist_ok=True)
        return p

    def load_script(self) -> Script:
        if not self.script_path.exists():
            raise SystemExit(f"台本がありません: {self.script_path}")
        with open(self.script_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return Script.model_validate(data)



# ===== フォントの解決（macOS / Windows 両対応）=====
# ヒラギノは macOS にしか無い。Windows では同じ重さの和文フォントが標準で入って
# いないので、**リポジトリ同梱の Noto Sans JP Black を最優先で探す**。
# これがあれば両OSで見た目が一致する。無い場合だけOS標準にフォールバックする。
# （2026-09-18 Windows移行の準備で追加）
FONT_CANDIDATES = {
    # 極太ゴシック。サムネの見出しと本編のテロップに使う
    "w9": [
        "assets/fonts/NotoSansJP-Black.otf",
        "assets/fonts/NotoSansJP-Black.ttf",
        "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc",          # macOS
        "C:/Windows/Fonts/BIZ-UDPGothicB.ttc",                      # Windows 10/11
        "C:/Windows/Fonts/YuGothB.ttc",                             # 游ゴシック Bold
        "C:/Windows/Fonts/meiryob.ttc",                             # メイリオ Bold
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",      # Linux
    ],
    # 太ゴシック。本文・スライド用
    "w6": [
        "assets/fonts/NotoSansJP-Bold.otf",
        "assets/fonts/NotoSansJP-Bold.ttf",
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "C:/Windows/Fonts/BIZ-UDPGothicB.ttc",
        "C:/Windows/Fonts/YuGothB.ttc",
        "C:/Windows/Fonts/meiryob.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    ],
}


def resolve_font(kind: str, root: Path | None = None) -> str:
    """フォントの実ファイルを探す。見つからなければ何が要るかを具体的に言う。"""
    root = root or Path.cwd()
    for cand in FONT_CANDIDATES.get(kind, []):
        p = Path(cand)
        if not p.is_absolute():
            p = root / cand
        if p.exists():
            return str(p)
    raise SystemExit(
        f"フォント（{kind}）が見つかりません。\n"
        "  Windows で動かす場合は Noto Sans JP を入れてください:\n"
        "    https://fonts.google.com/noto/specimen/Noto+Sans+JP から\n"
        "    Black(900) と Bold(700) を assets/fonts/ に置く\n"
        "    （ファイル名: NotoSansJP-Black.otf / NotoSansJP-Bold.otf）\n"
        "  これを入れると macOS と Windows で見た目が一致します。"
    )


def ffmpeg_bin() -> str:
    return os.environ.get("YTF_FFMPEG", "ffmpeg")


def ffprobe_bin() -> str:
    return os.environ.get("YTF_FFPROBE", "ffprobe")
