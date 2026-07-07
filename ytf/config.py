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


@dataclass
class Project:
    """projects/<slug>/ 以下の作業ディレクトリ。"""

    root: Path  # プロジェクトディレクトリ

    @classmethod
    def resolve(cls, cfg: Config, name: str) -> "Project":
        p = Path(name)
        if not p.exists():
            p = cfg.root / "projects" / name
        if not p.exists():
            raise SystemExit(f"プロジェクトが見つかりません: {name}")
        return cls(p.resolve())

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


def ffmpeg_bin() -> str:
    return os.environ.get("YTF_FFMPEG", "ffmpeg")


def ffprobe_bin() -> str:
    return os.environ.get("YTF_FFPROBE", "ffprobe")
