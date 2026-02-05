"""Pipeline configuration model."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PipelineConfig(BaseModel):
    """パイプライン設定.

    Attributes:
        max_review_retries: 最大レビューリトライ回数（1-10、デフォルト: 3）
        quality_threshold: 品質閾値（0.0-1.0、デフォルト: 0.6）
        default_word_count: デフォルト文字数（正の整数、デフォルト: 3000）
        default_pov: デフォルト視点（デフォルト: "三人称限定視点"）
    """

    max_review_retries: int = Field(default=3, ge=1, le=10)
    quality_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    default_word_count: int = Field(default=3000, gt=0)
    default_pov: str = "三人称限定視点"
