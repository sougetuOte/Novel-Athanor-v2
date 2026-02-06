"""Tests for L4 context_tool module.

Tests the three pure functions:
- serialize_context_result: ContextBuildResult -> dict
- format_context_as_markdown: dict -> Markdown string
- run_build_context: CLI wrapper for ContextBuilder
"""

from __future__ import annotations

from pathlib import Path

from src.core.context.context_builder import ContextBuildResult
from src.core.context.filtered_context import FilteredContext
from src.core.context.foreshadow_instruction import (
    ForeshadowInstruction,
    ForeshadowInstructions,
    InstructionAction,
)
from src.core.context.hint_collector import HintCollection


# Test helper: 最小限の ContextBuildResult を作成
def make_build_result(
    plot_l1: str | None = "テーマ: 贖罪",
    characters: dict[str, str] | None = None,
    forbidden_keywords: list[str] | None = None,
    instructions: list[ForeshadowInstruction] | None = None,
    success: bool = True,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
) -> ContextBuildResult:
    """最小限の ContextBuildResult を作成する."""
    ctx = FilteredContext(
        plot_l1=plot_l1,
        characters=characters or {},
        scene_id="ep010/seq_01",
    )
    fs_instructions = ForeshadowInstructions()
    if instructions:
        for inst in instructions:
            fs_instructions.add_instruction(inst)
    return ContextBuildResult(
        context=ctx,
        visibility_context=None,
        foreshadow_instructions=fs_instructions,
        forbidden_keywords=forbidden_keywords or [],
        hints=HintCollection(),
        success=success,
        errors=errors or [],
        warnings=warnings or [],
    )


# ============================================================================
# serialize_context_result tests
# ============================================================================


def test_serialize_minimal() -> None:
    """最小限の ContextBuildResult → dict 変換."""
    from src.agents.tools.context_tool import serialize_context_result

    result = make_build_result()
    data = serialize_context_result(result)

    assert data["success"] is True
    assert data["errors"] == []
    assert data["warnings"] == []
    assert data["prompt_dict"]["plot_theme"] == "テーマ: 贖罪"
    assert data["forbidden_keywords"] == []
    assert data["foreshadow_instructions"] == []


def test_serialize_with_characters() -> None:
    """キャラクター情報ありの変換."""
    from src.agents.tools.context_tool import serialize_context_result

    result = make_build_result(
        characters={"Alice": "主人公、25歳", "Bob": "相棒、30歳"}
    )
    data = serialize_context_result(result)

    assert "character_Alice" in data["prompt_dict"]
    assert "character_Bob" in data["prompt_dict"]
    assert data["prompt_dict"]["character_Alice"] == "主人公、25歳"


def test_serialize_with_foreshadow_instructions() -> None:
    """伏線指示あり（PLANT + NONE → active のみ出力）."""
    from src.agents.tools.context_tool import serialize_context_result

    instructions = [
        ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.PLANT,
            allowed_expressions=["glint"],
            forbidden_expressions=["royal"],
            note="初登場",
            subtlety_target=7,
        ),
        ForeshadowInstruction(
            foreshadowing_id="FS-002",
            action=InstructionAction.NONE,
        ),
    ]
    result = make_build_result(instructions=instructions)
    data = serialize_context_result(result)

    # NONE は active に含まれないため、1件のみ
    assert len(data["foreshadow_instructions"]) == 1
    inst = data["foreshadow_instructions"][0]
    assert inst["foreshadowing_id"] == "FS-001"
    assert inst["action"] == "plant"
    assert inst["allowed_expressions"] == ["glint"]
    assert inst["forbidden_expressions"] == ["royal"]
    assert inst["note"] == "初登場"
    assert inst["subtlety_target"] == 7


def test_serialize_with_forbidden_keywords() -> None:
    """禁止キーワードあり."""
    from src.agents.tools.context_tool import serialize_context_result

    result = make_build_result(forbidden_keywords=["royal", "princess", "crown"])
    data = serialize_context_result(result)

    assert data["forbidden_keywords"] == ["royal", "princess", "crown"]


def test_serialize_warnings_merged() -> None:
    """result.warnings + context.warnings がマージされる."""
    from src.agents.tools.context_tool import serialize_context_result

    ctx = FilteredContext(plot_l1="Theme", scene_id="ep010/seq_01")
    ctx.add_warning("context warning 1")
    ctx.add_warning("context warning 2")

    result = ContextBuildResult(
        context=ctx,
        visibility_context=None,
        foreshadow_instructions=ForeshadowInstructions(),
        forbidden_keywords=[],
        hints=HintCollection(),
        success=True,
        errors=[],
        warnings=["result warning 1"],
    )

    data = serialize_context_result(result)

    # result.warnings + context.warnings がマージされる
    assert len(data["warnings"]) == 3
    assert "result warning 1" in data["warnings"]
    assert "context warning 1" in data["warnings"]
    assert "context warning 2" in data["warnings"]


