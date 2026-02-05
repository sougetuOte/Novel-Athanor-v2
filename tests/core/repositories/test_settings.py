"""Tests for SettingsRepository."""

from pathlib import Path

import pytest

from src.core.models.settings import Settings
from src.core.repositories.base import EntityExistsError, EntityNotFoundError
from src.core.repositories.settings import SettingsRepository


class TestSettingsRepository:
    """SettingsRepository tests."""

    @pytest.fixture
    def temp_vault(self, tmp_path: Path) -> Path:
        """Create temporary vault."""
        return tmp_path

    @pytest.fixture
    def repo(self, temp_vault: Path) -> SettingsRepository:
        """Create test repository."""
        return SettingsRepository(temp_vault)

    @pytest.fixture
    def sample_settings(self) -> Settings:
        """Create sample settings."""
        return Settings(
            work_id="test-work",
            title="Test Novel",
            author="Test Author",
            genre="Fantasy",
            target_audience="Young Adult",
            episode_naming="第{n}話",
            volumes_enabled=True,
            default_ai_visibility=0,
        )

    def test_create_settings(
        self, repo: SettingsRepository, sample_settings: Settings
    ) -> None:
        """Settings can be created."""
        path = repo.create(sample_settings)

        assert path.exists()
        assert path.name == "settings.yaml"

    def test_create_duplicate_raises_error(
        self, repo: SettingsRepository, sample_settings: Settings
    ) -> None:
        """Creating duplicate settings raises error."""
        repo.create(sample_settings)

        with pytest.raises(EntityExistsError):
            repo.create(sample_settings)

    def test_read_settings(
        self, repo: SettingsRepository, sample_settings: Settings
    ) -> None:
        """Settings can be read."""
        repo.create(sample_settings)
        settings = repo.read("test-work")

        assert settings.work_id == "test-work"
        assert settings.title == "Test Novel"
        assert settings.author == "Test Author"
        assert settings.genre == "Fantasy"

    def test_read_nonexistent_raises_error(self, repo: SettingsRepository) -> None:
        """Reading nonexistent settings raises error."""
        with pytest.raises(EntityNotFoundError):
            repo.read("nonexistent")

    def test_update_settings(
        self, repo: SettingsRepository, sample_settings: Settings
    ) -> None:
        """Settings can be updated."""
        repo.create(sample_settings)

        sample_settings.title = "Updated Title"
        repo.update(sample_settings)

        updated = repo.read("test-work")
        assert updated.title == "Updated Title"

    def test_update_nonexistent_raises_error(
        self, repo: SettingsRepository, sample_settings: Settings
    ) -> None:
        """Updating nonexistent settings raises error."""
        with pytest.raises(EntityNotFoundError):
            repo.update(sample_settings)

    def test_delete_settings(
        self, repo: SettingsRepository, sample_settings: Settings
    ) -> None:
        """Settings can be deleted."""
        repo.create(sample_settings)
        repo.delete("test-work")

        assert not repo.exists("test-work")

    def test_delete_nonexistent_raises_error(self, repo: SettingsRepository) -> None:
        """Deleting nonexistent settings raises error."""
        with pytest.raises(EntityNotFoundError):
            repo.delete("nonexistent")

    def test_exists(
        self, repo: SettingsRepository, sample_settings: Settings
    ) -> None:
        """Existence check works."""
        assert not repo.exists("test-work")

        repo.create(sample_settings)
        assert repo.exists("test-work")

    def test_settings_file_format(
        self, repo: SettingsRepository, sample_settings: Settings, temp_vault: Path
    ) -> None:
        """Settings file is created in YAML format."""
        repo.create(sample_settings)
        settings_file = temp_vault / "settings.yaml"

        content = settings_file.read_text(encoding="utf-8")
        assert "work_id: test-work" in content
        assert "title: Test Novel" in content
        assert "author: Test Author" in content
