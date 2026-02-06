"""Algorithmic review tool.

This module provides:
1. Algorithmic review: forbidden keyword detection using L2 expression_filter.
2. Human Fallback: retry count management and fallback report generation.

Used by the Reviewer agent as a pre-check before LLM-based review.
"""

from __future__ import annotations

from typing import Any

from src.agents.config import MAX_REVIEW_RETRIES
from src.agents.models.review_result import (
    IssueSeverity,
    ReviewIssue,
    ReviewIssueType,
    ReviewResult,
    ReviewStatus,
)
from src.core.services.expression_filter import check_forbidden_keywords


def run_algorithmic_review(
    draft_text: str,
    forbidden_keywords: list[str],
) -> ReviewResult:
    """Run algorithmic review on draft text.

    Checks for forbidden keyword violations using L2 expression_filter.

    Args:
        draft_text: The draft text to review.
        forbidden_keywords: List of forbidden keywords.

    Returns:
        ReviewResult with status and issues.
    """
    violations = check_forbidden_keywords(draft_text, forbidden_keywords)

    if not violations:
        return ReviewResult(status=ReviewStatus.APPROVED)

    issues = [
        ReviewIssue(
            type=ReviewIssueType.FORBIDDEN_KEYWORD,
            severity=IssueSeverity.CRITICAL,
            location=v.context,
            detail=f"禁止キーワード '{v.keyword}' が検出されました（{len(v.positions)}箇所）",
            suggestion=f"'{v.keyword}' を使わない表現に変更してください",
        )
        for v in violations
    ]

    return ReviewResult(status=ReviewStatus.REJECTED, issues=issues)


def should_fallback(
    retry_count: int,
    max_retries: int = MAX_REVIEW_RETRIES,
) -> bool:
    """Determine if review should fallback to human.

    Args:
        retry_count: Number of review retries so far.
        max_retries: Maximum retries before fallback.

    Returns:
        True if human fallback should be triggered.
    """
    return retry_count >= max_retries


def format_fallback_report(
    retry_count: int,
    last_result: ReviewResult,
) -> dict[str, Any]:
    """Format a human fallback report.

    Args:
        retry_count: Number of retries performed.
        last_result: The last review result before fallback.

    Returns:
        Report dictionary with status, message, retry count, and last issues.
    """
    return {
        "status": "human_fallback",
        "message": f"自動修正の上限（{retry_count}回）に達しました。手動での確認が必要です。",
        "retry_count": retry_count,
        "last_issues": [
            issue.model_dump() for issue in last_result.issues
        ],
    }
