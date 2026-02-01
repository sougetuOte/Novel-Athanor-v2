# L3 レイヤー実装ガイド（Context Builder Layer）

**作成日**: 2026-01-26
**前提**: L0/L1/L2 完了済み
**フェーズ**: PLANNING → BUILDING
**対象仕様**: `docs/specs/novel-generator-v2/02_architecture.md` Section 2.4, `08_agent-design.md` Section 3

---

## 1. 概要

L3（Context Builder Layer）の実装ガイド。
L2（AI情報制御レイヤー）のサービスを統合し、シーン執筆に必要なコンテキストを構築する。

### L3 の責務

1. **シーン→関連ファイル特定**: 執筆対象シーンに必要なファイルを特定
2. **Lazy Loading**: 必要最小限のデータを遅延読み込み
3. **Phase Filtering**: `current_phase` に基づくキャラ/世界観のフィルタリング
4. **コンテキスト統合**: Plot/Summary/Characters/WorldSettings/Foreshadowing を統合
5. **伏線指示書生成**: AIに渡す伏線の「匂わせ」指示を生成

---

## 2. タスク一覧（細粒度分割）

### 凡例

| 記号 | 意味 |
|------|------|
| 🔲 | 未着手 |
| 📋 | 着手可能 |
| ✅ | 完了 |
| 🔀 | 並列実行可能グループ |

### L3-1: Context Builder 基盤

| ID | タスク | 優先度 | 依存 | ステータス | ドキュメント |
|----|--------|--------|------|-----------|-------------|
| L3-1-1a | SceneIdentifier データクラス定義 | P1 | - | ✅ | [L3-1-1a](L3-1-1a_scene-identifier.md) |
| L3-1-1b | シーン→ファイルパス解決ロジック | P1 | L3-1-1a, L1-3-2 | ✅ | [L3-1-1b](L3-1-1b_scene-file-resolver.md) |
| L3-1-1c | 関連キャラクター特定ロジック | P1 | L3-1-1b | ✅ | [L3-1-1c](L3-1-1c_character-identifier.md) |
| L3-1-1d | 関連世界観設定特定ロジック | P1 | L3-1-1b | ✅ | [L3-1-1d](L3-1-1d_world-setting-identifier.md) |
| L3-1-1e | シーン→ファイル特定テスト | P1 | L3-1-1c, L3-1-1d | ✅ | [L3-1-1e](L3-1-1e_scene-resolver-test.md) |

### L3-2: Lazy Loader

| ID | タスク | 優先度 | 依存 | ステータス | ドキュメント |
|----|--------|--------|------|-----------|-------------|
| L3-2-1a | LazyLoader プロトコル定義 | P1 | - | ✅ | [L3-2-1a](L3-2-1a_lazy-loader-protocol.md) |
| L3-2-1b | LazyLoadedContent データクラス | P1 | L3-2-1a | ✅ | [L3-2-1b](L3-2-1b_lazy-loaded-content.md) |
| L3-2-1c | Lazy読み込み実装（キャッシュ機構） | P1 | L3-2-1b | ✅ | [L3-2-1c](L3-2-1c_lazy-loader-impl.md) |
| L3-2-1d | Graceful Degradation 実装 | P1 | L3-2-1c | ✅ | [L3-2-1d](L3-2-1d_graceful-degradation.md) |
| L3-2-1e | LazyLoader テスト | P1 | L3-2-1d | ✅ | [L3-2-1e](L3-2-1e_lazy-loader-test.md) |

### L3-3: Phase Filter

| ID | タスク | 優先度 | 依存 | ステータス | ドキュメント |
|----|--------|--------|------|-----------|-------------|
| L3-3-1a | PhaseFilter プロトコル定義 | P1 | - | ✅ | [L3-3-1a](L3-3-1a_phase-filter-protocol.md) |
| L3-3-1b | キャラクター Phase フィルタ | P1 | L3-3-1a, L1-2-2 | ✅ | [L3-3-1b](L3-3-1b_character-phase-filter.md) |
| L3-3-1c | WorldSetting Phase フィルタ | P1 | L3-3-1a, L1-2-3 | ✅ | [L3-3-1c](L3-3-1c_world-setting-phase-filter.md) |
| L3-3-1d | PhaseFilter テスト | P1 | L3-3-1b, L3-3-1c | ✅ | [L3-3-1d](L3-3-1d_phase-filter-test.md) |

