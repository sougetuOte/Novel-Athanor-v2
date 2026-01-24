"""VaultPathResolver.

Vault 内のファイルパスを解決するユーティリティ。
"""

from pathlib import Path
from typing import Literal


class VaultPathResolver:
    """Vault 内のファイルパスを解決するクラス."""

    def __init__(self, vault_root: Path) -> None:
        """初期化.

        Args:
            vault_root: Vault のルートディレクトリ
        """
        self.vault_root = vault_root

    def resolve_episode(self, episode_number: int) -> Path:
        """エピソードファイルのパスを解決.

        Args:
            episode_number: エピソード番号

        Returns:
            エピソードファイルのパス
        """
        return self.vault_root / "episodes" / f"ep_{episode_number:04d}.md"

    def resolve_character(self, name: str) -> Path:
        """キャラクターファイルのパスを解決.

        Args:
            name: キャラクター名

        Returns:
            キャラクターファイルのパス
        """
        return self.vault_root / "characters" / f"{name}.md"

    def resolve_world_setting(self, name: str) -> Path:
        """世界観設定ファイルのパスを解決.

        Args:
            name: 設定名

        Returns:
            世界観設定ファイルのパス
        """
        return self.vault_root / "world" / f"{name}.md"

    def resolve_plot(
        self,
        level: Literal["L1", "L2", "L3"],
        chapter_number: int | None = None,
        chapter_name: str | None = None,
        sequence_number: int | None = None,
    ) -> Path:
        """プロットファイルのパスを解決.

        Args:
            level: プロットレベル (L1, L2, L3)
            chapter_number: 章番号 (L2, L3 で必要)
            chapter_name: 章名 (L2, L3 で必要)
            sequence_number: シーケンス番号 (L3 で必要)

        Returns:
            プロットファイルのパス
        """
        if level == "L1":
            return self.vault_root / "_plot" / "L1_overall.md"
        elif level == "L2":
            return (
                self.vault_root
                / "_plot"
                / "L2_chapters"
                / f"{chapter_number:02d}_{chapter_name}.md"
            )
        else:  # L3
            return (
                self.vault_root
                / "_plot"
                / "L3_sequences"
                / f"{chapter_number:02d}_{chapter_name}"
                / f"seq_{sequence_number:03d}.md"
            )

    def resolve_foreshadowing(self) -> Path:
        """伏線レジストリのパスを解決.

        Returns:
            伏線レジストリファイルのパス
        """
        return self.vault_root / "_foreshadowing" / "registry.yaml"

    def exists(self, path: Path) -> bool:
        """ファイルが存在するか確認.

        Args:
            path: vault_root からの相対パス

        Returns:
            ファイルが存在する場合 True
        """
        return (self.vault_root / path).exists()
