"""Review result parser.

This module parses LLM output text containing a YAML block into
a structured ReviewResult model.

Expected LLM output format:
    ```yaml
    result: approved | warning | rejected
    issues:
      - type: forbidden_keyword | similarity | subtlety | continuity | other
        severity: critical | warning | info
        location: "optional location"
        detail: "description of the issue"
        suggestion: "optional fix suggestion"
    ```
"""

from __future__ import annotations

import re
from typing import Any

import yaml

from src.agents.models.review_result import (
    IssueSeverity,
    ReviewIssue,
    ReviewIssueType,
    ReviewResult,
    ReviewStatus,
)


def parse_review_output(text: str) -> ReviewResult:
    """Parse LLM review output text into a ReviewResult.

    Extracts the first YAML code block from the text and parses it
    into a structured ReviewResult.

    Args:
        text: Raw LLM output containing a YAML code block.

    Returns:
        Parsed ReviewResult.

    Raises:
        ValueError: If no YAML block is found, YAML is malformed,
                    or required fields are missing.
    """
    yaml_content = _extract_yaml_block(text)
    data = _parse_yaml(yaml_content)
    return _build_review_result(data)


def _extract_yaml_block(text: str) -> str:
    """Extract YAML content from a fenced code block.

    Args:
        text: Text potentially containing a ```yaml ... ``` block.

    Returns:
        The YAML content string.

    Raises:
        ValueError: If no YAML block is found.
    """
    pattern = r"```yaml\s*\n(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match is None:
        msg = "No YAML code block found in the output."
        raise ValueError(msg)
    return match.group(1)


def _parse_yaml(content: str) -> dict[str, Any]:
    """Parse YAML string into a dictionary.

    Args:
        content: YAML string.

    Returns:
        Parsed dictionary.

    Raises:
        ValueError: If YAML parsing fails or result is not a dict.
    """
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        msg = f"Failed to parse YAML: {e}"
        raise ValueError(msg) from e

    if not isinstance(data, dict):
        msg = f"Expected YAML dict, got {type(data).__name__}"
        raise ValueError(msg)

    return data


def _build_review_result(data: dict[str, Any]) -> ReviewResult:
    """Build ReviewResult from parsed YAML data.

    Args:
        data: Parsed YAML dictionary.

    Returns:
        ReviewResult instance.

    Raises:
        ValueError: If required fields are missing or invalid.
    """
    if "result" not in data:
        msg = "Missing required field: 'result'"
        raise ValueError(msg)

    status = ReviewStatus(data["result"])
    raw_issues = data.get("issues") or []

    issues = [_build_review_issue(item) for item in raw_issues]

    return ReviewResult(status=status, issues=issues)


def _build_review_issue(item: dict[str, Any]) -> ReviewIssue:
    """Build a ReviewIssue from a YAML issue dict.

    Args:
        item: Dictionary with issue fields.

    Returns:
        ReviewIssue instance.
    """
    return ReviewIssue(
        type=ReviewIssueType(item["type"]),
        severity=IssueSeverity(item["severity"]),
        location=item.get("location", ""),
        detail=item["detail"],
        suggestion=item.get("suggestion", ""),
    )
