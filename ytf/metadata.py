"""タイトル・概要欄・タグの生成。VOICEVOXクレジットは使用キャラから自動で入る。"""

from __future__ import annotations

import json

from .config import Config, Project
from .voice import CutTiming


def _ts(sec: float) -> str:
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def build_metadata(cfg: Config, proj: Project, timings: list[CutTiming]) -> dict:
    script = proj.load_script()

    chapters = []
    for ct in timings:
        if ct.scene_start and ct.scene_title:
            chapters.append(f"{_ts(ct.start)} {ct.scene_title}")
    # YouTubeの章機能は 0:00 始まりが必須
    if chapters and not chapters[0].startswith("0:00"):
        chapters.insert(0, f"0:00 {script.meta.title}")

    credits = " / ".join(
        cfg.character(s)["credit"] for s in script.speakers_used()
    )
    description = cfg.get("metadata", "description_template", default="{summary}\n{credits}").format(
        summary=script.meta.summary,
        chapters="\n".join(chapters) or "0:00 本編",
        credits=credits,
    )
    tags = list(dict.fromkeys(
        list(script.meta.tags) + list(cfg.get("metadata", "tags_base", default=[]))
    ))
    return {
        "title": script.meta.title,
        "description": description,
        "tags": tags,
        "credits": credits,
    }


def run_metadata(cfg: Config, proj: Project, timings: list[CutTiming]) -> None:
    meta = build_metadata(cfg, proj, timings)
    (proj.out_dir / "metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    txt = "\n".join([
        "==== タイトル ====",
        meta["title"],
        "",
        "==== 概要欄 ====",
        meta["description"],
        "",
        "==== タグ ====",
        ", ".join(meta["tags"]),
    ])
    (proj.out_dir / "metadata.txt").write_text(txt, encoding="utf-8")
    print(f"メタデータ -> {proj.out_dir / 'metadata.txt'}")
