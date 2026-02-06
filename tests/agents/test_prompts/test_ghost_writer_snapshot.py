"""Snapshot tests for Ghost Writer formatter.

This module provides snapshot tests to ensure that format_writing_context()
output remains stable across changes.
"""

import pathlib

from src.agents.models.scene_requirements import SceneRequirements
from src.agents.prompts.ghost_writer import format_writing_context
from src.core.context import (
    ContextBuildResult,
    FilteredContext,
    ForeshadowInstruction,
    ForeshadowInstructions,
    InstructionAction,
)
from src.core.context.hint_collector import HintCollection

SNAPSHOT_DIR = pathlib.Path(__file__).parent / "snapshots"


def _create_full_context() -> tuple[ContextBuildResult, SceneRequirements]:
    """Create a ContextBuildResult with all fields populated.

    Returns:
        Tuple of (ContextBuildResult, SceneRequirements) with full data.
    """
    ctx = FilteredContext(
        plot_l1="テーマ：贖罪と再生。主人公は過去の過ちに向き合い成長する。",
        plot_l2="第3章：対立の激化。主人公とライバルの関係が決定的に変化する。",
        plot_l3="シーン5：酒場での再会。3年ぶりに故郷に戻った主人公が幼馴染と再会する。",
        summary_l1="冒険の始まりから現在まで。主人公は数々の試練を乗り越えてきた。",
        summary_l2="第3章の前半：ライバルとの遭遇、仲間の裏切り。",
        summary_l3="前のシーン：主人公は長い旅を経て故郷の町に到着した。",
        characters={
            "アリス": "主人公。25歳女性。元騎士団員。正義感が強いが過去のトラウマを抱える。",
            "ボブ": "幼馴染。40歳男性。酒場の主人。温厚だが芯は強い。",
        },
        world_settings={
            "魔法体系": "ルールベースの魔法。詠唱＋触媒が必要。",
            "地理": "北方大陸の港町。冬は厳しく、漁業が盛ん。",
        },
        style_guide="文体：硬質な三人称。短文を多用。会話は関西弁を避ける。",
        scene_id="ep010/seq01",
        current_phase="起",
    )

    instructions = ForeshadowInstructions()
    instructions.add_instruction(
        ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.PLANT,
            note="アリスの右手の傷を自然に描写。後の章で重要な伏線となる。",
        )
    )
    instructions.add_instruction(
        ForeshadowInstruction(
            foreshadowing_id="FS-002",
            action=InstructionAction.REINFORCE,
            note="ボブの酒場にある古い剣について触れること。",
        )
    )

    result_obj = ContextBuildResult(
        context=ctx,
        visibility_context=None,
        foreshadow_instructions=instructions,
        forbidden_keywords=["王族の血", "プリンセス", "選ばれし者"],
        hints=HintCollection(),
    )

    requirements = SceneRequirements(
        episode_id="ep010",
        sequence_id="seq01",
        chapter_id="ch03",
        current_phase="起",
        word_count=4000,
        pov="三人称限定視点",
        mood="懐かしさと緊張感の入り混じった雰囲気",
        special_instructions="再会シーンでは感情描写を丁寧に。ボブの表情変化に注目。",
    )

    return result_obj, requirements


def _create_minimal_context() -> tuple[ContextBuildResult, SceneRequirements]:
    """Create a ContextBuildResult with minimal fields.

    Returns:
        Tuple of (ContextBuildResult, SceneRequirements) with minimal data.
    """
    ctx = FilteredContext(plot_l1="テーマ：成長物語")
    result_obj = ContextBuildResult(
        context=ctx,
        visibility_context=None,
        foreshadow_instructions=ForeshadowInstructions(),
        forbidden_keywords=[],
        hints=HintCollection(),
    )
    requirements = SceneRequirements(episode_id="ep001")
    return result_obj, requirements


class TestGhostWriterSnapshot:
    """Snapshot tests for Ghost Writer formatter."""

    def test_full_output_matches_snapshot(self) -> None:
        """Test that full context output matches the stored snapshot."""
        result, requirements = _create_full_context()
        output = format_writing_context(result, requirements)

        snapshot_path = SNAPSHOT_DIR / "ghost_writer_full.txt"

        if not snapshot_path.exists():
            # Create snapshot on first run
            snapshot_path.write_text(output, encoding="utf-8")
            msg = (
                f"Snapshot created at {snapshot_path}. "
                "Run test again to verify."
            )
            raise AssertionError(msg)

        expected = snapshot_path.read_text(encoding="utf-8")
        assert (
            output == expected
        ), f"Output does not match snapshot at {snapshot_path}"

    def test_minimal_output_matches_snapshot(self) -> None:
        """Test that minimal context output matches the stored snapshot."""
        result, requirements = _create_minimal_context()
        output = format_writing_context(result, requirements)

        snapshot_path = SNAPSHOT_DIR / "ghost_writer_minimal.txt"

        if not snapshot_path.exists():
            # Create snapshot on first run
            snapshot_path.write_text(output, encoding="utf-8")
            msg = (
                f"Snapshot created at {snapshot_path}. "
                "Run test again to verify."
            )
            raise AssertionError(msg)

        expected = snapshot_path.read_text(encoding="utf-8")
        assert (
            output == expected
        ), f"Output does not match snapshot at {snapshot_path}"
