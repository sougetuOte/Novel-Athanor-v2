"""BaseRepository.

Markdown + YAML frontmatter 形式のエンティティに対する CRUD 操作の基底クラス。
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

import yaml
from pydantic import BaseModel

from src.core.parsers.frontmatter import parse_frontmatter

T = TypeVar("T", bound=BaseModel)


class RepositoryError(Exception):
    """リポジトリ操作の基底例外."""

    pass


class EntityNotFoundError(RepositoryError):
    """エンティティが見つからない場合の例外."""

    pass


class EntityExistsError(RepositoryError):
    """エンティティが既に存在する場合の例外."""

    pass


class BaseRepository(ABC, Generic[T]):
    """エンティティ CRUD 操作の基底クラス."""

    def __init__(self, vault_root: Path) -> None:
        """初期化.

        Args:
            vault_root: Vault のルートディレクトリ
        """
        self.vault_root = vault_root

    @abstractmethod
    def _get_path(self, identifier: str) -> Path:
        """エンティティのファイルパスを返す.

        Args:
            identifier: エンティティの識別子

        Returns:
            ファイルパス
        """
        pass

    @abstractmethod
    def _model_class(self) -> type[T]:
        """対象のモデルクラスを返す.

        Returns:
            モデルクラス
        """
        pass

    @abstractmethod
    def _get_identifier(self, entity: T) -> str:
        """エンティティから識別子を取得.

        Args:
            entity: エンティティ

        Returns:
            識別子
        """
        pass

    def create(self, entity: T) -> Path:
        """エンティティを新規作成.

        Args:
            entity: 作成するエンティティ

        Returns:
            作成されたファイルのパス

        Raises:
            EntityExistsError: エンティティが既に存在する場合
        """
        path = self._get_path(self._get_identifier(entity))
        if path.exists():
            raise EntityExistsError(f"Already exists: {path}")
        self._write(path, entity)
        return path

    def read(self, identifier: str) -> T:
        """エンティティを読み込み.

        Args:
            identifier: エンティティの識別子

        Returns:
            読み込んだエンティティ

        Raises:
            EntityNotFoundError: エンティティが見つからない場合
        """
        path = self._get_path(identifier)
        if not path.exists():
            raise EntityNotFoundError(f"Not found: {path}")
        return self._read(path)

    def update(self, entity: T) -> None:
        """エンティティを更新.

        Args:
            entity: 更新するエンティティ

        Raises:
            EntityNotFoundError: エンティティが見つからない場合
        """
        path = self._get_path(self._get_identifier(entity))
        if not path.exists():
            raise EntityNotFoundError(f"Not found: {path}")
        self._write(path, entity)

    def delete(self, identifier: str) -> None:
        """エンティティを削除.

        Args:
            identifier: エンティティの識別子

        Raises:
            EntityNotFoundError: エンティティが見つからない場合
        """
        path = self._get_path(identifier)
        if not path.exists():
            raise EntityNotFoundError(f"Not found: {path}")
        path.unlink()

    def exists(self, identifier: str) -> bool:
        """エンティティが存在するか確認.

        Args:
            identifier: エンティティの識別子

        Returns:
            存在する場合 True
        """
        return self._get_path(identifier).exists()

    def _read(self, path: Path) -> T:
        """ファイルからモデルを読み込み.

        Args:
            path: ファイルパス

        Returns:
            読み込んだモデル

        Note:
            body パラメータは Episode のような本文を持つモデル用。
            Character/WorldSetting など body フィールドを持たないモデルでは
            Pydantic の extra='ignore' により無視される。
            これらのモデルは frontmatter 内の sections フィールドでコンテンツを管理する。
        """
        content = path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(content)
        return self._model_class()(**frontmatter, body=body)

    def _write(self, path: Path, entity: T) -> None:
        """モデルをファイルに書き込み.

        Args:
            path: ファイルパス
            entity: 書き込むエンティティ
        """
        content = self._serialize(entity)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _serialize(self, entity: T) -> str:
        """エンティティを Markdown 形式にシリアライズ.

        Args:
            entity: シリアライズするエンティティ

        Returns:
            Markdown 形式の文字列
        """
        data = entity.model_dump(mode="json")

        # body は frontmatter 外
        body = data.pop("body", "")

        # frontmatter として出力
        yaml_content = yaml.dump(data, allow_unicode=True, default_flow_style=False)

        return f"---\n{yaml_content}---\n\n{body}"
