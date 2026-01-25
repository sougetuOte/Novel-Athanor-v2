# L3-2-1c: Lazy読み込み実装（キャッシュ機構）

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-2-1c |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-2-1b |
| フェーズ | Phase C（個別機能実装） |
| 参照仕様 | `docs/specs/novel-generator-v2/02_architecture.md` Section 2.4 |

## 概要

LazyLoader プロトコルの具象実装を作成する。
ファイルの遅延読み込みとインメモリキャッシュ機構を実装。

## 受け入れ条件

- [ ] `FileLazyLoader` クラスが実装されている
- [ ] `load()` で指定パスのファイルを読み込める
- [ ] `is_cached()` でキャッシュ状態を確認できる
- [ ] `clear_cache()` でキャッシュをクリアできる
- [ ] TTL（Time To Live）によるキャッシュ有効期限
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/lazy_loader.py`（既存ファイルに追加）
- テスト: `tests/core/context/test_lazy_loader.py`（既存ファイルに追加）

### クラス定義

```python
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, TypeVar, Generic
from dataclasses import dataclass, field

T = TypeVar('T')

@dataclass
class CacheEntry(Generic[T]):
    """キャッシュエントリ"""
    data: T
    loaded_at: datetime
    source: Path

    def is_expired(self, ttl_seconds: float) -> bool:
        """TTL切れかどうか"""
        age = (datetime.now() - self.loaded_at).total_seconds()
        return age > ttl_seconds


class FileLazyLoader:
    """ファイル遅延読み込み実装

    ファイルをオンデマンドで読み込み、
    インメモリキャッシュで再利用する。

    Attributes:
        vault_root: vault のルートパス
        cache_ttl_seconds: キャッシュ有効期限（秒）
    """

    def __init__(
        self,
        vault_root: Path,
        cache_ttl_seconds: float = 300.0,  # 5分
    ):
        self.vault_root = vault_root
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: dict[str, CacheEntry[str]] = {}

    def load(
        self,
        identifier: str,
        priority: LoadPriority,
    ) -> LazyLoadResult[str]:
        """ファイルを読み込む

        Args:
            identifier: ファイルパス（vault_root からの相対パス）
            priority: 読み込み優先度

        Returns:
            読み込み結果
        """
        # キャッシュチェック
        if self.is_cached(identifier):
            entry = self._cache[identifier]
            if not entry.is_expired(self.cache_ttl_seconds):
                return LazyLoadResult.ok(entry.data)

        # ファイル読み込み
        file_path = self.vault_root / identifier
        try:
            content = file_path.read_text(encoding='utf-8')
            self._cache[identifier] = CacheEntry(
                data=content,
                loaded_at=datetime.now(),
                source=file_path,
            )
            return LazyLoadResult.ok(content)
        except FileNotFoundError:
            error_msg = f"File not found: {file_path}"
            if priority == LoadPriority.REQUIRED:
                return LazyLoadResult.fail(error_msg)
            else:
                return LazyLoadResult(
                    success=True,
                    data=None,
                    warnings=[error_msg],
                )
        except Exception as e:
            return LazyLoadResult.fail(str(e))

    def is_cached(self, identifier: str) -> bool:
        """キャッシュ済みか確認"""
        return identifier in self._cache

    def clear_cache(self) -> None:
        """キャッシュをクリア"""
        self._cache.clear()

    def get_cache_stats(self) -> dict[str, int]:
        """キャッシュ統計を取得

        Returns:
            {"total": 件数, "expired": 期限切れ件数}
        """
        total = len(self._cache)
        expired = sum(
            1 for e in self._cache.values()
            if e.is_expired(self.cache_ttl_seconds)
        )
        return {"total": total, "expired": expired}

    def evict_expired(self) -> int:
        """期限切れキャッシュを削除

        Returns:
            削除した件数
        """
        expired_keys = [
            k for k, v in self._cache.items()
            if v.is_expired(self.cache_ttl_seconds)
        ]
        for k in expired_keys:
            del self._cache[k]
        return len(expired_keys)
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | load() 成功 | ファイル存在 |
| 2 | load() REQUIRED 失敗 | ファイルなし、エラー |
| 3 | load() OPTIONAL 失敗 | ファイルなし、警告 |
| 4 | is_cached() True | キャッシュ後 |
| 5 | is_cached() False | 未キャッシュ |
| 6 | clear_cache() | キャッシュクリア |
| 7 | キャッシュヒット | 2回目の load() |
| 8 | TTL 切れ | 期限切れでリロード |
| 9 | get_cache_stats() | 統計取得 |
| 10 | evict_expired() | 期限切れ削除 |

## キャッシュ戦略

| コンテンツ種別 | TTL | 理由 |
|---------------|-----|------|
| スタイルガイド | 長い（10分） | 変更頻度低 |
| 世界観設定 | 中（5分） | 変更頻度中 |
| プロット | 短い（2分） | 作業中に変更される可能性 |
| エピソード | 短い（1分） | 執筆中に変更される |

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
