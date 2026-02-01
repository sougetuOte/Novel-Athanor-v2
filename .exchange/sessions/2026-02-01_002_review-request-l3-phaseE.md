# レビュー依頼: L3 Phase E - 伏線・Visibility 統合 実装監査

## Meta

| 項目 | 値 |
|------|-----|
| Session ID | 2026-02-01_002 |
| 日時 | 2026-02-01 |
| 依頼者 | Camel (Claude Opus 4.5) |
| 依頼種別 | 実装レビュー（伏線・Visibility統合監査） |

---

## 1. 背景

L3（Context Builder Layer）の Phase E を実装完了しました。
Phase D は前回レビュー済み（2026-02-01_001、判定: A）です。

**今回の実装内容**:
- 伏線指示生成の改善（code-simplifier, Audit Warning 修正）
- ForbiddenKeywordCollector 実装
- VisibilityFilteringService 実装
- HintCollector 実装
- 統合テスト追加

**品質指標**:
- テスト: 655件 全パス（+79件）
- mypy: エラー 0 件
- ruff: 警告 0 件
- 内部監査: A 評価（Critical: 0, Warning: 0, Info: 5）

---

## 2. レビュー対象

### 2.1 伏線指示生成（既存コード改善）

| ファイル | 変更内容 |
|----------|---------|
| `foreshadowing_identifier.py` | set intersection, any() 最適化 |
| `instruction_generator.py` | 4メソッド→1メソッド統合, Audit Warning 修正 |

### 2.2 Phase E: 新規実装（4ファイル）

| ファイル | 内容 | テスト数 |
|----------|------|---------|
| `forbidden_keyword_collector.py` | 禁止キーワード収集（伏線+可視性+グローバル） | 11件 |
| `visibility_filtering.py` | 可視性フィルタリングサービス | 12件 |
| `hint_collector.py` | ヒント収集・統合 | 15件 |
| `foreshadow_instruction.py` | `get_for_foreshadowing()` 追加 | （既存テストに含む） |

### 2.3 統合テスト（2ファイル）

| ファイル | 内容 | テスト数 |
|----------|------|---------|
| `test_foreshadow_integration.py` | 伏線指示書生成の完全フロー | 8件 |
| `test_visibility_integration.py` | 可視性システムの完全フロー | 11件 |

---

## 3. レビュー観点

### 3.1 伏線システムとの連携

| コンポーネント | 連携先 |
|---------------|--------|
| ForeshadowingIdentifier | ForeshadowingRepository.list_all() |
| InstructionGeneratorImpl | ForeshadowingRepository.read() |
| ForbiddenKeywordCollector | ForeshadowInstructions.get_all_forbidden() |

### 3.2 可視性システムとの連携

| コンポーネント | 連携先 |
|---------------|--------|
| VisibilityFilteringService | L2 VisibilityController.filter() |
| HintCollector | VisibilityAwareContext.hints |

### 3.3 仕様書との整合性

| 仕様書 | 確認観点 |
|--------|----------|
| `04_ai-information-control.md` | AI可視性レベル（0-3） |
| `05_foreshadowing-system.md` | 伏線指示書の構造 |
| `08_agent-design.md` Section 8 | 禁止キーワード統合 |

---

## 4. 設計上の決定事項

### 4.1 ForbiddenKeywordCollector の3ソース統合

```python
def collect(self, scene, foreshadow_instructions):
    # 1. 伏線指示書から forbidden_expressions
    if foreshadow_instructions:
        fs_keywords = foreshadow_instructions.get_all_forbidden()
        result.add_from_source("foreshadowing", fs_keywords)

    # 2. visibility.yaml から global_forbidden_keywords
    visibility_keywords = self._collect_from_visibility()
    result.add_from_source("visibility", visibility_keywords)

    # 3. forbidden_keywords.txt からグローバル禁止リスト
    global_keywords = self._collect_from_global()
    result.add_from_source("global", global_keywords)

    result.finalize()  # 重複排除 + ソート
    return result
```

ソースの優先順位と統合方法は適切か？

### 4.2 HintCollector の優先度計算

```python
@dataclass
class CollectedHint:
    source: HintSource
    strength: float = 0.5
    priority: float = field(default=0.0, init=False)

    def __post_init__(self):
        source_weight = {
            HintSource.FORESHADOWING: 1.0,  # 伏線最優先
            HintSource.VISIBILITY: 0.8,
            HintSource.CHARACTER: 0.6,
            HintSource.WORLD: 0.5,
        }
        self.priority = source_weight[self.source] * self.strength
```

この優先度計算ロジックは適切か？

### 4.3 VisibilityFilteringService と L2 連携

```python
class VisibilityFilteringService:
    def __init__(self, visibility_controller: VisibilityController):
        self.visibility_controller = visibility_controller

    def filter_characters(self, characters: dict[str, str]) -> FilteringResult:
        for name, content in characters.items():
            # L2 の filter() を使用（可視性コメントベース）
            filter_result = self.visibility_controller.filter(content)
            filtered[name] = filter_result.content
            # AWARE セクションからヒントを収集
            for hint_text in filter_result.hints:
                hints.append(VisibilityHint(...))
```

