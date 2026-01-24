"""WorldSettingRepository.

WorldSetting エンティティの CRUD 操作を行うリポジトリ。
"""

from pathlib import Path

from src.core.models.world_setting import WorldSetting
from src.core.repositories.base import BaseRepository
from src.core.vault.path_resolver import VaultPathResolver


class WorldSettingRepository(BaseRepository[WorldSetting]):
    """WorldSetting リポジトリ."""

    def __init__(self, vault_root: Path) -> None:
        """初期化."""
        super().__init__(vault_root)
        self._path_resolver = VaultPathResolver(vault_root)

    def _get_path(self, identifier: str) -> Path:
        """世界観設定名からファイルパスを取得."""
        return self._path_resolver.resolve_world_setting(identifier)

    def _model_class(self) -> type[WorldSetting]:
        """WorldSetting クラスを返す."""
        return WorldSetting

    def _get_identifier(self, entity: WorldSetting) -> str:
        """世界観設定名を識別子として返す."""
        return entity.name

    def list_all(self) -> list[WorldSetting]:
        """全世界観設定を取得.

        Returns:
            世界観設定のリスト
        """
        world_dir = self.vault_root / "world"
        if not world_dir.exists():
            return []
        return [self._read(path) for path in world_dir.glob("*.md")]

    def get_by_category(self, category: str) -> list[WorldSetting]:
        """カテゴリでフィルタリング.

        Args:
            category: フィルタするカテゴリ

        Returns:
            指定カテゴリの世界観設定リスト
        """
        return [ws for ws in self.list_all() if ws.category == category]

    def get_by_tag(self, tag: str) -> list[WorldSetting]:
        """タグでフィルタリング.

        Args:
            tag: フィルタするタグ

        Returns:
            指定タグを持つ世界観設定のリスト
        """
        return [ws for ws in self.list_all() if tag in ws.tags]

    def update_phase(self, name: str, new_phase: str) -> None:
        """フェーズを更新.

        Args:
            name: 世界観設定名
            new_phase: 新しいフェーズ名

        Raises:
            ValueError: 指定されたフェーズが存在しない場合
        """
        ws = self.read(name)
        if not any(p.name == new_phase for p in ws.phases):
            raise ValueError(f"Unknown phase: {new_phase}")
        ws.current_phase = new_phase
        self.update(ws)
