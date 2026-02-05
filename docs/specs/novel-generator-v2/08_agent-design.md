# エージェント設計書

## 1. エージェント一覧

### 1.1 The Relay エージェント（中核）

| エージェント | 役割 | 責務 |
|-------------|------|------|
| **Chief Editor** | 統括 | タスク分解、エージェント指示、結果統合 |
| **Continuity Director** | 門番/記録係 | 情報フィルタリング、コンテキスト構築 |
| **Ghost Writer** | 執筆 | テキスト生成 |
| **Reviewer** | 校閲 | 情報漏洩チェック |
| **Quality Agent** | 品質管理 | スコアリング、改善提案 |

### 1.2 補助エージェント

| エージェント | 役割 | 責務 |
|-------------|------|------|
| **Consistency Agent** | 整合性 | キャラ/世界観/時系列の整合性チェック |
| **Foreshadowing Agent** | 伏線管理 | 伏線の追跡、アラート |
| **Extract Agent** | 抽出 | 設定/サマリの自動抽出 |
| **Style Agent** | 文体分析 | スタイルプロファイル生成 |

---

## 2. Chief Editor（編集長）

### 2.1 概要

```yaml
name: Chief Editor
role: オーケストレーション
implementation: Main System Prompt (CLAUDE.md)
```

### 2.2 責務

1. **ユーザー意図の解釈**: 自然言語入力からタスクを特定
2. **タスク分解**: 複雑なタスクをサブタスクに分解
3. **エージェント指示**: 適切なエージェントにタスクを委譲
4. **結果統合**: 各エージェントの出力を統合
5. **ユーザー報告**: 結果と推奨アクションを報告

### 2.3 判断ポイント

| 判断 | 基準 |
|------|------|
| エージェント選択 | タスク種別に基づく |
| リトライ判断 | 警告の重要度に基づく |
| 承認要求 | Phase-Gate に基づく |

---

## 3. Continuity Director（記録係/門番）

### 3.1 概要

```yaml
name: Continuity Director
role: 情報制御・整合性管理
implementation: .claude/agents/continuity-director.md
tools:
  - build_context  # L3 ContextBuilder.build_context(scene) を呼び出す必須ツール
```

### 3.2 責務

1. **AI Information Control Layer** を経由したコンテキスト構築
2. **Level 0-2** の秘密をフィルタリング
3. **伏線指示書**の作成（Level 2 の暗示指示）
4. **フェーズフィルタリング**（current_phase のみ）

### 3.3 SceneIdentifier 型定義

L3 コンテキスト構築のシーン識別に使用する不変データクラス。

```python
@dataclass(frozen=True)
class SceneIdentifier:
    """シーンを一意に識別する不変データクラス。

    episode_id のみ必須。その他はオプション。
    """
    episode_id: str                 # 必須。例: "010", "ep010"
    sequence_id: str | None = None  # 例: "seq_01"
    chapter_id: str | None = None   # 例: "ch_03"
    current_phase: str | None = None  # 例: "initial", "development", "climax", "resolution"

    # __str__() → "ep:010/seq:seq_01/ch:ch_03" 形式
```

### 3.4 ContextBuildResult 型定義

`ContextBuilder.build_context()` の戻り値型。L4 エージェントが使用する全コンテキスト情報を含む。

```python
@dataclass
class ContextBuildResult:
    """コンテキスト構築の完全な結果。

    L4 エージェント（Continuity Director, Ghost Writer 等）が
    必要とする全情報をまとめた型。
    """
    context: FilteredContext                         # 統合フィルター済みコンテキスト
    visibility_context: VisibilityAwareContext | None # 可視性フィルター済みコンテキスト（コントローラ未設定時 None）
    foreshadow_instructions: ForeshadowInstructions  # 伏線指示書
    forbidden_keywords: list[str]                    # 全ソース統合済み禁止キーワード
    hints: HintCollection                            # ヒント集約（可視性 + 伏線）
    success: bool = True                             # 構築成功フラグ
    errors: list[str] = field(default_factory=list)  # エラーメッセージ（L4で停止判定に使用）
    warnings: list[str] = field(default_factory=list)  # 警告メッセージ

    def has_errors(self) -> bool: ...
    def has_warnings(self) -> bool: ...
```

