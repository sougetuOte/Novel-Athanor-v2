# L1-4-3: Character リポジトリ

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L1-4-3 |
| 優先度 | P0 |
| ステータス | 🔲 backlog |
| 依存タスク | L1-4-1 |
| 参照仕様 | `docs/specs/novel-generator-v2/03_data-model.md` Section 3.2 |

## 概要

Character エンティティの CRUD 操作を行うリポジトリを実装する。

## 受け入れ条件

- [ ] `CharacterRepository` クラスが `BaseRepository` を継承している
- [ ] キャラクター名での読み書きができる
- [ ] フェーズ指定での状態取得ができる
- [ ] タグでのフィルタリングができる
- [ ] ユニットテストが存在する

## 技術的詳細

### クラス定義

```python
from pathlib import Path
from src.core.models.character import Character
from src.core.repositories.base import BaseRepository

class CharacterRepository(BaseRepository[Character]):
    def _get_path(self, identifier: str) -> Path:
        return self.vault_root / "characters" / f"{identifier}.md"

    def _model_class(self) -> type[Character]:
        return Character

    def _get_identifier(self, entity: Character) -> str:
        return entity.name

    def list_all(self) -> list[Character]:
        """全キャラクターを取得"""
        chars_dir = self.vault_root / "characters"
        if not chars_dir.exists():
            return []
        return [self._read(path) for path in chars_dir.glob("*.md")]

    def get_by_tag(self, tag: str) -> list[Character]:
        """タグでフィルタリング"""
        return [c for c in self.list_all() if tag in c.tags]

    def get_current_phase_content(
        self, name: str
    ) -> dict[str, str]:
        """現在のフェーズのコンテンツを取得"""
        char = self.read(name)
        if char.current_phase is None:
            return char.sections
        # current_phase に対応するセクションのみ返す
        # （実装詳細は Phase Filter と連携）
        return char.sections

    def update_phase(self, name: str, new_phase: str) -> None:
        """フェーズを更新"""
        char = self.read(name)
        if not any(p.name == new_phase for p in char.phases):
            raise ValueError(f"Unknown phase: {new_phase}")
        char.current_phase = new_phase
        self.update(char)
```

### ファイル配置

- `src/core/repositories/character.py`
- `tests/core/repositories/test_character.py`

## 実装メモ

（実装時に記録）

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
