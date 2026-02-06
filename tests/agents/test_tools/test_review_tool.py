"""Tests for Algorithmic Review Tool."""

from src.agents.models.review_result import (
    IssueSeverity,
    ReviewIssueType,
    ReviewResult,
    ReviewStatus,
)
from src.agents.tools.review_tool import run_algorithmic_review


class TestRunAlgorithmicReview:
    """Tests for run_algorithmic_review."""

    def test_clean_text_approved(self) -> None:
        """Text without forbidden keywords is approved."""
        result = run_algorithmic_review(
            draft_text="彼女は静かに微笑んだ。",
            forbidden_keywords=["王族", "血筋"],
        )
        assert isinstance(result, ReviewResult)
        assert result.status == ReviewStatus.APPROVED
        assert result.issues == []

    def test_single_violation_rejected(self) -> None:
        """Text with one forbidden keyword is rejected."""
        result = run_algorithmic_review(
            draft_text="彼女は王族の末裔だった。",
            forbidden_keywords=["王族", "血筋"],
        )
        assert result.status == ReviewStatus.REJECTED
        assert len(result.issues) == 1
        assert result.issues[0].type == ReviewIssueType.FORBIDDEN_KEYWORD
        assert result.issues[0].severity == IssueSeverity.CRITICAL
        assert "王族" in result.issues[0].detail

    def test_multiple_violations(self) -> None:
        """Text with multiple forbidden keywords generates multiple issues."""
        result = run_algorithmic_review(
            draft_text="王族の血筋を持つ高貴な存在。",
            forbidden_keywords=["王族", "血筋", "高貴"],
        )
        assert result.status == ReviewStatus.REJECTED
        assert len(result.issues) == 3
        keywords_found = {issue.detail.split("'")[1] for issue in result.issues if "'" in issue.detail}
        assert "王族" in keywords_found
        assert "血筋" in keywords_found
        assert "高貴" in keywords_found

    def test_empty_forbidden_keywords_approved(self) -> None:
        """Empty forbidden keywords list always approves."""
        result = run_algorithmic_review(
            draft_text="何でも書ける。王族も血筋も。",
            forbidden_keywords=[],
        )
        assert result.status == ReviewStatus.APPROVED
        assert result.issues == []

    def test_empty_draft_text_approved(self) -> None:
        """Empty draft text is approved."""
        result = run_algorithmic_review(
            draft_text="",
            forbidden_keywords=["王族"],
        )
        assert result.status == ReviewStatus.APPROVED

    def test_issue_has_location_context(self) -> None:
        """Issues include location context from the violation."""
        text = "遠い昔、この地を治めていたのは王族の末裔だった。"
        result = run_algorithmic_review(
            draft_text=text,
            forbidden_keywords=["王族"],
        )
        assert len(result.issues) == 1
        # location should have surrounding context
        assert result.issues[0].location != ""

    def test_has_critical_on_violation(self) -> None:
        """has_critical is True when forbidden keywords are found."""
        result = run_algorithmic_review(
            draft_text="王族の秘密",
            forbidden_keywords=["王族"],
        )
        assert result.has_critical is True

    def test_issue_count_matches_violations(self) -> None:
        """issue_count matches the number of violations."""
        result = run_algorithmic_review(
            draft_text="王族と血筋の物語。",
            forbidden_keywords=["王族", "血筋"],
        )
        assert result.issue_count == 2
