"""Foreshadowing repository.

伏線データを YAML レジストリ形式で管理するリポジトリ。
"""

from datetime import date
from pathlib import Path
from typing import Any

import yaml

from src.core.models.foreshadowing import Foreshadowing, ForeshadowingStatus
from src.core.repositories.base import EntityExistsError, EntityNotFoundError


class ForeshadowingRepository:
    """伏線リポジトリ.

    vault/{作品名}/_foreshadowing/registry.yaml を管理する。
    """

    def __init__(self, vault_root: Path, work_name: str) -> None:
        """初期化.

        Args:
            vault_root: Vault のルートディレクトリ
            work_name: 作品名
        """
        self.vault_root = vault_root
        self.work_name = work_name

    def _get_registry_path(self) -> Path:
        """レジストリファイルのパスを返す."""
        return self.vault_root / self.work_name / "_foreshadowing" / "registry.yaml"

    def _load_registry(self) -> dict[str, Any]:
        """レジストリを読み込む."""
        path = self._get_registry_path()
        if not path.exists():
            return {"version": "1.0", "last_updated": None, "foreshadowing": []}

        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        return data if data else {"version": "1.0", "last_updated": None, "foreshadowing": []}

    def _save_registry(self, data: dict[str, Any]) -> None:
        """レジストリを保存する."""
        path = self._get_registry_path()
        path.parent.mkdir(parents=True, exist_ok=True)

        data["last_updated"] = date.today().isoformat()
        content = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        path.write_text(content, encoding="utf-8")

    def _find_index(self, registry: dict[str, Any], fs_id: str) -> int | None:
        """ID から伏線のインデックスを検索."""
        for i, fs in enumerate(registry.get("foreshadowing", [])):
            if fs.get("id") == fs_id:
                return i
        return None

    def create(self, entity: Foreshadowing) -> None:
        """伏線を作成する.

        Args:
            entity: 作成する伏線

        Raises:
            EntityExistsError: 同じ ID の伏線が既に存在する場合
        """
        registry = self._load_registry()

        if self._find_index(registry, entity.id) is not None:
            raise EntityExistsError(f"Foreshadowing already exists: {entity.id}")

        registry["foreshadowing"].append(
            entity.model_dump(mode="json", exclude_none=True)
        )
        self._save_registry(registry)

    def read(self, fs_id: str) -> Foreshadowing:
        """伏線を読み込む.

        Args:
            fs_id: 伏線 ID

        Returns:
            伏線モデル

        Raises:
            EntityNotFoundError: 伏線が見つからない場合
        """
        registry = self._load_registry()
        idx = self._find_index(registry, fs_id)

        if idx is None:
            raise EntityNotFoundError(f"Foreshadowing not found: {fs_id}")

        return Foreshadowing(**registry["foreshadowing"][idx])

    def update(self, entity: Foreshadowing) -> None:
        """伏線を更新する.

        Args:
            entity: 更新する伏線

        Raises:
            EntityNotFoundError: 伏線が見つからない場合
        """
        registry = self._load_registry()
        idx = self._find_index(registry, entity.id)

        if idx is None:
            raise EntityNotFoundError(f"Foreshadowing not found: {entity.id}")

        registry["foreshadowing"][idx] = entity.model_dump(
            mode="json", exclude_none=True
        )
        self._save_registry(registry)

    def delete(self, fs_id: str) -> None:
        """伏線を削除する.

        Args:
            fs_id: 伏線 ID

        Raises:
            EntityNotFoundError: 伏線が見つからない場合
        """
        registry = self._load_registry()
        idx = self._find_index(registry, fs_id)

        if idx is None:
            raise EntityNotFoundError(f"Foreshadowing not found: {fs_id}")

        del registry["foreshadowing"][idx]
        self._save_registry(registry)

    def exists(self, fs_id: str) -> bool:
        """伏線が存在するか確認する.

        Args:
            fs_id: 伏線 ID

        Returns:
            存在する場合 True
        """
        registry = self._load_registry()
        return self._find_index(registry, fs_id) is not None

    def list_all(self) -> list[Foreshadowing]:
        """すべての伏線をリストする.

        Returns:
            伏線のリスト
        """
        registry = self._load_registry()
        return [
            Foreshadowing(**fs_data) for fs_data in registry.get("foreshadowing", [])
        ]

    def list_by_status(self, status: ForeshadowingStatus) -> list[Foreshadowing]:
        """ステータスでフィルタして伏線をリストする.

        Args:
            status: フィルタするステータス

        Returns:
            フィルタされた伏線のリスト
        """
        all_fs = self.list_all()
        return [fs for fs in all_fs if fs.status == status]
