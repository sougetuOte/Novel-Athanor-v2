"""Tests for PhaseFilter protocol and related classes."""

from datetime import date

import pytest

from src.core.context.phase_filter import (
    InvalidPhaseError,
    PhaseFilter,
    PhaseFilterError,
)


class TestPhaseFilterExceptions:
    """Test exception classes."""

    def test_phase_filter_error_exists(self):
        """PhaseFilterError が存在する."""
        error = PhaseFilterError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_invalid_phase_error_exists(self):
        """InvalidPhaseError が存在する."""
        error = InvalidPhaseError("Invalid phase: xyz")
        assert str(error) == "Invalid phase: xyz"
        assert isinstance(error, PhaseFilterError)

    def test_invalid_phase_error_inheritance(self):
        """InvalidPhaseError は PhaseFilterError を継承."""
        error = InvalidPhaseError("test")
        assert isinstance(error, PhaseFilterError)
        assert isinstance(error, Exception)


class TestPhaseFilterProtocol:
    """Test PhaseFilter protocol compliance."""

    def test_protocol_compliance_with_dict(self):
        """Protocol を満たす具象クラスを作成できる（dict型）."""

        class DictPhaseFilter:
            """Mock implementation for dict data."""

            def filter_by_phase(
                self, entity: dict, phase: str
            ) -> dict:
                """Filter dict by phase."""
                if "phases" not in entity:
                    return entity

                available_phases = list(entity["phases"].keys())
                if phase not in available_phases:
                    raise InvalidPhaseError(f"Invalid phase: {phase}")

                # Collect all phases up to and including the current phase
                result = {"name": entity.get("name", "")}
                result["filtered_data"] = entity["phases"].get(phase, {})
                return result

            def get_available_phases(self, entity: dict) -> list[str]:
                """Get available phases from dict."""
                if "phases" not in entity:
                    return []
                return list(entity["phases"].keys())

        filter_impl: PhaseFilter[dict] = DictPhaseFilter()

        # Test entity
        entity = {
            "name": "Alice",
            "phases": {
                "initial": {"description": "Village girl"},
                "arc_1_reveal": {"description": "Secret princess"},
            },
        }

        # get_available_phases works
        phases = filter_impl.get_available_phases(entity)
        assert "initial" in phases
        assert "arc_1_reveal" in phases

        # filter_by_phase works
        filtered = filter_impl.filter_by_phase(entity, "initial")
        assert filtered["name"] == "Alice"
        assert filtered["filtered_data"]["description"] == "Village girl"

    def test_protocol_compliance_with_custom_class(self):
        """Protocol を満たす具象クラスを作成できる（カスタムクラス型）."""

        class CharacterData:
            """Simple character data class."""

            def __init__(self, name: str, phases: dict[str, str]):
                self.name = name
                self.phases = phases

        class CharacterPhaseFilter:
            """Phase filter for CharacterData."""

            def filter_by_phase(
                self, entity: CharacterData, phase: str
            ) -> CharacterData:
                if phase not in entity.phases:
                    raise InvalidPhaseError(f"Invalid phase: {phase}")
                # Return new instance with filtered data
                return CharacterData(
                    name=entity.name,
                    phases={phase: entity.phases[phase]},
                )

            def get_available_phases(self, entity: CharacterData) -> list[str]:
                return list(entity.phases.keys())

        filter_impl: PhaseFilter[CharacterData] = CharacterPhaseFilter()

        character = CharacterData(
            name="Bob",
            phases={"start": "Unknown traveler", "reveal": "Lost prince"},
        )

        phases = filter_impl.get_available_phases(character)
        assert len(phases) == 2

        filtered = filter_impl.filter_by_phase(character, "start")
        assert filtered.name == "Bob"
        assert "start" in filtered.phases

    def test_invalid_phase_handling(self):
        """無効なフェーズが指定された場合の処理."""

        class StrictPhaseFilter:
            """Filter that validates phases strictly."""

            def filter_by_phase(self, entity: dict, phase: str) -> dict:
                valid_phases = self.get_available_phases(entity)
                if phase not in valid_phases:
                    raise InvalidPhaseError(
                        f"Phase '{phase}' not found. Available: {valid_phases}"
                    )
                return entity

            def get_available_phases(self, entity: dict) -> list[str]:
                return entity.get("phases", [])

        filter_impl: PhaseFilter[dict] = StrictPhaseFilter()
        entity = {"phases": ["phase_a", "phase_b"]}

        with pytest.raises(InvalidPhaseError) as exc_info:
            filter_impl.filter_by_phase(entity, "invalid_phase")

        assert "invalid_phase" in str(exc_info.value)


