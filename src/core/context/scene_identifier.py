"""Scene identifier for L3 context building.

This module defines the SceneIdentifier data class which uniquely identifies
a scene in the novel structure.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SceneIdentifier:
    """Identifies a specific scene in the novel structure.

    This immutable data class is used throughout L3 to specify which scene's
    context should be built. It supports hierarchical identification through
    episode, sequence, and chapter IDs.

    Attributes:
        episode_id: Episode identifier (required). Examples: "010", "ep010"
        sequence_id: Sequence identifier (optional). Example: "seq_01"
        chapter_id: Chapter identifier (optional). Example: "ch_03"
        current_phase: Current narrative phase (optional). Example: "arc_1_reveal"

    Examples:
        >>> scene = SceneIdentifier(episode_id="010")
        >>> scene = SceneIdentifier(episode_id="010", sequence_id="seq_01")
        >>> scene = SceneIdentifier(
        ...     episode_id="010",
        ...     sequence_id="seq_01",
        ...     chapter_id="ch_03",
        ...     current_phase="arc_1_reveal"
        ... )
    """

    episode_id: str
    sequence_id: str | None = None
    chapter_id: str | None = None
    current_phase: str | None = None

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if not self.episode_id:
            raise ValueError("episode_id is required")

    def __str__(self) -> str:
        """Return human-readable string representation.

        Format: ep:{episode_id}[/seq:{sequence_id}][/ch:{chapter_id}]

        Returns:
            String representation of the scene identifier.
        """
        parts = [f"ep:{self.episode_id}"]
        if self.sequence_id:
            parts.append(f"seq:{self.sequence_id}")
        if self.chapter_id:
            parts.append(f"ch:{self.chapter_id}")
        return "/".join(parts)
