"""Tests for PhaseFilter protocol and related classes."""

import pytest
from typing import TypeVar

from src.core.context.phase_filter import (
    PhaseFilter,
    PhaseFilterError,
    InvalidPhaseError,
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