### 3.5 L3 ContextBuilder（統合ファサード）

L3 Context Builder は収集・可視性フィルタリング・伏線指示書生成・禁止キーワード収集・ヒント収集を
すべて統合したファサードとして動作する。仕様初期の ContextBuilder + InformationController の
2コンポーネント分割は採用せず、単一の `ContextBuilder` クラスに統合している。

```
ContextBuilder（L3 統合ファサード）
├── ContextIntegrator → FilteredContext
│   ├── PlotCollector
│   ├── SummaryCollector
│   ├── CharacterCollector + CharacterPhaseFilter
│   ├── WorldSettingCollector + WorldSettingPhaseFilter
│   └── StyleGuideCollector
├── VisibilityFilteringService → VisibilityAwareContext
│   └── L2: VisibilityController
├── InstructionGenerator → ForeshadowInstructions
│   ├── ForeshadowingIdentifier
│   └── L1: ForeshadowingRepository
├── ForbiddenKeywordCollector → ForbiddenKeywordResult
└── HintCollector → HintCollection
```

```python
# L3 ContextBuilder の初期化と使用
builder = ContextBuilder(
    vault_root=Path("vault/作品名"),
    work_name="作品名",
    visibility_controller=visibility_controller,      # L2（オプション）
    foreshadowing_repository=foreshadowing_repo,       # L1（オプション）
    phase_order=["initial", "development", "climax", "resolution"]
)

# 主要メソッド: build_context
scene = SceneIdentifier(
    episode_id="010",
    sequence_id="seq_01",
    current_phase="development"
)
result: ContextBuildResult = builder.build_context(scene)
# result.context          → FilteredContext（基本コンテキスト）
# result.visibility_context → VisibilityAwareContext | None
# result.foreshadow_instructions → ForeshadowInstructions
# result.forbidden_keywords → list[str]
# result.hints            → HintCollection
# result.success          → bool
# result.errors           → list[str]
# result.warnings         → list[str]
```

### 3.6 処理フロー

`ContextBuilder.build_context(scene)` の内部処理フロー:

```python
def build_context(scene: SceneIdentifier) -> ContextBuildResult:
    warnings: list[str] = []
    errors: list[str] = []

    # Step 1: コンテキスト統合（各 Collector を順次実行）
    #   - PlotCollector: L1/L2/L3 プロット収集
    #   - SummaryCollector: L1/L2/L3 要約収集
    #   - CharacterCollector: フェーズフィルタ済みキャラクター収集
    #   - WorldSettingCollector: フェーズフィルタ済み世界観設定収集
    #   - StyleGuideCollector: スタイルガイド収集
    try:
        context, integration_warnings = integrator.integrate_with_warnings(
            scene, **collectors
        )
        warnings.extend(integration_warnings)
    except (OSError, ValueError, KeyError, TypeError) as e:
        errors.append(f"Context integration failed: {e}")
        context = FilteredContext()

    # Step 2: 伏線指示書生成（LRUキャッシュ付き）
    foreshadow_instructions = get_foreshadow_instructions(scene)

    # Step 3: 禁止キーワード収集（LRUキャッシュ付き）
    #   ソース: visibility設定、伏線のforbidden_expressions、グローバル禁止
    forbidden_keywords = get_forbidden_keywords(scene)

    # Step 4: 可視性フィルタリング（VisibilityController設定時のみ）
    visibility_context = visibility_filtering_service.filter_context(context)

    # Step 5: ヒント収集（可視性ヒント + 伏線ヒントを統合）
    hints = hint_collector.collect_all(
        visibility_context=visibility_context,
        foreshadow_instructions=foreshadow_instructions
    )

    return ContextBuildResult(
        context=context,
        visibility_context=visibility_context,
        foreshadow_instructions=foreshadow_instructions,
        forbidden_keywords=forbidden_keywords,
        hints=hints,
        success=(len(errors) == 0),
        errors=errors,
        warnings=warnings,
    )
```

