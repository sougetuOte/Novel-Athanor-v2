"""Foreshadowing model.

伏線管理システム（Chekhov's Gun Tracker）のデータモデル。
仕様書 05_foreshadowing-system.md に基づく実装。
"""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class ForeshadowingType(str, Enum):
    """伏線のタイプ."""

    CHARACTER_SECRET = "character_secret"
    PLOT_TWIST = "plot_twist"
    WORLD_REVEAL = "world_reveal"
    ITEM_SIGNIFICANCE = "item_significance"


class ForeshadowingStatus(str, Enum):
    """伏線のステータス.

    registered: アイデアとして登録、まだ本文には出ていない
    planted: 本文中に伏線が張られた
    reinforced: 伏線が強化・補強された
    revealed: 伏線が回収された
    abandoned: 回収を断念
    """

    REGISTERED = "registered"
    PLANTED = "planted"
    REINFORCED = "reinforced"
    REVEALED = "revealed"
    ABANDONED = "abandoned"


class ForeshadowingSeed(BaseModel):
    """伏線の種（設置内容）."""

    content: str
    description: str | None = None


class ForeshadowingPayoff(BaseModel):
    """伏線の回収."""

    content: str
    planned_episode: str | None = None
    description: str | None = None


class TimelineEntry(BaseModel):
    """伏線のタイムラインエントリ."""

    episode: str
    type: ForeshadowingStatus
    date: date
    expression: str
    subtlety: int = Field(ge=1, le=10)


class TimelineInfo(BaseModel):
    """伏線のタイムライン情報."""

    registered_at: date
    events: list[TimelineEntry] = Field(default_factory=list)


class RelatedElements(BaseModel):
    """伏線に関連する要素."""

    characters: list[str] = Field(default_factory=list)
    plot_threads: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)


class ForeshadowingAIVisibility(BaseModel):
    """伏線のAI可視性設定.

    level:
        0: AIに見せない（秘匿）
        1: 存在を認識させる
        2: 内容を認識させる
        3: 自由に使用可能
    """

    level: int = Field(default=0, ge=0, le=3)
    forbidden_keywords: list[str] = Field(default_factory=list)
    allowed_expressions: list[str] = Field(default_factory=list)


class Foreshadowing(BaseModel):
    """伏線モデル.

    ID命名規則: FS-{episode}-{slug}
    例: FS-03-rocket（第3話で植えたロケットの伏線）
    """

    id: str = Field(pattern=r"^FS-\d+-[a-z0-9-]+$")
    title: str
    fs_type: ForeshadowingType
    status: ForeshadowingStatus
    subtlety_level: int = Field(ge=1, le=10)

    ai_visibility: ForeshadowingAIVisibility = Field(
        default_factory=ForeshadowingAIVisibility
    )
    seed: ForeshadowingSeed | None = None
    payoff: ForeshadowingPayoff | None = None
    timeline: TimelineInfo | None = None
    related: RelatedElements = Field(default_factory=RelatedElements)
    prerequisite: list[str] = Field(default_factory=list)