### L3-4: Context Integrator（コンテキスト統合）

| ID | タスク | 優先度 | 依存 | ステータス | ドキュメント |
|----|--------|--------|------|-----------|-------------|
| L3-4-1a | FilteredContext データクラス定義 | P1 | - | ✅ | [L3-4-1a](L3-4-1a_filtered-context.md) |
| L3-4-1b | ContextIntegrator プロトコル定義 | P1 | L3-4-1a | ✅ | [L3-4-1b](L3-4-1b_context-integrator-protocol.md) |
| L3-4-2a | Plot コンテキスト収集 | P1 | L3-4-1b, L1-2-4 | ✅ | [L3-4-2a](L3-4-2a_plot-collector.md) |
| L3-4-2b | Summary コンテキスト収集 | P1 | L3-4-1b, L1-2-5 | ✅ | [L3-4-2b](L3-4-2b_summary-collector.md) |
| L3-4-2c | Character コンテキスト収集（Phaseフィルタ適用） | P1 | L3-4-1b, L3-3-1b | ✅ | [L3-4-2c](L3-4-2c_character-collector.md) |
| L3-4-2d | WorldSetting コンテキスト収集（Phaseフィルタ適用） | P1 | L3-4-1b, L3-3-1c | ✅ | [L3-4-2d](L3-4-2d_world-setting-collector.md) |
| L3-4-2e | StyleGuide コンテキスト収集 | P1 | L3-4-1b, L1-2-9 | ✅ | [L3-4-2e](L3-4-2e_style-guide-collector.md) |
| L3-4-3a | ContextIntegrator 統合テスト | P1 | L3-4-2a〜L3-4-2e | 📋 | [L3-4-3a](L3-4-3a_context-integrator-test.md) |

### L3-5: 伏線指示書生成

| ID | タスク | 優先度 | 依存 | ステータス | ドキュメント |
|----|--------|--------|------|-----------|-------------|
| L3-5-1a | ForeshadowInstruction データクラス | P1 | - | ✅ | [L3-5-1a](L3-5-1a_foreshadow-instruction.md) |
| L3-5-1b | InstructionGenerator プロトコル | P1 | L3-5-1a | ✅ | [L3-5-1b](L3-5-1b_instruction-generator-protocol.md) |
| L3-5-2a | シーン→関連伏線特定 | P1 | L3-5-1b, L2-3-1 | 🔲 | [L3-5-2a](L3-5-2a_scene-foreshadowing-identifier.md) |
| L3-5-2b | 伏線ステータス別指示生成 | P1 | L3-5-2a | 🔲 | [L3-5-2b](L3-5-2b_instruction-generator-impl.md) |
| L3-5-2c | 禁止キーワード収集 | P1 | L3-5-2b, L2-2-1 | 🔲 | [L3-5-2c](L3-5-2c_forbidden-keyword-collector.md) |
| L3-5-2d | 許可表現リスト収集 | P2 | L3-5-2b | 🔲 | [L3-5-2d](L3-5-2d_allowed-expression-collector.md) |
| L3-5-3a | 伏線指示書生成テスト | P1 | L3-5-2c | 🔲 | [L3-5-3a](L3-5-3a_foreshadow-instruction-test.md) |

### L3-6: Visibility 統合

