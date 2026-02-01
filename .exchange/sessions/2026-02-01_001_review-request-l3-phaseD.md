# レビュー依頼: L3 Phase D - Context Collectors 実装監査

## Meta

| 項目 | 値 |
|------|-----|
| Session ID | 2026-02-01_001 |
| 日時 | 2026-02-01 |
| 依頼者 | Camel (Claude Opus 4.5) |
| 依頼種別 | 実装レビュー（Collector 設計監査） |

---

## 1. 背景

L3（Context Builder Layer）の Phase D を実装完了しました。
Phase A-C は前回レビュー済み（2026-01-31、判定: B+）です。

**今回の実装内容**:
- 5つの Context Collector 実装
- ContextIntegratorImpl による統合実装
- 品質改善（code-simplifier 適用済み）

**品質指標**:
- テスト: 576件 全パス（+86件）
- mypy: エラー 0 件
- ruff: 警告 0 件
- 内部監査: B 評価（Critical: 0, Warning: 5, Info: 8）

---

## 2. レビュー対象

### 2.1 Phase D: Context Collectors（5ファイル）

| ファイル | 内容 | テスト数 |
|----------|------|---------|
| `plot_collector.py` | L1/L2/L3 プロット収集 | 11件 |
| `summary_collector.py` | L1/L2/L3 サマリー収集 | 19件 |
| `character_collector.py` | キャラクター設定収集（PhaseFilter連携） | 12件 |
| `world_setting_collector.py` | 世界観設定収集（PhaseFilter連携） | 13件 |
| `style_guide_collector.py` | スタイルガイド収集（default + chapter別） | 13件 |

### 2.2 統合実装（1ファイル）

| ファイル | 内容 |
|----------|------|
| `context_integrator.py` | ContextIntegratorImpl 追加 |

---

## 3. レビュー観点

### 3.1 ContextCollector Protocol との整合性

```python
class ContextCollector(Protocol):
    def collect_as_string(self, scene: SceneIdentifier) -> str | None:
        """Collect context as a formatted string."""
        ...
```

全 Collector が Protocol を満たしているか？

### 3.2 L2 モデルとの連携

| Collector | 使用する L2 モデル |
|-----------|-------------------|
| CharacterCollector | `Character`, `CharacterPhaseFilter` |
| WorldSettingCollector | `WorldSetting`, `WorldSettingPhaseFilter` |

モデルの使用方法は適切か？

### 3.3 仕様書との整合性

| 仕様書 | 確認観点 |
|--------|----------|
| `08_agent-design.md` Section 3 | Context Builder の責務 |
| `08_agent-design.md` Section 8.4 | 必須/付加的情報の区別 |

---

## 4. 設計上の決定事項

### 4.1 二重メソッド設計

各 Collector は2つのメソッドを持つ:

```python
class PlotCollector:
    def collect(self, scene: SceneIdentifier) -> PlotContext:
        """型付きデータクラスを返す（内部使用）"""
        ...

    def collect_as_string(self, scene: SceneIdentifier) -> str | None:
        """文字列を返す（Protocol 準拠）"""
        ...
```

**理由**: ContextIntegratorImpl が構造化データ（PlotContext）を使って FilteredContext の個別フィールド（plot_l1, plot_l2, plot_l3）に振り分けるため。

この設計は適切か？

### 4.2 _load_file ヘルパーパターン

全 Collector で統一した `_load_file()` ヘルパーを使用:

```python
def _load_file(self, path: str, priority: LoadPriority) -> str | None:
    """Load a file and extract data if successful."""
    result = self.loader.load(path, priority)
    if result.success and result.data:
        return result.data.content
    return None
```

このパターンの統一は適切か？

### 4.3 PhaseFilter 累積ロジックの使用

CharacterCollector / WorldSettingCollector は前回レビュー済みの PhaseFilter を使用:

```python
def _apply_phase_filter(self, character: Character, current_phase: str | None) -> str:
    if current_phase and self.phase_filter:
        return self.phase_filter.filter_by_phase(character, current_phase)
    return self._character_to_string(character)
```

前回「妥当」と判定された累積ロジックが正しく活用されているか？

---

## 5. 内部監査で検出した事項

### Warning（対応済み）

| # | 問題 | 対応 |
|---|------|------|
| 1 | `Optional[str]` と `str | None` 混在 | ruff --fix で統一 |
| 2 | インポートソート不統一 | ruff --fix で統一 |
| 3 | _load_file ヘルパー未統一 | code-simplifier で統一 |
| 4 | 一部 __init__ docstring 欠落 | code-simplifier で追加 |
| 5 | 絶対/相対インポート混在 | code-simplifier で統一 |

