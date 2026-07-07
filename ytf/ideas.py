"""ネタ出しステージ。ideas/backlog.yaml にストックを貯める。"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from .config import Config
from .llm import extract_yaml, generate, manual_handoff, render_prompt, resolve_mode


class Idea(BaseModel):
    id: str
    title: str            # 動画タイトル案
    hook: str             # 冒頭のつかみ（視聴者が続きを見たくなる一言）
    angle: str            # 解説の切り口
    score: int = 3        # 1-5 自己評価（需要×作りやすさ）
    status: str = "new"   # new / used / rejected


class Backlog(BaseModel):
    ideas: list[Idea] = Field(default_factory=list)


def backlog_path(cfg: Config) -> Path:
    return cfg.root / "ideas" / "backlog.yaml"


def load_backlog(cfg: Config) -> Backlog:
    p = backlog_path(cfg)
    if not p.exists():
        return Backlog()
    return Backlog.model_validate(yaml.safe_load(p.read_text(encoding="utf-8")) or {})


def save_backlog(cfg: Config, backlog: Backlog) -> None:
    p = backlog_path(cfg)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        yaml.safe_dump(backlog.model_dump(), allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def _build_prompt(cfg: Config, count: int, backlog: Backlog) -> str:
    existing = "\n".join(f"- {i.title}" for i in backlog.ideas) or "（まだない）"
    return render_prompt(
        cfg, "ideas.md",
        theme=cfg.get("channel", "theme", default=""),
        audience=cfg.get("channel", "audience", default=""),
        count=str(count),
        existing=existing,
    )


def _merge(cfg: Config, backlog: Backlog, yaml_text: str) -> int:
    data = yaml.safe_load(extract_yaml(yaml_text))
    if isinstance(data, dict) and "ideas" in data:
        data = data["ideas"]
    new = [Idea.model_validate(d) for d in data]
    known = {i.id for i in backlog.ideas} | {i.title for i in backlog.ideas}
    added = 0
    for idea in new:
        if idea.id in known or idea.title in known:
            continue
        backlog.ideas.append(idea)
        added += 1
    save_backlog(cfg, backlog)
    return added


def run_ideas(cfg: Config, count: int, response_file: str | None) -> None:
    backlog = load_backlog(cfg)
    if response_file:
        added = _merge(cfg, backlog, Path(response_file).read_text(encoding="utf-8"))
        print(f"{added} 件追加 -> {backlog_path(cfg)}")
        return

    prompt = _build_prompt(cfg, count, backlog)
    if resolve_mode(cfg) == "api":
        added = _merge(cfg, backlog, generate(cfg, prompt))
        print(f"{added} 件追加 -> {backlog_path(cfg)}")
    else:
        manual_handoff(
            prompt,
            cfg.root / "ideas" / "prompt.md",
            "ytf ideas --response <保存したファイル>",
        )


def list_ideas(cfg: Config) -> None:
    backlog = load_backlog(cfg)
    if not backlog.ideas:
        print("ネタがありません。`ytf ideas` で生成してください。")
        return
    for i in sorted(backlog.ideas, key=lambda x: -x.score):
        mark = {"new": " ", "used": "✓", "rejected": "x"}.get(i.status, "?")
        print(f"[{mark}] {i.score}★ {i.id}: {i.title}")
