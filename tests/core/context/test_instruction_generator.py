"""Tests for instruction generator protocol."""

from src.core.context.scene_identifier import SceneIdentifier
from src.core.context.foreshadow_instruction import (
    ForeshadowInstructions,
    ForeshadowInstruction,
    InstructionAction,
)
from src.core.context.instruction_generator import InstructionGenerator


class TestInstructionGeneratorProtocol:
    """Test InstructionGenerator protocol compliance."""

    def test_mock_implements_protocol(self):
        """Mock implements InstructionGenerator protocol."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                return ForeshadowInstructions()

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                return InstructionAction.NONE

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return []

        generator: InstructionGenerator = MockGenerator()
        scene = SceneIdentifier(episode_id="010")
        result = generator.generate(scene, [])
        assert isinstance(result, ForeshadowInstructions)

    def test_generate_with_empty_foreshadowings(self):
        """Generate empty instructions with no foreshadowings."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                return ForeshadowInstructions()

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                return InstructionAction.NONE

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return []

        generator: InstructionGenerator = MockGenerator()
        scene = SceneIdentifier(episode_id="010")
        result = generator.generate(scene, [])

        assert isinstance(result, ForeshadowInstructions)
        assert len(result.instructions) == 0
        assert len(result.global_forbidden_keywords) == 0

    def test_generate_with_foreshadowings(self):
        """Generate instructions with foreshadowings."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                instructions = ForeshadowInstructions()
                for fs in foreshadowings:
                    inst = ForeshadowInstruction(
                        foreshadowing_id=fs["id"],
                        action=InstructionAction.PLANT,
                    )
                    instructions.add_instruction(inst)
                return instructions

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                return InstructionAction.PLANT

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return []

        generator: InstructionGenerator = MockGenerator()
        scene = SceneIdentifier(episode_id="010")
        foreshadowings = [{"id": "FS-001"}, {"id": "FS-002"}]
        result = generator.generate(scene, foreshadowings)

        assert len(result.instructions) == 2
        assert result.instructions[0].foreshadowing_id == "FS-001"
        assert result.instructions[1].foreshadowing_id == "FS-002"

    def test_determine_action_plant(self):
        """Determine PLANT action."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                return ForeshadowInstructions()

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                if (
                    foreshadowing.get("status") == "registered"
                    and foreshadowing.get("plant_scene") == scene.episode_id
                ):
                    return InstructionAction.PLANT
                return InstructionAction.NONE

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return []

        generator: InstructionGenerator = MockGenerator()
        scene = SceneIdentifier(episode_id="010")
        foreshadowing = {
            "id": "FS-001",
            "status": "registered",
            "plant_scene": "010",
        }

        action = generator.determine_action(foreshadowing, scene)
        assert action == InstructionAction.PLANT

    def test_determine_action_reinforce(self):
        """Determine REINFORCE action."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                return ForeshadowInstructions()

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                if (
                    foreshadowing.get("status") == "planted"
                    and scene.episode_id in foreshadowing.get("reinforce_scenes", [])
                ):
                    return InstructionAction.REINFORCE
                return InstructionAction.NONE

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return []

        generator: InstructionGenerator = MockGenerator()
        scene = SceneIdentifier(episode_id="015")
        foreshadowing = {
            "id": "FS-001",
            "status": "planted",
            "reinforce_scenes": ["015", "020"],
        }

        action = generator.determine_action(foreshadowing, scene)
        assert action == InstructionAction.REINFORCE

    def test_determine_action_hint(self):
        """Determine HINT action."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                return ForeshadowInstructions()

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                if foreshadowing.get("status") == "planted":
                    return InstructionAction.HINT
                return InstructionAction.NONE

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return []

        generator: InstructionGenerator = MockGenerator()
        scene = SceneIdentifier(episode_id="012")
        foreshadowing = {
            "id": "FS-001",
            "status": "planted",
        }

        action = generator.determine_action(foreshadowing, scene)
        assert action == InstructionAction.HINT

    def test_determine_action_none(self):
        """Determine NONE action for revealed foreshadowing."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                return ForeshadowInstructions()

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                if foreshadowing.get("status") == "revealed":
                    return InstructionAction.NONE
                return InstructionAction.NONE

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return []

        generator: InstructionGenerator = MockGenerator()
        scene = SceneIdentifier(episode_id="050")
        foreshadowing = {
            "id": "FS-001",
            "status": "revealed",
        }

        action = generator.determine_action(foreshadowing, scene)
        assert action == InstructionAction.NONE

    def test_collect_forbidden_keywords_empty(self):
        """Collect forbidden keywords returns empty list when none exist."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                return ForeshadowInstructions()

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                return InstructionAction.NONE

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return instructions.get_all_forbidden()

        generator: InstructionGenerator = MockGenerator()
        instructions = ForeshadowInstructions()

        keywords = generator.collect_forbidden_keywords(instructions)
        assert keywords == []

    def test_collect_forbidden_keywords_deduplicates(self):
        """Collect forbidden keywords deduplicates and sorts."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                return ForeshadowInstructions()

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                return InstructionAction.NONE

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return instructions.get_all_forbidden()

        generator: InstructionGenerator = MockGenerator()
        instructions = ForeshadowInstructions()

        inst1 = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.PLANT,
            forbidden_expressions=["royal", "princess"],
        )
        inst2 = ForeshadowInstruction(
            foreshadowing_id="FS-002",
            action=InstructionAction.REINFORCE,
            forbidden_expressions=["princess", "blood"],
        )
        instructions.add_instruction(inst1)
        instructions.add_instruction(inst2)
        instructions.add_global_forbidden("royal")

        keywords = generator.collect_forbidden_keywords(instructions)
        # Should be deduplicated and sorted
        assert keywords == ["blood", "princess", "royal"]
