"""Tests for Character model."""

from datetime import date

import pytest
from pydantic import ValidationError

from src.core.models.character import AIVisibilitySettings, Character, Phase


class TestPhase:
    """Phase サブモデルのテスト."""

    def test_create_phase(self) -> None:
        """Phase を作成できる."""
        phase = Phase(name="序盤", episodes="1-10")

        assert phase.name == "序盤"
        assert phase.episodes == "1-10"

    def test_create_phase_open_ended(self) -> None:
        """終了未定のフェーズを作成できる."""
        phase = Phase(name="終盤", episodes="21-")

        assert phase.episodes == "21-"


class TestAIVisibilitySettings:
    """AIVisibilitySettings サブモデルのテスト."""

    def test_default_values(self) -> None:
        """デフォルト値が設定される."""
        settings = AIVisibilitySettings()

        assert settings.default == 0
        assert settings.hidden_section == 0

    def test_visibility_range(self) -> None:
        """可視性レベルは0-3の範囲."""
        settings = AIVisibilitySettings(default=3, hidden_section=2)

        assert settings.default == 3
        assert settings.hidden_section == 2

    def test_visibility_out_of_range(self) -> None:
        """範囲外の値はエラー."""
        with pytest.raises(ValidationError):
            AIVisibilitySettings(default=4)


class TestCharacter:
    """Character モデルのテスト."""

    def test_create_character_minimal(self) -> None:
        """最小限のフィールドでキャラクターを作成できる."""
        char = Character(
            name="主人公",
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

        assert char.type == "character"
        assert char.name == "主人公"
        assert char.phases == []
        assert char.current_phase is None
        assert char.tags == []
        assert char.sections == {}

    def test_create_character_with_phases(self) -> None:
        """フェーズ付きでキャラクターを作成できる."""
        char = Character(
            name="主人公",
            phases=[
                Phase(name="序盤", episodes="1-10"),
                Phase(name="中盤", episodes="11-20"),
            ],
            current_phase="序盤",
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

        assert len(char.phases) == 2
        assert char.current_phase == "序盤"
        assert char.phases[0].name == "序盤"

    def test_create_character_with_visibility(self) -> None:
        """AI可視性設定付きでキャラクターを作成できる."""
        char = Character(
            name="敵キャラ",
            ai_visibility=AIVisibilitySettings(default=2, hidden_section=3),
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

        assert char.ai_visibility.default == 2
        assert char.ai_visibility.hidden_section == 3

    def test_create_character_with_sections(self) -> None:
        """セクション付きでキャラクターを作成できる."""
        char = Character(
            name="主人公",
            sections={
                "基本情報": "名前: 太郎\n年齢: 25",
                "背景": "普通の会社員だったが...",
            },
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

        assert "基本情報" in char.sections
        assert "背景" in char.sections

    def test_character_to_dict(self) -> None:
        """キャラクターを辞書に変換できる."""
        char = Character(
            name="主人公",
            tags=["hero", "protagonist"],
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

        data = char.model_dump()

        assert data["type"] == "character"
        assert data["name"] == "主人公"
        assert data["tags"] == ["hero", "protagonist"]
