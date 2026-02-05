"""Tests for Settings model."""

import pytest
from pydantic import ValidationError

from src.core.models.settings import Settings


class TestSettings:
    """Settings model tests."""

    def test_create_settings_minimal(self) -> None:
        """Minimal Settings can be created with required fields."""
        settings = Settings(
            work_id="test-work",
            title="Test Novel",
            author="Test Author",
        )
        assert settings.work_id == "test-work"
        assert settings.title == "Test Novel"
        assert settings.author == "Test Author"

    def test_create_settings_full(self) -> None:
        """Full Settings can be created with all fields."""
        settings = Settings(
            work_id="test-work",
            title="Test Novel",
            author="Test Author",
            genre="Fantasy",
            target_audience="Young Adult",
            episode_naming="第{n}話",
            volumes_enabled=True,
            default_ai_visibility=0,
        )
        assert settings.genre == "Fantasy"
        assert settings.target_audience == "Young Adult"
        assert settings.episode_naming == "第{n}話"
        assert settings.volumes_enabled is True
        assert settings.default_ai_visibility == 0

    def test_settings_defaults(self) -> None:
        """Default values are set correctly."""
        settings = Settings(
            work_id="test-work",
            title="Test Novel",
            author="Test Author",
        )
        assert settings.genre == ""
        assert settings.target_audience == ""
        assert settings.episode_naming == "Episode {n}"
        assert settings.volumes_enabled is False
        assert settings.default_ai_visibility == 0  # Secure by Default

    def test_default_ai_visibility_secure_by_default(self) -> None:
        """Default AI visibility is 0 (HIDDEN) per Secure by Default principle."""
        settings = Settings(
            work_id="test-work",
            title="Test Novel",
            author="Test Author",
        )
        assert settings.default_ai_visibility == 0

    def test_ai_visibility_validation(self) -> None:
        """AI visibility level must be 0-3."""
        with pytest.raises(ValidationError):
            Settings(
                work_id="test-work",
                title="Test Novel",
                author="Test Author",
                default_ai_visibility=4,  # Invalid: must be 0-3
            )
        with pytest.raises(ValidationError):
            Settings(
                work_id="test-work",
                title="Test Novel",
                author="Test Author",
                default_ai_visibility=-1,  # Invalid: must be 0-3
            )
