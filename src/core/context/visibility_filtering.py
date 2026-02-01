"""Visibility filtering service for L3 context building.

This module provides filtering of context data based on AI visibility levels,
using the L2 VisibilityController for section-based filtering.
"""

from dataclasses import dataclass, field

from src.core.models.ai_visibility import AIVisibilityLevel
from src.core.services.visibility_controller import VisibilityController

from .filtered_context import FilteredContext
from .visibility_context import VisibilityAwareContext, VisibilityHint


@dataclass
class FilteringResult:
    """Result of a filtering operation.

    Attributes:
        filtered_data: The filtered data (dict or other).
        removed_count: Number of items/sections removed.
        hints: Generated visibility hints.
    """

    filtered_data: dict[str, str] = field(default_factory=dict)
    removed_count: int = 0
    hints: list[VisibilityHint] = field(default_factory=list)


class VisibilityFilteringService:
    """Service for filtering context based on AI visibility levels.

    This service integrates with L2's VisibilityController to filter
    characters, world settings, and other context content based on
    visibility comments embedded in the content.

    Attributes:
        visibility_controller: L2 VisibilityController for content filtering.
    """

    def __init__(
        self,
        visibility_controller: VisibilityController,
    ) -> None:
        """Initialize VisibilityFilteringService.

        Args:
            visibility_controller: L2 visibility controller instance.
        """
        self.visibility_controller = visibility_controller

    def filter_context(
        self,
        context: FilteredContext,
        target_level: AIVisibilityLevel = AIVisibilityLevel.KNOW,
    ) -> VisibilityAwareContext:
        """Filter entire context based on visibility.

        Args:
            context: The FilteredContext to filter.
            target_level: Target visibility level (default: KNOW).

        Returns:
            VisibilityAwareContext with filtered content and hints.
        """
        result = VisibilityAwareContext(
            base_context=context,
            current_visibility_level=target_level,
        )

        # Filter characters
        if context.characters:
            char_result = self.filter_characters(context.characters)
            result.filtered_characters = char_result.filtered_data
            for hint in char_result.hints:
                result.add_hint(hint)
            for _ in range(char_result.removed_count):
                pass  # removed_count already tracked

        # Filter world settings
        if context.world_settings:
            world_result = self.filter_world_settings(context.world_settings)
            result.filtered_world_settings = world_result.filtered_data
            for hint in world_result.hints:
                result.add_hint(hint)

        # Merge forbidden keywords from controller
        result.merge_forbidden_keywords(self.visibility_controller.forbidden_keywords)

        return result

    def filter_characters(
        self,
        characters: dict[str, str],
    ) -> FilteringResult:
        """Filter character information based on visibility.

        Args:
            characters: Dictionary of character name to content.

        Returns:
            FilteringResult with filtered characters and hints.
        """
        filtered: dict[str, str] = {}
        hints: list[VisibilityHint] = []
        removed_count = 0

        for name, content in characters.items():
            # Use VisibilityController to filter content
            filter_result = self.visibility_controller.filter(content)

            # Store filtered content
            filtered[name] = filter_result.content

            # Collect hints from AWARE sections
            for hint_text in filter_result.hints:
                hints.append(
                    VisibilityHint(
                        source_section=f"character.{name}",
                        hint_text=hint_text,
                        level=AIVisibilityLevel.AWARE,
                    )
                )

            # Track excluded sections
            removed_count += len(filter_result.excluded_sections)

        return FilteringResult(
            filtered_data=filtered,
            removed_count=removed_count,
            hints=hints,
        )

    def filter_world_settings(
        self,
        world_settings: dict[str, str],
    ) -> FilteringResult:
        """Filter world setting information based on visibility.

        Args:
            world_settings: Dictionary of setting name to content.

        Returns:
            FilteringResult with filtered settings and hints.
        """
        filtered: dict[str, str] = {}
        hints: list[VisibilityHint] = []
        removed_count = 0

        for name, content in world_settings.items():
            # Use VisibilityController to filter content
            filter_result = self.visibility_controller.filter(content)

            # Store filtered content
            filtered[name] = filter_result.content

            # Collect hints from AWARE sections
            for hint_text in filter_result.hints:
                hints.append(
                    VisibilityHint(
                        source_section=f"world_setting.{name}",
                        hint_text=hint_text,
                        level=AIVisibilityLevel.AWARE,
                    )
                )

            # Track excluded sections
            removed_count += len(filter_result.excluded_sections)

        return FilteringResult(
            filtered_data=filtered,
            removed_count=removed_count,
            hints=hints,
        )
