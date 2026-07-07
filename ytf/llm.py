"""LLM連携。

- api モード: Claude API (anthropic SDK) で全自動生成
- manual モード: プロンプトをファイルに書き出し、claude.ai 等に貼って
  返答をファイルで渡す（APIキー不要の半自動運用）

mode: auto は APIキーの有無で自動判定する。
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from .config import Config


def resolve_mode(cfg: Config) -> str:
    mode = cfg.get("llm", "mode", default="auto")
    if mode == "auto":
        return "api" if os.environ.get("ANTHROPIC_API_KEY") else "manual"
    return mode


def generate(cfg: Config, prompt: str, max_tokens: int = 32000) -> str:
    """Claude APIでテキストを生成する（apiモード時のみ呼ばれる）。"""
    try:
        import anthropic
    except ImportError:
        raise SystemExit(
            "anthropic パッケージがありません: pip install 'yt-factory[llm]' "
            "または pip install anthropic"
        )
    client = anthropic.Anthropic()
    model = cfg.get("llm", "model", default="claude-opus-4-8")
    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason == "refusal":
        raise SystemExit("LLMが生成を拒否しました。プロンプトを見直してください。")
    return next(b.text for b in msg.content if b.type == "text")


def manual_handoff(prompt: str, prompt_path: Path, response_hint: str) -> None:
    """manualモード: プロンプトを書き出して手順を案内し、終了する。"""
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")
    raise SystemExit(
        "\n".join([
            "== コピペ半自動モード ==",
            f"1. プロンプトを claude.ai 等に貼り付け: {prompt_path}",
            f"2. 返答（```yaml ブロックごと）をファイルに保存",
            f"3. 再実行: {response_hint}",
        ])
    )


YAML_FENCE_RE = re.compile(r"```(?:yaml|yml)?\s*\n(.*?)```", re.DOTALL)


def extract_yaml(text: str) -> str:
    """LLM出力からYAML本体を取り出す（フェンス優先、なければ全文）。"""
    m = YAML_FENCE_RE.search(text)
    return (m.group(1) if m else text).strip()


def render_prompt(cfg: Config, template_name: str, **vars: str) -> str:
    path = cfg.root / "prompts" / template_name
    template = path.read_text(encoding="utf-8")
    for k, v in vars.items():
        template = template.replace("{{" + k + "}}", str(v))
    return template
