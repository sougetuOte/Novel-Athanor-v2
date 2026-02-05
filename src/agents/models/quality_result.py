"""Quality result models for L4 quality agent."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from src.agents.models.review_result import IssueSeverity


class QualityAssessment(str, Enum):
    """品質評価."""

    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    NEEDS_IMPROVEMENT = "needs_improvement"


class QualityScore(BaseModel):
    """品質スコア.

    Attributes:
        coherence: 一貫性スコア（0.0-1.0）
        pacing: ペーシングスコア（0.0-1.0）
        prose: 文章品質スコア（0.0-1.0）
        character_score: キャラクター表現スコア（0.0-1.0）
        style: スタイルスコア（0.0-1.0）
        reader_excitement: 読者の引き込み度スコア（0.0-1.0）
        emotional_resonance: 感情共鳴スコア（0.0-1.0）
        overall: 総合スコア（0.0-1.0）
    """

    coherence: float = Field(ge=0.0, le=1.0)
    pacing: float = Field(ge=0.0, le=1.0)
    prose: float = Field(ge=0.0, le=1.0)
    character_score: float = Field(ge=0.0, le=1.0)
    style: float = Field(ge=0.0, le=1.0)
    reader_excitement: float = Field(ge=0.0, le=1.0)
    emotional_resonance: float = Field(ge=0.0, le=1.0)
    overall: float = Field(ge=0.0, le=1.0)

    def average(self) -> float:
        """overall を除く全フィールドの平均を計算する.

        Returns:
            Average of all score fields except overall.
        """
        scores = [
            self.coherence,
            self.pacing,
            self.prose,
            self.character_score,
            self.style,
            self.reader_excitement,
            self.emotional_resonance,
        ]
        return sum(scores) / len(scores)


class QualityIssue(BaseModel):
    """品質問題.

    Attributes:
        category: 問題カテゴリ
        severity: 重要度
        location: 問題箇所（デフォルト: 空文字）
        description: 問題の説明
        suggestion: 修正提案（デフォルト: 空文字）
    """

    category: str
    severity: IssueSeverity
    location: str = ""
    description: str
    suggestion: str = ""


class QualityResult(BaseModel):
    """品質評価結果.

    Attributes:
        scores: 品質スコア
        assessment: 品質評価
        issues: 問題リスト
        recommendations: 推奨事項リスト
    """

    scores: QualityScore
    assessment: QualityAssessment
    issues: list[QualityIssue] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

    @property
    def is_acceptable(self) -> bool:
        """品質が許容範囲内か.

        Returns:
            True if assessment is EXCELLENT, GOOD, or ACCEPTABLE.
        """
        return self.assessment in (
            QualityAssessment.EXCELLENT,
            QualityAssessment.GOOD,
            QualityAssessment.ACCEPTABLE,
        )