def test_serialize_error_result() -> None:
    """success=False, errors あり."""
    from src.agents.tools.context_tool import serialize_context_result

    result = make_build_result(
        success=False,
        errors=["Error 1", "Error 2"],
    )
    data = serialize_context_result(result)

    assert data["success"] is False
    assert data["errors"] == ["Error 1", "Error 2"]


# ============================================================================
# format_context_as_markdown tests
# ============================================================================


def test_format_minimal() -> None:
    """最小限の dict → Markdown."""
    from src.agents.tools.context_tool import format_context_as_markdown

    data = {
        "success": True,
        "errors": [],
        "warnings": [],
        "prompt_dict": {"plot_theme": "テーマ: 贖罪"},
        "forbidden_keywords": [],
        "foreshadow_instructions": [],
    }

    markdown = format_context_as_markdown(data)

    assert "## 全体テーマ" in markdown
    assert "テーマ: 贖罪" in markdown


def test_format_with_characters() -> None:
    """キャラクター情報の Markdown 出力."""
    from src.agents.tools.context_tool import format_context_as_markdown

    data = {
        "success": True,
        "errors": [],
        "warnings": [],
        "prompt_dict": {
            "plot_theme": "Theme",
            "character_Alice": "主人公、25歳",
            "character_Bob": "相棒、30歳",
        },
        "forbidden_keywords": [],
        "foreshadow_instructions": [],
    }

    markdown = format_context_as_markdown(data)

    assert "## キャラクター" in markdown
    assert "### Alice" in markdown
    assert "主人公、25歳" in markdown
    assert "### Bob" in markdown
    assert "相棒、30歳" in markdown


def test_format_with_world_settings() -> None:
    """世界観設定の出力."""
    from src.agents.tools.context_tool import format_context_as_markdown

    data = {
        "success": True,
        "errors": [],
        "warnings": [],
        "prompt_dict": {
            "world_Magic": "魔法は存在する",
            "world_History": "1000年前の戦争",
        },
        "forbidden_keywords": [],
        "foreshadow_instructions": [],
    }

    markdown = format_context_as_markdown(data)

    assert "## 世界観設定" in markdown
    assert "### Magic" in markdown
    assert "魔法は存在する" in markdown
    assert "### History" in markdown
    assert "1000年前の戦争" in markdown


def test_format_with_foreshadow_instructions() -> None:
    """伏線指示の出力."""
    from src.agents.tools.context_tool import format_context_as_markdown

    data = {
        "success": True,
        "errors": [],
        "warnings": [],
        "prompt_dict": {},
        "forbidden_keywords": [],
        "foreshadow_instructions": [
            {
                "foreshadowing_id": "FS-001",
                "action": "plant",
                "allowed_expressions": ["glint"],
                "forbidden_expressions": ["royal"],
                "note": "初登場",
                "subtlety_target": 7,
            }
        ],
    }

    markdown = format_context_as_markdown(data)

    assert "## 伏線指示" in markdown
    assert "FS-001: plant" in markdown
    assert "初登場" in markdown


def test_format_with_forbidden_keywords() -> None:
    """禁止キーワードの出力."""
    from src.agents.tools.context_tool import format_context_as_markdown

    data = {
        "success": True,
        "errors": [],
        "warnings": [],
        "prompt_dict": {},
        "forbidden_keywords": ["royal", "princess", "crown"],
        "foreshadow_instructions": [],
    }

    markdown = format_context_as_markdown(data)

    assert "## 禁止キーワード" in markdown
    assert "- royal" in markdown
    assert "- princess" in markdown
    assert "- crown" in markdown


def test_format_empty() -> None:
    """空の dict → 空文字列."""
    from src.agents.tools.context_tool import format_context_as_markdown

    data = {
        "success": True,
        "errors": [],
        "warnings": [],
        "prompt_dict": {},
        "forbidden_keywords": [],
        "foreshadow_instructions": [],
    }

    markdown = format_context_as_markdown(data)

    # 空の場合は何も出力されない
    assert markdown == ""


# ============================================================================
# run_build_context tests (Integration)
# ============================================================================


def test_run_build_context_minimal_vault(tmp_path: Path) -> None:
    """tmp_path に最小限の vault を作成、build_context が成功すること."""
    from src.agents.tools.context_tool import run_build_context

    # 最小限のディレクトリ構造を作成（空の vault でも success=True になる）
    vault_root = tmp_path / "vault"
    vault_root.mkdir()

    data = run_build_context(
        vault_root=str(vault_root),
        episode="010",
        sequence="seq_01",
    )

    assert data["success"] is True
    assert isinstance(data["errors"], list)
    assert isinstance(data["warnings"], list)
    assert isinstance(data["prompt_dict"], dict)
    assert isinstance(data["forbidden_keywords"], list)
    assert isinstance(data["foreshadow_instructions"], list)
