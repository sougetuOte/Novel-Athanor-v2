"""Foreshadowing identifier for L3 context building.

This module provides functionality to identify foreshadowing elements
relevant to a given scene, determining appropriate actions (PLANT/REINFORCE/HINT).
"""

import re
from dataclasses import dataclass

from src.core.models.foreshadowing import Foreshadowing, ForeshadowingStatus
from src.core.repositories.foreshadowing import ForeshadowingRepository

from .foreshadow_instruction import InstructionAction
from .scene_identifier import SceneIdentifier


@dataclass
class IdentifiedForeshadowing:
    """Identified foreshadowing information.

    Represents a foreshadowing element that has been identified as relevant
    to a specific scene, along with the suggested action.

    Attributes:
        foreshadowing_id: Unique identifier (e.g., "FS-010-secret").
        suggested_action: Recommended action for this foreshadowing.
        status: Current status of the foreshadowing.
        relevance_reason: Human-readable explanation of why this is relevant.
    """

    foreshadowing_id: str
    suggested_action: InstructionAction
    status: str
    relevance_reason: str


class ForeshadowingIdentifier:
    """Identifies foreshadowing elements relevant to a scene.

    Analyzes foreshadowing data from the repository and determines
    which elements are relevant to the current scene, along with
    suggested actions (PLANT/REINFORCE/HINT/NONE).

    Attributes:
        repository: Foreshadowing repository for data access.
    """

    # Pattern to extract episode from foreshadowing ID (FS-{episode}-{slug})
    _ID_PATTERN = re.compile(r"^FS-(\d+)-")

    def __init__(self, repository: ForeshadowingRepository) -> None:
        """Initialize ForeshadowingIdentifier.

        Args:
            repository: Foreshadowing repository instance.
        """
        self.repository = repository

    def identify(
        self,
        scene: SceneIdentifier,
        appearing_characters: list[str] | None = None,
    ) -> list[IdentifiedForeshadowing]:
        """Identify foreshadowing elements relevant to a scene.

        Analyzes all foreshadowing elements and returns those relevant
        to the specified scene, with suggested actions.

        Args:
            scene: Scene identifier.
            appearing_characters: List of characters appearing in the scene.
                Used for HINT identification.

        Returns:
            List of identified foreshadowing elements.
        """
        results: list[IdentifiedForeshadowing] = []
        already_identified_ids: set[str] = set()

        # Get all foreshadowing elements
        all_foreshadowings = self.repository.list_all()

        # 1. Find PLANT targets (registered + episode matches)
        for fs in all_foreshadowings:
            if self._should_plant(fs, scene):
                results.append(
                    IdentifiedForeshadowing(
                        foreshadowing_id=fs.id,
                        suggested_action=InstructionAction.PLANT,
                        status=fs.status.value,
                        relevance_reason=f"Episode {scene.episode_id} matches plant episode in ID",
                    )
                )
                already_identified_ids.add(fs.id)

        # 2. Find REINFORCE targets (planted + in reinforce timeline)
        for fs in all_foreshadowings:
            if fs.id not in already_identified_ids and self._should_reinforce(fs, scene):
                results.append(
                    IdentifiedForeshadowing(
                        foreshadowing_id=fs.id,
                        suggested_action=InstructionAction.REINFORCE,
                        status=fs.status.value,
                        relevance_reason=f"Episode {scene.episode_id} in reinforce timeline",
                    )
                )
                already_identified_ids.add(fs.id)

        # 3. Find HINT candidates (planted + related character appears)
        if appearing_characters:
            for fs in all_foreshadowings:
                if fs.id not in already_identified_ids and self._should_hint(
                    fs, scene, appearing_characters
                ):
                    results.append(
                        IdentifiedForeshadowing(
                            foreshadowing_id=fs.id,
                            suggested_action=InstructionAction.HINT,
                            status=fs.status.value,
                            relevance_reason="Related character appearing in scene",
                        )
                    )
                    already_identified_ids.add(fs.id)

        # 4. Check for reveal consideration
        for fs in all_foreshadowings:
            if fs.id not in already_identified_ids and self._is_reveal_episode(fs, scene):
                results.append(
                    IdentifiedForeshadowing(
                        foreshadowing_id=fs.id,
                        suggested_action=InstructionAction.REINFORCE,  # Prepare for reveal
                        status=fs.status.value,
                        relevance_reason=f"Episode {scene.episode_id} is planned reveal episode",
                    )
                )
                already_identified_ids.add(fs.id)

        return results

    def _should_plant(self, fs: Foreshadowing, scene: SceneIdentifier) -> bool:
        """Check if foreshadowing should be planted in this scene.

        Args:
            fs: Foreshadowing to check.
            scene: Scene identifier.

        Returns:
            True if this foreshadowing should be planted.
        """
        # Only registered foreshadowing can be planted
        if fs.status != ForeshadowingStatus.REGISTERED:
            return False

        # Check if episode in ID matches scene
        plant_episode = self._extract_episode_from_id(fs.id)
        if not plant_episode:
            return False

        return self._episode_matches(plant_episode, scene.episode_id)

    def _should_reinforce(self, fs: Foreshadowing, scene: SceneIdentifier) -> bool:
        """Check if foreshadowing should be reinforced in this scene.

        Args:
            fs: Foreshadowing to check.
            scene: Scene identifier.

        Returns:
            True if this foreshadowing should be reinforced.
        """
        # Only planted or reinforced can be reinforced further
        if fs.status not in (
            ForeshadowingStatus.PLANTED,
            ForeshadowingStatus.REINFORCED,
        ):
            return False

        # Check timeline for reinforce events matching this episode
        if fs.timeline and fs.timeline.events:
            for event in fs.timeline.events:
                if event.type == ForeshadowingStatus.REINFORCED:
                    if self._episode_matches(event.episode, scene.episode_id):
                        return True

        return False

    def _should_hint(
        self,
        fs: Foreshadowing,
        scene: SceneIdentifier,
        appearing_characters: list[str],
    ) -> bool:
        """Check if a hint should be given for this foreshadowing.

        Args:
            fs: Foreshadowing to check.
            scene: Scene identifier.
            appearing_characters: Characters appearing in the scene.

        Returns:
            True if a hint should be given.
        """
        # Only planted can receive hints
        if fs.status != ForeshadowingStatus.PLANTED:
            return False

        # Check if any related character appears
        if fs.related and fs.related.characters:
            for char in fs.related.characters:
                if char in appearing_characters:
                    return True

        return False

    def _is_reveal_episode(self, fs: Foreshadowing, scene: SceneIdentifier) -> bool:
        """Check if this is the planned reveal episode.

        Args:
            fs: Foreshadowing to check.
            scene: Scene identifier.

        Returns:
            True if this is the reveal episode.
        """
        # Check payoff's planned_episode
        if fs.payoff and fs.payoff.planned_episode:
            return self._episode_matches(fs.payoff.planned_episode, scene.episode_id)

        return False

    def _extract_episode_from_id(self, fs_id: str) -> str | None:
        """Extract episode number from foreshadowing ID.

        ID format: FS-{episode}-{slug}
        Example: FS-010-secret -> "010"

        Args:
            fs_id: Foreshadowing ID.

        Returns:
            Episode string, or None if not found.
        """
        match = self._ID_PATTERN.match(fs_id)
        if match:
            return match.group(1)
        return None

    def _episode_matches(self, ep1: str, ep2: str) -> bool:
        """Check if two episode identifiers match.

        Handles different formats (e.g., "010" vs "10", "ep010" vs "010").

        Args:
            ep1: First episode identifier.
            ep2: Second episode identifier.

        Returns:
            True if episodes match.
        """
        # Normalize: remove 'ep' prefix and leading zeros for comparison
        def normalize(ep: str) -> str:
            ep = ep.lower().replace("ep", "").lstrip("0")
            return ep if ep else "0"

        return normalize(ep1) == normalize(ep2)
