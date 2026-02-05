"""Tests for ForeshadowInstruction data classes."""

import pytest

from src.core.context.foreshadow_instruction import (
    ForeshadowInstruction,
    ForeshadowInstructions,
    InstructionAction,
)


class TestInstructionAction:
    """Test InstructionAction enum."""

    def test_plant_exists(self):
        """PLANT アクションが存在する."""
        assert InstructionAction.PLANT.value == "plant"

    def test_reinforce_exists(self):
        """REINFORCE アクションが存在する."""
        assert InstructionAction.REINFORCE.value == "reinforce"

    def test_hint_exists(self):
        """HINT アクションが存在する."""
        assert InstructionAction.HINT.value == "hint"

    def test_none_exists(self):
        """NONE アクションが存在する."""
        assert InstructionAction.NONE.value == "none"

    def test_all_actions(self):
        """全アクションが定義されている."""
        actions = list(InstructionAction)
        assert len(actions) == 4


class TestForeshadowInstructionCreation:
    """Test ForeshadowInstruction instance creation."""

    def test_create_minimal(self):
        """最小限のパラメータで生成できる."""
        inst = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.PLANT,
        )
        assert inst.foreshadowing_id == "FS-001"
        assert inst.action == InstructionAction.PLANT
        assert inst.allowed_expressions == []
        assert inst.forbidden_expressions == []
        assert inst.note is None
        assert inst.subtlety_target == 5

    def test_create_with_all_fields(self):
        """全フィールドを指定して生成できる."""
        inst = ForeshadowInstruction(
            foreshadowing_id="FS-002",
            action=InstructionAction.REINFORCE,
            allowed_expressions=["familiar light", "noble bearing"],
            forbidden_expressions=["royal blood", "princess"],
            note="Subtly hint at the character's hidden identity",
            subtlety_target=7,
        )
        assert inst.foreshadowing_id == "FS-002"
        assert inst.action == InstructionAction.REINFORCE
        assert len(inst.allowed_expressions) == 2
        assert len(inst.forbidden_expressions) == 2
        assert inst.note is not None
        assert inst.subtlety_target == 7


class TestForeshadowInstructionValidation:
    """Test ForeshadowInstruction validation."""

    def test_subtlety_target_valid_range_1(self):
        """subtlety_target=1 は有効."""
        inst = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.PLANT,
            subtlety_target=1,
        )
        assert inst.subtlety_target == 1

    def test_subtlety_target_valid_range_10(self):
        """subtlety_target=10 は有効."""
        inst = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.PLANT,
            subtlety_target=10,
        )
        assert inst.subtlety_target == 10

    def test_subtlety_target_0_raises_error(self):
        """subtlety_target=0 は ValueError."""
        with pytest.raises(ValueError, match="subtlety_target must be 1-10"):
            ForeshadowInstruction(
                foreshadowing_id="FS-001",
                action=InstructionAction.PLANT,
                subtlety_target=0,
            )

    def test_subtlety_target_11_raises_error(self):
        """subtlety_target=11 は ValueError."""
        with pytest.raises(ValueError, match="subtlety_target must be 1-10"):
            ForeshadowInstruction(
                foreshadowing_id="FS-001",
                action=InstructionAction.PLANT,
                subtlety_target=11,
            )


class TestForeshadowInstructionMethods:
    """Test ForeshadowInstruction methods."""

    def test_should_act_true_for_plant(self):
        """PLANT の場合 should_act() は True."""
        inst = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.PLANT,
        )
        assert inst.should_act() is True

    def test_should_act_true_for_reinforce(self):
        """REINFORCE の場合 should_act() は True."""
        inst = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.REINFORCE,
        )
        assert inst.should_act() is True

    def test_should_act_true_for_hint(self):
        """HINT の場合 should_act() は True."""
        inst = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.HINT,
        )
        assert inst.should_act() is True

    def test_should_act_false_for_none(self):
        """NONE の場合 should_act() は False."""
        inst = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.NONE,
        )
        assert inst.should_act() is False

    def test_is_planting_true(self):
        """PLANT の場合 is_planting() は True."""
        inst = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.PLANT,
        )
        assert inst.is_planting() is True

    def test_is_planting_false_for_reinforce(self):
        """REINFORCE の場合 is_planting() は False."""
        inst = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.REINFORCE,
        )
        assert inst.is_planting() is False


class TestForeshadowInstructionsCreation:
    """Test ForeshadowInstructions container creation."""

    def test_create_empty(self):
        """空のコンテナを生成できる."""
        container = ForeshadowInstructions()
        assert container.instructions == []
        assert container.global_forbidden_keywords == []

    def test_create_with_instructions(self):
        """指示リストを持つコンテナを生成できる."""
        inst1 = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.PLANT,
        )
        inst2 = ForeshadowInstruction(
            foreshadowing_id="FS-002",
            action=InstructionAction.HINT,
        )
        container = ForeshadowInstructions(
            instructions=[inst1, inst2],
            global_forbidden_keywords=["secret", "hidden"],
        )
        assert len(container.instructions) == 2
        assert len(container.global_forbidden_keywords) == 2


