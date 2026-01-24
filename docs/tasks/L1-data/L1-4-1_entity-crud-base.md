# L1-4-1: エンティティ CRUD 基底クラス

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L1-4-1 |
| 優先度 | P0 |
| ステータス | ✅ done |
| 依存タスク | L1-2-1, L1-1-1 |
| 参照仕様 | `docs/specs/novel-generator-v2/03_data-model.md` |

## 概要

Markdown + YAML frontmatter 形式のエンティティに対する CRUD 操作の基底クラスを実装する。

## 受け入れ条件

- [ ] `BaseRepository[T]` ジェネリッククラスが存在する
- [ ] `create`, `read`, `update`, `delete` メソッドが定義されている
- [ ] ファイル読み書きとモデル変換が統合されている
- [ ] エラーハンドリングが適切に行われている
- [ ] ユニットテストが存在する

## 技術的詳細

### クラス定義

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseRepository(ABC, Generic[T]):
    def __init__(self, vault_root: Path, parser: FrontmatterParser):
        self.vault_root = vault_root
        self.parser = parser

    @abstractmethod
    def _get_path(self, identifier: str) -> Path:
        """エンティティのファイルパスを返す"""
        pass

    @abstractmethod
    def _model_class(self) -> type[T]:
        """対象のモデルクラスを返す"""
        pass

    def create(self, entity: T) -> Path:
        """エンティティを新規作成"""
        path = self._get_path(self._get_identifier(entity))
        if path.exists():
            raise EntityExistsError(f"Already exists: {path}")
        self._write(path, entity)
        return path

    def read(self, identifier: str) -> T:
        """エンティティを読み込み"""
        path = self._get_path(identifier)
        if not path.exists():
            raise EntityNotFoundError(f"Not found: {path}")
        return self._read(path)

    def update(self, entity: T) -> None:
        """エンティティを更新"""
        path = self._get_path(self._get_identifier(entity))
        if not path.exists():
            raise EntityNotFoundError(f"Not found: {path}")
        self._write(path, entity)

    def delete(self, identifier: str) -> None:
        """エンティティを削除"""
        path = self._get_path(identifier)
        if not path.exists():
            raise EntityNotFoundError(f"Not found: {path}")
        path.unlink()

    def exists(self, identifier: str) -> bool:
        """エンティティが存在するか確認"""
        return self._get_path(identifier).exists()

    def _read(self, path: Path) -> T:
        """ファイルからモデルを読み込み"""
        content = path.read_text(encoding='utf-8')
        frontmatter, body = self.parser.parse(content)
        return self._model_class()(**frontmatter, body=body)

    def _write(self, path: Path, entity: T) -> None:
        """モデルをファイルに書き込み"""
        content = self._serialize(entity)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
```

### 例外クラス

```python
class RepositoryError(Exception):
    pass

class EntityNotFoundError(RepositoryError):
    pass

class EntityExistsError(RepositoryError):
    pass
```

### ファイル配置

- `src/core/repositories/base.py`
- `tests/core/repositories/test_base.py`

## 実装メモ

- 2026-01-24: TDD で実装
- Generic[T] でジェネリッククラスとして定義
- CRUD + exists メソッド実装
- カスタム例外: EntityNotFoundError, EntityExistsError
- テスト10件全て PASS

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
