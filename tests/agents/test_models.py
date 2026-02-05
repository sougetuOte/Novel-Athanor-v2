"""Tests for L4 agent I/O models."""

from __future__ import annotations

import pytest
from src.agents.models import (
    IssueSeverity,
    PipelineConfig,
    QualityAssessment,
    QualityIssue,
    QualityResult,
    QualityScore,
    ReviewIssue,
    ReviewIssueType,
    ReviewResult,
    ReviewStatus,
    SceneRequirements,
)
from src.core.context.scene_identifier import SceneIdentifier


class TestSceneRequirements:
    """Tests for SceneRequirements model."""

    def test_default_values(self) -> None:
        """デフォルト値での生成."""
        req = SceneRequirements(episode_id="010")
        assert req.episode_id == "010"
        assert req.sequence_id is None
        assert req.chapter_id is None
        assert req.current_phase is None
        assert req.word_count == 3000
        assert req.pov == "三人称限定視点"
        assert req.mood is None
        assert req.special_instructions is None

    def test_episode_id_required(self) -> None:
        """episode_id は必須（空文字エラー）."""
        with pytest.raises(ValueError, match="episode_id"):
            SceneRequirements(episode_id="")

    def test_word_count_positive(self) -> None:
        """word_count > 0 バリデーション."""
        with pytest.raises(ValueError):
            SceneRequirements(episode_id="010", word_count=0)
        with pytest.raises(ValueError):
            SceneRequirements(episode_id="010", word_count=-100)

    def test_to_scene_identifier(self) -> None:
        """to_scene_identifier() 変換."""
        req = SceneRequirements(
            episode_id="010",
            sequence_id="seq_01",
            chapter_id="ch_03",
            current_phase="development",
        )
        scene = req.to_scene_identifier()
        assert isinstance(scene, SceneIdentifier)
        assert scene.episode_id == "010"
        assert scene.sequence_id == "seq_01"
        assert scene.chapter_id == "ch_03"
        assert scene.current_phase == "development"

    def test_all_fields_specified(self) -> None:
        """全フィールド指定での生成."""
        req = SceneRequirements(
            episode_id="010",
            sequence_id="seq_02",
            chapter_id="ch_05",
            current_phase="climax",
            word_count=5000,
            pov="一人称",
            mood="緊迫感のある",
            special_instructions="戦闘シーンを中心に",
        )
        assert req.episode_id == "010"
        assert req.sequence_id == "seq_02"
        assert req.chapter_id == "ch_05"
        assert req.current_phase == "climax"
        assert req.word_count == 5000
        assert req.pov == "一人称"
        assert req.mood == "緊迫感のある"
        assert req.special_instructions == "戦闘シーンを中心に"


class TestReviewResult:
    """Tests for ReviewResult model."""

    def test_approved_empty_issues(self) -> None:
        """APPROVED + 空 issues."""
        result = ReviewResult(status=ReviewStatus.APPROVED, issues=[])
        assert result.status == ReviewStatus.APPROVED
        assert result.issues == []
        assert not result.has_critical
        assert result.issue_count == 0

    def test_rejected_with_critical_issue(self) -> None:
        """REJECTED + critical issue."""
        issue = ReviewIssue(
            type=ReviewIssueType.FORBIDDEN_KEYWORD,
            severity=IssueSeverity.CRITICAL,
            location="第3段落",
            detail="「王族」が使用されています",
            suggestion="「高貴な雰囲気」に変更",
        )
        result = ReviewResult(status=ReviewStatus.REJECTED, issues=[issue])
        assert result.status == ReviewStatus.REJECTED
        assert len(result.issues) == 1
        assert result.has_critical
        assert result.issue_count == 1

    def test_has_critical_property(self) -> None:
        """has_critical プロパティ."""
        # Critical なし
        result = ReviewResult(
            status=ReviewStatus.WARNING,
            issues=[
                ReviewIssue(
                    type=ReviewIssueType.SUBTLETY,
                    severity=IssueSeverity.WARNING,
                    detail="暗示が強すぎる",
                )
            ],
        )
        assert not result.has_critical

        # Critical あり
        result_with_critical = ReviewResult(
            status=ReviewStatus.REJECTED,
            issues=[
                ReviewIssue(
                    type=ReviewIssueType.FORBIDDEN_KEYWORD,
                    severity=IssueSeverity.CRITICAL,
                    detail="禁止キーワード",
                )
            ],
        )
        assert result_with_critical.has_critical

    def test_issue_count_property(self) -> None:
        """issue_count プロパティ."""
        result = ReviewResult(
            status=ReviewStatus.WARNING,
            issues=[
                ReviewIssue(
                    type=ReviewIssueType.SUBTLETY,
                    severity=IssueSeverity.INFO,
                    detail="Issue 1",
                ),
                ReviewIssue(
                    type=ReviewIssueType.SIMILARITY,
                    severity=IssueSeverity.WARNING,
                    detail="Issue 2",
                ),
            ],
        )
        assert result.issue_count == 2

    def test_review_issue_type_enum(self) -> None:
        """ReviewIssueType Enum 値."""
        assert ReviewIssueType.FORBIDDEN_KEYWORD == "forbidden_keyword"
        assert ReviewIssueType.SIMILARITY == "similarity"
        assert ReviewIssueType.SUBTLETY == "subtlety"
        assert ReviewIssueType.CONTINUITY == "continuity"
        assert ReviewIssueType.OTHER == "other"


