"""Visibility-aware context data classes for L3 context building.

This module defines data classes for representing context information
that has been filtered based on AI visibility levels. It provides hints
for Level 1-2 information and tracks excluded sections.
"""

from dataclasses import dataclass, field

from src.core.models.ai_visibility import AIVisibilityLevel
from .filtered_context import FilteredContext


@dataclass
class VisibilityHint:
    """Visibility hint for Level 1-2 information.

    Instead of including the actual content for Level 1-2 visibility,
    this class provides indirect hints that guide the AI's awareness
    without revealing the full information.

    Attributes:
        source_section: The section from which this hint originates.
        hint_text: The actual hint text to provide to the AI.
        level: The visibility level of the original content.

    Examples:
        >>> hint = VisibilityHint(
        ...     source_section="character.alice.secret",
        ...     hint_text="Alice carries herself with unexpected grace.",
        ...     level=AIVisibilityLevel.AWARE,
        ... )
    """

    source_section: str
    hint_text: str
    level: AIVisibilityLevel


@dataclass
class VisibilityAwareContext:
    """Context filtered by AI visibility levels.

    This class wraps a FilteredContext with additional visibility-related
    information. It tracks which sections were excluded due to visibility
    restrictions and provides hints for Level 1-2 content.

    Attributes:
        base_context: The underlying filtered context.
        hints: List of visibility hints for Level 1-2 content.
        excluded_sections: Names of sections excluded due to visibility.
        current_visibility_level: The visibility level applied during filtering.
        forbidden_keywords: Keywords that must not appear in generated text.

    Examples:
        >>> base = FilteredContext(plot_l1="Theme: Adventure")
        >>> ctx = VisibilityAwareContext(
        ...     base_context=base,
        ...     current_visibility_level=AIVisibilityLevel.KNOW,
        ... )
        >>> ctx.add_hint(VisibilityHint(
        ...     source_section="character.bob",
        ...     hint_text="Bob seems nervous.",
        ...     level=AIVisibilityLevel.AWARE,
        ... ))
    """

    base_context: FilteredContext
    hints: list[VisibilityHint] = field(default_factory=list)
    excluded_sections: list[str] = field(default_factory=list)
    current_visibility_level: AIVisibilityLevel = AIVisibilityLevel.USE
    forbidden_keywords: list[str] = field(default_factory=list)

    def get_hints_by_level(self, level: AIVisibilityLevel) -> list[VisibilityHint]:
        """Get hints filtered by visibility level.

        Args:
            level: The visibility level to filter by.

        Returns:
            List of hints matching the specified level.
        """
        return [h for h in self.hints if h.level == level]

    def has_hints(self) -> bool:
        """Check if any hints are available.

        Returns:
            True if there is at least one hint.
        """
        return len(self.hints) > 0

    def count_excluded(self) -> int:
        """Get the count of excluded sections.

        Returns:
            Number of sections excluded due to visibility restrictions.
        """
        return len(self.excluded_sections)

    def add_hint(self, hint: VisibilityHint) -> None:
        """Add a visibility hint.

        Args:
            hint: The hint to add.
        """
        self.hints.append(hint)

    def add_excluded_section(self, section: str) -> None:
        """Add an excluded section.

        Duplicates are ignored.

        Args:
            section: The section name to mark as excluded.
        """
        if section not in self.excluded_sections:
            self.excluded_sections.append(section)

    def merge_forbidden_keywords(self, keywords: list[str]) -> None:
        """Merge additional forbidden keywords.

        Keywords are deduplicated and the result is sorted alphabetically.

        Args:
            keywords: List of keywords to add to the forbidden list.
        """
        current_set = set(self.forbidden_keywords)
        current_set.update(keywords)
        self.forbidden_keywords = sorted(current_set)

    def to_ghost_writer_context(self) -> dict:
        """Convert to a context dictionary for Ghost Writer.

        Creates a flat dictionary suitable for prompt construction,
        including hints as a formatted string and metadata about
        visibility filtering.

        Returns:
            Dictionary with context fields and metadata.
        """
        result = self.base_context.to_prompt_dict()

        # Add hints if available
        if self.hints:
            hint_texts = [h.hint_text for h in self.hints]
            result["foreshadow_hints"] = "\n".join(hint_texts)

        # Add metadata
        result["_excluded_count"] = self.count_excluded()
        result["_visibility_level"] = self.current_visibility_level.value

        return result