| ID | タスク | 優先度 | 依存 | ステータス | ドキュメント |
|----|--------|--------|------|-----------|-------------|
| L3-6-1a | VisibilityAwareContext データクラス | P1 | L3-4-1a | ✅ | [L3-6-1a](L3-6-1a_visibility-aware-context.md) |
| L3-6-1b | Visibility フィルタリング統合 | P1 | L3-6-1a, L2-1-4 | 🔲 | [L3-6-1b](L3-6-1b_visibility-filtering-integration.md) |
| L3-6-1c | Hint 収集・統合 | P1 | L3-6-1b | 🔲 | [L3-6-1c](L3-6-1c_hint-collection.md) |
| L3-6-1d | Visibility統合テスト | P1 | L3-6-1c | 🔲 | [L3-6-1d](L3-6-1d_visibility-integration-test.md) |

### L3-7: Context Builder ファサード

| ID | タスク | 優先度 | 依存 | ステータス | ドキュメント |
|----|--------|--------|------|-----------|-------------|
| L3-7-1a | ContextBuilder クラス定義 | P1 | L3-2-1c, L3-3-1b, L3-4-1b | 🔲 | [L3-7-1a](L3-7-1a_context-builder-facade.md) |
| L3-7-1b | build_context() メソッド実装 | P1 | L3-7-1a, L3-6-1b | 🔲 | [L3-7-1b](L3-7-1b_build-context-impl.md) |
| L3-7-1c | get_foreshadow_instructions() 実装 | P1 | L3-7-1a, L3-5-2b | 🔲 | [L3-7-1c](L3-7-1c_get-foreshadow-instructions-impl.md) |
| L3-7-1d | get_forbidden_keywords() 実装 | P1 | L3-7-1a, L3-5-2c | 🔲 | [L3-7-1d](L3-7-1d_get-forbidden-keywords-impl.md) |
| L3-7-2a | ContextBuilder 統合テスト | P1 | L3-7-1b, L3-7-1c, L3-7-1d | 🔲 | [L3-7-2a](L3-7-2a_context-builder-test.md) |

### L3-8: AoT Parallel Collector（P2 - 将来実装）

| ID | タスク | 優先度 | 依存 | ステータス |
|----|--------|--------|------|-----------|
| L3-8-1a | Atom 定義（並列収集単位） | P2 | L3-7-1a | 🔲 |
| L3-8-1b | 並列実行フレームワーク | P2 | L3-8-1a | 🔲 |
| L3-8-1c | 結果マージロジック | P2 | L3-8-1b | 🔲 |
| L3-8-2a | AoT Collector テスト | P2 | L3-8-1c | 🔲 |

---

## 3. 実装順序（依存グラフ）

