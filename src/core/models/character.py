"""Character model.

キャラクター設定を表現する Pydantic モデル。フェーズ管理に対応。
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class Phase(BaseModel):
    """キャラクターのフェーズ（物語の進行段階）."""

    name: str
    episodes: str  # "1-10" or "11-" 形式


class AIVisibilitySettings(BaseModel):
    """AI可視性設定.

    0: AIに見せない
    1: Level1 AIに見せる
    2: Level2 AIに見せる
    3: 全てのAIに見せる
    """

    default: int = Field(default=0, ge=0, le=3)
    hidden_section: int = Field(default=0, ge=0, le=3)


class Character(BaseModel):
    """キャラクターモデル."""

    type: Literal["character"] = "character"
    name: str
    phases: list[Phase] = Field(default_factory=list)
    current_phase: str | None = None
    ai_visibility: AIVisibilitySettings = Field(default_factory=AIVisibilitySettings)
    created: date
    updated: date
    tags: list[str] = Field(default_factory=list)

    # セクション別コンテンツ
    sections: dict[str, str] = Field(default_factory=dict)
