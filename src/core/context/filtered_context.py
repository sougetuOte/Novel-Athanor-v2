"""Filtered context data class for L3 context building.

This module defines the FilteredContext data class which holds all the
context information needed for AI text generation, after visibility
and phase filtering has been applied.
"""

from dataclasses import dataclass, field


@dataclass
class FilteredContext:
    """Filtered context ready for AI consumption.

    This data class holds all context information that has passed through
    AI visibility filtering and phase filtering. It is the primary output
    of the L3 Context Builder layer and serves as input for L4 agents
    (Ghost Writer, etc.).

    Attributes:
        plot_l1: L1 plot (theme, overall direction).
        plot_l2: L2 plot (chapter objectives, state changes).
        plot_l3: L3 plot (scene composition, scene list).
        summary_l1: L1 summary (overall summary).
        summary_l2: L2 summary (chapter summary).
        summary_l3: L3 summary (recent scene summary).
        characters: Character information keyed by name (phase-filtered).
        world_settings: World setting information keyed by name (phase-filtered).
        style_guide: Style guide content.
        scene_id: Identifier of the target scene.
        current_phase: Current narrative phase.
        warnings: List of warning messages generated during context building.

    Examples:
        >>> ctx = FilteredContext(
        ...     plot_l1="Theme: Redemption through sacrifice",
        ...     characters={"Alice": "Protagonist, age 25, seeking answers"},
        ...     scene_id="ep010/seq_01",
        ... )
        >>> ctx.has_plot()
        True
        >>> ctx.get_character_names()
        ['Alice']
    """

    # Plot information (hierarchical)
    plot_l1: str | None = None
    plot_l2: str | None = None
    plot_l3: str | None = None

    # Summary information (hierarchical)
    summary_l1: str | None = None
    summary_l2: str | None = None
    summary_l3: str | None = None

    # Character information (phase-filtered)
    # key: character name, value: filtered setting text
    characters: dict[str, str] = field(default_factory=dict)

    # World setting information (phase-filtered)
    # key: setting name, value: filtered setting text
    world_settings: dict[str, str] = field(default_factory=dict)

    # Style guide
    style_guide: str | None = None

    # Meta information
    scene_id: str = ""
    current_phase: str | None = None
    warnings: list[str] = field(default_factory=list)

    def has_plot(self) -> bool:
        """Check if any plot information is available.

        Returns:
            True if at least one of plot_l1, plot_l2, or plot_l3 is set.
        """
        return any([self.plot_l1, self.plot_l2, self.plot_l3])

    def has_summary(self) -> bool:
        """Check if any summary information is available.

        Returns:
            True if at least one of summary_l1, summary_l2, or summary_l3 is set.
        """
        return any([self.summary_l1, self.summary_l2, self.summary_l3])

    def get_character_names(self) -> list[str]:
        """Get list of character names in this context.

        Returns:
            List of character names.
        """
        return list(self.characters.keys())

    def add_warning(self, warning: str) -> None:
        """Add a warning message.

        Args:
            warning: The warning message to add.
        """
        self.warnings.append(warning)

    def to_prompt_dict(self) -> dict[str, str]:
        """Convert to flat dictionary for prompt construction.

        This method creates a flattened dictionary suitable for use in
        constructing prompts for Ghost Writer and other AI agents.

        Returns:
            Dictionary with standardized keys for each context element.
        """
        result: dict[str, str] = {}

        # Plot information
        if self.plot_l1:
            result["plot_theme"] = self.plot_l1
        if self.plot_l2:
            result["plot_chapter"] = self.plot_l2
        if self.plot_l3:
            result["plot_scene"] = self.plot_l3

        # Summary information
        if self.summary_l1:
            result["summary_overall"] = self.summary_l1
        if self.summary_l2:
            result["summary_chapter"] = self.summary_l2
        if self.summary_l3:
            result["summary_recent"] = self.summary_l3

        # Character information
        for name, info in self.characters.items():
            result[f"character_{name}"] = info

        # World settings
        for name, info in self.world_settings.items():
            result[f"world_{name}"] = info

        # Style guide
        if self.style_guide:
            result["style_guide"] = self.style_guide

        return result

    def merge(self, other: "FilteredContext") -> "FilteredContext":
        """Merge with another FilteredContext.

        Creates a new FilteredContext by merging self with other.
        Self's non-None values take precedence over other's values.
        Dictionaries and lists are combined.

        Args:
            other: The other FilteredContext to merge with.

        Returns:
            A new FilteredContext with merged content.
        """
        # Merge characters and world_settings
        merged_characters = {**other.characters, **self.characters}
        merged_world_settings = {**other.world_settings, **self.world_settings}
        merged_warnings = self.warnings + other.warnings

        return FilteredContext(
            plot_l1=self.plot_l1 if self.plot_l1 else other.plot_l1,
            plot_l2=self.plot_l2 if self.plot_l2 else other.plot_l2,
            plot_l3=self.plot_l3 if self.plot_l3 else other.plot_l3,
            summary_l1=self.summary_l1 if self.summary_l1 else other.summary_l1,
            summary_l2=self.summary_l2 if self.summary_l2 else other.summary_l2,
            summary_l3=self.summary_l3 if self.summary_l3 else other.summary_l3,
            characters=merged_characters,
            world_settings=merged_world_settings,
            style_guide=self.style_guide if self.style_guide else other.style_guide,
            scene_id=self.scene_id if self.scene_id else other.scene_id,
            current_phase=(
                self.current_phase if self.current_phase else other.current_phase
            ),
            warnings=merged_warnings,
        )