```
Phase A: 基盤データクラス定義（並列可能）
┌─────────────────────────────────────────────────────────────┐
│  L3-1-1a (SceneIdentifier)                                  │
│  L3-2-1a (LazyLoader Protocol)                              │
│  L3-3-1a (PhaseFilter Protocol)                             │
│  L3-4-1a (FilteredContext)                                  │
│  L3-5-1a (ForeshadowInstruction)                            │
│  L3-6-1a (VisibilityAwareContext)                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
Phase B: プロトコル定義（並列可能）
┌─────────────────────────────────────────────────────────────┐
│  L3-2-1b (LazyLoadedContent)                                │
│  L3-4-1b (ContextIntegrator Protocol)                       │
│  L3-5-1b (InstructionGenerator Protocol)                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
Phase C: 個別機能実装
┌─────────────────────────────────────────────────────────────┐
│  グループC1（シーン解決）:                                  │
│    L3-1-1b → L3-1-1c/L3-1-1d → L3-1-1e                      │
│                                                             │
│  グループC2（Lazy Loader）:                                 │
│    L3-2-1c → L3-2-1d → L3-2-1e                              │
│                                                             │
│  グループC3（Phase Filter）:                                │
│    L3-3-1b / L3-3-1c → L3-3-1d                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
Phase D: コンテキスト収集（並列可能）
┌─────────────────────────────────────────────────────────────┐
│  L3-4-2a (Plot)                                             │
│  L3-4-2b (Summary)                                          │
│  L3-4-2c (Character)                                        │
│  L3-4-2d (WorldSetting)                                     │
│  L3-4-2e (StyleGuide)                                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
Phase E: 伏線・Visibility 統合
┌─────────────────────────────────────────────────────────────┐
│  L3-5-2a → L3-5-2b → L3-5-2c → L3-5-3a                      │
│  L3-6-1b → L3-6-1c → L3-6-1d                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
Phase F: ファサード統合
┌─────────────────────────────────────────────────────────────┐
│  L3-7-1a → L3-7-1b / L3-7-1c / L3-7-1d → L3-7-2a            │
└─────────────────────────────────────────────────────────────┘
                              ↓
Phase G: 統合テスト
┌─────────────────────────────────────────────────────────────┐
│  L3-4-3a (ContextIntegrator)                                │
│  L3-7-2a (ContextBuilder)                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. 並列作業ガイド

### 作業者別分担案（2名の場合）

| 作業者 | 担当領域 | タスク |
|--------|----------|--------|
| A | シーン解決 + Lazy Loader | L3-1-*, L3-2-* |
| B | Phase Filter + Context収集 | L3-3-*, L3-4-* |
| A/B | 伏線・Visibility | L3-5-*, L3-6-*（完了順で担当） |
| A+B | ファサード統合 | L3-7-*（共同作業） |

### 手戻り最小化のための分離点

各タスクは以下のインターフェースで分離されており、手戻り時の影響範囲が限定される：

1. **SceneIdentifier**: シーン特定の入出力契約
2. **LazyLoader Protocol**: 遅延読み込みの抽象
3. **PhaseFilter Protocol**: フェーズフィルタの抽象
4. **FilteredContext**: コンテキスト統合の出力形式
5. **ForeshadowInstruction**: 伏線指示の形式

**手戻り発生時**: プロトコル/データクラスの変更は影響範囲が大きいため、Phase A/B は慎重にレビューする。

---

## 5. ディレクトリ構成

### 新規作成ファイル

```
src/core/
├── context/                          # L3 新規ディレクトリ
│   ├── __init__.py
│   ├── scene_identifier.py           # L3-1-1a
│   ├── scene_resolver.py             # L3-1-1b, L3-1-1c, L3-1-1d
│   ├── lazy_loader.py                # L3-2-*
│   ├── phase_filter.py               # L3-3-*
│   ├── context_integrator.py         # L3-4-*
│   ├── foreshadow_instruction.py     # L3-5-*
│   ├── visibility_context.py         # L3-6-*
│   └── context_builder.py            # L3-7-* (ファサード)
│
tests/core/
└── context/                          # L3 テスト
    ├── __init__.py
    ├── test_scene_resolver.py        # L3-1-1e
    ├── test_lazy_loader.py           # L3-2-1e
    ├── test_phase_filter.py          # L3-3-1d
    ├── test_context_integrator.py    # L3-4-3a
    ├── test_foreshadow_instruction.py # L3-5-3a
    ├── test_visibility_context.py    # L3-6-1d
    └── test_context_builder.py       # L3-7-2a
```

### 初期セットアップ手順

```bash
# context ディレクトリ作成
mkdir -p src/core/context tests/core/context
touch src/core/context/__init__.py tests/core/context/__init__.py
```

---

## 6. 各タスクの詳細仕様

### 6.1 L3-1-1a: SceneIdentifier データクラス

**ファイル**: `src/core/context/scene_identifier.py`

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True)
class SceneIdentifier:
    """シーンを一意に特定する識別子"""

    # 必須: エピソード番号 (例: "010", "ep010")
    episode_id: str

    # オプション: シーケンス番号 (例: "seq_01")
    sequence_id: Optional[str] = None

    # オプション: 章番号
    chapter_id: Optional[str] = None

    # オプション: 現在のフェーズ (例: "arc_1_reveal")
    current_phase: Optional[str] = None

    def __post_init__(self):
        if not self.episode_id:
            raise ValueError("episode_id is required")
```

**テストケース**:
- 正常: episode_id のみ指定
- 正常: 全フィールド指定
- 異常: episode_id が空 → ValueError

---

