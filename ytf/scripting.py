"""台本生成ステージ。ネタ(Idea) → script.yaml。"""

from __future__ import annotations

import re
from pathlib import Path

import yaml
from pydantic import ValidationError

from .config import Config
from .ideas import load_backlog, save_backlog
from .llm import extract_yaml, generate, manual_handoff, render_prompt, resolve_mode
from .schema import Script


def _char_budget(cfg: Config) -> int:
    """目標尺から台本の総文字数目安を出す（≈ 8モーラ/秒 ÷ 1.1倍速）。"""
    minutes = float(cfg.get("channel", "target_length_minutes", default=9))
    return int(minutes * 60 * 8 * 1.1 * 0.55)  # 漢字かな混じり文の補正込み


def _characters_desc(cfg: Config) -> str:
    lines = []
    for key, ch in cfg.characters.items():
        lines.append(f"- speaker名 `{key}`（{ch['display_name']}）: {ch.get('role', '')}")
    return "\n".join(lines)


def _build_prompt(cfg: Config, idea_title: str, idea_hook: str, idea_angle: str) -> str:
    return render_prompt(
        cfg, "script.md",
        theme=cfg.get("channel", "theme", default=""),
        audience=cfg.get("channel", "audience", default=""),
        characters=_characters_desc(cfg),
        title=idea_title,
        hook=idea_hook,
        angle=idea_angle,
        char_budget=str(_char_budget(cfg)),
        minutes=str(cfg.get("channel", "target_length_minutes", default=9)),
    )


def validate_script_text(yaml_text: str) -> Script:
    data = yaml.safe_load(extract_yaml(yaml_text))
    return Script.model_validate(data)


def save_script(cfg: Config, script: Script) -> Path:
    proj_dir = cfg.root / "projects" / script.meta.slug
    proj_dir.mkdir(parents=True, exist_ok=True)
    path = proj_dir / "script.yaml"
    path.write_text(
        yaml.safe_dump(script.model_dump(exclude_none=True),
                       allow_unicode=True, sort_keys=False, width=200),
        encoding="utf-8",
    )
    return path


def run_script(cfg: Config, idea_id: str | None, topic: str | None,
               response_file: str | None) -> None:
    # ネタの特定（backlogのID指定 or フリーテキスト）
    backlog = load_backlog(cfg)
    idea = None
    if idea_id:
        idea = next((i for i in backlog.ideas if i.id == idea_id), None)
        if idea is None:
            raise SystemExit(f"ネタが見つかりません: {idea_id}（`ytf ideas --list` で確認）")
        title, hook, angle = idea.title, idea.hook, idea.angle
    elif topic:
        title, hook, angle = topic, "", ""
    elif not response_file:
        raise SystemExit("--idea <id> か --topic <テーマ> を指定してください")

    if response_file:
        script = validate_script_text(Path(response_file).read_text(encoding="utf-8"))
        path = save_script(cfg, script)
        print(f"台本を保存: {path}")
        return

    prompt = _build_prompt(cfg, title, hook, angle)
    if resolve_mode(cfg) != "api":
        manual_handoff(
            prompt,
            cfg.root / "projects" / "_prompt_script.md",
            "ytf script --response <保存したファイル>",
        )

    # APIモード: バリデーション失敗時はエラー内容を渡してリトライ
    text = generate(cfg, prompt)
    for attempt in range(3):
        try:
            script = validate_script_text(text)
            break
        except (ValidationError, yaml.YAMLError) as e:
            if attempt == 2:
                dump = cfg.root / "projects" / "_failed_script.txt"
                dump.write_text(text, encoding="utf-8")
                raise SystemExit(f"台本の検証に3回失敗。生出力: {dump}\n{e}")
            print(f"検証エラー、修正を依頼中... ({attempt + 1}/2)")
            text = generate(
                cfg,
                prompt + "\n\n前回の出力は次のエラーで無効でした。"
                "同じ形式で全文を修正して出力し直してください:\n" + str(e)[:2000],
            )

    path = save_script(cfg, script)
    if idea is not None:
        idea.status = "used"
        save_backlog(cfg, backlog)
    total = sum(len(c.text) for _, _, c in script.all_cuts())
    print(f"台本を保存: {path}（{len(script.scenes)}シーン / 約{total}文字）")