### 3.7 出力例

`ContextBuildResult` のフィールドに対応した出力例:

```yaml
# result.context (FilteredContext)
context:
  plot_l1: "テーマと全体方向性..."
  plot_l2: "章の目的..."
  plot_l3: "シーン構成..."
  summary_l1: "全体の流れ..."
  summary_l2: "章の要約..."
  summary_l3: "直近のあらすじ..."
  characters:
    アイラ: "現在の状態（フェーズフィルタ済み）..."
  world_settings:
    魔法体系: "概要（フェーズフィルタ済み）..."
  style_guide: "文体ガイド..."
  scene_id: "ep:010/seq:seq_01"
  current_phase: "development"

# result.visibility_context (VisibilityAwareContext | None)
visibility_context:
  base_context: "(上記 context と同一)"
  hints:
    - category: "character"
      entity_id: "アイラ"
      hint_text: "アイラには隠された背景がある"
      level: AWARE  # Level 1
  excluded_sections:
    - "character.闇の王"     # Level 0: HIDDEN → 除外
  forbidden_keywords:
    - "王族"
    - "血筋"
  filtered_characters:
    アイラ: "フィルター済みテキスト..."
  filtered_world_settings:
    魔法体系: "フィルター済みテキスト..."

# result.foreshadow_instructions (ForeshadowInstructions)
foreshadow_instructions:
  instructions:
    - foreshadowing_id: "FS-001"
      action: "reinforce"
      allowed_expressions:
        - "彼女の瞳には見覚えのある光があった"
      forbidden_expressions:
        - "王族"
        - "血筋"
      note: "第3章の伏線を強化する暗示を挿入"
      subtlety_target: 7
  global_forbidden_keywords:
    - "禁忌の魔法"

# result.forbidden_keywords (list[str])
forbidden_keywords:
  - "王族"
  - "血筋"
  - "禁忌の魔法"

# result.hints (HintCollection)
hints:
  hints:
    - source: "visibility"
      category: "character"
      entity_id: "アイラ"
      hint_text: "アイラには隠された背景がある"
      strength: 0.5
    - source: "foreshadowing"
      category: "foreshadowing"
      entity_id: "FS-001"
      hint_text: "彼女の瞳には見覚えのある光があった"
      strength: 0.7

# result.success / errors / warnings
success: true
errors: []
warnings:
  - "Summary L3 not found for ep:010"
```

---

## 4. Ghost Writer（執筆担当）

### 4.1 概要

```yaml
name: Ghost Writer
role: 実テキスト生成
implementation: .claude/agents/ghost-writer.md
skills:
  - plot-theories
  - character-theories
  - style-guidelines
```

### 4.2 責務

1. **与えられたコンテキストに基づく執筆**
2. **スタイルガイドの遵守**
3. **伏線指示書に従った暗示の挿入**
4. **禁止表現の回避**

### 4.3 入力

```yaml
context: "(Continuity Director から)"
foreshadow_instructions: "(伏線指示書)"
style_guide: "(文体ガイド)"
scene_requirements:
  word_count: 3000
  pov: "三人称限定視点（主人公）"
  mood: "緊張感のある"
```

### 4.4 制約

- 渡されていない情報には触れない
- 伏線指示書の指示に従う
- 禁止キーワードを使用しない
- スタイルガイドに従う

---

## 5. Reviewer（校閲担当）

### 5.1 概要

```yaml
name: Reviewer
role: 情報漏洩チェック
implementation: .claude/agents/reviewer.md
tools:
  - review_draft  # 必須ツール
```

### 5.2 責務

