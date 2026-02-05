"""Tests for BaseRepository."""

from datetime import date
from pathlib import Path

import pytest

from src.core.models.episode import Episode
from src.core.repositories.base import (
    BaseRepository,
    EntityExistsError,
    EntityNotFoundError,
)


class EpisodeRepository(BaseRepository[Episode]):
    """テスト用の Episode リポジトリ."""

    def _get_path(self, identifier: str) -> Path:
        episode_number = int(identifier)
        return self.vault_root / "episodes" / f"ep_{episode_number:04d}.md"

    def _model_class(self) -> type[Episode]:
        return Episode

    def _get_identifier(self, entity: Episode) -> str:
        return str(entity.episode_number)


class TestBaseRepository:
    """BaseRepository のテスト."""

    @pytest.fixture
    def temp_vault(self, tmp_path: Path) -> Path:
        """テスト用の一時 vault を作成."""
        (tmp_path / "episodes").mkdir()
        return tmp_path

    @pytest.fixture
    def repo(self, temp_vault: Path) -> EpisodeRepository:
        """テスト用リポジトリを作成."""
        return EpisodeRepository(temp_vault)

    @pytest.fixture
    def sample_episode(self) -> Episode:
        """サンプルエピソードを作成."""
        return Episode(
            work="テスト作品",
            episode_number=1,
            title="第一話",
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
            body="本文です。",
        )

    def test_create(
        self, repo: EpisodeRepository, sample_episode: Episode, temp_vault: Path
    ) -> None:
        """エンティティを作成できる."""
        path = repo.create(sample_episode)

        assert path.exists()
        assert path == temp_vault / "episodes" / "ep_0001.md"

    def test_create_duplicate_raises_error(
        self, repo: EpisodeRepository, sample_episode: Episode
    ) -> None:
        """重複作成はエラー."""
        repo.create(sample_episode)

        with pytest.raises(EntityExistsError):
            repo.create(sample_episode)

    def test_read(self, repo: EpisodeRepository, sample_episode: Episode) -> None:
        """エンティティを読み込める."""
        repo.create(sample_episode)

        loaded = repo.read("1")

        assert loaded.work == sample_episode.work
        assert loaded.episode_number == sample_episode.episode_number
        assert loaded.title == sample_episode.title

    def test_read_nonexistent_raises_error(self, repo: EpisodeRepository) -> None:
        """存在しないエンティティの読み込みはエラー."""
        with pytest.raises(EntityNotFoundError):
            repo.read("999")

    def test_update(self, repo: EpisodeRepository, sample_episode: Episode) -> None:
        """エンティティを更新できる."""
        repo.create(sample_episode)

        sample_episode.title = "更新後タイトル"
        repo.update(sample_episode)

        loaded = repo.read("1")
        assert loaded.title == "更新後タイトル"

    def test_update_nonexistent_raises_error(
        self, repo: EpisodeRepository, sample_episode: Episode
    ) -> None:
        """存在しないエンティティの更新はエラー."""
        with pytest.raises(EntityNotFoundError):
            repo.update(sample_episode)

    def test_delete(self, repo: EpisodeRepository, sample_episode: Episode) -> None:
        """エンティティを削除できる."""
        repo.create(sample_episode)
        assert repo.exists("1")

        repo.delete("1")

        assert not repo.exists("1")

    def test_delete_nonexistent_raises_error(self, repo: EpisodeRepository) -> None:
        """存在しないエンティティの削除はエラー."""
        with pytest.raises(EntityNotFoundError):
            repo.delete("999")

    def test_exists(self, repo: EpisodeRepository, sample_episode: Episode) -> None:
        """存在確認ができる."""
        assert not repo.exists("1")

        repo.create(sample_episode)

        assert repo.exists("1")
