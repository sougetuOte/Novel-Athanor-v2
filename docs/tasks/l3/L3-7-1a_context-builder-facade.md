# L3-7-1a: ContextBuilder クラス定義

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-7-1a |
| 優先度 | P1 |
| ステータス | done |
| 完了日 | 2026-02-04 |
| 依存タスク | L3-2-1c, L3-3-1b, L3-4-1b |
| 並列実行 | Phase F（前提タスク完了後） |
| 参照仕様 | `docs/specs/novel-generator-v2/08_agent-design.md` Section 3.3 |

## 概要

L3 レイヤー全体のファサード（入り口）となる ContextBuilder クラスを定義する。
Continuity Director から呼び出される `build_context()` の実体となる。

## 受け入れ条件

- [ ] `ContextBuilder` クラスが定義されている
- [ ] 依存コンポーネントがコンストラクタで注入される（DI）
- [ ] `ContextBuildResult` データクラスが定義されている
- [ ] `build_context()` メソッドシグネチャが定義されている
- [ ] ユニットテスト（モック使用）が存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/context_builder.py`
- テスト: `tests/core/context/test_context_builder.py`

### クラス定義

```python
from dataclasses import dataclass, field
from typing import Protocol
from pathlib import Path

from .scene_identifier import SceneIdentifier
from .context_integrator import FilteredContext
from .foreshadow_instruction import ForeshadowInstructions

@dataclass
class ContextBuildResult:
    """コンテキスト構築結果

    Attributes:
        context: フィルタリング済みコンテキスト
        foreshadow_instructions: 伏線指示書
        forbidden_keywords: 全禁止キーワードリスト
        success: 構築成功したか
        errors: エラーメッセージリスト
        warnings: 警告メッセージリスト
    """
    context: FilteredContext
    foreshadow_instructions: ForeshadowInstructions
    forbidden_keywords: list[str] = field(default_factory=list)
    success: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def has_errors(self) -> bool:
        """エラーがあるか"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """警告があるか"""
        return len(self.warnings) > 0

# Protocol 定義（依存注入用）
class SceneResolverProtocol(Protocol):
    def resolve_files(self, scene: SceneIdentifier) -> list[Path]:
        ...

class LazyLoaderProtocol(Protocol):
    def load(self, identifier: str, priority: "LoadPriority") -> "LazyLoadResult":
        ...

class PhaseFilterProtocol(Protocol):
    def filter_by_phase(self, entity: any, phase: str) -> any:
        ...

class ContextIntegratorProtocol(Protocol):
    def integrate(self, scene: SceneIdentifier) -> FilteredContext:
        ...

class InstructionGeneratorProtocol(Protocol):
    def generate(self, scene: SceneIdentifier) -> ForeshadowInstructions:
        ...

class VisibilityControllerProtocol(Protocol):
    def get_filtered_context(self, content: str, level: int) -> "FilteredContent":
        ...

class ContextBuilder:
    """コンテキスト構築ファサード

    L3 レイヤーのエントリーポイント。
    各コンポーネントを組み合わせてシーンのコンテキストを構築する。

    仕様書参照: 08_agent-design.md Section 3.3
    """

    def __init__(
        self,
        vault_root: Path,
        scene_resolver: SceneResolverProtocol,
        lazy_loader: LazyLoaderProtocol,
        phase_filter: PhaseFilterProtocol,
        context_integrator: ContextIntegratorProtocol,
        instruction_generator: InstructionGeneratorProtocol,
        visibility_controller: VisibilityControllerProtocol,
    ):
        """依存コンポーネントを注入して初期化

        Args:
            vault_root: Vault のルートパス
            scene_resolver: シーン→ファイル解決
            lazy_loader: 遅延読み込み
            phase_filter: フェーズフィルタ
            context_integrator: コンテキスト統合
            instruction_generator: 伏線指示書生成
            visibility_controller: AI可視性制御
        """
        self._vault_root = vault_root
        self._scene_resolver = scene_resolver
        self._lazy_loader = lazy_loader
        self._phase_filter = phase_filter
        self._context_integrator = context_integrator
        self._instruction_generator = instruction_generator
        self._visibility_controller = visibility_controller

    def build_context(self, scene: SceneIdentifier) -> ContextBuildResult:
        """シーンのコンテキストを構築する

        1. シーンに関連するファイルを特定
        2. 必要なデータを遅延読み込み
        3. フェーズに基づいてフィルタリング
        4. AI可視性に基づいてフィルタリング
        5. 伏線指示書を生成
        6. 結果を統合して返却

        Args:
            scene: 対象シーンの識別子

        Returns:
            ContextBuildResult: 構築結果
        """
        # 実装は L3-7-1b で行う
        raise NotImplementedError("Implemented in L3-7-1b")

    def get_foreshadow_instructions(
        self, scene: SceneIdentifier
    ) -> ForeshadowInstructions:
        """伏線指示書のみを取得する

        Args:
            scene: 対象シーンの識別子

        Returns:
            ForeshadowInstructions: 伏線指示書
        """
        # 実装は L3-7-1c で行う
        raise NotImplementedError("Implemented in L3-7-1c")

    def get_forbidden_keywords(self, scene: SceneIdentifier) -> list[str]:
        """禁止キーワードリストのみを取得する

        Args:
            scene: 対象シーンの識別子

        Returns:
            list[str]: 禁止キーワードリスト
        """
        # 実装は L3-7-1d で行う
        raise NotImplementedError("Implemented in L3-7-1d")
```

### テストケース（モック使用）

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | インスタンス生成 | 全依存を注入して生成 |
| 2 | build_context() 呼び出し | モックで正常系確認 |
| 3 | ContextBuildResult 生成 | 成功結果の生成 |
| 4 | ContextBuildResult エラー | has_errors() の動作 |
| 5 | ContextBuildResult 警告 | has_warnings() の動作 |

## 設計根拠

### なぜファサードパターンか

L3 レイヤーは複数のコンポーネント（SceneResolver, LazyLoader, PhaseFilter,
ContextIntegrator, InstructionGenerator, VisibilityController）で構成される。
これらを直接 L4 から呼び出すと複雑になるため、ファサードで単一の
エントリーポイントを提供する。

### なぜ依存注入（DI）か

1. **テスト容易性**: モックを注入してユニットテスト可能
2. **柔軟性**: 実装の差し替えが容易
3. **明示的な依存**: 必要なコンポーネントが明確

### Protocol の活用

Python の Protocol を使用することで、具体クラスへの依存を避け、
インターフェースに対してプログラミングできる。

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
