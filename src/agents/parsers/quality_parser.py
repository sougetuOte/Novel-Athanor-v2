"""Quality result parser.

This module parses LLM output text containing a YAML block into
a structured QualityResult model.

Expected LLM output format:
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
    assessment: good | excellent | acceptable | needs_improvement
    issues:
      - category: "pacing"
        severity: critical | warning | info
        location: "optional location"
        description: "description"
        suggestion: "optional suggestion"
    recommendations:
      - "recommendation text"
    ```
"""

from __future__ import annotations

import re
from typing import Any

import yaml

from src.agents.models.quality_result import (
    QualityAssessment,
    QualityIssue,
    QualityResult,
    QualityScore,
)
from src.agents.models.review_result import IssueSeverity


def parse_quality_output(text: str) -> QualityResult:
    """Parse LLM quality output text into a QualityResult.

    Extracts the first YAML code block from the text and parses it
    into a structured QualityResult.

    Args:
        text: Raw LLM output containing a YAML code block.

    Returns:
        Parsed QualityResult.

    Raises:
        ValueError: If no YAML block is found, YAML is malformed,
                    or required fields are missing/invalid.
    """
    yaml_content = _extract_yaml_block(text)
    data = _parse_yaml(yaml_content)
    return _build_quality_result(data)


def _extract_yaml_block(text: str) -> str:
    """Extract YAML content from a fenced code block."""
    pattern = r"```yaml\s*\n(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match is None:
        msg = "No YAML code block found in the output."
        raise ValueError(msg)
    return match.group(1)


def _parse_yaml(content: str) -> dict[str, Any]:
    """Parse YAML string into a dictionary."""
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        msg = f"Failed to parse YAML: {e}"
        raise ValueError(msg) from e

    if not isinstance(data, dict):
        msg = f"Expected YAML dict, got {type(data).__name__}"
        raise ValueError(msg)

    return data


def _build_quality_result(data: dict[str, Any]) -> QualityResult:
    """Build QualityResult from parsed YAML data."""
    if "scores" not in data:
        msg = "Missing required field: 'scores'"
        raise ValueError(msg)
    if "assessment" not in data:
        msg = "Missing required field: 'assessment'"
        raise ValueError(msg)

    scores = QualityScore(**data["scores"])
    assessment = QualityAssessment(data["assessment"])

    raw_issues = data.get("issues") or []
    issues = [_build_quality_issue(item) for item in raw_issues]

    recommendations = data.get("recommendations") or []

    return QualityResult(
        scores=scores,
        assessment=assessment,
        issues=issues,
        recommendations=recommendations,
    )


def _build_quality_issue(item: dict[str, Any]) -> QualityIssue:
    """Build a QualityIssue from a YAML issue dict."""
    return QualityIssue(
        category=item["category"],
        severity=IssueSeverity(item["severity"]),
        location=item.get("location", ""),
        description=item["description"],
        suggestion=item.get("suggestion", ""),
    )
