"""CharacterRepository.

Character エンティティの CRUD 操作を行うリポジトリ。
"""

from pathlib import Path

from src.core.models.character import Character
from src.core.repositories.base import BaseRepository


class CharacterRepository(BaseRepository[Character]):
    """Character リポジトリ."""

    def _get_path(self, identifier: str) -> Path:
        """キャラクター名からファイルパスを取得."""
        return self.vault_root / "characters" / f"{identifier}.md"

    def _model_class(self) -> type[Character]:
        """Character クラスを返す."""
        return Character

    def _get_identifier(self, entity: Character) -> str:
        """キャラクター名を識別子として返す."""
        return entity.name

    def list_all(self) -> list[Character]:
        """全キャラクターを取得.

        Returns:
            キャラクターのリスト
        """
        chars_dir = self.vault_root / "characters"
        if not chars_dir.exists():
            return []
        return [self._read(path) for path in chars_dir.glob("*.md")]

    def get_by_tag(self, tag: str) -> list[Character]:
        """タグでフィルタリング.

        Args:
            tag: フィルタするタグ

        Returns:
            指定タグを持つキャラクターのリスト
        """
        return [c for c in self.list_all() if tag in c.tags]

    def get_current_phase_content(self, name: str) -> dict[str, str]:
        """現在のフェーズのコンテンツを取得.

        Args:
            name: キャラクター名

        Returns:
            セクション辞書
        """
        char = self.read(name)
        if char.current_phase is None:
            return char.sections
        # current_phase に対応するセクションのみ返す
        # （現時点では全セクションを返す。Phase Filter は別タスクで実装）
        return char.sections

    def update_phase(self, name: str, new_phase: str) -> None:
        """フェーズを更新.

        Args:
            name: キャラクター名
            new_phase: 新しいフェーズ名

        Raises:
            ValueError: 指定されたフェーズが存在しない場合
        """
        char = self.read(name)
        if not any(p.name == new_phase for p in char.phases):
            raise ValueError(f"Unknown phase: {new_phase}")
        char.current_phase = new_phase
        self.update(char)
