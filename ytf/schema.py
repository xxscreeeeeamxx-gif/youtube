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


MOTIONS = {"zoom-in", "zoom-out", "pan-left", "pan-right", "none"}
TELOP_SIZES = {"sm", "md", "lg", "xl"}
TELOP_POSITIONS = {
    f"{v}-{h}"
    for v in ("top", "middle", "bottom")
    for h in ("left", "center", "right")
}


class Telop(BaseModel):
    """画面に大きく出すキーワードテロップ。重要な一言だけを出す。

    スタイル（大きさ・位置・色・縁・光彩）はカットごとに内容へ合わせて指定する。
    """
    text: str
    size: str = "lg"                  # sm / md / lg / xl
    position: str = "bottom-center"   # top/middle/bottom - left/center/right
    color: str = "#FFFFFF"            # 文字色
    stroke: str = "#1E222E"           # 縁取り色
    glow: str | None = None           # 光彩色（例 "#CC0000"。None なら光彩なし）
    anim: str = "up"                  # 登場アニメ none / fade / up / down

    @field_validator("anim")
    @classmethod
    def anim_valid(cls, v: str) -> str:
        if v not in {"none", "fade", "up", "down"}:
            raise ValueError("anim は none / fade / up / down のいずれか")
        return v

    @field_validator("size")
    @classmethod
    def size_valid(cls, v: str) -> str:
        if v not in TELOP_SIZES:
            raise ValueError(f"telop.size は {sorted(TELOP_SIZES)} のいずれか")
        return v

    @field_validator("position")
    @classmethod
    def position_valid(cls, v: str) -> str:
        if v not in TELOP_POSITIONS:
            raise ValueError("telop.position は top/middle/bottom - left/center/right の組合せ")
        return v


class Cut(BaseModel):
    """1セリフ = 1カット。"""
    speaker: str
    text: str
    emotion: str = "normal"   # normal/happy/surprised/thinking/angry/sad
    reading: str | None = None  # 読み上げの手動上書き（誤読修正用。表示は text のまま）
    telops: list[Telop] = Field(default_factory=list)
    slide: Slide | None = None
    image: str | None = None  # プロジェクト相対 or assets相対の画像パス
    video: str | None = None  # 動画クリップ（音は使わずナレーション優先）
    video_span: int = 1       # この動画を何カット分にまたがって連続再生するか
    video_speed: float = 1.0  # 再生速度。0.5でスロー、2.0で倍速
    video_full: bool = False  # True で全画面表示（False はカード内）
    motion: str | None = None  # 画面の動き。未指定は自動（ゆっくりズーム交互）
    pause_after: float | None = None  # 秒。None は channel.yaml の既定値

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("セリフが空です")
        return v.strip()

    @field_validator("motion")
    @classmethod
    def motion_valid(cls, v: str | None) -> str | None:
        if v is not None and v not in MOTIONS:
            raise ValueError(f"motion は {sorted(MOTIONS)} のいずれか")
        return v

    @field_validator("video_span")
    @classmethod
    def span_valid(cls, v: int) -> int:
        if v < 1:
            raise ValueError("video_span は1以上")
        return v

    @field_validator("video_speed")
    @classmethod
    def speed_valid(cls, v: float) -> float:
        if not 0.1 <= v <= 4.0:
            raise ValueError("video_speed は 0.1〜4.0")
        return v


class Scene(BaseModel):
    id: str
    title: str = ""            # 画面上部の見出しバー（空なら非表示）
    background: str = "default"
    short: bool = False        # True ならショート動画として切り出す
    # このシーン（＝1画像）の動き。1方向のみ・カットをまたいで連続。
    # 未指定ならシーンごとに自動割当（zoom-in→pan-left→zoom-out→pan-right）
    motion: str | None = None
    cuts: list[Cut]

    @field_validator("motion")
    @classmethod
    def motion_valid(cls, v: str | None) -> str | None:
        if v is not None and v not in MOTIONS:
            raise ValueError(f"scene.motion は {sorted(MOTIONS)} のいずれか")
        return v


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
