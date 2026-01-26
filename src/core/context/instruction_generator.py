"""Instruction generator protocol for L3 context building.

This module defines the protocol for generating foreshadowing
instructions based on scene context and foreshadowing data.
"""

from typing import Any, Protocol

from .foreshadow_instruction import (
    ForeshadowInstructions,
    InstructionAction,
)
from .scene_identifier import SceneIdentifier


class InstructionGenerator(Protocol):
    """Protocol for generating foreshadowing instructions.

    Implementations analyze foreshadowing data and scene context
    to generate appropriate instructions for the Ghost Writer.
    """

    def generate(
        self,
        scene: SceneIdentifier,
        foreshadowings: list[dict[str, Any]],
    ) -> ForeshadowInstructions:
        """Generate foreshadowing instructions for a scene.

        Args:
            scene: The scene identifier.
            foreshadowings: List of foreshadowing data from L2 ForeshadowingManager.

        Returns:
            Generated ForeshadowInstructions.
        """
        ...

    def determine_action(
        self,
        foreshadowing: dict[str, Any],
        scene: SceneIdentifier,
    ) -> InstructionAction:
        """Determine the action for a foreshadowing element.

        Based on the foreshadowing status and scene relationship,
        determines the appropriate action (PLANT/REINFORCE/HINT/NONE).

        Decision logic:
        - registered + plant_scene matches -> PLANT
        - planted + in reinforce_scenes -> REINFORCE
        - planted + otherwise -> HINT or NONE
        - revealed -> NONE

        Args:
            foreshadowing: Foreshadowing data dict.
            scene: The scene identifier.

        Returns:
            The determined InstructionAction.
        """
        ...

    def collect_forbidden_keywords(
        self,
        instructions: ForeshadowInstructions,
    ) -> list[str]:
        """Collect all forbidden keywords from instructions.

        Args:
            instructions: The foreshadowing instructions.

        Returns:
            Deduplicated list of forbidden keywords.
        """
        ...
