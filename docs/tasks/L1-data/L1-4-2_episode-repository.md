# L1-4-2: Episode リポジトリ

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L1-4-2 |
| 優先度 | P0 |
| ステータス | 🔲 backlog |
| 依存タスク | L1-4-1 |
| 参照仕様 | `docs/specs/novel-generator-v2/03_data-model.md` Section 3.1 |

## 概要

Episode エンティティの CRUD 操作を行うリポジトリを実装する。

## 受け入れ条件

- [ ] `EpisodeRepository` クラスが `BaseRepository` を継承している
- [ ] エピソード番号での読み書きができる
- [ ] 一覧取得ができる
- [ ] 範囲指定での取得ができる（例: ep 10-20）
- [ ] ユニットテストが存在する

## 技術的詳細

### クラス定義

```python
from pathlib import Path
from src.core.models.episode import Episode
from src.core.repositories.base import BaseRepository

class EpisodeRepository(BaseRepository[Episode]):
    def _get_path(self, identifier: str) -> Path:
        episode_number = int(identifier)
        return self.vault_root / "episodes" / f"ep_{episode_number:04d}.md"

    def _model_class(self) -> type[Episode]:
        return Episode

    def _get_identifier(self, entity: Episode) -> str:
        return str(entity.episode_number)

    def list_all(self) -> list[Episode]:
        """全エピソードを取得"""
        episodes_dir = self.vault_root / "episodes"
        if not episodes_dir.exists():
            return []
        episodes = []
        for path in sorted(episodes_dir.glob("ep_*.md")):
            episodes.append(self._read(path))
        return episodes

    def get_range(self, start: int, end: int) -> list[Episode]:
        """範囲指定でエピソードを取得"""
        return [
            self.read(str(n))
            for n in range(start, end + 1)
            if self.exists(str(n))
        ]

    def get_by_status(self, status: str) -> list[Episode]:
        """ステータスでフィルタリング"""
        return [ep for ep in self.list_all() if ep.status == status]

    def get_latest(self) -> Episode | None:
        """最新のエピソードを取得"""
        episodes = self.list_all()
        return episodes[-1] if episodes else None
```

### ファイル配置

- `src/core/repositories/episode.py`
- `tests/core/repositories/test_episode.py`

## 実装メモ

（実装時に記録）

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
