"""Hint collector for L3 context building.

This module collects and integrates hints from various sources
(visibility, foreshadowing) for the Ghost Writer.
"""

from dataclasses import dataclass, field
from enum import Enum

from .foreshadow_instruction import ForeshadowInstructions, InstructionAction
from .visibility_context import VisibilityAwareContext


class HintSource(Enum):
    """Source of a hint.

    Attributes:
        FORESHADOWING: Hint from foreshadowing system.
        VISIBILITY: Hint from visibility filtering system.
        CHARACTER: Hint from character settings.
        WORLD: Hint from world settings.
    """

    FORESHADOWING = "foreshadowing"
    VISIBILITY = "visibility"
    CHARACTER = "character"
    WORLD = "world"


@dataclass
class CollectedHint:
    """A collected hint from any source.

    Attributes:
        source: Source of the hint.
        category: Category (character, world_setting, foreshadowing, etc.).
        entity_id: Related entity ID.
        hint_text: The actual hint text.
        strength: Hint strength (0.0-1.0).
        priority: Calculated priority (set in __post_init__).
    """

    source: HintSource
    category: str
    entity_id: str
    hint_text: str
    strength: float = 0.5
    priority: float = field(default=0.0, init=False)

    # Source weights for priority calculation
    _SOURCE_WEIGHTS: dict[HintSource, float] = field(
        default_factory=lambda: {
            HintSource.FORESHADOWING: 1.0,
            HintSource.VISIBILITY: 0.8,
            HintSource.CHARACTER: 0.6,
            HintSource.WORLD: 0.5,
        },
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        """Calculate priority based on source and strength."""
        weight = self._SOURCE_WEIGHTS.get(self.source, 0.5)
        self.priority = weight * self.strength


@dataclass
class HintCollection:
    """Collection of hints organized by category and entity.

    Attributes:
        hints: All hints (can be sorted by priority).
        by_category: Hints grouped by category.
        by_entity: Hints grouped by entity ID.
    """

    hints: list[CollectedHint] = field(default_factory=list)
    by_category: dict[str, list[CollectedHint]] = field(default_factory=dict)
    by_entity: dict[str, list[CollectedHint]] = field(default_factory=dict)

    def add(self, hint: CollectedHint) -> None:
        """Add a hint to the collection.

        Args:
            hint: The hint to add.
        """
        self.hints.append(hint)

        # Index by category
        if hint.category not in self.by_category:
            self.by_category[hint.category] = []
        self.by_category[hint.category].append(hint)

        # Index by entity
        if hint.entity_id not in self.by_entity:
            self.by_entity[hint.entity_id] = []
        self.by_entity[hint.entity_id].append(hint)

    def sort_by_priority(self) -> None:
        """Sort all hints by priority (descending)."""
        self.hints.sort(key=lambda h: h.priority, reverse=True)
        for hints in self.by_category.values():
            hints.sort(key=lambda h: h.priority, reverse=True)
        for hints in self.by_entity.values():
            hints.sort(key=lambda h: h.priority, reverse=True)

    def get_top_hints(self, n: int = 5) -> list[CollectedHint]:
        """Get top N hints by priority.

        Args:
            n: Number of hints to return.

        Returns:
            Top N hints.
        """
        return self.hints[:n]


class HintCollector:
    """Collects and integrates hints from various sources.

    This class gathers hints from:
    1. Visibility context (AWARE-level sections)
    2. Foreshadowing instructions (HINT action)

    And formats them for the Ghost Writer prompt.
    """

    def collect_all(
        self,
        visibility_context: VisibilityAwareContext | None = None,
        foreshadow_instructions: ForeshadowInstructions | None = None,
    ) -> HintCollection:
        """Collect hints from all sources.

        Args:
            visibility_context: Visibility-aware context with hints.
            foreshadow_instructions: Foreshadowing instructions.

        Returns:
            Integrated hint collection.
        """
        collection = HintCollection()

        # Collect from visibility context
        if visibility_context:
            for hint in self._collect_from_visibility(visibility_context):
                collection.add(hint)

        # Collect from foreshadowing instructions
        if foreshadow_instructions:
            for hint in self._collect_from_foreshadowing(foreshadow_instructions):
                collection.add(hint)

        # Sort by priority
        collection.sort_by_priority()

        return collection

    def _collect_from_visibility(
        self,
        context: VisibilityAwareContext,
    ) -> list[CollectedHint]:
        """Collect hints from visibility context.

        Args:
            context: Visibility-aware context.

        Returns:
            List of collected hints.
        """
        collected: list[CollectedHint] = []

        for hint in context.hints:
            # Use structured fields directly (category and entity_id)
            collected.append(
                CollectedHint(
                    source=HintSource.VISIBILITY,
                    category=hint.category,
                    entity_id=hint.entity_id,
                    hint_text=hint.hint_text,
                    strength=0.5,  # Default strength for visibility hints
                )
            )

        return collected

    def _collect_from_foreshadowing(
        self,
        instructions: ForeshadowInstructions,
    ) -> list[CollectedHint]:
        """Collect hints from foreshadowing instructions.

        Only HINT action instructions are collected as hints.
        PLANT/REINFORCE are handled directly by the instruction system.

        Args:
            instructions: Foreshadowing instructions.

        Returns:
            List of collected hints.
        """
        collected: list[CollectedHint] = []

        for inst in instructions.instructions:
            if inst.action == InstructionAction.HINT:
                hint_text = self._generate_hint_text(inst)
                collected.append(
                    CollectedHint(
                        source=HintSource.FORESHADOWING,
                        category="foreshadowing",
                        entity_id=inst.foreshadowing_id,
                        hint_text=hint_text,
                        strength=self._action_to_strength(inst.action),
                    )
                )

        return collected

    def _generate_hint_text(self, inst: "ForeshadowInstruction") -> str:  # noqa: F821
        """Generate hint text from instruction.

        Args:
            inst: Foreshadowing instruction.

        Returns:
            Hint text.
        """
        if inst.note:
            return inst.note

        return f"{inst.foreshadowing_id}に関連する要素を控えめに匂わせてください"

    def _action_to_strength(self, action: InstructionAction) -> float:
        """Map action to strength value.

        Args:
            action: Instruction action.

        Returns:
            Strength value (0.0-1.0).
        """
        strength_map = {
            InstructionAction.PLANT: 0.8,
            InstructionAction.REINFORCE: 0.6,
            InstructionAction.HINT: 0.3,
            InstructionAction.NONE: 0.0,
        }
        return strength_map.get(action, 0.5)

    def format_for_prompt(
        self,
        collection: HintCollection,
        max_hints: int = 5,
    ) -> str:
        """Format hints for Ghost Writer prompt.

        Args:
            collection: Hint collection.
            max_hints: Maximum number of hints to include.

        Returns:
            Formatted string for prompt.
        """
        if not collection.hints:
            return ""

        lines = ["## 執筆時のヒント\n"]
        lines.append("以下の要素を、自然な形で匂わせてください：\n")

        for hint in collection.get_top_hints(max_hints):
            intensity = self._strength_to_word(hint.strength)
            lines.append(f"- [{intensity}] {hint.hint_text}")

        return "\n".join(lines)

    def _strength_to_word(self, strength: float) -> str:
        """Convert strength to descriptive word.

        Args:
            strength: Strength value (0.0-1.0).

        Returns:
            Descriptive word in Japanese.
        """
        if strength >= 0.7:
            return "重要"
        elif strength >= 0.4:
            return "中程度"
        else:
            return "控えめ"

    def format_by_category(
        self,
        collection: HintCollection,
    ) -> dict[str, str]:
        """Format hints grouped by category.

        Args:
            collection: Hint collection.

        Returns:
            Dictionary of category to formatted hints.
        """
        result: dict[str, str] = {}

        for category, hints in collection.by_category.items():
            lines = [f"### {category} ヒント"]
            for hint in hints:
                lines.append(f"- {hint.hint_text}")
            result[category] = "\n".join(lines)

        return result


# Import for type annotation
from .foreshadow_instruction import ForeshadowInstruction  # noqa: E402
