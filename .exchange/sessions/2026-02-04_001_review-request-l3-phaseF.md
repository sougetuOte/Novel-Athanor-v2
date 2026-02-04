# レビュー依頼: L3 Phase F - ContextBuilder ファサード 実装監査

## Meta

| 項目 | 値 |
|------|-----|
| Session ID | 2026-02-04_001 |
| 日時 | 2026-02-04 |
| 依頼者 | Camel (Claude Opus 4.5) |
| 依頼種別 | 実装レビュー（ContextBuilder ファサード監査） |

---

## 1. 背景

L3（Context Builder Layer）の Phase F（最終フェーズ）を実装完了しました。
Phase E は前回レビュー済み（2026-02-01_002、判定: 要確認）です。

**Phase F の内容**:
L3 レイヤー全体を統合する ContextBuilder ファサードの実装。
L4 エージェント（Continuity Director, Ghost Writer）が使用する単一エントリーポイントを提供。

**品質指標**:
- テスト: 726件 全パス（Phase F で +71件）
- mypy: エラー 0 件
- ruff: 警告 0 件
- 内部監査: B 評価（Critical: 1, Warning: 22, Info: 18）
- 即時修正 7件を実施済み（Critical 解消、Warning 一部解消）

---

## 2. レビュー対象

### 2.1 ContextBuilder ファサード（新規: 1ファイル）

| ファイル | 内容 | 行数 |
|----------|------|------|
| `context_builder.py` | ContextBuilder クラス + ContextBuildResult データクラス | ~500行 |

### 2.2 監査修正（既存ファイル変更: 3ファイル）

| ファイル | 変更内容 |
|----------|---------|
| `hint_collector.py` | `from __future__ import annotations` 追加、末尾遅延import削除 |
| `instruction_generator.py` | 関数内 import をファイル先頭に移動 |
| `__init__.py` | ContextBuilder, ContextBuildResult エクスポート追加 |

### 2.3 テスト（新規: 6ファイル）

| ファイル | 内容 | テスト数 |
|----------|------|---------|
| `conftest.py` | 共通フィクスチャ（scene, builder） | - |
| `test_context_builder.py` | 初期化・データクラステスト | 15件 |
| `test_context_builder_build.py` | build_context() テスト | 7件 |
| `test_context_builder_foreshadow.py` | 伏線指示メソッドテスト | 16件 |
| `test_context_builder_forbidden.py` | 禁止キーワードメソッドテスト | 17件 |
| `test_context_builder_integration.py` | E2E統合テスト | 16件 |

---

## 3. レビュー観点

### 3.1 ファサードパターンの適用

| 観点 | 説明 |
|------|------|
| 単一エントリーポイント | ContextBuilder が L3 の唯一の public API か |
| 内部コンポーネント隠蔽 | Collector, Integrator, Filter 等が外部に漏れていないか |
| L4 からの利用性 | build_context() のインターフェースは L4 にとって十分か |

### 3.2 L2 サービスとの連携

| コンポーネント | 連携先 |
|---------------|--------|
| ContextBuilder | VisibilityController（Optional） |
| ContextBuilder | ForeshadowingRepository（Optional） |
| InstructionGeneratorImpl | ForeshadowingRepository.read() |
| VisibilityFilteringService | VisibilityController.filter() |
| ForbiddenKeywordCollector | ForeshadowInstructions（禁止表現） |

### 3.3 仕様書との整合性

| 仕様書 | 確認観点 |
|--------|----------|
| `02_architecture.md` | Context Builder の責務 (Section 2.4) |
| `04_ai-information-control.md` | AI可視性フィルタリング |
| `05_foreshadowing-system.md` | 伏線指示書の生成と統合 |
| `08_agent-design.md` | 禁止キーワード統合 (Section 8) |

---

## 4. 設計上の決定事項

### 4.1 Hybrid DI パターン

```python
class ContextBuilder:
    def __init__(
        self,
        vault_root: Path,
        *,
        work_name: str = "",
        visibility_controller: VisibilityController | None = None,
        foreshadowing_repository: ForeshadowingRepository | None = None,
        phase_order: list[str] | None = None,
    ) -> None:
```