1. **禁止キーワードチェック**
2. **秘密内容との類似度チェック**
3. **設定文直接引用チェック**
4. **暗示過剰チェック**

### 5.3 入力

```yaml
draft_text: "(Ghost Writer の出力)"
secrets:
  - id: SEC-001
    content: "アイラは実は王族の血筋"
    visibility: 2
    forbidden_keywords: ["王族", "血筋", "高貴"]
forbidden_keywords_global: ["禁忌の魔法", "最終兵器"]
```

### 5.4 出力

```yaml
result: "approved" | "warning" | "rejected"
issues:
  - type: "forbidden_keyword"
    severity: "critical"
    location: "第3段落"
    detail: "「王族」というキーワードが使用されています"
    suggestion: "「高貴な雰囲気」などの曖昧な表現に変更"
```

### 5.5 Human Fallback（ループ防止）

Reviewerが3回連続で否決した場合、自動修正を諦めてユーザーに差し戻す。

```python
MAX_RETRY_COUNT = 3

def review_with_fallback(draft, secrets, retry_count=0):
    result = reviewer.check(draft, secrets)

    if result['status'] == 'rejected':
        if retry_count >= MAX_RETRY_COUNT:
            # Human Fallback: ユーザーに差し戻し
            return {
                'status': 'human_fallback',
                'message': '自動修正の上限に達しました。手動での確認が必要です。',
                'rejection_history': result['rejection_history'],
                'last_issues': result['issues']
            }
        # 自動リトライ
        revised_draft = ghost_writer.revise(draft, result['issues'])
        return review_with_fallback(revised_draft, secrets, retry_count + 1)

    return result
```

---

## 6. Quality Agent（品質管理担当）

### 6.1 概要

```yaml
name: Quality Agent
role: 品質評価
implementation: .claude/agents/quality-agent.md
skills:
  - quality-standards
```

### 6.2 責務

1. **品質スコアリング**（coherence, pacing, prose, character_score, style, reader_excitement, emotional_resonance）
2. **改善提案の生成**
3. **閾値との比較**

### 6.3 出力

```yaml
scores:
  coherence: 0.72
  pacing: 0.65
  prose: 0.78
  character_score: 0.70
  style: 0.75
  reader_excitement: 0.68
  emotional_resonance: 0.65
  overall: 0.70

assessment: "good"

issues:
  - category: "pacing"
    severity: "warning"
    location: "第3段落〜第5段落"
    description: "説明が長く、テンポが落ちています"
    suggestion: "対話で情報を伝えることを検討"

recommendations:
  - priority: "high"
    action: "第3-5段落を対話形式にリライト"
```

### 6.4 エージェント統合オプション

運用効率を高めるため、以下のエージェントは統合可能:

| 統合グループ | 統合対象 | 統合名 | 備考 |
|-------------|---------|--------|------|
| **Auditor Group** | Reviewer + Quality + Consistency | Quality Assurance Agent | 品質監査全般 |

**注意**: Ghost Writer（生成）とReviewer（評価）は必ず分離すること。生成と評価の責務は混同してはならない。

```yaml
# 統合構成（オプション）
auditor_group:
  name: "Quality Assurance Agent"
  components:
    - reviewer
    - quality_agent
    - consistency_agent
  mode: "sequential"  # 順次実行
```

---

## 7. 補助エージェント

### 7.1 Consistency Agent

```yaml
name: Consistency Agent
role: 整合性チェック
implementation: .claude/agents/consistency-agent.md

checks:
  - character_consistency
  - world_consistency
  - timeline_consistency
  - foreshadowing_consistency
  - phase_consistency

output:
  passed: 4
  warnings: 1
  errors: 0
  details: [...]
```

### 7.2 Foreshadowing Agent

```yaml
name: Foreshadowing Agent
role: 伏線管理
implementation: .claude/agents/foreshadowing-agent.md

functions:
  - register_foreshadowing
  - plant_foreshadowing
  - reinforce_foreshadowing
  - reveal_foreshadowing
  - check_foreshadowing_for_scene
  - generate_alerts
```

