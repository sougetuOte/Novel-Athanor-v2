# L3-4-1b: ContextIntegrator プロトコル定義

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-4-1b |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-4-1a |
| フェーズ | Phase B（プロトコル定義） |
| 参照仕様 | `docs/specs/novel-generator-v2/08_agent-design.md` Section 3 |

## 概要

各種コンテキスト（Plot/Summary/Character/WorldSetting/StyleGuide）を
統合するためのプロトコルを定義する。

## 受け入れ条件

- [ ] `ContextIntegrator` プロトコルが定義されている
- [ ] `integrate()` メソッドが定義されている
- [ ] 入力は `SceneIdentifier` と各種コレクター
- [ ] 出力は `FilteredContext`
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/context_integrator.py`（新規）
- テスト: `tests/core/context/test_context_integrator.py`（新規）

### クラス定義

```python
from typing import Protocol, Optional
from .scene_identifier import SceneIdentifier
from .filtered_context import FilteredContext

class ContextCollector(Protocol):
    """個別コンテキスト収集プロトコル"""

    def collect(self, scene: SceneIdentifier) -> Optional[str]:
        """シーンに関連するコンテキストを収集

        Args:
            scene: シーン識別子

        Returns:
            収集したコンテキスト文字列、なければNone
        """
        ...

class ContextIntegrator(Protocol):
    """コンテキスト統合プロトコル

    各種コレクターからコンテキストを収集し、
    FilteredContext に統合する責務を持つ。
    """

    def integrate(
        self,
        scene: SceneIdentifier,
        *,
        plot_collector: Optional[ContextCollector] = None,
        summary_collector: Optional[ContextCollector] = None,
        character_collector: Optional[ContextCollector] = None,
        world_collector: Optional[ContextCollector] = None,
        style_collector: Optional[ContextCollector] = None,
    ) -> FilteredContext:
        """コンテキストを統合する

        Args:
            scene: シーン識別子
            plot_collector: プロット収集（L1/L2/L3）
            summary_collector: サマリ収集（L1/L2/L3）
            character_collector: キャラクター収集
            world_collector: 世界観設定収集
            style_collector: スタイルガイド収集

        Returns:
            統合されたFilteredContext
        """
        ...

    def integrate_with_warnings(
        self,
        scene: SceneIdentifier,
        **collectors
    ) -> tuple[FilteredContext, list[str]]:
        """コンテキストを統合し、警告も返す

        Returns:
            (FilteredContext, 警告リスト)
        """
        ...
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | プロトコル準拠 | Mockで準拠確認 |
| 2 | integrate() 全コレクター | 全コレクターから収集 |
| 3 | integrate() 一部のみ | 一部コレクターのみ |
| 4 | integrate_with_warnings() | 警告付き統合 |
| 5 | コレクターなし | 空のFilteredContext |

## 仕様との関連

`08_agent-design.md` Section 3 で定義された Continuity Director の
内部ロジック分割における「Context Builder（収集）」に対応する。

```
Continuity Director
├── Context Builder（収集） ← ContextIntegrator
│   └── 関連ファイルの特定と読み込み
└── Information Controller（フィルタリング）
    └── AI可視性に基づくフィルタリング
```

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
