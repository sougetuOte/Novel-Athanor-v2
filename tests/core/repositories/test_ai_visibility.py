"""Tests for AIVisibilityRepository."""

from pathlib import Path

import pytest

from src.core.models.ai_visibility import (
    AIVisibilityLevel,
    EntityVisibilityConfig,
    SectionVisibility,
    VisibilityConfig,
)
from src.core.repositories.ai_visibility import AIVisibilityRepository
from src.core.repositories.base import EntityExistsError, EntityNotFoundError


class TestAIVisibilityRepository:
    """AIVisibilityRepository tests."""

    @pytest.fixture
    def temp_vault(self, tmp_path: Path) -> Path:
        """Create temporary vault."""
        (tmp_path / "_ai_control").mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def repo(self, temp_vault: Path) -> AIVisibilityRepository:
        """Create test repository."""
        return AIVisibilityRepository(temp_vault)

    @pytest.fixture
    def sample_visibility_config(self) -> VisibilityConfig:
        """Create sample visibility config."""
        return VisibilityConfig(
            version="1.0",
            default_visibility=AIVisibilityLevel.HIDDEN,
            entities=[
                EntityVisibilityConfig(
                    entity_type="character",
                    entity_name="主人公",
                    default_level=AIVisibilityLevel.USE,
                    sections=[
                        SectionVisibility(
                            section_name="基本情報",
                            level=AIVisibilityLevel.USE,
                        ),
                        SectionVisibility(
                            section_name="隠し設定",
                            level=AIVisibilityLevel.HIDDEN,
                            forbidden_keywords=["秘密", "真実"],
                        ),
                    ],
                ),
                EntityVisibilityConfig(
                    entity_type="world_setting",
                    entity_name="魔法システム",
                    default_level=AIVisibilityLevel.KNOW,
                ),
            ],
        )

    def test_create_visibility_config(
        self, repo: AIVisibilityRepository, sample_visibility_config: VisibilityConfig
    ) -> None:
        """Visibility config can be created."""
        path = repo.create(sample_visibility_config)

        assert path.exists()
        assert path.name == "visibility.yaml"
        assert "_ai_control" in str(path)

    def test_create_duplicate_raises_error(
        self, repo: AIVisibilityRepository, sample_visibility_config: VisibilityConfig
    ) -> None:
        """Creating duplicate visibility config raises error."""
        repo.create(sample_visibility_config)

        with pytest.raises(EntityExistsError):
            repo.create(sample_visibility_config)

    def test_read_visibility_config(
        self, repo: AIVisibilityRepository, sample_visibility_config: VisibilityConfig
    ) -> None:
        """Visibility config can be read."""
        repo.create(sample_visibility_config)
        config = repo.read()

        assert config.version == "1.0"
        assert config.default_visibility == AIVisibilityLevel.HIDDEN
        assert len(config.entities) == 2

    def test_read_nonexistent_raises_error(self, repo: AIVisibilityRepository) -> None:
        """Reading nonexistent visibility config raises error."""
        with pytest.raises(EntityNotFoundError):
            repo.read()

    def test_update_visibility_config(
        self, repo: AIVisibilityRepository, sample_visibility_config: VisibilityConfig
    ) -> None:
        """Visibility config can be updated."""
        repo.create(sample_visibility_config)

        sample_visibility_config.default_visibility = AIVisibilityLevel.AWARE
        repo.update(sample_visibility_config)

        updated = repo.read()
        assert updated.default_visibility == AIVisibilityLevel.AWARE

    def test_delete_visibility_config(
        self, repo: AIVisibilityRepository, sample_visibility_config: VisibilityConfig
    ) -> None:
        """Visibility config can be deleted."""
        repo.create(sample_visibility_config)
        repo.delete()

        assert not repo.exists()

    def test_exists(
        self, repo: AIVisibilityRepository, sample_visibility_config: VisibilityConfig
    ) -> None:
        """Existence check works."""
        assert not repo.exists()

        repo.create(sample_visibility_config)
        assert repo.exists()

    def test_get_entity_config(
        self, repo: AIVisibilityRepository, sample_visibility_config: VisibilityConfig
    ) -> None:
        """Can get entity config from visibility config."""
        repo.create(sample_visibility_config)
        config = repo.read()

        entity = config.get_entity("character", "主人公")
        assert entity is not None
        assert entity.entity_name == "主人公"
        assert entity.default_level == AIVisibilityLevel.USE
        assert len(entity.sections) == 2

    def test_visibility_config_file_format(
        self,
        repo: AIVisibilityRepository,
        sample_visibility_config: VisibilityConfig,
        temp_vault: Path,
    ) -> None:
        """Visibility config file is created in YAML format."""
        repo.create(sample_visibility_config)
        config_file = temp_vault / "_ai_control" / "visibility.yaml"

        content = config_file.read_text(encoding="utf-8")
        assert "version: '1.0'" in content
        assert "default_visibility: 0" in content
        assert "entity_type: character" in content
        assert "entity_name: 主人公" in content