### 7.3 Extract Agent

```yaml
name: Extract Agent
role: 設定抽出
implementation: .claude/agents/extract-agent.md

functions:
  - extract_character
  - extract_world_setting
  - extract_summary
```

### 7.4 Style Agent

```yaml
name: Style Agent
role: 文体分析
implementation: .claude/agents/style-agent.md

functions:
  - analyze_style
  - generate_profile
  - create_style_guide
```

---

## 8. エージェント間通信

### 8.1 設計方針：パイプライン処理

**問題**: YAML形式による厳密なメッセージング は、Claude Code環境（シングルコンテキストウィンドウ）においてトークンを浪費する。

**解決策**: エージェント間のやり取りは、厳密なYAML通信ではなく、**パイプライン処理**として抽象化する。会話履歴としてのメッセージ交換は最小限に留める。

```python
# パイプライン処理モデル
def execute_draft_pipeline(scene: SceneIdentifier):
    # Step 1: コンテキスト構築（Continuity Director → L3 ContextBuilder）
    result: ContextBuildResult = context_builder.build_context(scene)

    # L4 停止判定: L3 は全エラーを warning/error として収集するのみ。
    # 必須コンテキスト失敗（result.errors 非空）の場合は L4 が停止を判定する。
    if result.has_errors():
        raise FatalContextError(
            f"必須コンテキスト取得失敗: {result.errors}"
        )

    # Step 2: 下書き生成（Ghost Writer）
    # → ContextBuildResult のフィールドを直接注入（YAML通信なし）
    draft = ghost_writer.generate(
        context=result.visibility_context or result.context,
        foreshadow_instructions=result.foreshadow_instructions,
        forbidden_keywords=result.forbidden_keywords,
        hints=result.hints,
    )

    # Step 3: レビュー（Reviewer）
    review_result = reviewer.check(draft, result.forbidden_keywords)

    # Step 4: 品質チェック（Quality Agent）
    quality_result = quality_agent.evaluate(draft)

    return {
        'draft': draft,
        'review': review_result,
        'quality': quality_result,
        'context_warnings': result.warnings,
    }
```

### 8.2 内部通信形式（デバッグ用）

内部ログとして構造化データを記録するが、コンテキストには含めない。

```yaml
# .claude/logs/pipeline_log.yaml（デバッグ用）
pipeline_execution:
  scene_id: "seq_01_ep010"
  timestamp: "2026-01-24T10:30:00"
  steps:
    - agent: "Continuity Director"
      action: "build_context"
      duration_ms: 1200
      status: "success"
    - agent: "Ghost Writer"
      action: "generate"
      duration_ms: 15000
      status: "success"
      tokens_used: 2500
```

### 8.3 Prompt Caching 活用（層別役割分担）

キャッシュ戦略を L3（ローカル）と L4（API）の2層で管理する。

#### L3: ローカル LRU キャッシュ

L3 ContextBuilder は内部に OrderedDict ベースの LRU キャッシュを保持し、
同一シーンの繰り返しアクセスを高速化する。キャッシュ上限は `_MAX_CACHE_SIZE = 128`。

```python
# L3 ローカルキャッシュ（ContextBuilder 内部）
# キー: "{episode_id}:{sequence_id}" 形式
_instruction_cache: OrderedDict[str, ForeshadowInstructions]  # 伏線指示書キャッシュ
_forbidden_cache: OrderedDict[str, list[str]]                  # 禁止キーワードキャッシュ
_forbidden_result_cache: OrderedDict[str, ForbiddenKeywordResult]  # ソース付き禁止KWキャッシュ

# キャッシュ制御メソッド
builder.clear_instruction_cache()   # 伏線指示書キャッシュクリア
builder.clear_forbidden_cache()     # 禁止キーワードキャッシュクリア
builder.clear_all_caches()          # 全キャッシュクリア
```

