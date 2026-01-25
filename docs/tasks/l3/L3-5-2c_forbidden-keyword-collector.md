# L3-5-2c: 禁止キーワード収集

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-5-2c |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-5-2b, L2-2-1 |
| フェーズ | Phase E（伏線・Visibility 統合） |
| 参照仕様 | `docs/specs/novel-generator-v2/04_ai-information-control.md` |

## 概要

シーン執筆時に使用してはいけない禁止キーワードを収集するロジックを実装する。
伏線の禁止表現、AI 可視性設定、グローバル禁止リストを統合。

## 受け入れ条件

- [ ] `ForbiddenKeywordCollector` クラスが実装されている
- [ ] 伏線の forbidden_expressions を収集できる
- [ ] AI 可視性設定の禁止キーワードを収集できる
- [ ] グローバル禁止リストを収集できる
- [ ] 重複排除・ソートができる
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/forbidden_keyword_collector.py`（新規）
- テスト: `tests/core/context/test_forbidden_keyword_collector.py`（新規）

### クラス定義

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from src.core.services.expression_filter import ExpressionFilter
from .scene_identifier import SceneIdentifier
from .foreshadow_instruction import ForeshadowInstructions
from .lazy_loader import FileLazyLoader, LoadPriority

@dataclass
class ForbiddenKeywordResult:
    """禁止キーワード収集結果

    Attributes:
        keywords: 統合された禁止キーワードリスト（ソート済み）
        sources: キーワードの出所情報（デバッグ用）
    """
    keywords: list[str] = field(default_factory=list)
    sources: dict[str, list[str]] = field(default_factory=dict)

    def add_from_source(self, source: str, keywords: list[str]) -> None:
        """出所を記録しながらキーワードを追加"""
        self.sources[source] = keywords
        # 統合リストに追加（後で重複排除）

    def finalize(self) -> None:
        """重複排除とソートを実行"""
        all_keywords = set()
        for kw_list in self.sources.values():
            all_keywords.update(kw_list)
        self.keywords = sorted(all_keywords)


class ForbiddenKeywordCollector:
    """禁止キーワード収集

    複数のソースから禁止キーワードを収集し、
    統合されたリストを生成する。

    Attributes:
        vault_root: vault ルートパス
        loader: 遅延読み込みローダー
        expression_filter: L2 の表現フィルタ
    """

    def __init__(
        self,
        vault_root: Path,
        loader: FileLazyLoader,
        expression_filter: Optional[ExpressionFilter] = None,
    ):
        self.vault_root = vault_root
        self.loader = loader
        self.expression_filter = expression_filter

    def collect(
        self,
        scene: SceneIdentifier,
        foreshadow_instructions: Optional[ForeshadowInstructions] = None,
    ) -> ForbiddenKeywordResult:
        """禁止キーワードを収集

        収集ソース:
        1. 伏線指示書の forbidden_expressions
        2. AI 可視性設定のグローバル禁止キーワード
        3. 作品全体のグローバル禁止リスト

        Args:
            scene: シーン識別子
            foreshadow_instructions: 伏線指示書（あれば）

        Returns:
            収集結果
        """
        result = ForbiddenKeywordResult()

        # 1. 伏線からの禁止キーワード
        if foreshadow_instructions:
            fs_keywords = foreshadow_instructions.get_all_forbidden()
            result.add_from_source("foreshadowing", fs_keywords)

        # 2. AI 可視性設定からの禁止キーワード
        visibility_keywords = self._collect_from_visibility()
        result.add_from_source("visibility", visibility_keywords)

        # 3. グローバル禁止リスト
        global_keywords = self._collect_global_forbidden()
        result.add_from_source("global", global_keywords)

        # 4. L2 ExpressionFilter からの禁止キーワード
        if self.expression_filter:
            filter_keywords = self._collect_from_expression_filter(scene)
            result.add_from_source("expression_filter", filter_keywords)

        result.finalize()
        return result

    def _collect_from_visibility(self) -> list[str]:
        """AI 可視性設定から禁止キーワードを収集

        パス: _ai_control/visibility.yaml
        """
        result = self.loader.load(
            "_ai_control/visibility.yaml",
            LoadPriority.OPTIONAL,
        )
        if not result.success or not result.data:
            return []

        # YAML パース
        import yaml
        try:
            data = yaml.safe_load(result.data)
            return data.get("global_forbidden_keywords", [])
        except yaml.YAMLError:
            return []

    def _collect_global_forbidden(self) -> list[str]:
        """グローバル禁止リストを収集

        パス: _ai_control/forbidden_keywords.txt
        """
        result = self.loader.load(
            "_ai_control/forbidden_keywords.txt",
            LoadPriority.OPTIONAL,
        )
        if not result.success or not result.data:
            return []

        # 1行1キーワード形式
        lines = result.data.strip().split("\n")
        return [line.strip() for line in lines if line.strip() and not line.startswith("#")]

    def _collect_from_expression_filter(
        self, scene: SceneIdentifier
    ) -> list[str]:
        """L2 ExpressionFilter から禁止キーワードを収集

        ExpressionFilter が保持している
        現在有効な禁止キーワードを取得。
        """
        if not self.expression_filter:
            return []

        # ExpressionFilter の API を使用
        # TODO: L2 との具体的な連携方法を確定
        return self.expression_filter.get_forbidden_keywords(
            phase=scene.current_phase
        )

    def collect_as_list(
        self,
        scene: SceneIdentifier,
        foreshadow_instructions: Optional[ForeshadowInstructions] = None,
    ) -> list[str]:
        """禁止キーワードをリストとして取得（シンプル版）"""
        result = self.collect(scene, foreshadow_instructions)
        return result.keywords
```

### vault 構造

```
vault/{作品名}/
└── _ai_control/
    ├── visibility.yaml           # AI 可視性設定
    │   global_forbidden_keywords:
    │     - 王族
    │     - 血筋
    │
    └── forbidden_keywords.txt    # グローバル禁止リスト
        # 作品全体で使ってはいけない言葉
        禁忌の魔法
        最終兵器
        真の名前
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | collect() 伏線のみ | 伏線からの収集 |
| 2 | collect() 可視性のみ | visibility.yaml から |
| 3 | collect() グローバルのみ | forbidden_keywords.txt から |
| 4 | collect() 全ソース | 全ソース統合 |
| 5 | collect() 重複排除 | 同じキーワード |
| 6 | collect() ソート | アルファベット順 |
| 7 | _collect_from_visibility() | YAML パース |
| 8 | _collect_global_forbidden() | テキスト行パース |
| 9 | sources 記録 | デバッグ情報 |
| 10 | collect_as_list() | シンプル版 |

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
