# L3-2-1d: Graceful Degradation 実装

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-2-1d |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-2-1c |
| フェーズ | Phase C（個別機能実装） |
| 参照仕様 | `docs/specs/novel-generator-v2/08_agent-design.md` Section 8.4 |

## 概要

コンテキスト取得失敗時の段階的劣化（Graceful Degradation）を実装する。
必須コンテキストと付加的コンテキストで異なる振る舞いを実現。

## 受け入れ条件

- [ ] `GracefulLoader` クラスが実装されている
- [ ] 必須コンテキスト失敗時はエラーを返す
- [ ] 付加的コンテキスト失敗時は警告付きで続行
- [ ] 警告メッセージが収集される
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/lazy_loader.py`（既存ファイルに追加）
- テスト: `tests/core/context/test_lazy_loader.py`（既存ファイルに追加）

### クラス定義

```python
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

@dataclass
class GracefulLoadResult:
    """Graceful Degradation 対応の読み込み結果

    Attributes:
        success: 全体として成功したか（必須コンテキストが全て取得できた）
        data: 読み込んだデータのマップ
        errors: 致命的エラーのリスト（必須コンテキストの取得失敗）
        warnings: 警告のリスト（付加的コンテキストの取得失敗）
        missing_required: 取得できなかった必須コンテキストのリスト
        missing_optional: 取得できなかった付加的コンテキストのリスト
    """
    success: bool
    data: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    missing_required: list[str] = field(default_factory=list)
    missing_optional: list[str] = field(default_factory=list)


class GracefulLoader:
    """Graceful Degradation 対応ローダー

    必須と付加的のコンテキストを区別し、
    付加的コンテキストの取得失敗では処理を継続する。
    """

    def __init__(self, base_loader: FileLazyLoader):
        """
        Args:
            base_loader: 基本となる LazyLoader 実装
        """
        self.base_loader = base_loader

    def load_with_graceful_degradation(
        self,
        required: dict[str, str],  # {識別名: パス}
        optional: dict[str, str],  # {識別名: パス}
    ) -> GracefulLoadResult:
        """Graceful Degradation でコンテキストを読み込む

        Args:
            required: 必須コンテキストのマップ（失敗時はエラー）
            optional: 付加的コンテキストのマップ（失敗時は警告）

        Returns:
            読み込み結果

        Examples:
            >>> result = loader.load_with_graceful_degradation(
            ...     required={
            ...         "characters": "characters/アイラ.md",
            ...         "plot": "_plot/l3_ep010.md",
            ...     },
            ...     optional={
            ...         "references": "references/magic.md",
            ...         "past_summary": "_summary/l2_chapter01.md",
            ...     },
            ... )
        """
        result = GracefulLoadResult(success=True)

        # 必須コンテキストの読み込み
        for name, path in required.items():
            load_result = self.base_loader.load(path, LoadPriority.REQUIRED)
            if load_result.success and load_result.data is not None:
                result.data[name] = load_result.data
            else:
                result.success = False
                result.errors.append(
                    f"必須コンテキスト取得失敗: {name} ({path})"
                )
                result.missing_required.append(name)

        # 付加的コンテキストの読み込み
        for name, path in optional.items():
            load_result = self.base_loader.load(path, LoadPriority.OPTIONAL)
            if load_result.success and load_result.data is not None:
                result.data[name] = load_result.data
            else:
                result.warnings.append(
                    f"付加的コンテキスト取得失敗（続行）: {name} ({path})"
                )
                result.missing_optional.append(name)
                # 警告を引き継ぐ
                result.warnings.extend(load_result.warnings)

        return result

    def load_batch(
        self,
        items: list[tuple[str, str, LoadPriority]],
    ) -> GracefulLoadResult:
        """バッチで読み込み

        Args:
            items: [(識別名, パス, 優先度), ...]

        Returns:
            読み込み結果
        """
        required = {
            name: path
            for name, path, priority in items
            if priority == LoadPriority.REQUIRED
        }
        optional = {
            name: path
            for name, path, priority in items
            if priority == LoadPriority.OPTIONAL
        }
        return self.load_with_graceful_degradation(required, optional)
```

### 仕様との対応

`08_agent-design.md` Section 8.4 の定義：

| コンテキスト種別 | 重要度 | 取得失敗時の挙動 |
|-----------------|--------|-----------------|
| キャラ設定 | **必須** | エラー停止 |
| プロット情報 | **必須** | エラー停止 |
| スタイルガイド | **必須** | エラー停止 |
| 参考資料 | 付加的 | 警告付きで続行 |
| 過去サマリ | 付加的 | 警告付きで続行 |

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | 全件成功 | required + optional 全て存在 |
| 2 | required 失敗 | 必須が1件不在→success=False |
| 3 | optional 失敗 | 付加的が不在→success=True, warnings |
| 4 | 混合パターン | required成功、optional一部失敗 |
| 5 | 全件失敗 | 全て不在 |
| 6 | load_batch() | バッチ読み込み |
| 7 | missing_required | 不在リスト確認 |
| 8 | missing_optional | 不在リスト確認 |

### 使用例

```python
# コンテキストビルダーでの使用
loader = GracefulLoader(file_lazy_loader)

result = loader.load_with_graceful_degradation(
    required={
        "character_aira": "characters/アイラ.md",
        "plot_l3": "_plot/l3_ep010.md",
        "style": "_style_guides/default.md",
    },
    optional={
        "reference_magic": "references/magic.md",
        "summary_l2": "_summary/l2_chapter01.md",
    },
)

if not result.success:
    raise FatalContextError(
        f"必須コンテキスト取得失敗: {result.missing_required}"
    )

# 警告があれば記録
for warning in result.warnings:
    logger.warning(warning)

# データを使用
context = build_context(result.data)
```

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
