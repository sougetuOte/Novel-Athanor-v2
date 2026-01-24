"""CharacterRepository.

Character エンティティの CRUD 操作を行うリポジトリ。
"""

from pathlib import Path

from src.core.models.character import Character
from src.core.repositories.base import BaseRepository
from src.core.vault.path_resolver import VaultPathResolver


class CharacterRepository(BaseRepository[Character]):
    """Character リポジトリ."""

    def __init__(self, vault_root: Path) -> None:
        """初期化."""
        super().__init__(vault_root)
        self._path_resolver = VaultPathResolver(vault_root)

    def _get_path(self, identifier: str) -> Path:
        """キャラクター名からファイルパスを取得."""
        return self._path_resolver.resolve_character(identifier)

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

        Note:
            現時点では全セクションを返す。
            Phase Filter による current_phase に基づくフィルタリングは
            L2 フェーズ（Phase Filter 実装タスク）で対応予定。
        """
        char = self.read(name)
        # TODO(L2-phase-filter): current_phase に基づくセクションフィルタリング
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
