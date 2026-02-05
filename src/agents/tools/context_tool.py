"""Context tool for L4 agent pipeline.

L3 ContextBuilder を CLI 経由で呼び出すためのツール。
build-context: コンテキスト構築 → JSON出力
format-context: JSON → Markdown プロンプトテキスト変換
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.core.context.context_builder import ContextBuilder, ContextBuildResult
from src.core.context.scene_identifier import SceneIdentifier


def serialize_context_result(result: ContextBuildResult) -> dict[str, Any]:
    """ContextBuildResult を JSON シリアライズ可能な dict に変換する.

    Args:
        result: L3 ContextBuildResult

    Returns:
        JSON シリアライズ可能な dict。以下のキーを含む:
        - success: bool
        - errors: list[str]
        - warnings: list[str] (context.warnings もマージ)
        - prompt_dict: dict[str, str] (FilteredContext.to_prompt_dict())
        - forbidden_keywords: list[str]
        - foreshadow_instructions: list[dict] (active のみ)
    """
    # FilteredContext.to_prompt_dict() を使用
    prompt_dict = result.context.to_prompt_dict()

    # warnings をマージ
    all_warnings = list(result.warnings)
    if result.context.warnings:
        all_warnings.extend(result.context.warnings)

    # foreshadow_instructions を active のみシリアライズ
    instructions_data = []
    for inst in result.foreshadow_instructions.get_active_instructions():
        instructions_data.append(
            {
                "foreshadowing_id": inst.foreshadowing_id,
                "action": inst.action.value,
                "allowed_expressions": inst.allowed_expressions,
                "forbidden_expressions": inst.forbidden_expressions,
                "note": inst.note,
                "subtlety_target": inst.subtlety_target,
            }
        )

    return {
        "success": result.success,
        "errors": result.errors,
        "warnings": all_warnings,
        "prompt_dict": prompt_dict,
        "forbidden_keywords": result.forbidden_keywords,
        "foreshadow_instructions": instructions_data,
    }


def format_context_as_markdown(context_data: dict[str, Any]) -> str:
    """シリアライズ済みコンテキスト dict を Markdown プロンプトテキストに変換する.

    Args:
        context_data: serialize_context_result() の出力 dict

    Returns:
        Markdown フォーマットのプロンプトテキスト
    """
    sections: list[str] = []
    prompt_dict = context_data.get("prompt_dict", {})

    # プロット
    for key, label in [
        ("plot_theme", "全体テーマ"),
        ("plot_chapter", "章プロット"),
        ("plot_scene", "シーンプロット"),
    ]:
        if key in prompt_dict:
            sections.append(f"## {label}\n{prompt_dict[key]}")

    # サマリ
    for key, label in [
        ("summary_overall", "全体サマリ"),
        ("summary_chapter", "章サマリ"),
        ("summary_recent", "直近サマリ"),
    ]:
        if key in prompt_dict:
            sections.append(f"## {label}\n{prompt_dict[key]}")

    # キャラクター
    char_items = [(k, v) for k, v in prompt_dict.items() if k.startswith("character_")]
    if char_items:
        char_lines = []
        for k, v in char_items:
            name = k.removeprefix("character_")
            char_lines.append(f"### {name}\n{v}")
        sections.append("## キャラクター\n\n" + "\n\n".join(char_lines))

    # 世界観設定
    world_items = [(k, v) for k, v in prompt_dict.items() if k.startswith("world_")]
    if world_items:
        world_lines = []
        for k, v in world_items:
            name = k.removeprefix("world_")
            world_lines.append(f"### {name}\n{v}")
        sections.append("## 世界観設定\n\n" + "\n\n".join(world_lines))

    # スタイルガイド
    if "style_guide" in prompt_dict:
        sections.append(f"## スタイルガイド\n{prompt_dict['style_guide']}")

    # 伏線指示
    instructions = context_data.get("foreshadow_instructions", [])
    if instructions:
        instr_lines = []
        for instr in instructions:
            line = f"- {instr['foreshadowing_id']}: {instr['action']}"
            if instr.get("note"):
                line += f" — {instr['note']}"
            instr_lines.append(line)
        sections.append("## 伏線指示\n" + "\n".join(instr_lines))

    # 禁止キーワード
    forbidden = context_data.get("forbidden_keywords", [])
    if forbidden:
        kw_lines = [f"- {kw}" for kw in forbidden]
        sections.append("## 禁止キーワード\n" + "\n".join(kw_lines))

    return "\n\n---\n\n".join(sections)


def run_build_context(
    vault_root: str,
    episode: str,
    sequence: str | None = None,
    chapter: str | None = None,
    phase: str | None = None,
) -> dict[str, Any]:
    """コンテキストを構築し、シリアライズ済み dict を返す.

    Args:
        vault_root: vault ルートパス
        episode: エピソード ID
        sequence: シーケンス ID (optional)
        chapter: チャプター ID (optional)
        phase: フェーズ (optional)

    Returns:
        serialize_context_result() の出力
    """
    scene = SceneIdentifier(
        episode_id=episode,
        sequence_id=sequence,
        chapter_id=chapter,
        current_phase=phase,
    )
    builder = ContextBuilder(vault_root=Path(vault_root))
    result = builder.build_context(scene)
    return serialize_context_result(result)
