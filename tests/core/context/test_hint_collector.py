"""Tests for HintCollector."""

import pytest

from src.core.context.filtered_context import FilteredContext
from src.core.context.foreshadow_instruction import (
    ForeshadowInstruction,
    ForeshadowInstructions,
    InstructionAction,
)
from src.core.context.visibility_context import (
    VisibilityAwareContext,
    VisibilityHint,
)
from src.core.models.ai_visibility import AIVisibilityLevel


class TestHintCollectorImport:
    """Test imports."""

    def test_import(self):
        """HintCollector can be imported."""
        from src.core.context.hint_collector import (
            CollectedHint,
            HintCollection,
            HintCollector,
            HintSource,
        )

        assert HintCollector is not None
        assert HintCollection is not None
        assert CollectedHint is not None
        assert HintSource is not None


class TestHintSource:
    """Tests for HintSource enum."""

    def test_source_values(self):
        """HintSource has expected values."""
        from src.core.context.hint_collector import HintSource

        assert HintSource.FORESHADOWING.value == "foreshadowing"
        assert HintSource.VISIBILITY.value == "visibility"


class TestCollectedHint:
    """Tests for CollectedHint dataclass."""

    def test_priority_calculation(self):
        """Priority is calculated based on source and strength."""
        from src.core.context.hint_collector import CollectedHint, HintSource

        hint = CollectedHint(
            source=HintSource.FORESHADOWING,
            category="foreshadowing",
            entity_id="FS-001",
            hint_text="Test hint",
            strength=0.5,
        )

        # FORESHADOWING weight = 1.0, strength = 0.5
        assert hint.priority == 0.5

    def test_priority_visibility_source(self):
        """Visibility source has lower weight."""
        from src.core.context.hint_collector import CollectedHint, HintSource

        hint = CollectedHint(
            source=HintSource.VISIBILITY,
            category="character",
            entity_id="Alice",
            hint_text="Test hint",
            strength=0.5,
        )

        # VISIBILITY weight = 0.8, strength = 0.5
        assert hint.priority == 0.4


class TestHintCollection:
    """Tests for HintCollection."""

    def test_add_hint(self):
        """Add hint to collection."""
        from src.core.context.hint_collector import (
            CollectedHint,
            HintCollection,
            HintSource,
        )

        collection = HintCollection()
        hint = CollectedHint(
            source=HintSource.FORESHADOWING,
            category="foreshadowing",
            entity_id="FS-001",
            hint_text="Test hint",
        )

        collection.add(hint)

        assert len(collection.hints) == 1
        assert "foreshadowing" in collection.by_category
        assert "FS-001" in collection.by_entity

    def test_sort_by_priority(self):
        """Sort hints by priority descending."""
        from src.core.context.hint_collector import (
            CollectedHint,
            HintCollection,
            HintSource,
        )

        collection = HintCollection()
        collection.add(
            CollectedHint(
                source=HintSource.VISIBILITY,
                category="character",
                entity_id="Alice",
                hint_text="Low priority",
                strength=0.3,
            )
        )
        collection.add(
            CollectedHint(
                source=HintSource.FORESHADOWING,
                category="foreshadowing",
                entity_id="FS-001",
                hint_text="High priority",
                strength=0.8,
            )
        )

        collection.sort_by_priority()

        assert collection.hints[0].entity_id == "FS-001"
        assert collection.hints[1].entity_id == "Alice"

    def test_get_top_hints(self):
        """Get top N hints."""
        from src.core.context.hint_collector import (
            CollectedHint,
            HintCollection,
            HintSource,
        )

        collection = HintCollection()
        for i in range(10):
            collection.add(
                CollectedHint(
                    source=HintSource.FORESHADOWING,
                    category="test",
                    entity_id=f"FS-{i:03d}",
                    hint_text=f"Hint {i}",
                    strength=0.1 * i,
                )
            )
        collection.sort_by_priority()

        top_5 = collection.get_top_hints(5)

        assert len(top_5) == 5


