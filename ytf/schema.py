"""台本（script.yaml）のスキーマ定義。

台本がパイプライン全体の「単一の真実」であり、
音声・字幕・映像・メタデータはすべてここから決定的に生成される。
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator


class Thumbnail(BaseModel):
    top: str = ""      # サムネ上段の煽り文（短く）
    bottom: str = ""   # サムネ下段の大文字（最重要ワード）


class Meta(BaseModel):
    title: str
    slug: str
    summary: str = ""
    tags: list[str] = Field(default_factory=list)
    thumbnail: Thumbnail = Field(default_factory=Thumbnail)

    @field_validator("slug")
    @classmethod
    def slug_safe(cls, v: str) -> str:
        if not re.fullmatch(r"[a-z0-9][a-z0-9\-_]*", v):
            raise ValueError("slug は半角英数小文字とハイフンのみ")
        return v


class Slide(BaseModel):
    """画面中央に出す図解カード。"""
    title: str = ""
    bullets: list[str] = Field(default_factory=list)
    big: str = ""      # 一言をドンと出したいとき（bullets より優先）


class Cut(BaseModel):
    """1セリフ = 1カット。"""
    speaker: str
    text: str
    emotion: str = "normal"   # normal/happy/surprised/thinking/angry/sad
    slide: Slide | None = None
    image: str | None = None  # プロジェクト相対 or assets相対の画像パス
    pause_after: float | None = None  # 秒。None は channel.yaml の既定値

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("セリフが空です")
        return v.strip()


class Scene(BaseModel):
    id: str
    title: str = ""            # 画面上部の見出しバー（空なら非表示）
    background: str = "default"
    short: bool = False        # True ならショート動画として切り出す
    cuts: list[Cut]


class Script(BaseModel):
    meta: Meta
    scenes: list[Scene]

    def all_cuts(self) -> list[tuple[Scene, int, Cut]]:
        out = []
        for scene in self.scenes:
            for i, cut in enumerate(scene.cuts):
                out.append((scene, i, cut))
        return out

    def speakers_used(self) -> list[str]:
        seen: dict[str, None] = {}
        for _, _, cut in self.all_cuts():
            seen.setdefault(cut.speaker, None)
        return list(seen)


READING_RE = re.compile(r"\[([^|\[\]]+)\|([^|\[\]]+)\]")


def split_reading(text: str) -> tuple[str, str]:
    """`[表示|よみ]` 記法を (字幕用テキスト, 読み上げ用テキスト) に分離する。

    例: "今日は[NASA|ナサ]の話" -> ("今日はNASAの話", "今日はナサの話")
    """
    display = READING_RE.sub(lambda m: m.group(1), text)
    spoken = READING_RE.sub(lambda m: m.group(2), text)
    return display, spoken
