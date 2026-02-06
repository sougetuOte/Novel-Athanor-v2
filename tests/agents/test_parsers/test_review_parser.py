"""Tests for Review Result Parser."""

import pytest

from src.agents.models.review_result import (
    IssueSeverity,
    ReviewIssueType,
    ReviewResult,
    ReviewStatus,
)
from src.agents.parsers.review_parser import parse_review_output


class TestParseReviewOutput:
    """Tests for parse_review_output."""

    def test_parse_approved_yaml(self) -> None:
        """Parse an approved review with no issues."""
        text = """
レビュー結果です。

```yaml
result: approved
issues: []
```

以上です。
"""
        result = parse_review_output(text)
        assert isinstance(result, ReviewResult)
        assert result.status == ReviewStatus.APPROVED
        assert result.issues == []

    def test_parse_rejected_with_issues(self) -> None:
        """Parse a rejected review with multiple issues."""
        text = """
以下の問題が見つかりました。

```yaml
result: rejected
issues:
  - type: forbidden_keyword
    severity: critical
    location: "第3段落"
    detail: "「王族」というキーワードが使用されています"
    suggestion: "「高貴な雰囲気」などの曖昧な表現に変更"
  - type: subtlety
    severity: warning
    location: "第5段落"
    detail: "伏線の暗示が明示的すぎます"
    suggestion: "より間接的な表現を使用"
```
"""
        result = parse_review_output(text)
        assert result.status == ReviewStatus.REJECTED
        assert len(result.issues) == 2
        assert result.issues[0].type == ReviewIssueType.FORBIDDEN_KEYWORD
        assert result.issues[0].severity == IssueSeverity.CRITICAL
        assert result.issues[0].location == "第3段落"
        assert "王族" in result.issues[0].detail
        assert result.issues[1].type == ReviewIssueType.SUBTLETY
        assert result.issues[1].severity == IssueSeverity.WARNING

    def test_parse_warning_status(self) -> None:
        """Parse a warning review."""
        text = """```yaml
result: warning
issues:
  - type: similarity
    severity: warning
    detail: "秘密情報との類似度が高い箇所があります"
```"""
        result = parse_review_output(text)
        assert result.status == ReviewStatus.WARNING
        assert len(result.issues) == 1
        assert result.issues[0].type == ReviewIssueType.SIMILARITY

    def test_parse_minimal_issue_fields(self) -> None:
        """Parse issue with only required fields (type, severity, detail)."""
        text = """```yaml
result: rejected
issues:
  - type: other
    severity: info
    detail: "軽微な問題です"
```"""
        result = parse_review_output(text)
        assert result.issues[0].location == ""
        assert result.issues[0].suggestion == ""
        assert result.issues[0].detail == "軽微な問題です"

    def test_parse_no_yaml_block_raises(self) -> None:
        """Raise ValueError when no YAML block is found."""
        text = "This is just plain text without any YAML."
        with pytest.raises(ValueError, match="YAML"):
            parse_review_output(text)

    def test_parse_invalid_yaml_raises(self) -> None:
        """Raise ValueError when YAML is malformed."""
        text = """```yaml
result: [invalid yaml
  { broken
```"""
        with pytest.raises(ValueError):
            parse_review_output(text)

    def test_parse_missing_result_field_raises(self) -> None:
        """Raise ValueError when result field is missing."""
        text = """```yaml
issues: []
```"""
        with pytest.raises(ValueError, match="result"):
            parse_review_output(text)

    def test_parse_unknown_status_raises(self) -> None:
        """Raise ValueError for unknown status values."""
        text = """```yaml
result: unknown_status
issues: []
```"""
        with pytest.raises(ValueError):
            parse_review_output(text)

    def test_parse_continuity_issue_type(self) -> None:
        """Parse continuity issue type."""
        text = """```yaml
result: warning
issues:
  - type: continuity
    severity: warning
    detail: "前のシーンとの整合性に問題"
```"""
        result = parse_review_output(text)
        assert result.issues[0].type == ReviewIssueType.CONTINUITY

    def test_has_critical_property(self) -> None:
        """Test ReviewResult.has_critical property via parsed result."""
        text = """```yaml
result: rejected
issues:
  - type: forbidden_keyword
    severity: critical
    detail: "禁止キーワード検出"
  - type: subtlety
    severity: warning
    detail: "暗示が強すぎる"
```"""
        result = parse_review_output(text)
        assert result.has_critical is True

    def test_no_critical_property(self) -> None:
        """Test has_critical is False when only warnings."""
        text = """```yaml
result: warning
issues:
  - type: subtlety
    severity: warning
    detail: "軽微な問題"
```"""
        result = parse_review_output(text)
        assert result.has_critical is False

    def test_parse_handles_extra_text_around_yaml(self) -> None:
        """Parser extracts YAML block from surrounding prose."""
        text = """
レビューを完了しました。結果は以下の通りです。

```yaml
result: approved
issues: []
```

問題は見つかりませんでした。このテキストは公開可能です。
"""
        result = parse_review_output(text)
        assert result.status == ReviewStatus.APPROVED
