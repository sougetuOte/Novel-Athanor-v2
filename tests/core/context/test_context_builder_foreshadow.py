"""Tests for ContextBuilder foreshadow instruction methods (L3-7-1c)."""


from src.core.context.foreshadow_instruction import (
    ForeshadowInstruction,
    ForeshadowInstructions,
    InstructionAction,
)


class TestGetForeshadowInstructions:
    """Tests for get_foreshadow_instructions()."""

    def test_returns_instructions(self, builder, scene):
        """T12: get_foreshadow_instructions returns ForeshadowInstructions."""
        result = builder.get_foreshadow_instructions(scene)
        assert isinstance(result, ForeshadowInstructions)

    def test_without_repository_returns_empty(self, builder, scene):
        """T15: Without repository, returns empty instructions."""
        result = builder.get_foreshadow_instructions(scene)
        assert len(result.instructions) == 0

    def test_with_cache(self, builder, scene):
        """T13: Second call uses cache."""
        result1 = builder.get_foreshadow_instructions(scene)
        result2 = builder.get_foreshadow_instructions(scene)
        assert result1 is result2  # Same object from cache

    def test_cache_bypass(self, builder, scene):
        """T14: use_cache=False bypasses cache."""
        result1 = builder.get_foreshadow_instructions(scene)
        result2 = builder.get_foreshadow_instructions(scene, use_cache=False)
        # Should be different objects (regenerated)
        assert result1 is not result2


class TestGetForeshadowInstructionsAsPrompt:
    """Tests for get_foreshadow_instructions_as_prompt()."""

    def test_returns_string(self, builder, scene):
        """T16: Returns formatted string."""
        result = builder.get_foreshadow_instructions_as_prompt(scene)
        assert isinstance(result, str)

    def test_empty_when_no_instructions(self, builder, scene):
        """T16b: Returns empty string when no instructions."""
        result = builder.get_foreshadow_instructions_as_prompt(scene)
        assert result == ""


class TestFormatInstructionsForPrompt:
    """Tests for _format_instructions_for_prompt()."""

    def test_format_plant(self, builder):
        """T17: PLANT action formats correctly."""
        instructions = ForeshadowInstructions()
        instructions.add_instruction(ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.PLANT,
            allowed_expressions=["glint in her eyes"],
            note="伏線の初回設置。",
        ))
        result = builder._format_instructions_for_prompt(instructions)
        assert "FS-001" in result
        assert "設置" in result or "PLANT" in result or "植え付け" in result

    def test_format_reinforce(self, builder):
        """T17b: REINFORCE action formats correctly."""
        instructions = ForeshadowInstructions()
        instructions.add_instruction(ForeshadowInstruction(
            foreshadowing_id="FS-002",
            action=InstructionAction.REINFORCE,
            note="伏線の強化。",
        ))
        result = builder._format_instructions_for_prompt(instructions)
        assert "FS-002" in result

    def test_format_hint(self, builder):
        """T17c: HINT action formats correctly."""
        instructions = ForeshadowInstructions()
        instructions.add_instruction(ForeshadowInstruction(
            foreshadowing_id="FS-003",
            action=InstructionAction.HINT,
            note="控えめなヒント。",
        ))
        result = builder._format_instructions_for_prompt(instructions)
        assert "FS-003" in result

    def test_format_none_excluded(self, builder):
        """T18: NONE action items are excluded from prompt."""
        instructions = ForeshadowInstructions()
        instructions.add_instruction(ForeshadowInstruction(
            foreshadowing_id="FS-004",
            action=InstructionAction.NONE,
        ))
        result = builder._format_instructions_for_prompt(instructions)
        assert "FS-004" not in result

    def test_format_empty(self, builder):
        """T18b: Empty instructions return empty string."""
        instructions = ForeshadowInstructions()
        result = builder._format_instructions_for_prompt(instructions)
        assert result == ""


class TestGetActiveForeshadowings:
    """Tests for get_active_foreshadowings()."""

    def test_returns_id_list(self, builder, scene):
        """T19: Returns list of foreshadowing IDs."""
        result = builder.get_active_foreshadowings(scene)
        assert isinstance(result, list)

    def test_empty_without_repository(self, builder, scene):
        """T19b: Returns empty list without repository."""
        result = builder.get_active_foreshadowings(scene)
        assert result == []


class TestGetForeshadowingSummary:
    """Tests for get_foreshadowing_summary()."""

    def test_returns_dict(self, builder, scene):
        """T20: Returns action-count dictionary."""
        result = builder.get_foreshadowing_summary(scene)
        assert isinstance(result, dict)

    def test_empty_without_repository(self, builder, scene):
        """T20b: Returns empty dict without repository."""
        result = builder.get_foreshadowing_summary(scene)
        assert result == {}


class TestClearInstructionCache:
    """Tests for clear_instruction_cache()."""

    def test_clear_cache(self, builder, scene):
        """T21: Cache is cleared after clear_instruction_cache()."""
        # Build cache
        result1 = builder.get_foreshadow_instructions(scene)
        # Clear
        builder.clear_instruction_cache()
        # New call should return different object
        result2 = builder.get_foreshadow_instructions(scene)
        assert result1 is not result2