class TestPhaseFilterUseCases:
    """Test practical use cases for phase filtering."""

    def test_character_phase_progression(self):
        """キャラクター情報のフェーズ進行テスト."""

        class CumulativePhaseFilter:
            """Filter that accumulates information up to the specified phase."""

            def __init__(self, phase_order: list[str]):
                self.phase_order = phase_order

            def filter_by_phase(self, entity: dict, phase: str) -> dict:
                if phase not in self.phase_order:
                    raise InvalidPhaseError(f"Unknown phase: {phase}")

                # Get all phases up to and including the current one
                phase_index = self.phase_order.index(phase)
                applicable_phases = self.phase_order[: phase_index + 1]

                # Accumulate data
                result = {"name": entity.get("name")}
                accumulated_info = []
                for p in applicable_phases:
                    if p in entity.get("phases", {}):
                        accumulated_info.append(entity["phases"][p])
                result["info"] = " | ".join(accumulated_info)
                return result

            def get_available_phases(self, entity: dict) -> list[str]:
                return [p for p in self.phase_order if p in entity.get("phases", {})]

        # Define phase progression
        phase_order = ["initial", "arc_1", "arc_2", "finale"]
        filter_impl: PhaseFilter[dict] = CumulativePhaseFilter(phase_order)

        character = {
            "name": "Hero",
            "phases": {
                "initial": "A young farmer",
                "arc_1": "Discovers magic powers",
                "arc_2": "Trained by mentor",
                "finale": "Defeats evil lord",
            },
        }

        # At arc_1, should see initial + arc_1
        filtered_arc1 = filter_impl.filter_by_phase(character, "arc_1")
        assert "young farmer" in filtered_arc1["info"]
        assert "magic powers" in filtered_arc1["info"]
        assert "mentor" not in filtered_arc1["info"]

        # At finale, should see everything
        filtered_finale = filter_impl.filter_by_phase(character, "finale")
        assert "young farmer" in filtered_finale["info"]
        assert "evil lord" in filtered_finale["info"]

    def test_empty_entity_handling(self):
        """空のエンティティの処理."""

        class SafePhaseFilter:
            """Filter that handles empty entities gracefully."""

            def filter_by_phase(self, entity: dict, phase: str) -> dict:
                return entity  # Return as-is if no phases

            def get_available_phases(self, entity: dict) -> list[str]:
                return []

        filter_impl: PhaseFilter[dict] = SafePhaseFilter()
        empty_entity: dict = {}

        result = filter_impl.filter_by_phase(empty_entity, "any_phase")
        assert result == {}
        assert filter_impl.get_available_phases(empty_entity) == []