### 6.2 L3-2-1a: LazyLoader プロトコル

**ファイル**: `src/core/context/lazy_loader.py`

```python
from typing import Protocol, TypeVar, Generic, Optional
from dataclasses import dataclass
from enum import Enum

T = TypeVar('T')

class LoadPriority(Enum):
    """読み込み優先度（Graceful Degradation用）"""
    REQUIRED = "required"      # 必須（失敗時はエラー）
    OPTIONAL = "optional"      # 付加的（失敗時は警告して続行）

@dataclass
class LazyLoadResult(Generic[T]):
    """遅延読み込み結果"""
    success: bool
    data: Optional[T]
    error: Optional[str] = None
    warnings: list[str] = field(default_factory=list)

class LazyLoader(Protocol[T]):
    """遅延読み込みプロトコル"""

    def load(self, identifier: str, priority: LoadPriority) -> LazyLoadResult[T]:
        """指定されたidentifierのデータを読み込む"""
        ...

    def is_cached(self, identifier: str) -> bool:
        """キャッシュ済みかどうか"""
        ...

    def clear_cache(self) -> None:
        """キャッシュをクリア"""
        ...
```

---

### 6.3 L3-3-1a: PhaseFilter プロトコル

**ファイル**: `src/core/context/phase_filter.py`

```python
from typing import Protocol, TypeVar
from src.core.models.character import Character
from src.core.models.world_setting import WorldSetting

T = TypeVar('T')

class PhaseFilter(Protocol[T]):
    """フェーズに基づくフィルタリングプロトコル"""

    def filter_by_phase(self, entity: T, phase: str) -> T:
        """指定フェーズに適用可能な情報のみを抽出"""
        ...

    def get_available_phases(self, entity: T) -> list[str]:
        """エンティティで利用可能なフェーズ一覧"""
        ...
```

---

### 6.4 L3-4-1a: FilteredContext データクラス

**ファイル**: `src/core/context/context_integrator.py`

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class FilteredContext:
    """フィルタリング済みコンテキスト"""

    # Plot 情報
    plot_l1: Optional[str] = None    # テーマ、全体方向性
    plot_l2: Optional[str] = None    # 章の目的
    plot_l3: Optional[str] = None    # シーン構成

    # Summary 情報
    summary_l1: Optional[str] = None
    summary_l2: Optional[str] = None
    summary_l3: Optional[str] = None

    # キャラクター（フェーズフィルタ済み）
    characters: dict[str, str] = field(default_factory=dict)

    # 世界観設定（フェーズフィルタ済み）
    world_settings: dict[str, str] = field(default_factory=dict)

    # スタイルガイド
    style_guide: Optional[str] = None

    # メタ情報
    scene_id: str = ""
    current_phase: Optional[str] = None
    warnings: list[str] = field(default_factory=list)
```

---

### 6.5 L3-5-1a: ForeshadowInstruction データクラス

**ファイル**: `src/core/context/foreshadow_instruction.py`

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class InstructionAction(Enum):
    """伏線指示アクション"""
    PLANT = "plant"           # 初回設置
    REINFORCE = "reinforce"   # 強化
    HINT = "hint"             # ヒント提示
    NONE = "none"             # 今回は触れない

@dataclass
class ForeshadowInstruction:
    """伏線指示書"""

    # 伏線ID
    foreshadowing_id: str

    # 今回のアクション
    action: InstructionAction

    # 許可表現（使ってよい表現）
    allowed_expressions: list[str] = field(default_factory=list)

    # 禁止表現（絶対に使ってはいけない）
    forbidden_expressions: list[str] = field(default_factory=list)

    # 指示メモ（自然言語での補足）
    note: Optional[str] = None

    # Subtlety レベル（1-10、低いほど露骨）
    subtlety_target: int = 5

@dataclass
class ForeshadowInstructions:
    """シーン全体の伏線指示書"""

    instructions: list[ForeshadowInstruction] = field(default_factory=list)
    global_forbidden_keywords: list[str] = field(default_factory=list)

    def get_all_forbidden(self) -> list[str]:
        """全禁止キーワードを取得"""
        result = list(self.global_forbidden_keywords)
        for inst in self.instructions:
            result.extend(inst.forbidden_expressions)
        return list(set(result))
```