class TestForeshadowInstructionsGetAllForbidden:
    """Test get_all_forbidden() method."""

    def test_get_all_forbidden_empty(self):
        """空コンテナは空リストを返す."""
        container = ForeshadowInstructions()
        assert container.get_all_forbidden() == []

    def test_get_all_forbidden_global_only(self):
        """グローバル禁止キーワードのみ."""
        container = ForeshadowInstructions(
            global_forbidden_keywords=["secret", "hidden"]
        )
        forbidden = container.get_all_forbidden()
        assert "secret" in forbidden
        assert "hidden" in forbidden

    def test_get_all_forbidden_instructions_only(self):
        """個別指示の禁止キーワードのみ."""
        inst = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.PLANT,
            forbidden_expressions=["royal", "blood"],
        )
        container = ForeshadowInstructions(instructions=[inst])
        forbidden = container.get_all_forbidden()
        assert "royal" in forbidden
        assert "blood" in forbidden

    def test_get_all_forbidden_combined(self):
        """グローバルと個別の両方を統合."""
        inst = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.PLANT,
            forbidden_expressions=["royal"],
        )
        container = ForeshadowInstructions(
            instructions=[inst],
            global_forbidden_keywords=["secret"],
        )
        forbidden = container.get_all_forbidden()
        assert "royal" in forbidden
        assert "secret" in forbidden

    def test_get_all_forbidden_deduplicates(self):
        """重複キーワードは除去される."""
        inst = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.PLANT,
            forbidden_expressions=["secret", "royal"],
        )
        container = ForeshadowInstructions(
            instructions=[inst],
            global_forbidden_keywords=["secret", "hidden"],  # "secret" が重複
        )
        forbidden = container.get_all_forbidden()
        # "secret" は1回のみ
        assert forbidden.count("secret") == 1


class TestForeshadowInstructionsGetActive:
    """Test get_active_instructions() method."""

    def test_get_active_empty(self):
        """空コンテナは空リストを返す."""
        container = ForeshadowInstructions()
        assert container.get_active_instructions() == []

    def test_get_active_filters_none_action(self):
        """NONE アクションは除外される."""
        inst_active = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.PLANT,
        )
        inst_inactive = ForeshadowInstruction(
            foreshadowing_id="FS-002",
            action=InstructionAction.NONE,
        )
        container = ForeshadowInstructions(
            instructions=[inst_active, inst_inactive]
        )
        active = container.get_active_instructions()
        assert len(active) == 1
        assert active[0].foreshadowing_id == "FS-001"


class TestForeshadowInstructionsHelpers:
    """Test helper methods."""

    def test_add_instruction(self):
        """指示を追加できる."""
        container = ForeshadowInstructions()
        inst = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.PLANT,
        )
        container.add_instruction(inst)
        assert len(container.instructions) == 1

    def test_add_global_forbidden(self):
        """グローバル禁止キーワードを追加できる."""
        container = ForeshadowInstructions()
        container.add_global_forbidden("secret")
        container.add_global_forbidden("hidden")
        assert "secret" in container.global_forbidden_keywords
        assert "hidden" in container.global_forbidden_keywords

    def test_add_global_forbidden_no_duplicate(self):
        """重複するグローバル禁止キーワードは追加されない."""
        container = ForeshadowInstructions()
        container.add_global_forbidden("secret")
        container.add_global_forbidden("secret")  # 重複
        assert container.global_forbidden_keywords.count("secret") == 1

    def test_count_by_action(self):
        """アクション別カウントを取得できる."""
        inst1 = ForeshadowInstruction(
            foreshadowing_id="FS-001", action=InstructionAction.PLANT
        )
        inst2 = ForeshadowInstruction(
            foreshadowing_id="FS-002", action=InstructionAction.PLANT
        )
        inst3 = ForeshadowInstruction(
            foreshadowing_id="FS-003", action=InstructionAction.HINT
        )
        inst4 = ForeshadowInstruction(
            foreshadowing_id="FS-004", action=InstructionAction.NONE
        )
        container = ForeshadowInstructions(
            instructions=[inst1, inst2, inst3, inst4]
        )
        counts = container.count_by_action()
        assert counts[InstructionAction.PLANT] == 2
        assert counts[InstructionAction.HINT] == 1
        assert counts[InstructionAction.NONE] == 1
        assert InstructionAction.REINFORCE not in counts