class TestQualityResult:
    """Tests for QualityResult model."""

    def test_all_scores_within_range(self) -> None:
        """全スコア 0.0-1.0 範囲."""
        score = QualityScore(
            coherence=0.8,
            pacing=0.7,
            prose=0.9,
            character_score=0.75,
            style=0.85,
            reader_excitement=0.65,
            emotional_resonance=0.7,
            overall=0.75,
        )
        result = QualityResult(
            scores=score,
            assessment=QualityAssessment.GOOD,
            issues=[],
            recommendations=[],
        )
        assert result.scores.coherence == 0.8
        assert result.scores.pacing == 0.7
        assert result.scores.overall == 0.75

    def test_score_out_of_range_error(self) -> None:
        """範囲外スコアのバリデーションエラー."""
        with pytest.raises(ValueError):
            QualityScore(
                coherence=1.5,  # 範囲外
                pacing=0.7,
                prose=0.9,
                character_score=0.75,
                style=0.85,
                reader_excitement=0.65,
                emotional_resonance=0.7,
                overall=0.75,
            )

        with pytest.raises(ValueError):
            QualityScore(
                coherence=-0.1,  # 範囲外
                pacing=0.7,
                prose=0.9,
                character_score=0.75,
                style=0.85,
                reader_excitement=0.65,
                emotional_resonance=0.7,
                overall=0.75,
            )

    def test_average_method(self) -> None:
        """average() メソッド."""
        score = QualityScore(
            coherence=1.0,
            pacing=0.8,
            prose=0.6,
            character_score=0.4,
            style=0.5,
            reader_excitement=0.7,
            emotional_resonance=0.0,
            overall=0.0,  # overall は average 計算から除外される
        )
        # (1.0 + 0.8 + 0.6 + 0.4 + 0.5 + 0.7 + 0.0) / 7
        expected = 4.0 / 7
        assert abs(score.average() - expected) < 0.001

    def test_quality_assessment_enum(self) -> None:
        """QualityAssessment Enum."""
        assert QualityAssessment.EXCELLENT == "excellent"
        assert QualityAssessment.GOOD == "good"
        assert QualityAssessment.ACCEPTABLE == "acceptable"
        assert QualityAssessment.NEEDS_IMPROVEMENT == "needs_improvement"

    def test_is_acceptable_property(self) -> None:
        """is_acceptable プロパティ."""
        # Acceptable
        result_acceptable = QualityResult(
            scores=QualityScore(
                coherence=0.7,
                pacing=0.6,
                prose=0.7,
                character_score=0.6,
                style=0.7,
                reader_excitement=0.5,
                emotional_resonance=0.6,
                overall=0.65,
            ),
            assessment=QualityAssessment.ACCEPTABLE,
        )
        assert result_acceptable.is_acceptable

        # Needs Improvement
        result_bad = QualityResult(
            scores=QualityScore(
                coherence=0.4,
                pacing=0.3,
                prose=0.5,
                character_score=0.4,
                style=0.4,
                reader_excitement=0.3,
                emotional_resonance=0.4,
                overall=0.4,
            ),
            assessment=QualityAssessment.NEEDS_IMPROVEMENT,
        )
        assert not result_bad.is_acceptable


class TestPipelineConfig:
    """Tests for PipelineConfig model."""

    def test_default_values(self) -> None:
        """デフォルト値."""
        config = PipelineConfig()
        assert config.max_review_retries == 3
        assert config.quality_threshold == 0.6
        assert config.default_word_count == 3000
        assert config.default_pov == "三人称限定視点"

    def test_custom_values(self) -> None:
        """カスタム値."""
        config = PipelineConfig(
            max_review_retries=5,
            quality_threshold=0.7,
            default_word_count=5000,
            default_pov="一人称",
        )
        assert config.max_review_retries == 5
        assert config.quality_threshold == 0.7
        assert config.default_word_count == 5000
        assert config.default_pov == "一人称"

    def test_max_review_retries_validation(self) -> None:
        """max_review_retries >= 1 バリデーション."""
        with pytest.raises(ValueError):
            PipelineConfig(max_review_retries=0)
        with pytest.raises(ValueError):
            PipelineConfig(max_review_retries=-1)
