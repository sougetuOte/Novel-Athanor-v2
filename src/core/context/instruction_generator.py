"""Instruction generator protocol and implementation for L3 context building.

This module defines the protocol for generating foreshadowing
instructions based on scene context and foreshadowing data,
as well as the concrete implementation.
"""

from typing import Any, Protocol

from src.core.models.foreshadowing import Foreshadowing
from src.core.repositories.foreshadowing import ForeshadowingRepository

from .foreshadow_instruction import (
    ForeshadowInstruction,
    ForeshadowInstructions,
    InstructionAction,
)
from .foreshadowing_identifier import ForeshadowingIdentifier, IdentifiedForeshadowing
from .scene_identifier import SceneIdentifier


class InstructionGenerator(Protocol):
    """Protocol for generating foreshadowing instructions.

    Implementations analyze foreshadowing data and scene context
    to generate appropriate instructions for the Ghost Writer.
    """

    def generate(
        self,
        scene: SceneIdentifier,
        appearing_characters: list[str] | None = None,
    ) -> ForeshadowInstructions:
        """Generate foreshadowing instructions for a scene.

        Args:
            scene: The scene identifier.
            appearing_characters: Characters appearing in the scene (for HINT detection).

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


class InstructionGeneratorImpl:
    """Concrete implementation of InstructionGenerator.

    Generates foreshadowing instructions by using ForeshadowingIdentifier
    to find relevant foreshadowing elements and creating appropriate
    instructions for each.

    Attributes:
        repository: Foreshadowing repository for data access.
        identifier: Foreshadowing identifier for scene analysis.
    """

    # Instruction notes by action type
    _ACTION_NOTES: dict[InstructionAction, str] = {
        InstructionAction.PLANT: "伏線の初回設置。",
        InstructionAction.REINFORCE: "伏線の強化。控えめに想起させてください。",
        InstructionAction.HINT: "非常に控えめなヒントのみ。気づかなくても問題ない程度に。",
        InstructionAction.NONE: "この伏線には今回触れないでください。",
    }

    # Base subtlety values by action type
    _BASE_SUBTLETY: dict[InstructionAction, int] = {
        InstructionAction.PLANT: 4,
        InstructionAction.REINFORCE: 6,
        InstructionAction.HINT: 8,
        InstructionAction.NONE: 10,
    }

    def __init__(
        self,
        repository: ForeshadowingRepository,
        identifier: ForeshadowingIdentifier,
    ) -> None:
        """Initialize InstructionGeneratorImpl.

        Args:
            repository: Foreshadowing repository instance.
            identifier: Foreshadowing identifier instance.
        """
        self.repository = repository
        self.identifier = identifier

    def generate(
        self,
        scene: SceneIdentifier,
        appearing_characters: list[str] | None = None,
    ) -> ForeshadowInstructions:
        """Generate foreshadowing instructions for a scene.

        Args:
            scene: The scene identifier.
            appearing_characters: Characters appearing in the scene.

        Returns:
            Generated ForeshadowInstructions.
        """
        instructions = ForeshadowInstructions()

        # Identify relevant foreshadowing elements
        identified = self.identifier.identify(scene, appearing_characters)

        # Generate instruction for each identified element
        for item in identified:
            instruction = self._generate_instruction(item)
            if instruction is not None:
                instructions.add_instruction(instruction)

        return instructions

    def _generate_instruction(
        self,
        identified: IdentifiedForeshadowing,
    ) -> ForeshadowInstruction | None:
        """Generate a single instruction from identified foreshadowing.

        Args:
            identified: Identified foreshadowing element.

        Returns:
            Generated instruction, or None if foreshadowing not found.
        """
        try:
            fs = self.repository.read(identified.foreshadowing_id)
        except (KeyError, FileNotFoundError):
            # Foreshadowing was identified but no longer exists in repository
            return None
        action = identified.suggested_action

        # Build note (PLANT may include seed description)
        note = self._ACTION_NOTES[action]
        if action == InstructionAction.PLANT and fs.seed and fs.seed.description:
            note = f"{note} {fs.seed.description}"

        # NONE action doesn't use allowed_expressions
        allowed = [] if action == InstructionAction.NONE else list(fs.ai_visibility.allowed_expressions)

        return ForeshadowInstruction(
            foreshadowing_id=fs.id,
            action=action,
            allowed_expressions=allowed,
            forbidden_expressions=list(fs.ai_visibility.forbidden_keywords),
            note=note,
            subtlety_target=self._calculate_subtlety(fs, action),
        )

    def _calculate_subtlety(
        self,
        fs: Foreshadowing,
        action: InstructionAction,
    ) -> int:
        """Calculate subtlety_target based on action and foreshadowing settings.

        Args:
            fs: Foreshadowing data.
            action: The action being taken.

        Returns:
            Subtlety target (1-10).
        """
        base = self._BASE_SUBTLETY.get(action, 5)

        # Adjust based on foreshadowing's own subtlety_level
        if fs.subtlety_level >= 7:
            adjustment = 2
        elif fs.subtlety_level <= 3:
            adjustment = -2
        else:
            adjustment = 0

        return max(1, min(10, base + adjustment))

    def determine_action(
        self,
        foreshadowing: dict[str, Any],
        scene: SceneIdentifier,
    ) -> InstructionAction:
        """Determine action for a foreshadowing element (Protocol method).

        This method determines the action for a single foreshadowing element
        by reading it from the repository and checking its status and timeline
        against the scene.

        Args:
            foreshadowing: Foreshadowing data as dict (must have 'id' key).
            scene: Scene identifier.

        Returns:
            Determined action.
        """
        fs_id = foreshadowing.get("id")
        if not fs_id:
            return InstructionAction.NONE

        try:
            fs = self.repository.read(fs_id)
        except (KeyError, FileNotFoundError):
            return InstructionAction.NONE

        # Check status and determine action directly
        from src.core.models.foreshadowing import ForeshadowingStatus

        # REGISTERED -> check if this is plant episode
        if fs.status == ForeshadowingStatus.REGISTERED:
            plant_episode = self.identifier._extract_episode_from_id(fs_id)
            if plant_episode and self.identifier._episode_matches(plant_episode, scene.episode_id):
                return InstructionAction.PLANT

        # PLANTED/REINFORCED -> check for reinforce timeline
        if fs.status in (ForeshadowingStatus.PLANTED, ForeshadowingStatus.REINFORCED):
            if fs.timeline and fs.timeline.events:
                for event in fs.timeline.events:
                    if event.type == ForeshadowingStatus.REINFORCED:
                        if self.identifier._episode_matches(event.episode, scene.episode_id):
                            return InstructionAction.REINFORCE

        # Check if reveal episode
        if fs.payoff and fs.payoff.planned_episode:
            if self.identifier._episode_matches(fs.payoff.planned_episode, scene.episode_id):
                return InstructionAction.REINFORCE

        return InstructionAction.NONE

    def collect_forbidden_keywords(
        self,
        instructions: ForeshadowInstructions,
    ) -> list[str]:
        """Collect all forbidden keywords from instructions.

        Args:
            instructions: Foreshadowing instructions.

        Returns:
            Deduplicated list of forbidden keywords.
        """
        return instructions.get_all_forbidden()