- L2 サービスは Optional パラメータとして外部注入
- L3 内部コンポーネント（Collector, Integrator, Filter）は `__init__` 内で自動構築
- 仕様書の Protocol ベース 6 引数方式から変更

この DI 方式は適切か？

### 4.2 ContextBuildResult の構成

```python
@dataclass
class ContextBuildResult:
    context: FilteredContext
    visibility_context: VisibilityAwareContext | None
    foreshadow_instructions: ForeshadowInstructions
    forbidden_keywords: list[str]
    hints: HintCollection
    success: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
```

- `visibility_context` と `hints` は仕様書にないが Phase E の成果物として追加
- `errors` リストは現在使用されていない（常に空、success は常に True）

errors の活用方針について助言が欲しい。

### 4.3 キャッシュ戦略

```python
# キャッシュキー: "{episode_id}:{sequence_id}"
self._instruction_cache: dict[str, ForeshadowInstructions] = {}
self._forbidden_cache: dict[str, list[str]] = {}
self._forbidden_result_cache: dict[str, ForbiddenKeywordResult] = {}
```

- `current_phase` がキャッシュキーに含まれていない
- サイズ上限なし（LRU 未導入）
- `build_context()` は `get_forbidden_keywords()` 経由でキャッシュを利用（監査修正後）

キャッシュキーに `current_phase` を含めるべきか？

### 4.4 ExpressionFilter の除外

仕様書 L3-7-1b では `ExpressionFilter` を L2 依存として想定していたが、実装では除外。
理由: ExpressionFilter は L4 Reviewer の責務であり、L3 では禁止キーワードのリスト管理のみ担当。

この設計判断は妥当か？

---

## 5. 内部監査結果サマリー

### 5.1 即時修正済み（7件）

| # | 内容 | 対応 |
|---|------|------|
| FIX-01 | conftest.py 不在、フィクスチャ重複 | conftest.py 作成、4ファイルから重複削除 |
| FIX-02 | 未使用 MagicMock import | 削除 |
| FIX-03 | `except Exception:` で例外情報握りつぶし | `except Exception as e:` に変更 |
| FIX-04 | `build_context()` が forbidden keyword をキャッシュしない | `get_forbidden_keywords()` 経由に統一 |
| FIX-05 | hint_collector.py の末尾遅延 import | `from __future__ import annotations` に変更 |
| FIX-06 | instruction_generator.py の関数内 import | ファイル先頭に移動 |
| FIX-07 | タスクドキュメント5件のステータスが backlog | done に更新 |

### 5.2 残存 Warning（次スプリントで対応予定）

| # | 内容 | 重要度 |
|---|------|--------|
| 1 | `errors` リストが常に空（success 常に True） | Warning |
| 2 | 広範な `except Exception` 使用（3箇所） | Warning |
| 3 | logging 機構の不在 | Warning |
| 4 | キャッシュに上限がない | Warning |
| 5 | NONE 指示がプロンプトに出力されない | Warning |
| 6 | テスト命名規約の不統一 | Warning |
| 7 | エッジケーステスト不足 | Warning |

---

## 6. 特に確認してほしい点

### 6.1 build_context() のオーケストレーション

```python
def build_context(self, scene: SceneIdentifier) -> ContextBuildResult:
    # 1. Context integration (collect all context data)
    context, integration_warnings = self._integrator.integrate_with_warnings(...)

    # 2. Foreshadowing instructions (optional)
    foreshadow_instructions = self.get_foreshadow_instructions(scene)

    # 3. Forbidden keywords (uses cache)
    forbidden_keywords = self.get_forbidden_keywords(scene)

    # 4. Visibility filtering (optional)
    visibility_context = self._visibility_filtering_service.filter_context(context)

    # 5. Hint collection
    hints = self._hint_collector.collect_all(
        visibility_context=visibility_context,
        foreshadow_instructions=foreshadow_instructions,
    )

    return ContextBuildResult(...)
```

この5ステップのオーケストレーション順序は適切か？
特に、forbidden keywords の取得にforeshadow_instructions が必要なため、
ステップ2→3は順序依存がある。

### 6.2 Graceful Degradation の一貫性

- `visibility_controller = None` → `visibility_context = None`（正常動作）
- `foreshadowing_repository = None` → 空の `ForeshadowInstructions`（正常動作）
- 各ステップの例外 → `warnings` に記録して続行

