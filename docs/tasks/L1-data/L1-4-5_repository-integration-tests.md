# L1-4-5: リポジトリ統合テスト

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L1-4-5 |
| 優先度 | P0 |
| ステータス | 🔲 backlog |
| 依存タスク | L1-4-2, L1-4-3 |
| 参照仕様 | `docs/internal/02_DEVELOPMENT_FLOW.md` Phase 2 |

## 概要

リポジトリ層の統合テストを作成し、実際のファイルシステム操作が正しく動作することを検証する。

## 受け入れ条件

- [ ] 一時ディレクトリでのテストが動作する
- [ ] CRUD 全操作のテストが PASS する
- [ ] 複数リポジトリ間の連携テストが存在する
- [ ] エラーケースのテストが存在する
- [ ] カバレッジ 90% 以上

## テストケース

### CRUD 操作

| ケース | 操作 | 期待結果 |
|--------|------|---------|
| 新規作成 | create | ファイルが生成される |
| 読み込み | read | モデルが復元される |
| 更新 | update | ファイルが更新される |
| 削除 | delete | ファイルが削除される |
| 存在確認 | exists | 正しく判定される |

### エラーケース

| ケース | 操作 | 期待結果 |
|--------|------|---------|
| 存在しないエンティティ読み込み | read | EntityNotFoundError |
| 重複作成 | create（既存） | EntityExistsError |
| 存在しないエンティティ削除 | delete | EntityNotFoundError |

### 統合テスト

| ケース | 説明 |
|--------|------|
| 往復テスト | create → read で同一データ |
| 一覧更新 | create → list_all で含まれる |
| ファイル形式 | 生成されたファイルが有効な Markdown |

### テスト構成

```python
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

@pytest.fixture
def temp_vault():
    """テスト用の一時 vault を作成"""
    with TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir)
        (vault / "episodes").mkdir()
        (vault / "characters").mkdir()
        yield vault

def test_episode_crud(temp_vault):
    repo = EpisodeRepository(temp_vault, parser)
    # create
    episode = Episode(...)
    repo.create(episode)
    # read
    loaded = repo.read("1")
    assert loaded.title == episode.title
    # update
    loaded.status = "complete"
    repo.update(loaded)
    # delete
    repo.delete("1")
    assert not repo.exists("1")
```

### ファイル配置

- `tests/core/repositories/test_integration.py`

## 実装メモ

（実装時に記録）

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
