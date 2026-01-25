"""AI Visibility model (complete version).

AI情報制御システムの可視性設定モデル。
仕様書 04_ai-information-control.md に基づく実装。
"""

from enum import IntEnum
from typing import Union

from pydantic import BaseModel, Field, field_validator


class AIVisibilityLevel(IntEnum):
    """AI可視性レベル.

    0: HIDDEN  - 完全秘匿: AIは存在すら知らない
    1: AWARE   - 認識のみ: 「何かある」と知る
    2: KNOW    - 内容認識: 内容を知っているが文章には出さない（暗示は可）
    3: USE     - 使用可能: 完全に把握、文章で使ってよい
    """

    HIDDEN = 0
    AWARE = 1
    KNOW = 2
    USE = 3


class AllowedExpression(BaseModel):
    """許可された表現.

    Level 2 (KNOW) で使用可能な暗示表現。
    """

    expression: str
    context: str | None = None


class AIVisibility(BaseModel):
    """AI可視性設定.

    Secure by Default 原則に基づき、デフォルトは HIDDEN。
    """

    level: AIVisibilityLevel = AIVisibilityLevel.HIDDEN
    forbidden_keywords: list[str] = Field(default_factory=list)
    allowed_expressions: list[AllowedExpression] = Field(default_factory=list)

    @field_validator("allowed_expressions", mode="before")
    @classmethod
    def coerce_expressions(
        cls, v: list[Union[str, AllowedExpression, dict]]
    ) -> list[AllowedExpression]:
        """文字列リストも AllowedExpression リストに変換する."""
        if not v:
            return []
        result = []
        for item in v:
            if isinstance(item, str):
                result.append(AllowedExpression(expression=item))
            elif isinstance(item, dict):
                result.append(AllowedExpression(**item))
            else:
                result.append(item)
        return result

    @field_validator("level", mode="before")
    @classmethod
    def coerce_level(cls, v: int | AIVisibilityLevel) -> AIVisibilityLevel:
        """整数からレベルに変換する."""
        if isinstance(v, int):
            if v < 0 or v > 3:
                raise ValueError(f"level must be 0-3, got {v}")
            return AIVisibilityLevel(v)
        return v


class SectionVisibility(BaseModel):
    """セクション別可視性設定.

    エンティティ内のセクション（例: 基本情報、隠し設定）ごとの可視性。
    """

    section_name: str
    level: AIVisibilityLevel = AIVisibilityLevel.HIDDEN
    forbidden_keywords: list[str] = Field(default_factory=list)
    allowed_expressions: list[str] = Field(default_factory=list)


class EntityVisibilityConfig(BaseModel):
    """エンティティ別可視性設定.

    キャラクター、世界観設定などのエンティティごとの設定。
    """

    entity_type: str
    entity_name: str
    default_level: AIVisibilityLevel = AIVisibilityLevel.HIDDEN
    sections: list[SectionVisibility] = Field(default_factory=list)


class VisibilityConfig(BaseModel):
    """可視性設定全体.

    vault/{作品名}/_ai_control/visibility.yaml に対応。
    """

    version: str = "1.0"
    default_visibility: AIVisibilityLevel = AIVisibilityLevel.HIDDEN
    entities: list[EntityVisibilityConfig] = Field(default_factory=list)

    def get_entity(
        self, entity_type: str, entity_name: str
    ) -> EntityVisibilityConfig | None:
        """エンティティ設定を取得する.

        Args:
            entity_type: エンティティタイプ（character, world_setting など）
            entity_name: エンティティ名

        Returns:
            該当するエンティティ設定、見つからない場合は None
        """
        for entity in self.entities:
            if entity.entity_type == entity_type and entity.entity_name == entity_name:
                return entity
        return None