class TestHintCollectorCollectAll:
    """Tests for collect_all method."""

    def test_collect_all_empty(self):
        """Collect with no sources returns empty collection."""
        from src.core.context.hint_collector import HintCollector

        collector = HintCollector()
        result = collector.collect_all()

        assert len(result.hints) == 0

    def test_collect_from_visibility_context(self):
        """Collect hints from visibility context."""
        from src.core.context.hint_collector import HintCollector

        visibility_context = VisibilityAwareContext(
            base_context=FilteredContext(),
        )
        visibility_context.add_hint(
            VisibilityHint(
                category="character",
                entity_id="Alice",
                hint_text="Alice has a mysterious past",
                level=AIVisibilityLevel.AWARE,
            )
        )

        collector = HintCollector()
        result = collector.collect_all(visibility_context=visibility_context)

        assert len(result.hints) == 1
        assert result.hints[0].hint_text == "Alice has a mysterious past"

    def test_collect_from_foreshadow_instructions(self):
        """Collect hints from foreshadow instructions (HINT action only)."""
        from src.core.context.hint_collector import HintCollector

        instructions = ForeshadowInstructions()
        instructions.add_instruction(
            ForeshadowInstruction(
                foreshadowing_id="FS-001",
                action=InstructionAction.HINT,
                note="Subtly hint at the secret",
                subtlety_target=8,
            )
        )
        # PLANT should not be collected as hint
        instructions.add_instruction(
            ForeshadowInstruction(
                foreshadowing_id="FS-002",
                action=InstructionAction.PLANT,
                subtlety_target=4,
            )
        )

        collector = HintCollector()
        result = collector.collect_all(foreshadow_instructions=instructions)

        # Only HINT action should be collected
        assert len(result.hints) == 1
        assert result.hints[0].entity_id == "FS-001"

    def test_collect_all_combined(self):
        """Collect from both visibility and foreshadowing."""
        from src.core.context.hint_collector import HintCollector

        visibility_context = VisibilityAwareContext(
            base_context=FilteredContext(),
        )
        visibility_context.add_hint(
            VisibilityHint(
                category="character",
                entity_id="Alice",
                hint_text="Alice hint",
                level=AIVisibilityLevel.AWARE,
            )
        )

        instructions = ForeshadowInstructions()
        instructions.add_instruction(
            ForeshadowInstruction(
                foreshadowing_id="FS-001",
                action=InstructionAction.HINT,
                note="Foreshadowing hint",
                subtlety_target=8,
            )
        )

        collector = HintCollector()
        result = collector.collect_all(
            visibility_context=visibility_context,
            foreshadow_instructions=instructions,
        )

        assert len(result.hints) == 2


class TestHintCollectorFormat:
    """Tests for formatting methods."""

    def test_format_for_prompt_empty(self):
        """Empty collection returns empty string."""
        from src.core.context.hint_collector import HintCollection, HintCollector

        collector = HintCollector()
        collection = HintCollection()

        result = collector.format_for_prompt(collection)

        assert result == ""

    def test_format_for_prompt_with_hints(self):
        """Format hints for prompt."""
        from src.core.context.hint_collector import (
            CollectedHint,
            HintCollection,
            HintCollector,
            HintSource,
        )

        collection = HintCollection()
        collection.add(
            CollectedHint(
                source=HintSource.FORESHADOWING,
                category="foreshadowing",
                entity_id="FS-001",
                hint_text="Hint about the secret",
                strength=0.8,
            )
        )
        collection.sort_by_priority()

        collector = HintCollector()
        result = collector.format_for_prompt(collection)

        assert "執筆時のヒント" in result
        assert "Hint about the secret" in result

    def test_format_by_category(self):
        """Format hints by category."""
        from src.core.context.hint_collector import (
            CollectedHint,
            HintCollection,
            HintCollector,
            HintSource,
        )

        collection = HintCollection()
        collection.add(
            CollectedHint(
                source=HintSource.VISIBILITY,
                category="character",
                entity_id="Alice",
                hint_text="Alice hint",
            )
        )
        collection.add(
            CollectedHint(
                source=HintSource.VISIBILITY,
                category="world_setting",
                entity_id="Magic",
                hint_text="Magic hint",
            )
        )

        collector = HintCollector()
        result = collector.format_by_category(collection)

        assert "character" in result
        assert "world_setting" in result
        assert "Alice hint" in result["character"]


class TestHintCollectorStrengthMapping:
    """Tests for strength to word mapping."""

    def test_strength_to_word(self):
        """Strength is mapped to descriptive words."""
        from src.core.context.hint_collector import HintCollector

        collector = HintCollector()

        assert collector._strength_to_word(0.9) == "重要"
        assert collector._strength_to_word(0.5) == "中程度"
        assert collector._strength_to_word(0.2) == "控えめ"
