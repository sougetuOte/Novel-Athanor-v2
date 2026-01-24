"""Integration tests for repositories."""

from datetime import date
from pathlib import Path

import pytest

from src.core.models.character import Character, Phase
from src.core.models.episode import Episode
from src.core.repositories.character import CharacterRepository
from src.core.repositories.episode import EpisodeRepository


class TestRepositoryIntegration:
    """リポジトリ統合テスト."""

    @pytest.fixture
    def temp_vault(self, tmp_path: Path) -> Path:
        """テスト用の一時 vault を作成."""
        (tmp_path / "episodes").mkdir()
        (tmp_path / "characters").mkdir()
        return tmp_path

    @pytest.fixture
    def episode_repo(self, temp_vault: Path) -> EpisodeRepository:
        """Episode リポジトリを作成."""
        return EpisodeRepository(temp_vault)

    @pytest.fixture
    def character_repo(self, temp_vault: Path) -> CharacterRepository:
        """Character リポジトリを作成."""
        return CharacterRepository(temp_vault)

    def test_crud_roundtrip_episode(self, episode_repo: EpisodeRepository) -> None:
        """Episode の CRUD 往復テスト."""
        # Create
        original = Episode(
            work="テスト作品",
            episode_number=1,
            title="第一話",
            status="draft",
            tags=["action", "drama"],
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
            body="本文です。\n\n## セクション1\n\n内容。",
        )
        episode_repo.create(original)

        # Read
        loaded = episode_repo.read("1")
        assert loaded.work == original.work
        assert loaded.episode_number == original.episode_number
        assert loaded.title == original.title
        assert loaded.tags == original.tags
        assert "本文です。" in loaded.body

        # Update
        loaded.status = "complete"
        loaded.word_count = 1000
        episode_repo.update(loaded)

        updated = episode_repo.read("1")
        assert updated.status == "complete"
        assert updated.word_count == 1000

        # Delete
        episode_repo.delete("1")
        assert not episode_repo.exists("1")

    def test_crud_roundtrip_character(
        self, character_repo: CharacterRepository
    ) -> None:
        """Character の CRUD 往復テスト."""
        # Create
        original = Character(
            name="主人公",
            phases=[
                Phase(name="序盤", episodes="1-10"),
                Phase(name="中盤", episodes="11-20"),
            ],
            current_phase="序盤",
            tags=["hero"],
            sections={"基本情報": "名前: 太郎\n年齢: 25"},
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )
        character_repo.create(original)

        # Read
        loaded = character_repo.read("主人公")
        assert loaded.name == original.name
        assert len(loaded.phases) == 2
        assert loaded.current_phase == "序盤"
        assert "基本情報" in loaded.sections

        # Update
        loaded.tags.append("protagonist")
        character_repo.update(loaded)

        updated = character_repo.read("主人公")
        assert "protagonist" in updated.tags

        # Delete
        character_repo.delete("主人公")
        assert not character_repo.exists("主人公")

    def test_list_after_create(
        self, episode_repo: EpisodeRepository, temp_vault: Path
    ) -> None:
        """作成後のリスト取得テスト."""
        # 複数エピソード作成
        for i in range(1, 4):
            ep = Episode(
                work="テスト",
                episode_number=i,
                title=f"第{i}話",
                created=date(2026, 1, 24),
                updated=date(2026, 1, 24),
            )
            episode_repo.create(ep)

        # リストに含まれることを確認
        episodes = episode_repo.list_all()
        assert len(episodes) == 3

        episode_numbers = [e.episode_number for e in episodes]
        assert 1 in episode_numbers
        assert 2 in episode_numbers
        assert 3 in episode_numbers

    def test_markdown_file_format(
        self, episode_repo: EpisodeRepository, temp_vault: Path
    ) -> None:
        """生成されたファイルが有効な Markdown 形式."""
        episode = Episode(
            work="テスト",
            episode_number=1,
            title="第一話",
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
            body="本文です。",
        )
        path = episode_repo.create(episode)

        # ファイル内容を確認
        content = path.read_text(encoding="utf-8")

        # frontmatter 形式
        assert content.startswith("---\n")
        assert "---\n\n" in content  # frontmatter の終端

        # フィールドが含まれる
        assert "work:" in content
        assert "episode_number:" in content
        assert "title:" in content

        # 本文が含まれる
        assert "本文です。" in content

    def test_multiple_repositories_same_vault(
        self,
        episode_repo: EpisodeRepository,
        character_repo: CharacterRepository,
        temp_vault: Path,
    ) -> None:
        """複数リポジトリが同じ vault で動作."""
        # Episode を作成
        episode = Episode(
            work="テスト",
            episode_number=1,
            title="第一話",
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )
        episode_repo.create(episode)

        # Character を作成
        character = Character(
            name="主人公",
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )
        character_repo.create(character)

        # 両方存在することを確認
        assert episode_repo.exists("1")
        assert character_repo.exists("主人公")

        # それぞれのディレクトリに保存されている
        assert (temp_vault / "episodes" / "ep_0001.md").exists()
        assert (temp_vault / "characters" / "主人公.md").exists()
