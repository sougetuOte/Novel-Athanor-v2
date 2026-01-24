"""WorldSetting model.

世界観設定を表現する Pydantic モデル。フェーズ管理に対応。
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from src.core.models.character import AIVisibilitySettings, Phase


class WorldSetting(BaseModel):
    """世界観設定モデル."""

    type: Literal["world_setting"] = "world_setting"
    name: str
    category: str  # 例: "Geography", "Magic System", "Organizations" など
    phases: list[Phase] = Field(default_factory=list)
    current_phase: str | None = None
    ai_visibility: AIVisibilitySettings = Field(default_factory=AIVisibilitySettings)
    created: date
    updated: date
    tags: list[str] = Field(default_factory=list)

    # セクション別コンテンツ
    sections: dict[str, str] = Field(default_factory=dict)
