"""Tests for EpisodeRepository."""

from datetime import date
from pathlib import Path

import pytest

from src.core.models.episode import Episode
from src.core.repositories.episode import EpisodeRepository


class TestEpisodeRepository:
    """EpisodeRepository のテスト."""

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
    def sample_episodes(self, repo: EpisodeRepository) -> list[Episode]:
        """サンプルエピソードを作成."""
        episodes = []
        for i in range(1, 4):
            ep = Episode(
                work="テスト作品",
                episode_number=i,
                title=f"第{i}話",
                status="draft" if i < 3 else "complete",
                created=date(2026, 1, 24),
                updated=date(2026, 1, 24),
            )
            repo.create(ep)
            episodes.append(ep)
        return episodes

    def test_list_all(
        self, repo: EpisodeRepository, sample_episodes: list[Episode]
    ) -> None:
        """全エピソードを取得できる."""
        episodes = repo.list_all()

        assert len(episodes) == 3
        assert episodes[0].episode_number == 1
        assert episodes[1].episode_number == 2
        assert episodes[2].episode_number == 3

    def test_list_all_empty(self, repo: EpisodeRepository) -> None:
        """エピソードがない場合は空リストを返す."""
        episodes = repo.list_all()

        assert episodes == []

    def test_get_range(
        self, repo: EpisodeRepository, sample_episodes: list[Episode]
    ) -> None:
        """範囲指定でエピソードを取得できる."""
        episodes = repo.get_range(1, 2)

        assert len(episodes) == 2
        assert episodes[0].episode_number == 1
        assert episodes[1].episode_number == 2

    def test_get_by_status(
        self, repo: EpisodeRepository, sample_episodes: list[Episode]
    ) -> None:
        """ステータスでフィルタリングできる."""
        drafts = repo.get_by_status("draft")
        completes = repo.get_by_status("complete")

        assert len(drafts) == 2
        assert len(completes) == 1
        assert completes[0].episode_number == 3

    def test_get_latest(
        self, repo: EpisodeRepository, sample_episodes: list[Episode]
    ) -> None:
        """最新のエピソードを取得できる."""
        latest = repo.get_latest()

        assert latest is not None
        assert latest.episode_number == 3

    def test_get_latest_empty(self, repo: EpisodeRepository) -> None:
        """エピソードがない場合は None を返す."""
        latest = repo.get_latest()

        assert latest is None