class TestCharacterPhaseFilter:
    """Test CharacterPhaseFilter concrete implementation."""

    @pytest.fixture
    def phase_order(self):
        """Define phase progression order."""
        return ["initial", "arc_1", "arc_2", "finale"]

    @pytest.fixture
    def character(self):
        """Create a test character with phases."""
        from src.core.models.character import Character, Phase

        return Character(
            name="Alice",
            phases=[
                Phase(name="initial", episodes="1-5"),
                Phase(name="arc_1", episodes="6-15"),
                Phase(name="finale", episodes="16-"),
            ],
            sections={
                "basic": "Basic info visible always",
                "initial_secret": "Secret for initial phase",
                "arc_1_reveal": "Revealed in arc_1",
            },
            created=date(2026, 1, 26),
            updated=date(2026, 1, 26),
        )

    @pytest.fixture
    def filter(self, phase_order):
        """Create CharacterPhaseFilter instance."""
        from src.core.context.phase_filter import CharacterPhaseFilter

        return CharacterPhaseFilter(phase_order)

    def test_filter_by_phase_initial(self, filter, character):
        """Filter character at initial phase - should only see initial phase."""
        filtered = filter.filter_by_phase(character, "initial")
        assert filtered.name == "Alice"

        # Only initial phase should be included
        phase_names = [p.name for p in filtered.phases]
        assert "initial" in phase_names
        assert "arc_1" not in phase_names
        assert "finale" not in phase_names

    def test_filter_by_phase_arc_1(self, filter, character):
        """Filter at arc_1 - should see initial + arc_1, but not finale."""
        filtered = filter.filter_by_phase(character, "arc_1")
        phase_names = [p.name for p in filtered.phases]
        assert "initial" in phase_names
        assert "arc_1" in phase_names
        assert "finale" not in phase_names

    def test_filter_by_phase_finale(self, filter, character):
        """Filter at finale - should see all phases."""
        filtered = filter.filter_by_phase(character, "finale")
        phase_names = [p.name for p in filtered.phases]
        assert "initial" in phase_names
        assert "arc_1" in phase_names
        assert "finale" in phase_names

    def test_filter_by_phase_arc_2_no_data(self, filter, character):
        """Filter at arc_2 - character has no arc_2 data, but filter should work."""
        # arc_2 is in phase_order but not in character's phases
        filtered = filter.filter_by_phase(character, "arc_2")
        phase_names = [p.name for p in filtered.phases]
        # Should see initial and arc_1, but not finale
        assert "initial" in phase_names
        assert "arc_1" in phase_names
        assert "arc_2" not in phase_names
        assert "finale" not in phase_names

    def test_filter_by_phase_invalid(self, filter, character):
        """Filter with invalid phase should raise InvalidPhaseError."""
        with pytest.raises(InvalidPhaseError) as exc_info:
            filter.filter_by_phase(character, "unknown_phase")
        assert "unknown_phase" in str(exc_info.value)

    def test_get_available_phases(self, filter, character):
        """Get phases that are available in the character."""
        phases = filter.get_available_phases(character)
        assert "initial" in phases
        assert "arc_1" in phases
        assert "finale" in phases
        # arc_2 is in phase_order but not in character
        assert "arc_2" not in phases

    def test_get_available_phases_empty(self, filter):
        """Get phases from character with no phases."""
        from src.core.models.character import Character

        char = Character(
            name="NPC",
            created=date(2026, 1, 26),
            updated=date(2026, 1, 26),
        )
        phases = filter.get_available_phases(char)
        assert phases == []

    def test_to_context_string(self, filter, character):
        """Convert filtered character to context string."""
        context = filter.to_context_string(character, "initial")
        assert "Alice" in context
        assert "basic" in context.lower() or "Basic info" in context

    def test_filter_preserves_other_fields(self, filter, character):
        """Filter should preserve other fields like name, sections, etc."""
        filtered = filter.filter_by_phase(character, "initial")
        assert filtered.name == character.name
        assert filtered.sections == character.sections
        assert filtered.created == character.created
        assert filtered.updated == character.updated
        assert filtered.tags == character.tags

    def test_filter_preserves_all_fields_via_model_copy(self, filter):
        """filter_by_phase preserves all fields including any new ones.

        This test validates that using model_copy(update={...}) ensures
        all fields are preserved even if new fields are added to the model.
        """
        from src.core.models.character import AIVisibilitySettings, Character, Phase

        # Character with all fields populated
        character = Character(
            name="Test",
            type="character",
            phases=[
                Phase(name="initial", episodes="1-5"),
                Phase(name="arc_1", episodes="6-10"),
            ],
            current_phase="initial",
            ai_visibility=AIVisibilitySettings(),
            sections={"background": "Test background"},
            created=date(2024, 1, 1),
            updated=date(2024, 1, 2),
            tags=["tag1", "tag2"],
        )

        result = filter.filter_by_phase(character, "initial")

        # Should preserve all non-phase fields
        assert result.name == "Test"
        assert result.type == "character"
        assert result.current_phase == "initial"
        assert result.sections == {"background": "Test background"}
        assert result.created == date(2024, 1, 1)
        assert result.updated == date(2024, 1, 2)
        assert result.tags == ["tag1", "tag2"]
        # Phase should be filtered
        assert len(result.phases) == 1
        assert result.phases[0].name == "initial"


