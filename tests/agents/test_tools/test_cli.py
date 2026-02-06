"""Tests for L4 CLI entry point.

Tests the CLI parser and main entry point:
- create_parser: Argument parsing
- main: CLI execution and output
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# ============================================================================
# create_parser tests
# ============================================================================


def test_parser_build_context_args() -> None:
    """build-context 引数パース."""
    from src.agents.tools.cli import create_parser

    parser = create_parser()
    args = parser.parse_args(
        [
            "build-context",
            "--vault-root",
            "vault/work",
            "--episode",
            "010",
            "--sequence",
            "seq_01",
            "--chapter",
            "ch01",
            "--phase",
            "initial",
        ]
    )

    assert args.command == "build-context"
    assert args.vault_root == "vault/work"
    assert args.episode == "010"
    assert args.sequence == "seq_01"
    assert args.chapter == "ch01"
    assert args.phase == "initial"


def test_parser_build_context_required_args() -> None:
    """必須引数なしでエラー."""
    from src.agents.tools.cli import create_parser

    parser = create_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["build-context"])


def test_parser_format_context_args() -> None:
    """format-context 引数パース."""
    from src.agents.tools.cli import create_parser

    parser = create_parser()
    args = parser.parse_args(["format-context", "--input", "data.json"])

    assert args.command == "format-context"
    assert args.input == "data.json"


def test_parser_no_command() -> None:
    """コマンドなしで help."""
    from src.agents.tools.cli import create_parser

    parser = create_parser()
    args = parser.parse_args([])

    assert args.command is None


# ============================================================================
# main tests
# ============================================================================


def test_main_no_command_returns_1() -> None:
    """コマンドなし → return 1."""
    from src.agents.tools.cli import main

    exit_code = main([])
    assert exit_code == 1


def test_main_build_context_outputs_json(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:  # type: ignore[type-arg]
    """build-context → JSON 出力 (capsys で検証)."""
    from src.agents.tools.cli import main

    # tmp_path で最小 vault を用意
    vault_root = tmp_path / "vault"
    vault_root.mkdir()

    exit_code = main(
        [
            "build-context",
            "--vault-root",
            str(vault_root),
            "--episode",
            "010",
        ]
    )

    assert exit_code == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)

    assert data["success"] is True
    assert "prompt_dict" in data
    assert "forbidden_keywords" in data
    assert "foreshadow_instructions" in data


def test_main_format_context_from_file(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:  # type: ignore[type-arg]
    """format-context --input file → Markdown 出力."""
    from src.agents.tools.cli import main

    # tmp_path に JSON ファイルを作成
    json_file = tmp_path / "context.json"
    test_data = {
        "success": True,
        "errors": [],
        "warnings": [],
        "prompt_dict": {"plot_theme": "テーマ: 贖罪"},
        "forbidden_keywords": ["royal"],
        "foreshadow_instructions": [],
    }
    json_file.write_text(json.dumps(test_data, ensure_ascii=False), encoding="utf-8")

    exit_code = main(["format-context", "--input", str(json_file)])

    assert exit_code == 0

    captured = capsys.readouterr()
    markdown = captured.out

    assert "## 全体テーマ" in markdown
    assert "テーマ: 贖罪" in markdown
    assert "## 禁止キーワード" in markdown
    assert "- royal" in markdown


# ============================================================================
# check-review CLI tests
# ============================================================================


def test_parser_check_review_args() -> None:
    """check-review 引数パース."""
    from src.agents.tools.cli import create_parser

    parser = create_parser()
    args = parser.parse_args(
        ["check-review", "--draft", "draft.txt", "--keywords", "王族,血筋"]
    )

    assert args.command == "check-review"
    assert args.draft == "draft.txt"
    assert args.keywords == "王族,血筋"


def test_main_check_review_clean(
    tmp_path: Path, capsys: pytest.CaptureFixture,  # type: ignore[type-arg]
) -> None:
    """check-review with clean text → approved."""
    from src.agents.tools.cli import main

    draft_file = tmp_path / "draft.txt"
    draft_file.write_text("彼女は静かに微笑んだ。", encoding="utf-8")

    exit_code = main(
        ["check-review", "--draft", str(draft_file), "--keywords", "王族,血筋"]
    )
    assert exit_code == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["status"] == "approved"
    assert data["issues"] == []


def test_main_check_review_violation(
    tmp_path: Path, capsys: pytest.CaptureFixture,  # type: ignore[type-arg]
) -> None:
    """check-review with violation → rejected."""
    from src.agents.tools.cli import main

    draft_file = tmp_path / "draft.txt"
    draft_file.write_text("彼女は王族の末裔だった。", encoding="utf-8")

    exit_code = main(
        ["check-review", "--draft", str(draft_file), "--keywords", "王族,血筋"]
    )
    assert exit_code == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["status"] == "rejected"
    assert len(data["issues"]) == 1
    assert data["issues"][0]["type"] == "forbidden_keyword"