#### L4: Claude API Prompt Caching

共通コンテキスト（世界観、スタイルガイド等）は Claude API の Prompt Caching 機能を利用し、
全エージェントで共有キャッシュヒットを狙う。

```python
# L4 API レベルキャッシュ戦略
CACHED_CONTEXT = {
    'world_settings': True,   # キャッシュ対象（変更頻度低）
    'style_guide': True,      # キャッシュ対象（変更頻度低）
    'characters': False,      # フェーズ依存のため都度取得
    'plot_context': False     # シーン依存のため都度取得
}
```

### 8.4 Graceful Degradation（段階的劣化 — 層別責務分担）

エラーハンドリングを L3 と L4 の層別責務で分担する。

#### L3 の責務: warning/error 収集（停止しない）

L3 ContextBuilder は全てのコンテキスト収集失敗を **warning または error として記録し、
処理を続行する**（liberal graceful degradation）。L3 自体は停止判定を行わない。

```python
# L3 ContextBuilder.build_context() 内部の挙動
# - 各 Collector の失敗 → warnings に追加して続行
# - ContextIntegrator の致命的失敗 → errors に追加、空 FilteredContext で続行
# - 可視性フィルタリング失敗 → warnings に追加して続行
# - 禁止キーワード収集失敗 → warnings に追加、空リストで続行
#
# 結果: ContextBuildResult.errors / warnings に全情報を格納
```

#### L4 の責務: 停止判定

L4 エージェント（Continuity Director / Chief Editor）が `ContextBuildResult` の
`errors` フィールドを評価し、必須コンテキスト失敗時にはエラー停止を判定する。

| コンテキスト種別 | 重要度 | L3 の挙動 | L4 の判定 |
|-----------------|--------|----------|----------|
| キャラ設定 | **必須** | error 記録 + 続行 | errors 非空 → 停止 |
| プロット情報 | **必須** | error 記録 + 続行 | errors 非空 → 停止 |
| スタイルガイド | **必須** | error 記録 + 続行 | errors 非空 → 停止 |
| 伏線指示書 | 付加的 | warning 記録 + 空指示で続行 | warnings をログ出力 |
| 禁止キーワード | 付加的 | warning 記録 + 空リストで続行 | warnings をログ出力 |
| 可視性フィルタ | 付加的 | warning 記録 + None で続行 | warnings をログ出力 |
| 参考資料 | 付加的 | warning 記録 + 続行 | warnings をログ出力 |
| 過去サマリ | 付加的 | warning 記録 + 続行 | warnings をログ出力 |

```python
# L4 パイプラインでの停止判定
result: ContextBuildResult = context_builder.build_context(scene)

if result.has_errors():
    # L4 が停止を判定
    raise FatalContextError(
        f"必須コンテキスト取得失敗: {result.errors}"
    )

if result.has_warnings():
    # 警告はログ出力して続行
    for w in result.warnings:
        logger.warning("Context warning: %s", w)
```

---

## 9. エージェント設定ファイル構造

### 9.1 ディレクトリ構成

```
.claude/agents/
├── chief-editor.md          # 統括（CLAUDE.mdに統合）
├── continuity-director.md   # 門番
├── ghost-writer.md          # 執筆
├── reviewer.md              # 校閲
├── quality-agent.md         # 品質
├── consistency-agent.md     # 整合性
├── foreshadowing-agent.md   # 伏線
├── extract-agent.md         # 抽出
└── style-agent.md           # 文体
```

### 9.2 エージェント定義テンプレート

```markdown
# {Agent Name}

## Identity

あなたは {role} を担当するエージェントです。

## Responsibilities

1. ...
2. ...

## Tools

- `tool_name`: 説明

## Input

- `param1`: 説明
- `param2`: 説明

## Output

```yaml
output_format:
  ...
```

## Constraints

- ...
- ...

## Examples

### Example 1

Input:
...

Output:
...
```
