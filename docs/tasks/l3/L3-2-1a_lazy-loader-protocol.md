# L3-2-1a: LazyLoader プロトコル定義

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-2-1a |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | なし |
| 並列実行 | Phase A グループ（他プロトコルと並列可） |
| 参照仕様 | `docs/specs/novel-generator-v2/02_architecture.md` Section 2.4 |

## 概要

必要最小限のデータを遅延読み込みするための Protocol（インターフェース）を定義する。
Graceful Degradation（段階的劣化）をサポートし、付加的なデータの読み込み失敗時は警告を出しつつ処理を継続できる。

## 受け入れ条件

- [ ] `LazyLoader` Protocol が typing.Protocol を継承している
- [ ] `LoadPriority` Enum が定義されている（REQUIRED / OPTIONAL）
- [ ] `LazyLoadResult` ジェネリックデータクラスが定義されている
- [ ] `load()`, `is_cached()`, `clear_cache()` メソッドがProtocolに定義されている
- [ ] ユニットテスト（Protocol準拠確認）が存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/lazy_loader.py`
- テスト: `tests/core/context/test_lazy_loader.py`

### クラス定義

```python
from typing import Protocol, TypeVar, Generic, Optional
from dataclasses import dataclass, field
from enum import Enum

T = TypeVar('T')

class LoadPriority(Enum):
    """読み込み優先度（Graceful Degradation用）

    - REQUIRED: 必須データ。読み込み失敗時はエラー停止
    - OPTIONAL: 付加的データ。読み込み失敗時は警告して続行
    """
    REQUIRED = "required"
    OPTIONAL = "optional"

@dataclass
class LazyLoadResult(Generic[T]):
    """遅延読み込み結果

    Attributes:
        success: 読み込み成功したか
        data: 読み込んだデータ（失敗時はNone）
        error: エラーメッセージ（成功時はNone）
        warnings: 警告メッセージのリスト
    """
    success: bool
    data: Optional[T]
    error: Optional[str] = None
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def ok(cls, data: T, warnings: list[str] | None = None) -> "LazyLoadResult[T]":
        """成功結果を生成"""
        return cls(success=True, data=data, warnings=warnings or [])

    @classmethod
    def fail(cls, error: str) -> "LazyLoadResult[T]":
        """失敗結果を生成"""
        return cls(success=False, data=None, error=error)

class LazyLoader(Protocol[T]):
    """遅延読み込みプロトコル

    このProtocolを実装するクラスは、指定されたidentifierに対して
    データを遅延読み込みし、キャッシュ機構を提供する。
    """

    def load(self, identifier: str, priority: LoadPriority) -> LazyLoadResult[T]:
        """指定されたidentifierのデータを読み込む

        Args:
            identifier: データを特定する識別子
            priority: 読み込み優先度（REQUIRED/OPTIONAL）

        Returns:
            LazyLoadResult: 読み込み結果
        """
        ...

    def is_cached(self, identifier: str) -> bool:
        """指定されたidentifierがキャッシュ済みかどうか

        Args:
            identifier: データを特定する識別子

        Returns:
            bool: キャッシュ済みならTrue
        """
        ...

    def clear_cache(self) -> None:
        """キャッシュをクリアする"""
        ...
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | Protocol準拠確認 | 具体クラスがProtocolを満たすことを確認 |
| 2 | LazyLoadResult.ok() | 成功結果の生成確認 |
| 3 | LazyLoadResult.fail() | 失敗結果の生成確認 |
| 4 | LoadPriority列挙確認 | REQUIRED, OPTIONAL が存在 |
| 5 | LazyLoadResult warnings | 警告リストの動作確認 |

## Graceful Degradation 設計

| コンテキスト種別 | 優先度 | 失敗時の挙動 |
|-----------------|--------|-------------|
| キャラ設定 | REQUIRED | エラー停止 |
| プロット情報 | REQUIRED | エラー停止 |
| スタイルガイド | REQUIRED | エラー停止 |
| 参考資料 | OPTIONAL | 警告付きで続行 |
| 過去サマリ | OPTIONAL | 警告付きで続行 |

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
