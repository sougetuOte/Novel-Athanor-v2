"""Tests for quality result parser."""

import pytest

from src.agents.models.quality_result import (
    QualityAssessment,
    QualityResult,
    QualityScore,
)
from src.agents.models.review_result import IssueSeverity
from src.agents.parsers.quality_parser import parse_quality_output

VALID_YAML_FULL = """\
Some LLM explanation text here.

```yaml
scores:
  coherence: 0.72
  pacing: 0.65
  prose: 0.78
  character_score: 0.70
  style: 0.75
  reader_excitement: 0.68
  emotional_resonance: 0.65
  overall: 0.70
assessment: good
issues:
  - category: pacing
    severity: warning
    location: "第3段落〜第5段落"
    description: "説明が長く、テンポが落ちています"
    suggestion: "対話で情報を伝えることを検討"
recommendations:
  - "第3-5段落を対話形式にリライト"
  - "冒頭のペーシングを改善"
```

以上が評価結果です。
"""

VALID_YAML_MINIMAL = """\
```yaml
scores:
  coherence: 0.80
  pacing: 0.80
  prose: 0.80
  character_score: 0.80
  style: 0.80
  reader_excitement: 0.80
  emotional_resonance: 0.80
  overall: 0.80
assessment: good
```
"""

VALID_YAML_EXCELLENT = """\
```yaml
scores:
  coherence: 0.95
  pacing: 0.90
  prose: 0.92
  character_score: 0.88
  style: 0.91
  reader_excitement: 0.93
  emotional_resonance: 0.89
  overall: 0.91
assessment: excellent
issues: []
recommendations: []
```
"""

VALID_YAML_NEEDS_IMPROVEMENT = """\
```yaml
scores:
  coherence: 0.30
  pacing: 0.25
  prose: 0.40
  character_score: 0.35
  style: 0.30
  reader_excitement: 0.20
  emotional_resonance: 0.25
  overall: 0.29
assessment: needs_improvement
issues:
  - category: coherence
    severity: critical
    description: "ストーリーの流れが途切れている"
  - category: prose
    severity: warning
    location: "全体"
    description: "文体が不安定"
    suggestion: "一貫した文体で書き直す"
recommendations:
  - "全体的な構成を見直す"
```
"""


class TestParseQualityOutput:
    """Tests for parse_quality_output()."""

    def test_parses_full_output(self) -> None:
        """Should parse a complete YAML output."""
        result = parse_quality_output(VALID_YAML_FULL)

        assert isinstance(result, QualityResult)
        assert isinstance(result.scores, QualityScore)
        assert result.scores.coherence == 0.72
        assert result.scores.pacing == 0.65
        assert result.scores.overall == 0.70
        assert result.assessment == QualityAssessment.GOOD

    def test_parses_issues(self) -> None:
        """Should parse issues correctly."""
        result = parse_quality_output(VALID_YAML_FULL)

        assert len(result.issues) == 1
        issue = result.issues[0]
        assert issue.category == "pacing"
        assert issue.severity == IssueSeverity.WARNING
        assert issue.location == "第3段落〜第5段落"
        assert "テンポ" in issue.description

    def test_parses_recommendations(self) -> None:
        """Should parse recommendations as list of strings."""
        result = parse_quality_output(VALID_YAML_FULL)

        assert len(result.recommendations) == 2
        assert "対話形式" in result.recommendations[0]

    def test_parses_minimal_output(self) -> None:
        """Should parse minimal output (no issues/recommendations)."""
        result = parse_quality_output(VALID_YAML_MINIMAL)

        assert result.scores.coherence == 0.80
        assert result.assessment == QualityAssessment.GOOD
        assert result.issues == []
        assert result.recommendations == []

    def test_parses_excellent_assessment(self) -> None:
        """Should parse excellent assessment."""
        result = parse_quality_output(VALID_YAML_EXCELLENT)

        assert result.assessment == QualityAssessment.EXCELLENT
        assert result.is_acceptable is True

    def test_parses_needs_improvement(self) -> None:
        """Should parse needs_improvement assessment."""
        result = parse_quality_output(VALID_YAML_NEEDS_IMPROVEMENT)

        assert result.assessment == QualityAssessment.NEEDS_IMPROVEMENT
        assert result.is_acceptable is False
        assert len(result.issues) == 2

    def test_issue_without_optional_fields(self) -> None:
        """Issues without location/suggestion should use defaults."""
        result = parse_quality_output(VALID_YAML_NEEDS_IMPROVEMENT)

        # First issue has no location or suggestion
        issue = result.issues[0]
        assert issue.location == ""
        assert issue.suggestion == ""

    def test_raises_on_no_yaml_block(self) -> None:
        """Should raise ValueError if no YAML block found."""
        with pytest.raises(ValueError, match="No YAML code block"):
            parse_quality_output("Just some text without YAML.")

    def test_raises_on_missing_scores(self) -> None:
        """Should raise ValueError if scores field is missing."""
        text = """\
```yaml
assessment: good
```
"""
        with pytest.raises(ValueError, match="scores"):
            parse_quality_output(text)

    def test_raises_on_missing_assessment(self) -> None:
        """Should raise ValueError if assessment field is missing."""
        text = """\
```yaml
scores:
  coherence: 0.80
  pacing: 0.80
  prose: 0.80
  character_score: 0.80
  style: 0.80
  reader_excitement: 0.80
  emotional_resonance: 0.80
  overall: 0.80
```
"""
        with pytest.raises(ValueError, match="assessment"):
            parse_quality_output(text)

    def test_raises_on_invalid_yaml(self) -> None:
        """Should raise ValueError on malformed YAML."""
        text = """\
```yaml
scores: [invalid
```
"""
        with pytest.raises(ValueError, match="YAML"):
            parse_quality_output(text)

    def test_raises_on_invalid_assessment_value(self) -> None:
        """Should raise ValueError on invalid assessment value."""
        text = """\
```yaml
scores:
  coherence: 0.80
  pacing: 0.80
  prose: 0.80
  character_score: 0.80
  style: 0.80
  reader_excitement: 0.80
  emotional_resonance: 0.80
  overall: 0.80
assessment: fantastic
```
"""
        with pytest.raises(ValueError):
            parse_quality_output(text)
