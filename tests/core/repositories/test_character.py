"""Tests for CharacterRepository."""

from datetime import date
from pathlib import Path

import pytest

from src.core.models.character import Character, Phase
from src.core.repositories.character import CharacterRepository


class TestCharacterRepository:
    """CharacterRepository のテスト."""

    @pytest.fixture
    def temp_vault(self, tmp_path: Path) -> Path:
        """テスト用の一時 vault を作成."""
        (tmp_path / "characters").mkdir()
        return tmp_path

    @pytest.fixture
    def repo(self, temp_vault: Path) -> CharacterRepository:
        """テスト用リポジトリを作成."""
        return CharacterRepository(temp_vault)

    @pytest.fixture
    def sample_characters(self, repo: CharacterRepository) -> list[Character]:
        """サンプルキャラクターを作成."""
        chars = [
            Character(
                name="主人公",
                phases=[Phase(name="序盤", episodes="1-10")],
                current_phase="序盤",
                tags=["hero", "protagonist"],
                created=date(2026, 1, 24),
                updated=date(2026, 1, 24),
                sections={"基本情報": "テスト"},
            ),
            Character(
                name="ヒロイン",
                tags=["heroine", "protagonist"],
                created=date(2026, 1, 24),
                updated=date(2026, 1, 24),
            ),
            Character(
                name="敵キャラ",
                tags=["villain"],
                created=date(2026, 1, 24),
                updated=date(2026, 1, 24),
            ),
        ]
        for char in chars:
            repo.create(char)
        return chars

    def test_list_all(
        self, repo: CharacterRepository, sample_characters: list[Character]
    ) -> None:
        """全キャラクターを取得できる."""
        characters = repo.list_all()

        assert len(characters) == 3

    def test_list_all_empty(self, repo: CharacterRepository) -> None:
        """キャラクターがない場合は空リストを返す."""
        characters = repo.list_all()

        assert characters == []

    def test_get_by_tag(
        self, repo: CharacterRepository, sample_characters: list[Character]
    ) -> None:
        """タグでフィルタリングできる."""
        protagonists = repo.get_by_tag("protagonist")
        villains = repo.get_by_tag("villain")

        assert len(protagonists) == 2
        assert len(villains) == 1
        assert villains[0].name == "敵キャラ"

    def test_get_current_phase_content(
        self, repo: CharacterRepository, sample_characters: list[Character]
    ) -> None:
        """現在のフェーズのコンテンツを取得できる."""
        content = repo.get_current_phase_content("主人公")

        assert "基本情報" in content

    def test_update_phase(
        self, repo: CharacterRepository, sample_characters: list[Character]
    ) -> None:
        """フェーズを更新できる."""
        # まず新しいフェーズを追加
        char = repo.read("主人公")
        char.phases.append(Phase(name="中盤", episodes="11-20"))
        repo.update(char)

        # フェーズを更新
        repo.update_phase("主人公", "中盤")

        updated = repo.read("主人公")
        assert updated.current_phase == "中盤"

    def test_update_phase_invalid_raises_error(
        self, repo: CharacterRepository, sample_characters: list[Character]
    ) -> None:
        """存在しないフェーズへの更新はエラー."""
        with pytest.raises(ValueError, match="Unknown phase"):
            repo.update_phase("主人公", "存在しないフェーズ")
