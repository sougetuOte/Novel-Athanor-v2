"""Tests for Human Fallback logic."""

from src.agents.config import MAX_REVIEW_RETRIES
from src.agents.models.review_result import (
    IssueSeverity,
    ReviewIssue,
    ReviewIssueType,
    ReviewResult,
    ReviewStatus,
)
from src.agents.tools.review_tool import (
    format_fallback_report,
    should_fallback,
)


class TestShouldFallback:
    """Tests for should_fallback."""

    def test_below_max_retries(self) -> None:
        """Returns False when retry count is below max."""
        assert should_fallback(retry_count=0) is False
        assert should_fallback(retry_count=1) is False
        assert should_fallback(retry_count=MAX_REVIEW_RETRIES - 1) is False

    def test_at_max_retries(self) -> None:
        """Returns True when retry count equals max."""
        assert should_fallback(retry_count=MAX_REVIEW_RETRIES) is True

    def test_above_max_retries(self) -> None:
        """Returns True when retry count exceeds max."""
        assert should_fallback(retry_count=MAX_REVIEW_RETRIES + 1) is True

    def test_custom_max_retries(self) -> None:
        """Custom max_retries overrides default."""
        assert should_fallback(retry_count=2, max_retries=2) is True
        assert should_fallback(retry_count=1, max_retries=2) is False

    def test_fallback_disabled(self) -> None:
        """When max_retries is 0, always fallback."""
        assert should_fallback(retry_count=0, max_retries=0) is True


class TestFormatFallbackReport:
    """Tests for format_fallback_report."""

    def test_report_contains_status(self) -> None:
        """Report contains human_fallback status."""
        last_result = ReviewResult(
            status=ReviewStatus.REJECTED,
            issues=[
                ReviewIssue(
                    type=ReviewIssueType.FORBIDDEN_KEYWORD,
                    severity=IssueSeverity.CRITICAL,
                    detail="禁止キーワード '王族' が検出されました",
                )
            ],
        )
        report = format_fallback_report(
            retry_count=3,
            last_result=last_result,
        )
        assert "human_fallback" in report["status"]

    def test_report_contains_retry_count(self) -> None:
        """Report contains the retry count."""
        last_result = ReviewResult(status=ReviewStatus.REJECTED)
        report = format_fallback_report(retry_count=3, last_result=last_result)
        assert report["retry_count"] == 3

    def test_report_contains_last_issues(self) -> None:
        """Report contains the last review issues."""
        issues = [
            ReviewIssue(
                type=ReviewIssueType.FORBIDDEN_KEYWORD,
                severity=IssueSeverity.CRITICAL,
                detail="禁止キーワード検出",
            ),
            ReviewIssue(
                type=ReviewIssueType.SUBTLETY,
                severity=IssueSeverity.WARNING,
                detail="暗示が強すぎる",
            ),
        ]
        last_result = ReviewResult(status=ReviewStatus.REJECTED, issues=issues)
        report = format_fallback_report(retry_count=3, last_result=last_result)
        assert len(report["last_issues"]) == 2
        assert report["last_issues"][0]["type"] == "forbidden_keyword"

    def test_report_contains_message(self) -> None:
        """Report contains a human-readable message."""
        last_result = ReviewResult(status=ReviewStatus.REJECTED)
        report = format_fallback_report(retry_count=3, last_result=last_result)
        assert "message" in report
        assert len(report["message"]) > 0