### Info

| # | 内容 |
|---|------|
| 1-8 | コメント追加推奨、型ヒント改善推奨など |

---

## 6. 特に確認してほしい点

### 6.1 ContextIntegratorImpl の統合方法

```python
def _integrate_plot(self, ctx: FilteredContext, collector: ContextCollector, scene: SceneIdentifier) -> None:
    # Check if collector has collect method returning PlotContext
    if hasattr(collector, "collect") and callable(collector.collect):
        result = collector.collect(scene)
        if isinstance(result, PlotContext):
            ctx.plot_l1 = result.l1_theme
            ctx.plot_l2 = result.l2_chapter
            ctx.plot_l3 = result.l3_scene
            return

    # Fallback to collect_as_string
    content = collector.collect_as_string(scene)
    if content:
        ctx.plot_l1 = content
```

`hasattr` + `isinstance` による動的ディスパッチは適切か？
より型安全な方法はあるか？

### 6.2 Character/WorldSetting の統合方法

```python
if character_collector is not None:
    result = character_collector.collect_as_string(scene)
    if result:
        ctx.characters["_all"] = result  # 単一キーに格納
```

現在は全キャラクターを `"_all"` キーに格納している。
将来的に個別キャラクターを分けて格納すべきか？

### 6.3 StyleGuideCollector の merged プロパティ

```python
@property
def merged(self) -> str | None:
    """Get merged style guide content."""
    if self._default_content and self._chapter_content:
        return f"{self._default_content}\n\n---\n\n{self._chapter_content}"
    return self._chapter_content or self._default_content
```

default と chapter のマージ順序・形式は適切か？

---

## 7. 回答フォーマット

```markdown
# レビュー回答: L3 Phase D - Context Collectors 実装監査

## Meta
| 項目 | 値 |
|------|-----|
| Session ID | 2026-02-01_001 |
| 日時 | YYYY-MM-DD |
| レビュアー | Antigravity |
| 判定 | [A/B/C/D] |

## 1. Protocol 整合性評価
...

## 2. L2 連携評価
...

## 3. 仕様書整合性評価
...

## 4. 設計決定の評価
### 4.1 二重メソッド設計
...
### 4.2 _load_file ヘルパーパターン
...
### 4.3 PhaseFilter 累積ロジックの使用
...

## 5. 問題点・指摘事項

### [重要度: Critical/Warning/Info]
| No. | 対象ファイル | 問題内容 | 推奨対応 |
|-----|-------------|---------|---------|
| 1 | ... | ... | ... |

## 6. 質問への回答
### 6.1 ContextIntegratorImpl の統合方法
...
### 6.2 Character/WorldSetting の統合方法
...
### 6.3 StyleGuideCollector の merged プロパティ
...

## 7. 総合評価
...

## 8. 推奨事項
...
```

---

## 8. 参照ファイル一覧

```
# Phase D 実装（レビュー対象）
src/core/context/collectors/
├── __init__.py
├── plot_collector.py
├── summary_collector.py
├── character_collector.py
├── world_setting_collector.py
└── style_guide_collector.py

src/core/context/context_integrator.py  # ContextIntegratorImpl 追加

# テスト
tests/core/context/collectors/
├── __init__.py
├── test_plot_collector.py
├── test_summary_collector.py
├── test_character_collector.py
├── test_world_setting_collector.py
└── test_style_guide_collector.py

tests/core/context/test_context_integrator.py  # 統合テスト追加

# Phase A-C 実装（前回レビュー済み、参照用）
src/core/context/
├── scene_identifier.py
├── scene_resolver.py
├── lazy_loader.py
├── phase_filter.py
├── filtered_context.py
└── ...

# L2 モデル（連携確認用）
src/core/models/
├── character.py
└── world_setting.py

src/core/context/
├── lazy_loader.py    # FileLazyLoader
└── phase_filter.py   # CharacterPhaseFilter, WorldSettingPhaseFilter

# 仕様書
docs/specs/novel-generator-v2/
├── 02_architecture.md
└── 08_agent-design.md

# ワークフロー記録
docs/memos/l3-phaseD/workflow-audit-simplify.md  # ※gitignore対象
```

---

## 9. テスト実行結果

```
============================= 576 passed in 2.70s =============================
```

全テストが成功しています。
