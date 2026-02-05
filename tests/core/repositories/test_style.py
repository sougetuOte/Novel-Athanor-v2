"""Tests for StyleGuideRepository and StyleProfileRepository."""

from datetime import date
from pathlib import Path

import pytest

from src.core.models.style import POVType, StyleGuide, StyleProfile, TenseType
from src.core.repositories.base import EntityExistsError, EntityNotFoundError
from src.core.repositories.style import StyleGuideRepository, StyleProfileRepository


class TestStyleGuideRepository:
    """StyleGuideRepository tests."""

    @pytest.fixture
    def temp_vault(self, tmp_path: Path) -> Path:
        """Create temporary vault."""
        (tmp_path / "_style_guides").mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def repo(self, temp_vault: Path) -> StyleGuideRepository:
        """Create test repository."""
        return StyleGuideRepository(temp_vault)

    @pytest.fixture
    def sample_guide(self) -> StyleGuide:
        """Create sample style guide."""
        return StyleGuide(
            work="test-work",
            pov=POVType.THIRD_PERSON_LIMITED,
            tense=TenseType.PAST,
            style_characteristics=["簡潔な文章", "リズミカルな描写"],
            avoid_expressions=["いわゆる", "まさに"],
            created=date(2026, 1, 1),
            updated=date(2026, 1, 25),
        )

    def test_create_style_guide(
        self, repo: StyleGuideRepository, sample_guide: StyleGuide
    ) -> None:
        """Style guide can be created."""
        path = repo.create(sample_guide)

        assert path.exists()
        assert path.name == "test-work.yaml"
        assert "_style_guides" in str(path)

    def test_create_duplicate_raises_error(
        self, repo: StyleGuideRepository, sample_guide: StyleGuide
    ) -> None:
        """Creating duplicate style guide raises error."""
        repo.create(sample_guide)

        with pytest.raises(EntityExistsError):
            repo.create(sample_guide)

    def test_read_style_guide(
        self, repo: StyleGuideRepository, sample_guide: StyleGuide
    ) -> None:
        """Style guide can be read."""
        repo.create(sample_guide)
        guide = repo.read("test-work")

        assert guide.work == "test-work"
        assert guide.pov == POVType.THIRD_PERSON_LIMITED
        assert guide.tense == TenseType.PAST
        assert "簡潔な文章" in guide.style_characteristics

    def test_read_nonexistent_raises_error(
        self, repo: StyleGuideRepository
    ) -> None:
        """Reading nonexistent style guide raises error."""
        with pytest.raises(EntityNotFoundError):
            repo.read("nonexistent")

    def test_update_style_guide(
        self, repo: StyleGuideRepository, sample_guide: StyleGuide
    ) -> None:
        """Style guide can be updated."""
        repo.create(sample_guide)

        sample_guide.style_characteristics.append("新しい特徴")
        repo.update(sample_guide)

        updated = repo.read("test-work")
        assert "新しい特徴" in updated.style_characteristics

    def test_delete_style_guide(
        self, repo: StyleGuideRepository, sample_guide: StyleGuide
    ) -> None:
        """Style guide can be deleted."""
        repo.create(sample_guide)
        repo.delete("test-work")

        assert not repo.exists("test-work")


class TestStyleProfileRepository:
    """StyleProfileRepository tests."""

    @pytest.fixture
    def temp_vault(self, tmp_path: Path) -> Path:
        """Create temporary vault."""
        (tmp_path / "_style_profiles").mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def repo(self, temp_vault: Path) -> StyleProfileRepository:
        """Create test repository."""
        return StyleProfileRepository(temp_vault)

    @pytest.fixture
    def sample_profile(self) -> StyleProfile:
        """Create sample style profile."""
        return StyleProfile(
            work="test-work",
            avg_sentence_length=25.5,
            dialogue_ratio=0.35,
            ttr=0.68,
            pos_ratios={"名詞": 0.25, "動詞": 0.15, "形容詞": 0.08},
            frequent_words=["彼女", "思った", "言った"],
            sample_episodes=[1, 2, 3],
            analyzed_at=date(2026, 1, 25),
        )

    def test_create_style_profile(
        self, repo: StyleProfileRepository, sample_profile: StyleProfile
    ) -> None:
        """Style profile can be created."""
        path = repo.create(sample_profile)

        assert path.exists()
        assert path.name == "test-work.yaml"
        assert "_style_profiles" in str(path)

    def test_create_duplicate_raises_error(
        self, repo: StyleProfileRepository, sample_profile: StyleProfile
    ) -> None:
        """Creating duplicate style profile raises error."""
        repo.create(sample_profile)

        with pytest.raises(EntityExistsError):
            repo.create(sample_profile)

    def test_read_style_profile(
        self, repo: StyleProfileRepository, sample_profile: StyleProfile
    ) -> None:
        """Style profile can be read."""
        repo.create(sample_profile)
        profile = repo.read("test-work")

        assert profile.work == "test-work"
        assert profile.avg_sentence_length == 25.5
        assert profile.dialogue_ratio == 0.35
        assert profile.ttr == 0.68

    def test_read_nonexistent_raises_error(
        self, repo: StyleProfileRepository
    ) -> None:
        """Reading nonexistent style profile raises error."""
        with pytest.raises(EntityNotFoundError):
            repo.read("nonexistent")

    def test_update_style_profile(
        self, repo: StyleProfileRepository, sample_profile: StyleProfile
    ) -> None:
        """Style profile can be updated."""
        repo.create(sample_profile)

        sample_profile.avg_sentence_length = 30.0
        repo.update(sample_profile)

        updated = repo.read("test-work")
        assert updated.avg_sentence_length == 30.0

    def test_delete_style_profile(
        self, repo: StyleProfileRepository, sample_profile: StyleProfile
    ) -> None:
        """Style profile can be deleted."""
        repo.create(sample_profile)
        repo.delete("test-work")

        assert not repo.exists("test-work")
