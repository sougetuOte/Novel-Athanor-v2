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
  - get_filtered_context  # 必須ツール
```

### 3.2 責務

1. **AI Information Control Layer** を経由したコンテキスト構築
2. **Level 0-2** の秘密をフィルタリング
3. **伏線指示書**の作成（Level 2 の暗示指示）
4. **フェーズフィルタリング**（current_phase のみ）

### 3.3 内部ロジック分割

責務過多を避けるため、内部ロジックを2つのサブコンポーネントに分割する。

```
Continuity Director
├── Context Builder（収集）
│   └── 関連ファイルの特定と読み込み
└── Information Controller（フィルタリング）
    └── AI可視性に基づくフィルタリング
```

```python
class ContinuityDirector:
    def __init__(self):
        self.context_builder = ContextBuilder()
        self.info_controller = InformationController()

    def build_context(self, scene_id):
        # Step 1: 収集（Context Builder）
        raw_context = self.context_builder.gather(scene_id)

        # Step 2: フィルタリング（Information Controller）
        filtered_context = self.info_controller.filter(
            raw_context,
            visibility_config=self.load_visibility_config()
        )

        return filtered_context
```

### 3.4 処理フロー

```python
def process(scene_id):
    # 1. 対象ファイル特定
    files = identify_relevant_files(scene_id)

    # 2. AI可視性設定読み込み
    visibility_config = load_visibility_config()

    # 3. フィルタリング
    context = {}
    hints = []
    forbidden = []

    for file in files:
        filtered = apply_visibility_filter(file, visibility_config)
        context.update(filtered['context'])
        hints.extend(filtered['hints'])
        forbidden.extend(filtered['forbidden'])

    # 4. フェーズフィルタリング
    context = apply_phase_filter(context, current_phase)

    # 5. 伏線指示書作成
    foreshadow_instructions = create_foreshadow_instructions(
        scene_id, hints
    )

    return {
        'context': context,
        'foreshadow_instructions': foreshadow_instructions,
        'forbidden_keywords': forbidden
    }
```

### 3.5 出力

```yaml
filtered_context:
  plot_l1: "テーマと全体方向性..."
  plot_l2: "章の目的..."
  plot_l3: "シーン構成..."
  summary: "これまでの流れ..."
  characters:
    アイラ: "現在の状態（フィルタ済み）..."
  world_settings:
    魔法体系: "概要（フィルタ済み）..."
  style_guide: "文体ガイド..."

foreshadow_instructions:
  - id: FS-001
    action: "reinforce"
    allowed_expressions:
      - "彼女の瞳には見覚えのある光があった"
    forbidden_expressions:
      - "王族"
      - "血筋"

forbidden_keywords:
  - "王族"
  - "血筋"
  - "禁忌の魔法"
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
def execute_draft_pipeline(scene_id):
    # Step 1: コンテキスト構築（Continuity Director）
    context = continuity_director.build_context(scene_id)

    # Step 2: 下書き生成（Ghost Writer）
    # → コンテキストを直接注入（YAML通信なし）
    draft = ghost_writer.generate(
        context=context['filtered_context'],
        foreshadow_instructions=context['foreshadow_instructions'],
        forbidden_keywords=context['forbidden_keywords']
    )

    # Step 3: レビュー（Reviewer）
    review_result = reviewer.check(draft, context['secrets'])

    # Step 4: 品質チェック（Quality Agent）
    quality_result = quality_agent.evaluate(draft)

    return {
        'draft': draft,
        'review': review_result,
        'quality': quality_result
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

### 8.3 Prompt Caching 活用

共通コンテキスト（世界観、スタイルガイド等）は Prompt Caching 機能を利用し、全エージェントで共有キャッシュヒットを狙う。

```python
# キャッシュ戦略
CACHED_CONTEXT = {
    'world_settings': True,   # キャッシュ対象（変更頻度低）
    'style_guide': True,      # キャッシュ対象（変更頻度低）
    'characters': False,      # フェーズ依存のため都度取得
    'plot_context': False     # シーン依存のため都度取得
}
```

### 8.4 Graceful Degradation（段階的劣化）

コンテキスト取得に失敗した場合の挙動を、コンテキストの重要度で分ける。

| コンテキスト種別 | 重要度 | 取得失敗時の挙動 |
|-----------------|--------|-----------------|
| キャラ設定 | **必須** | エラー停止 |
| プロット情報 | **必須** | エラー停止 |
| スタイルガイド | **必須** | エラー停止 |
| 参考資料 | 付加的 | 警告付きで続行 |
| 過去サマリ | 付加的 | 警告付きで続行 |

```python
def gather_context_with_graceful_degradation(scene_id):
    context = {}
    warnings = []

    # 必須コンテキスト（失敗時はエラー）
    for required in ['characters', 'plot', 'style_guide']:
        try:
            context[required] = load_context(required, scene_id)
        except ContextLoadError as e:
            raise FatalContextError(f"必須コンテキスト取得失敗: {required}")

    # 付加的コンテキスト（失敗時は警告して続行）
    for optional in ['references', 'past_summaries']:
        try:
            context[optional] = load_context(optional, scene_id)
        except ContextLoadError as e:
            warnings.append(f"付加的コンテキスト取得失敗: {optional}")
            context[optional] = None  # デフォルト値

    return {'context': context, 'warnings': warnings}
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
