"""Review result models for L4 reviewer agent."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ReviewIssueType(str, Enum):
    """レビュー問題のタイプ."""

    FORBIDDEN_KEYWORD = "forbidden_keyword"
    SIMILARITY = "similarity"
    SUBTLETY = "subtlety"
    CONTINUITY = "continuity"
    OTHER = "other"


class IssueSeverity(str, Enum):
    """問題の重要度."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class ReviewStatus(str, Enum):
    """レビューステータス."""

    APPROVED = "approved"
    WARNING = "warning"
    REJECTED = "rejected"


class ReviewIssue(BaseModel):
    """レビュー問題の詳細.

    Attributes:
        type: 問題のタイプ
        severity: 重要度
        location: 問題箇所（デフォルト: 空文字）
        detail: 問題の詳細説明
        suggestion: 修正提案（デフォルト: 空文字）
    """

    type: ReviewIssueType
    severity: IssueSeverity
    location: str = ""
    detail: str
    suggestion: str = ""


class ReviewResult(BaseModel):
    """レビュー結果.

    Attributes:
        status: レビューステータス
        issues: 問題リスト
    """

    status: ReviewStatus
    issues: list[ReviewIssue] = Field(default_factory=list)

    @property
    def has_critical(self) -> bool:
        """Critical な問題が含まれているか.

        Returns:
            True if any issue has CRITICAL severity.
        """
        return any(issue.severity == IssueSeverity.CRITICAL for issue in self.issues)

    @property
    def issue_count(self) -> int:
        """問題数.

        Returns:
            Total number of issues.
        """
        return len(self.issues)