---

### 6.6 L3-7-1a: ContextBuilder ファサード

**ファイル**: `src/core/context/context_builder.py`

```python
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from .scene_identifier import SceneIdentifier
from .context_integrator import FilteredContext
from .foreshadow_instruction import ForeshadowInstructions

@dataclass
class ContextBuildResult:
    """コンテキスト構築結果"""
    context: FilteredContext
    foreshadow_instructions: ForeshadowInstructions
    forbidden_keywords: list[str]
    success: bool
    errors: list[str]
    warnings: list[str]

class ContextBuilder:
    """コンテキスト構築ファサード（L3のエントリーポイント）"""

    def __init__(
        self,
        vault_root: Path,
        # 依存注入
        scene_resolver: "SceneResolver",
        lazy_loader: "LazyLoader",
        phase_filter: "PhaseFilter",
        context_integrator: "ContextIntegrator",
        instruction_generator: "InstructionGenerator",
        visibility_filter: "VisibilityController",
    ):
        self.vault_root = vault_root
        self.scene_resolver = scene_resolver
        self.lazy_loader = lazy_loader
        self.phase_filter = phase_filter
        self.context_integrator = context_integrator
        self.instruction_generator = instruction_generator
        self.visibility_filter = visibility_filter

    def build_context(self, scene: SceneIdentifier) -> ContextBuildResult:
        """シーンのコンテキストを構築する"""
        # 実装は L3-7-1b で
        ...
```

---

## 7. 終了条件

### 必須条件（全て満たすこと）

- [ ] 全 P1 タスク（37件）の実装完了
- [ ] 全テストがパス
- [ ] mypy エラー 0 件
- [ ] ruff 警告 0 件
- [ ] 新規コードのテストカバレッジ 90% 以上

### 成果物チェックリスト

- [ ] `src/core/context/` ディレクトリ作成（8ファイル）
- [ ] `tests/core/context/` テストディレクトリ（7ファイル）
- [ ] 各コンポーネントのユニットテスト
- [ ] ContextBuilder 統合テスト
- [ ] バックログ更新（完了タスクを ✅ に）

### 品質基準

- 仕様書 `02_architecture.md` Section 2.4 との整合性
- 仕様書 `08_agent-design.md` Section 3 との整合性
- L2 サービス（VisibilityController, ExpressionFilter, ForeshadowingManager）の正しい活用
- 既存テストが壊れていないこと

---

## 8. 実装ルール

### TDD サイクル厳守

1. **Red**: 失敗するテストを先に書く
2. **Green**: テストを通す最小限のコード
3. **Refactor**: 設計改善

### 禁止事項

- テストなしでの本実装
- スコープ外タスク（P2: L3-8-*）への着手
- 仕様書にない機能の追加
- L2 レイヤーへの変更（必要なら相談）

### 疑問発生時

実装中に仕様の曖昧さや設計上の疑問が発生した場合:
1. **即座に作業を中断**
2. **ユーザーに相談**
3. **承認を得てから再開**

---

## 9. 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成（細粒度タスク分割） |
| 2026-01-26 | Phase A 実装完了（119テストパス）、全フェーズのタスクドキュメント作成 |
| 2026-01-26 | Phase B 実装完了（144テストパス）: LazyLoadedContent, ContextIntegrator, InstructionGenerator |
| 2026-01-26 | Phase C 主要タスク完了（187テストパス）: SceneResolver, FileLazyLoader, CharacterPhaseFilter, WorldSettingPhaseFilter |
| 2026-01-31 | Phase C 完了（490テストパス）: キャラクター/世界観特定、GracefulLoader、PhaseFilter テスト |
| 2026-02-01 | Phase D Collectors 完了（565テストパス）: Plot/Summary/Character/WorldSetting/StyleGuide Collector |
