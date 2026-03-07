# Architectural Standards & Quality Gates

本ドキュメントは、"Living Architect" がコードを生成・レビューする際の基準値（Quality Gates）である。

## 1. Design Principles (設計原則)

### Single Source of Truth (SSOT)

- 設定値、定数、型定義は一箇所で定義する。重複定義はバグの温床とみなす。
- ドキュメントとコードが乖離した場合、ドキュメントを正とする。

### Cognitive Load Management (認知負荷の管理)

- **Magic Numbers/Strings**: 禁止。定数化すること。
- **Function Length**: 1 関数は 1 画面（約 30-50 行）を目安とする。
- **Naming**: 「何が入っているか」だけでなく「何のためにあるか」がわかる名前をつける。

## 2. Documentation Standards (ドキュメント基準)

### ADR (Architectural Decision Records)

重要な技術的決定（ライブラリ選定、DB 設計、アーキテクチャ変更）を行う際は、必ず ADR を作成すること。

- Status, Context, Decision, Consequences を記述する。

### Docstrings & Comments

- **What**: コードで語る。
- **Why**: コメントで語る。
- **Workaround**: `FIXME` または `HACK` タグと理由を記述する。

## 3. Spec Maturity (仕様の成熟度)

- **Unambiguous**: 自然言語の曖昧さが排除されている。
- **Testable**: テストケースとして記述可能である。
- **Atomic**: 独立して実装・検証可能である。

## 4. Refactoring Triggers (リファクタリングのトリガー)

以下の兆候が見られた場合、機能追加を停止し、リファクタリングを優先する。

- **Deep Nesting**: ネスト > 3 階層
- **Long Function**: 行数 > 50 行
- **Duplication**: 重複 > 2 回（パーサー等の定型処理）、一般コードは 3 回 (Rule of Three)
- **Parameter Explosion**: 引数 > 4 個
- **Nested Ternary**: ネストした三項演算子
- **Dense One-liner**: 理解に時間がかかるワンライナー

> **2026-03-07 更新**: DRY 基準を「3回」→「定型処理は2回」に引き下げ。
> Full Review で 3 パーサーに同一 YAML 抽出コードが重複していた事例を受けて改定。

## 5. Code Clarity Principle（コード明確性原則）

**Clarity over Brevity（明確さ > 簡潔さ）** を原則とする。

### 推奨
- 読みやすさを最優先する
- 明示的なコードを書く（暗黙の挙動に頼らない）
- 適切な抽象化を維持する（1箇所でしか使わなくても意味のある抽象化は残す）
- 条件分岐は switch/if-else で明確に書く

### 禁止
- ネストした三項演算子
- 読みやすさを犠牲にした行数削減
- 複数の関心事を1つの関数に統合
- デバッグ・拡張を困難にする「賢い」コード
- 3行程度の類似コードを無理に共通化

### 判断基準
「このコードを3ヶ月後の自分が読んで、すぐに理解できるか？」

## 6. Python Safety Patterns (Python 安全性パターン)

> **2026-03-07 追加**: Full Review で発見された Critical/Warning パターンの再発防止。
> 詳細ルールは `.claude/rules/building-checklist.md` R-7〜R-11 を参照。

### 6.1 スレッド安全性 (R-7)

`concurrent.futures` で並列処理を行う場合、共有オブジェクトへの書き込みは禁止。

```python
# BAD: 共有 ctx を複数スレッドから変更
def _run_collector(self, ctx, collector):  # ctx は共有
    ctx.plot_l1 = collector.collect()       # 競合

# GOOD: スレッドローカルな結果を返し、メインスレッドでマージ
def _run_collector_isolated(self, collector) -> FilteredContext:
    local_ctx = FilteredContext(...)
    local_ctx.plot_l1 = collector.collect()
    return local_ctx  # メインスレッドでマージ
```

### 6.2 ミュータブル引数の保護 (R-8)

```python
# BAD: 呼び出し側のリストを破壊する可能性
def process(keywords = None):
    keywords = keywords or []
    keywords.append("new")  # 呼び出し側の [] を変更してしまう

# GOOD: 防御コピー
def process(keywords = None):
    keywords = list(keywords) if keywords else []
    keywords.append("new")  # 安全
```

### 6.3 None vs falsy の区別 (R-9)

```python
# BAD: 空文字列 "" や 空リスト [] を None と混同
if self.plot_l1:  # "" や [] も False

# GOOD: None だけを判定
if self.plot_l1 is not None:  # "" や [] は通す
```

### 6.4 仕様ドリフト防止 (S-1 強化)

実装を変更した場合、以下を同一コミット内で確認・更新する:
- `docs/specs/` のデータモデル定義（フィールド名、型、Enum値）
- `docs/specs/` のアーキテクチャ図・ディレクトリツリー
- Agent 定義の記述（`.claude/agents/` 内の補助 agent 言及等）

> **教訓**: L4 実装完了後の Full Review で `02_architecture.md` のディレクトリ構造、
> `06_quality-management.md` の QualityScore 定義、`08_agent-design.md` の
> Continuity Director 記述が実装と乖離していた。BUILDING 中の S-1 適用だけでは不十分で、
> 監査時にも仕様突合を必須とする。

### 6.5 デッドコード・残骸の除去

- 未宣言の属性への代入（`self._foo = x` で `_foo` が `__init__` にない）は即座に削除。
- 完了済みフェーズの `try/except ImportError` fallback は除去する。
- 完了済みタスクを参照する `TODO(...)` コメントは除去する。

## 7. Technology Trend Awareness (トレンド適応)

- ライブラリの Deprecated 状況を定期的に確認する。
- 長期保守性を最優先し、枯れた技術と最新技術のバランスをとる。
