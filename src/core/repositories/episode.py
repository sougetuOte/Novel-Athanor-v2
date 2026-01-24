"""EpisodeRepository.

Episode エンティティの CRUD 操作を行うリポジトリ。
"""

from pathlib import Path

from src.core.models.episode import Episode
from src.core.repositories.base import BaseRepository


class EpisodeRepository(BaseRepository[Episode]):
    """Episode リポジトリ."""

    def _get_path(self, identifier: str) -> Path:
        """エピソード番号からファイルパスを取得."""
        episode_number = int(identifier)
        return self.vault_root / "episodes" / f"ep_{episode_number:04d}.md"

    def _model_class(self) -> type[Episode]:
        """Episode クラスを返す."""
        return Episode

    def _get_identifier(self, entity: Episode) -> str:
        """エピソード番号を識別子として返す."""
        return str(entity.episode_number)

    def list_all(self) -> list[Episode]:
        """全エピソードを取得.

        Returns:
            エピソード番号順にソートされたリスト
        """
        episodes_dir = self.vault_root / "episodes"
        if not episodes_dir.exists():
            return []
        episodes = []
        for path in sorted(episodes_dir.glob("ep_*.md")):
            episodes.append(self._read(path))
        return episodes

    def get_range(self, start: int, end: int) -> list[Episode]:
        """範囲指定でエピソードを取得.

        Args:
            start: 開始エピソード番号
            end: 終了エピソード番号（含む）

        Returns:
            指定範囲のエピソードリスト
        """
        return [
            self.read(str(n)) for n in range(start, end + 1) if self.exists(str(n))
        ]

    def get_by_status(self, status: str) -> list[Episode]:
        """ステータスでフィルタリング.

        Args:
            status: フィルタするステータス

        Returns:
            指定ステータスのエピソードリスト
        """
        return [ep for ep in self.list_all() if ep.status == status]

    def get_latest(self) -> Episode | None:
        """最新のエピソードを取得.

        Returns:
            最新のエピソード、存在しない場合は None
        """
        episodes = self.list_all()
        return episodes[-1] if episodes else None
