"""Secret model.

エンティティに紐づく秘密情報のモデル。
仕様書 04_ai-information-control.md に基づく実装。
"""

from enum import Enum

from pydantic import BaseModel, Field, field_validator

from src.core.models.ai_visibility import AIVisibilityLevel


class SecretImportance(str, Enum):
    """秘密の重要度.

    類似度チェックの閾値調整に使用。
    """

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# 重要度ごとの類似度閾値調整値
_THRESHOLD_ADJUSTMENTS = {
    SecretImportance.CRITICAL: -0.15,  # 0.55: 最も敏感
    SecretImportance.HIGH: -0.10,  # 0.60
    SecretImportance.MEDIUM: 0.0,  # 0.70: 基準値
    SecretImportance.LOW: 0.05,  # 0.75: 緩い
}

_BASE_THRESHOLD = 0.70


class Secret(BaseModel):
    """秘密情報モデル.

    キャラクターや世界観設定に紐づく秘密情報。
    AI情報制御による漏洩防止対象となる。
    """

    id: str
    content: str
    visibility: AIVisibilityLevel = AIVisibilityLevel.HIDDEN
    importance: SecretImportance = SecretImportance.MEDIUM
    forbidden_keywords: list[str] = Field(default_factory=list)
    allowed_expressions: list[str] = Field(default_factory=list)
    related_entity: str | None = None
    notes: str | None = None

    @field_validator("visibility", mode="before")
    @classmethod
    def coerce_visibility(cls, v: int | AIVisibilityLevel) -> AIVisibilityLevel:
        """整数から可視性レベルに変換する."""
        if isinstance(v, int):
            if v < 0 or v > 3:
                raise ValueError(f"visibility must be 0-3, got {v}")
            return AIVisibilityLevel(v)
        return v

    def get_similarity_threshold(self, base_threshold: float = _BASE_THRESHOLD) -> float:
        """重要度に応じた類似度閾値を取得する.

        Args:
            base_threshold: 基準閾値（デフォルト: 0.70）

        Returns:
            調整後の閾値
        """
        adjustment = _THRESHOLD_ADJUSTMENTS.get(self.importance, 0.0)
        return base_threshold + adjustment