class TestWorldSettingPhaseFilter:
    """Test WorldSettingPhaseFilter concrete implementation."""

    @pytest.fixture
    def phase_order(self):
        """Define phase progression order."""
        return ["initial", "arc_1", "arc_2", "finale"]

    @pytest.fixture
    def world_setting(self):
        """Create a test world setting with phases."""
        from src.core.models.world_setting import Phase, WorldSetting

        return WorldSetting(
            name="Magic System",
            category="System",
            phases=[
                Phase(name="initial", episodes="1-5"),
                Phase(name="arc_2", episodes="10-15"),
            ],
            sections={
                "basic": "Basic magic rules",
                "advanced": "Advanced concepts revealed later",
            },
            created=date(2026, 1, 26),
            updated=date(2026, 1, 26),
        )

    @pytest.fixture
    def filter(self, phase_order):
        """Create WorldSettingPhaseFilter instance."""
        from src.core.context.phase_filter import WorldSettingPhaseFilter

        return WorldSettingPhaseFilter(phase_order)

    def test_filter_by_phase_initial(self, filter, world_setting):
        """Filter world setting at initial phase."""
        filtered = filter.filter_by_phase(world_setting, "initial")
        assert filtered.name == "Magic System"
        assert filtered.category == "System"

        phase_names = [p.name for p in filtered.phases]
        assert "initial" in phase_names
        assert "arc_2" not in phase_names

    def test_filter_by_phase_arc_1(self, filter, world_setting):
        """Filter at arc_1 - should see initial but not arc_2."""
        filtered = filter.filter_by_phase(world_setting, "arc_1")
        phase_names = [p.name for p in filtered.phases]
        assert "initial" in phase_names
        assert "arc_2" not in phase_names

    def test_filter_by_phase_arc_2(self, filter, world_setting):
        """Filter at arc_2 - should see both initial and arc_2."""
        filtered = filter.filter_by_phase(world_setting, "arc_2")
        phase_names = [p.name for p in filtered.phases]
        assert "initial" in phase_names
        assert "arc_2" in phase_names

    def test_filter_by_phase_invalid(self, filter, world_setting):
        """Invalid phase should raise InvalidPhaseError."""
        with pytest.raises(InvalidPhaseError):
            filter.filter_by_phase(world_setting, "unknown_phase")

    def test_get_available_phases(self, filter, world_setting):
        """Get available phases from world setting."""
        phases = filter.get_available_phases(world_setting)
        assert "initial" in phases
        assert "arc_2" in phases
        # arc_1 and finale are not in this world setting
        assert "arc_1" not in phases
        assert "finale" not in phases

    def test_to_context_string(self, filter, world_setting):
        """Convert filtered world setting to context string."""
        context = filter.to_context_string(world_setting, "initial")
        assert "Magic System" in context
        assert "System" in context

    def test_filter_preserves_other_fields(self, filter, world_setting):
        """Filter should preserve other fields."""
        filtered = filter.filter_by_phase(world_setting, "initial")
        assert filtered.name == world_setting.name
        assert filtered.category == world_setting.category
        assert filtered.sections == world_setting.sections
        assert filtered.created == world_setting.created
        assert filtered.updated == world_setting.updated

    def test_filter_preserves_all_fields_via_model_copy(self, filter):
        """filter_by_phase preserves all fields including any new ones.

        This test validates that using model_copy(update={...}) ensures
        all fields are preserved even if new fields are added to the model.
        """
        from src.core.models.character import AIVisibilitySettings, Phase
        from src.core.models.world_setting import WorldSetting

        # WorldSetting with all fields populated
        world_setting = WorldSetting(
            name="TestSetting",
            category="Location",
            phases=[
                Phase(name="initial", episodes="1-5"),
                Phase(name="arc_1", episodes="6-10"),
            ],
            current_phase="initial",
            ai_visibility=AIVisibilitySettings(),
            sections={"description": "Test description"},
            created=date(2024, 1, 1),
            updated=date(2024, 1, 2),
            tags=["tag1", "tag2"],
        )

        result = filter.filter_by_phase(world_setting, "initial")

        # Should preserve all non-phase fields
        assert result.name == "TestSetting"
        assert result.category == "Location"
        assert result.current_phase == "initial"
        assert result.sections == {"description": "Test description"}
        assert result.created == date(2024, 1, 1)
        assert result.updated == date(2024, 1, 2)
        assert result.tags == ["tag1", "tag2"]
        # Phase should be filtered
        assert len(result.phases) == 1
        assert result.phases[0].name == "initial"
