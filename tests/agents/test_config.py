"""Tests for L4 agent pipeline configuration constants."""

from __future__ import annotations

import pytest

from src.agents.config import (
    DEFAULT_POV,
    DEFAULT_WORD_COUNT,
    HUMAN_FALLBACK_ENABLED,
    MAX_REVIEW_RETRIES,
    QUALITY_THRESHOLD_ACCEPTABLE,
    QUALITY_THRESHOLD_EXCELLENT,
    QUALITY_THRESHOLD_GOOD,
    QUALITY_THRESHOLDS,
    get_assessment,
)


class TestConstants:
    """Tests for pipeline configuration constants."""

    def test_max_review_retries(self) -> None:
        """MAX_REVIEW_RETRIES == 3."""
        assert MAX_REVIEW_RETRIES == 3

    def test_quality_thresholds_keys(self) -> None:
        """QUALITY_THRESHOLDS に excellent, good, acceptable キーが存在."""
        assert "excellent" in QUALITY_THRESHOLDS
        assert "good" in QUALITY_THRESHOLDS
        assert "acceptable" in QUALITY_THRESHOLDS

    def test_quality_thresholds_order(self) -> None:
        """閾値の大小関係: excellent > good > acceptable > 0."""
        assert QUALITY_THRESHOLD_EXCELLENT > QUALITY_THRESHOLD_GOOD
        assert QUALITY_THRESHOLD_GOOD > QUALITY_THRESHOLD_ACCEPTABLE
        assert QUALITY_THRESHOLD_ACCEPTABLE > 0

    def test_default_word_count_positive(self) -> None:
        """DEFAULT_WORD_COUNT > 0."""
        assert DEFAULT_WORD_COUNT > 0

    def test_default_pov_nonempty(self) -> None:
        """DEFAULT_POV は非空文字列."""
        assert isinstance(DEFAULT_POV, str)
        assert len(DEFAULT_POV) > 0

    def test_human_fallback_enabled_is_bool(self) -> None:
        """HUMAN_FALLBACK_ENABLED は bool."""
        assert isinstance(HUMAN_FALLBACK_ENABLED, bool)


class TestGetAssessment:
    """Tests for get_assessment function."""

    def test_excellent_range(self) -> None:
        """0.90 → "excellent"."""
        assert get_assessment(0.90) == "excellent"

    def test_good_range(self) -> None:
        """0.75 → "good"."""
        assert get_assessment(0.75) == "good"

    def test_acceptable_range(self) -> None:
        """0.55 → "acceptable"."""
        assert get_assessment(0.55) == "acceptable"

    def test_needs_improvement_range(self) -> None:
        """0.30 → "needs_improvement"."""
        assert get_assessment(0.30) == "needs_improvement"

    def test_boundary_excellent(self) -> None:
        """境界値: 0.85 → "excellent" (ちょうど閾値)."""
        assert get_assessment(0.85) == "excellent"

    def test_boundary_good(self) -> None:
        """境界値: 0.70 → "good" (ちょうど閾値)."""
        assert get_assessment(0.70) == "good"

    def test_boundary_acceptable(self) -> None:
        """境界値: 0.50 → "acceptable" (ちょうど閾値)."""
        assert get_assessment(0.50) == "acceptable"

    def test_out_of_range_negative(self) -> None:
        """範囲外: -0.1 → ValueError."""
        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            get_assessment(-0.1)

    def test_out_of_range_above_one(self) -> None:
        """範囲外: 1.1 → ValueError."""
        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            get_assessment(1.1)

    def test_boundary_zero(self) -> None:
        """境界値: 0.0 → "needs_improvement"."""
        assert get_assessment(0.0) == "needs_improvement"

    def test_boundary_one(self) -> None:
        """境界値: 1.0 → "excellent"."""
        assert get_assessment(1.0) == "excellent"

    def test_just_below_excellent(self) -> None:
        """0.85 より小さい値は good."""
        assert get_assessment(0.8499) == "good"

    def test_just_below_good(self) -> None:
        """0.70 より小さい値は acceptable."""
        assert get_assessment(0.6999) == "acceptable"

    def test_just_below_acceptable(self) -> None:
        """0.50 より小さい値は needs_improvement."""
        assert get_assessment(0.4999) == "needs_improvement"