L2 VisibilityController との連携方法は適切か？

---

## 5. Audit Warning 修正内容

### 修正済み事項

| # | 問題 | 対応 |
|---|------|------|
| WARN-001 | Protocol/Impl シグネチャ不一致 | Protocol を `appearing_characters` パラメータに統一 |
| WARN-002 | `repository.read()` 例外処理なし | try/except で KeyError, FileNotFoundError を処理 |
| WARN-003 | `determine_action()` が毎回全スキャン | 単一 foreshadowing を直接読んで判定 |

### code-simplifier 改善

| ファイル | 改善内容 |
|----------|---------|
| `foreshadowing_identifier.py` | set intersection, any() comprehension |
| `instruction_generator.py` | 4つの `_generate_*` → 1つの `_generate_instruction` |

---

## 6. 特に確認してほしい点

### 6.1 InstructionGenerator Protocol の変更

**変更前**:
```python
def generate(self, scene: SceneIdentifier, foreshadowings: list[dict[str, Any]]) -> ForeshadowInstructions:
```

**変更後**:
```python
def generate(self, scene: SceneIdentifier, appearing_characters: list[str] | None = None) -> ForeshadowInstructions:
```

Impl が ForeshadowingRepository を内部で使用するため、外部からの foreshadowings 引数を削除。
この Protocol 変更は妥当か？

### 6.2 VisibilityHint のフィールド設計

現在:
```python
@dataclass
class VisibilityHint:
    source_section: str  # "character.Alice" 形式
    hint_text: str
    level: AIVisibilityLevel
```

HintCollector で `source_section` を parse して category/entity_id を抽出。
別フィールドで持つべきか？

### 6.3 HINT アクションのみ HintCollector で収集

```python
def _collect_from_foreshadowing(self, instructions):
    for inst in instructions.instructions:
        if inst.action == InstructionAction.HINT:  # HINT のみ
            collected.append(CollectedHint(...))
```

PLANT/REINFORCE は InstructionGenerator の指示書として直接扱い、
HINT のみを HintCollector で収集。この分離は適切か？

---

## 7. 回答フォーマット

```markdown
# レビュー回答: L3 Phase E - 伏線・Visibility 統合 実装監査

## Meta
| 項目 | 値 |
|------|-----|
| Session ID | 2026-02-01_002 |
| 日時 | YYYY-MM-DD |
| レビュアー | Antigravity |
| 判定 | [A/B/C/D] |

## 1. 伏線システム連携評価
...

## 2. 可視性システム連携評価
...

## 3. 仕様書整合性評価
...

## 4. 設計決定の評価
### 4.1 ForbiddenKeywordCollector の3ソース統合
...
### 4.2 HintCollector の優先度計算
...
### 4.3 VisibilityFilteringService と L2 連携
...

## 5. 問題点・指摘事項

### [重要度: Critical/Warning/Info]
| No. | 対象ファイル | 問題内容 | 推奨対応 |
|-----|-------------|---------|---------|
| 1 | ... | ... | ... |

## 6. 質問への回答
### 6.1 InstructionGenerator Protocol の変更
...
### 6.2 VisibilityHint のフィールド設計
...
### 6.3 HINT アクションのみ HintCollector で収集
...

## 7. 総合評価
...

## 8. 推奨事項
...
```

---

## 8. 参照ファイル一覧

```
# Phase E 実装（レビュー対象）
src/core/context/
├── foreshadowing_identifier.py      # 改善済み
├── instruction_generator.py         # 改善済み + Audit Warning 修正
├── foreshadow_instruction.py        # get_for_foreshadowing() 追加
├── forbidden_keyword_collector.py   # 新規
├── visibility_filtering.py          # 新規
├── hint_collector.py                # 新規
└── visibility_context.py            # filtered_characters/world_settings 追加

# テスト
tests/core/context/
├── test_foreshadowing_identifier.py
├── test_instruction_generator.py
├── test_forbidden_keyword_collector.py   # 新規
├── test_visibility_filtering.py          # 新規
├── test_hint_collector.py                # 新規
├── test_foreshadow_integration.py        # 新規（統合テスト）
└── test_visibility_integration.py        # 新規（統合テスト）

# L2 連携先（参照用）
src/core/services/
├── visibility_controller.py         # L2 可視性コントローラー
└── expression_filter.py             # 禁止キーワードチェック

src/core/repositories/
└── foreshadowing.py                 # ForeshadowingRepository

# 仕様書
docs/specs/novel-generator-v2/
├── 04_ai-information-control.md
├── 05_foreshadowing-system.md
└── 08_agent-design.md
```

---

## 9. テスト実行結果

```
============================= 655 passed in 2.25s =============================
```

全テストが成功しています。

---

## 10. 次のフェーズ

Phase E 完了後、次は **Phase F: Context Builder ファサード** に進む予定:
- L3-7-1a: ContextBuilder Protocol
- L3-7-1b: build_context() 実装
- L3-7-1c: get_foreshadow_instructions() 実装
- L3-7-1d: get_forbidden_keywords() 実装
- L3-7-2a: ContextBuilder 統合テスト
