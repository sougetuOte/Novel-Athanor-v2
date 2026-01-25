# L3-2-1e: LazyLoader テスト

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-2-1e |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-2-1d |
| フェーズ | Phase C（個別機能実装） |
| 参照仕様 | `docs/specs/novel-generator-v2/08_agent-design.md` Section 8.4 |

## 概要

LazyLoader 関連クラス（FileLazyLoader, GracefulLoader）の
統合テストを実装する。

## 受け入れ条件

- [ ] FileLazyLoader の全メソッドテスト
- [ ] GracefulLoader の全メソッドテスト
- [ ] キャッシュ動作の検証
- [ ] Graceful Degradation の検証
- [ ] テストカバレッジ 90% 以上

## 技術的詳細

### ファイル配置

- テスト: `tests/core/context/test_lazy_loader.py`（既存ファイルに追加）

### テストフィクスチャ

```python
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch
import time

@pytest.fixture
def mock_vault(tmp_path: Path) -> Path:
    """テスト用 vault 構造を作成"""
    vault = tmp_path / "test_vault"
    vault.mkdir()

    # テストファイル作成
    (vault / "characters").mkdir()
    (vault / "characters" / "アイラ.md").write_text("# アイラ\n設定内容")
    (vault / "_plot").mkdir()
    (vault / "_plot" / "l3_ep010.md").write_text("# プロット\n内容")
    (vault / "_style_guides").mkdir()
    (vault / "_style_guides" / "default.md").write_text("# スタイル\n内容")

    return vault

@pytest.fixture
def file_loader(mock_vault: Path) -> FileLazyLoader:
    """FileLazyLoader インスタンス"""
    return FileLazyLoader(mock_vault, cache_ttl_seconds=1.0)

@pytest.fixture
def graceful_loader(file_loader: FileLazyLoader) -> GracefulLoader:
    """GracefulLoader インスタンス"""
    return GracefulLoader(file_loader)
```

### テストケース一覧

#### FileLazyLoader テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | load() 成功 | ファイル存在、内容取得 |
| 2 | load() REQUIRED 失敗 | ファイルなし、success=False |
| 3 | load() OPTIONAL 失敗 | ファイルなし、警告付きsuccess=True |
| 4 | is_cached() 初回 | False |
| 5 | is_cached() 読み込み後 | True |
| 6 | clear_cache() | キャッシュクリア確認 |
| 7 | キャッシュヒット | 2回目のload()でキャッシュ使用 |
| 8 | TTL 期限切れ | 期限切れ後に再読み込み |
| 9 | get_cache_stats() | 統計値確認 |
| 10 | evict_expired() | 期限切れエントリ削除 |

#### GracefulLoader テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 11 | load_with_graceful_degradation() 全成功 | 全て存在 |
| 12 | required 1件失敗 | success=False |
| 13 | required 複数失敗 | success=False、複数エラー |
| 14 | optional 1件失敗 | success=True、warnings |
| 15 | optional 複数失敗 | success=True、複数warnings |
| 16 | 混合パターン | required成功、optional一部失敗 |
| 17 | missing_required 確認 | リスト内容確認 |
| 18 | missing_optional 確認 | リスト内容確認 |
| 19 | load_batch() | バッチ読み込み |

#### 統合テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 20 | 現実的シナリオ | キャラ+プロット+スタイル |
| 21 | 参照資料なし | 付加的コンテンツ不在 |
| 22 | 日本語ファイル名 | エンコーディング確認 |
| 23 | 大量ファイル | パフォーマンス確認 |

### テスト実装例

```python
class TestFileLazyLoader:
    """FileLazyLoader のテスト"""

    def test_load_success(self, file_loader: FileLazyLoader):
        """ファイル読み込み成功"""
        result = file_loader.load(
            "characters/アイラ.md",
            LoadPriority.REQUIRED
        )

        assert result.success is True
        assert result.data is not None
        assert "アイラ" in result.data
        assert result.error is None

    def test_load_required_not_found(self, file_loader: FileLazyLoader):
        """REQUIRED で存在しないファイル"""
        result = file_loader.load(
            "characters/存在しない.md",
            LoadPriority.REQUIRED
        )

        assert result.success is False
        assert result.data is None
        assert result.error is not None

    def test_cache_hit(self, file_loader: FileLazyLoader):
        """キャッシュヒット確認"""
        # 1回目
        file_loader.load("characters/アイラ.md", LoadPriority.REQUIRED)
        assert file_loader.is_cached("characters/アイラ.md")

        # 2回目（キャッシュから）
        result = file_loader.load("characters/アイラ.md", LoadPriority.REQUIRED)
        assert result.success is True

    def test_cache_expiry(self, file_loader: FileLazyLoader):
        """TTL 期限切れ"""
        file_loader.load("characters/アイラ.md", LoadPriority.REQUIRED)

        # TTL (1秒) 待機
        time.sleep(1.1)

        stats = file_loader.get_cache_stats()
        assert stats["expired"] == 1


class TestGracefulLoader:
    """GracefulLoader のテスト"""

    def test_all_success(self, graceful_loader: GracefulLoader):
        """全件成功パターン"""
        result = graceful_loader.load_with_graceful_degradation(
            required={
                "character": "characters/アイラ.md",
                "plot": "_plot/l3_ep010.md",
            },
            optional={
                "style": "_style_guides/default.md",
            },
        )

        assert result.success is True
        assert len(result.data) == 3
        assert result.errors == []
        assert result.warnings == []

    def test_required_failure(self, graceful_loader: GracefulLoader):
        """必須コンテキスト失敗"""
        result = graceful_loader.load_with_graceful_degradation(
            required={
                "character": "characters/存在しない.md",
            },
            optional={},
        )

        assert result.success is False
        assert len(result.errors) == 1
        assert "存在しない" in result.missing_required

    def test_optional_failure_continues(self, graceful_loader: GracefulLoader):
        """付加的コンテキスト失敗で継続"""
        result = graceful_loader.load_with_graceful_degradation(
            required={
                "character": "characters/アイラ.md",
            },
            optional={
                "reference": "references/存在しない.md",
            },
        )

        assert result.success is True
        assert "character" in result.data
        assert len(result.warnings) >= 1
        assert "存在しない" in result.missing_optional
```

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