全コンポーネントの障害隔離は十分か？

### 6.3 プロンプトフォーマット

```python
def _format_instructions_for_prompt(self, instructions):
    # PLANT/REINFORCE/HINT のみ出力、NONE は含まない
    lines = ["## 伏線指示書\n"]
    for inst in active:
        label = _ACTION_LABELS.get(inst.action, str(inst.action.value))
        lines.append(f"### {inst.foreshadowing_id} [{label}]")
        ...
```

仕様書では NONE 指示（「触れてはいけない伏線」セクション）も出力する設計。
現在は active な指示のみ出力。NONE 指示の出力は必要か？

---

## 7. 回答フォーマット

```markdown
# レビュー回答: L3 Phase F - ContextBuilder ファサード 実装監査

## Meta
| 項目 | 値 |
|------|-----|
| Session ID | 2026-02-04_001 |
| 日時 | YYYY-MM-DD |
| レビュアー | Antigravity |
| 判定 | [A/B/C/D] |

## 1. ファサードパターン評価
...

## 2. L2 連携評価
...

## 3. 仕様書整合性評価
...

## 4. 設計決定の評価
### 4.1 Hybrid DI パターン
...
### 4.2 ContextBuildResult の構成
...
### 4.3 キャッシュ戦略
...
### 4.4 ExpressionFilter の除外
...

## 5. 問題点・指摘事項

### [重要度: Critical/Warning/Info]
| No. | 対象ファイル | 問題内容 | 推奨対応 |
|-----|-------------|---------|---------|
| 1 | ... | ... | ... |

## 6. 質問への回答
### 6.1 build_context() のオーケストレーション
...
### 6.2 Graceful Degradation の一貫性
...
### 6.3 プロンプトフォーマット
...

## 7. 総合評価
...

## 8. 推奨事項
...
```

---

## 8. 参照ファイル一覧

```
# Phase F 実装（レビュー対象）
src/core/context/
├── context_builder.py          # 新規（ファサード）
├── __init__.py                 # 更新（エクスポート追加）
├── hint_collector.py           # 監査修正（import 整理）
└── instruction_generator.py    # 監査修正（import 整理）

# テスト
tests/core/context/
├── conftest.py                         # 新規（共通フィクスチャ）
├── test_context_builder.py             # 新規（初期化テスト 15件）
├── test_context_builder_build.py       # 新規（build テスト 7件）
├── test_context_builder_foreshadow.py  # 新規（伏線テスト 16件）
├── test_context_builder_forbidden.py   # 新規（禁止KWテスト 17件）
└── test_context_builder_integration.py # 新規（統合テスト 16件）

# L3 内部コンポーネント（Phase A-E で実装済み、参照用）
src/core/context/
├── scene_identifier.py
├── scene_resolver.py
├── lazy_loader.py
├── phase_filter.py
├── filtered_context.py
├── context_integrator.py
├── collectors/
│   ├── plot_collector.py
│   ├── summary_collector.py
│   ├── character_collector.py
│   ├── world_setting_collector.py
│   └── style_guide_collector.py
├── foreshadow_instruction.py
├── foreshadowing_identifier.py
├── instruction_generator.py
├── forbidden_keyword_collector.py
├── visibility_filtering.py
├── visibility_context.py
└── hint_collector.py

# L2 連携先（参照用）
src/core/services/visibility_controller.py
src/core/repositories/foreshadowing.py

# 仕様書
docs/specs/novel-generator-v2/
├── 02_architecture.md          # Section 2.4 Context Builder
├── 04_ai-information-control.md
├── 05_foreshadowing-system.md
└── 08_agent-design.md          # Section 8 禁止キーワード

# 監査レポート
docs/memos/2026-02-04-L3-PhaseF-audit-report.md
```

---

## 9. テスト実行結果

```
============================= 726 passed in 2.50s =============================
```

全テストが成功しています。

---

## 10. 次のフェーズ

Phase F 完了により L3 レイヤーの P1 タスクは全て完了。
次は以下のいずれかに進む予定:
- L4 エージェントレイヤーの設計・実装
- L3-8: AoT Parallel Collector（P2 最適化タスク）
- L2 残 P2 タスク
