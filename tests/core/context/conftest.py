"""Shared fixtures for context builder tests."""

from datetime import date
from pathlib import Path

import pytest

from src.core.context.context_builder import ContextBuilder
from src.core.context.scene_identifier import SceneIdentifier
from src.core.models.foreshadowing import (
    Foreshadowing,
    ForeshadowingAIVisibility,
    ForeshadowingPayoff,
    ForeshadowingSeed,
    ForeshadowingStatus,
    ForeshadowingType,
    RelatedElements,
    TimelineEntry,
    TimelineInfo,
)


@pytest.fixture
def scene() -> SceneIdentifier:
    """Standard test scene identifier."""
    return SceneIdentifier(
        episode_id="ep010", sequence_id="seq_01", current_phase="initial"
    )


@pytest.fixture
def builder(tmp_path: Path) -> ContextBuilder:
    """Create a ContextBuilder with empty vault."""
    return ContextBuilder(vault_root=tmp_path)


def create_foreshadowing(
    fs_id: str,
    status: ForeshadowingStatus,
    *,
    title: str | None = None,
    plant_episode: str | None = None,
    reinforce_episodes: list[str] | None = None,
    reveal_episode: str | None = None,
    related_characters: list[str] | None = None,
    forbidden_keywords: list[str] | None = None,
    allowed_expressions: list[str] | None = None,
    seed_description: str | None = None,
    subtlety_level: int = 5,
) -> Foreshadowing:
    """Helper to create foreshadowing with full configuration.

    This is the unified helper used across foreshadowing-related tests.
    All parameters are optional with sensible defaults.
    """
    timeline_events: list[TimelineEntry] = []

    # Auto-detect plant_episode from ID if not provided and status >= PLANTED
    effective_plant_episode = plant_episode
    if effective_plant_episode is None and status in (
        ForeshadowingStatus.PLANTED,
        ForeshadowingStatus.REINFORCED,
        ForeshadowingStatus.REVEALED,
    ):
        parts = fs_id.split("-")
        if len(parts) >= 2:
            effective_plant_episode = parts[1]

    if effective_plant_episode:
        timeline_events.append(
            TimelineEntry(
                episode=effective_plant_episode,
                type=ForeshadowingStatus.PLANTED,
                date=date.today(),
                expression="planted expression",
                subtlety=subtlety_level,
            )
        )

    if reinforce_episodes:
        for ep in reinforce_episodes:
            timeline_events.append(
                TimelineEntry(
                    episode=ep,
                    type=ForeshadowingStatus.REINFORCED,
                    date=date.today(),
                    expression="reinforced expression",
                    subtlety=subtlety_level + 1,
                )
            )

    payoff = None
    if reveal_episode:
        payoff = ForeshadowingPayoff(
            content="payoff content",
            planned_episode=reveal_episode,
        )

    seed = ForeshadowingSeed(content="seed content")
    if seed_description:
        seed = ForeshadowingSeed(content="seed content", description=seed_description)

    return Foreshadowing(
        id=fs_id,
        title=title or f"Foreshadowing {fs_id}",
        fs_type=ForeshadowingType.PLOT_TWIST,
        status=status,
        subtlety_level=subtlety_level,
        ai_visibility=ForeshadowingAIVisibility(
            level=2,
            forbidden_keywords=forbidden_keywords or ["secret", "truth"],
            allowed_expressions=allowed_expressions or ["mysterious", "shadow"],
        ),
        seed=seed,
        payoff=payoff,
        timeline=TimelineInfo(
            registered_at=date.today(),
            events=timeline_events,
        ),
        related=RelatedElements(
            characters=related_characters or [],
            plot_threads=[],
            locations=[],
        ),
    )
