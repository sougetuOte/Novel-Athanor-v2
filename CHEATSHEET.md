# Living Architect Model チートシート

## ディレクトリ構造

```
.claude/
├── rules/                 # ガードレール・行動規範（自動ロード）
├── commands/              # スラッシュコマンド
├── agents/                # サブエージェント
├── skills/                # オーケストレーション・テンプレート出力
├── states/                # 機能ごとの進捗状態
└── current-phase.md       # 現在のフェーズ

CLAUDE.md                  # 憲法（コア原則のみ）
CHEATSHEET.md              # このファイル（クイックリファレンス）
docs/internal/             # プロセス SSOT
docs/specs/                # 仕様書
docs/adr/                  # アーキテクチャ決定記録
```

## Rules ファイル一覧

| ファイル | 内容 |
|---------|------|
| `core-identity.md` | Living Architect 行動規範 |
| `phase-planning.md` | PLANNING ガードレール |
| `phase-building.md` | BUILDING ガードレール |
| `phase-auditing.md` | AUDITING ガードレール |
| `security-commands.md` | コマンド安全基準（Allow/Deny List） |
| `model-selection.md` | モデル選定ガイド |
| `decision-making.md` | 意思決定プロトコル |
| `self-modification.md` | **プロジェクト自己改造ルール（計画優先原則）** |

## フェーズコマンド

| コマンド | 用途 | 禁止事項 |
|---------|------|---------|
| `/planning` | 要件定義・設計・タスク分解 | コード生成禁止 |
| `/building` | TDD実装 | 仕様なし実装禁止 |
| `/auditing` | レビュー・監査・リファクタ | 修正の直接実施禁止 |
| `/project-status` | 進捗状況の表示 | - |

## 承認ゲート

```
requirements → [承認] → design → [承認] → tasks → [承認] → BUILDING → [承認] → AUDITING
```

- 各サブフェーズ完了時に「承認」が必要
- 未承認のまま次に進むことは禁止

## セッション管理コマンド

| コマンド | 用途 | コンテキスト消費 |
|---------|------|----------------|
| `/quick-save` | 軽量セーブ（SESSION_STATE.md のみ） | 3-4% |
| `/full-save` | フルセーブ（commit + push + daily） | 約10% |
| `/full-load` | セッション復元（次セッション開始時） | 2-3% |

### セーブの使い分け
- **普段**: `/quick-save`（残量 25% 以下でも安全）
- **一日の終わり**: `/full-save`（残量に余裕があるとき）
- **次セッション開始時**: `/full-load`

### StatusLine
画面下部にコンテキスト残量を常時表示（要 Python 3.x）:
```
[Opus 4.6] ▓▓▓░░░░░░░ 70% $1.23
```
- 緑 (>30%): 安全
- 黄 (15-30%): 注意
- 赤 (<=15%): `/quick-save` 推奨

## サブエージェント

### 汎用エージェント

| エージェント | 呼び出し例 | フェーズ |
|-------------|-----------|---------|
| `requirement-analyst` | 「要件を整理して」 | PLANNING |
| `design-architect` | 「APIを設計して」 | PLANNING |
| `task-decomposer` | 「タスクを分割して」 | PLANNING |
| `tdd-developer` | 「TASK-001を実装して」 | BUILDING |
| `quality-auditor` | 「src/を監査して」 | AUDITING |
| `doc-writer` | 「ドキュメントを更新して」「仕様を策定して」 | ALL |
| `test-runner` | 「テストを実行して」 | BUILDING |

### プロジェクト固有エージェント（Novel-Athanor-v2）

| エージェント | 用途 | フェーズ |
|-------------|------|---------|
| `ghost-writer` | シーンテキスト生成（小説本文の執筆） | BUILDING |
| `reviewer` | テキストレビュー・禁止KWチェック・Human Fallback | BUILDING |
| `quality-agent` | 品質スコアリング | BUILDING |
| `style-agent` | 文体分析・StyleGuide/Profile 自動生成 | BUILDING |

## スキル

| スキル | 用途 | 呼び出し例 |
|--------|------|-----------|
| `lam-orchestrate` | タスク分解・並列実行の自動調整 | 「lam-orchestrateで実行して」 |
| `adr-template` | ADR作成テンプレート | `/adr-create` 実行時に自動適用 |
| `spec-template` | 仕様書作成テンプレート | 仕様書作成時に自動適用 |
| `analyze-style` | 文体分析・StyleGuide/Profile 生成 | `/analyze-style` |

## 典型的なプロジェクトの進め方

```
1. /planning
   ├── 要件整理 (requirement-analyst)
   │   └── → 「承認」
   ├── 設計 (design-architect)
   │   └── → 「承認」
   └── タスク分割 (task-decomposer)
       └── → 「承認」

2. /building
   └── タスクごとに TDD サイクル (tdd-developer)
       Red → Green → Refactor → 次のタスク
       └── → 「承認」

3. /auditing
   └── 品質監査 (quality-auditor)
       └── → 「承認」→ 完了
```

## 状態管理

| ファイル | 用途 |
|---------|------|
| `.claude/current-phase.md` | 現在のフェーズ |
| `.claude/states/<feature>.json` | 機能ごとの進捗・承認状態 |
| `SESSION_STATE.md` | セッション間の引き継ぎ（/quick-save で生成） |

## 補助コマンド

| コマンド | 用途 |
|---------|------|
| `/focus` | 現在のタスクに集中 |
| `/daily` | 日次振り返り |
| `/adr-create` | ADR作成支援 |
| `/security-review` | セキュリティレビュー |
| `/impact-analysis` | 変更の影響分析 |

## 参照ドキュメント (SSOT)

| ファイル | 内容 |
|---------|------|
| `docs/internal/00_PROJECT_STRUCTURE.md` | ディレクトリ構成・命名規則・状態管理 |
| `docs/internal/01_REQUIREMENT_MANAGEMENT.md` | 要件定義プロセス |
| `docs/internal/02_DEVELOPMENT_FLOW.md` | 開発フロー・TDD |
| `docs/internal/03_QUALITY_STANDARDS.md` | 品質基準 |
| `docs/internal/04_RELEASE_OPS.md` | リリース・デプロイ・緊急対応 |
| `docs/internal/05_MCP_INTEGRATION.md` | MCP 連携・MEMORY.md 運用ポリシー |
| `docs/internal/06_DECISION_MAKING.md` | 意思決定（3 Agents + AoT） |
| `docs/internal/07_SECURITY_AND_AUTOMATION.md` | コマンド安全基準（Allow/Deny List） |

## Novel-Athanor-v2 仕様書

| ファイル | 内容 |
|---------|------|
| `docs/specs/novel-generator-v2/00_overview.md` | システム概要 |
| `docs/specs/novel-generator-v2/01_requirements.md` | 機能/非機能要件 |
| `docs/specs/novel-generator-v2/02_architecture.md` | アーキテクチャ設計 |
| `docs/specs/novel-generator-v2/03_data-model.md` | データモデル |
| `docs/specs/novel-generator-v2/04_ai-information-control.md` | AI情報制御（4段階可視性） |
| `docs/specs/novel-generator-v2/05_foreshadowing-system.md` | 伏線管理システム |
| `docs/specs/novel-generator-v2/06_quality-management.md` | 品質管理 |
| `docs/specs/novel-generator-v2/07_workflow.md` | ワークフロー（The Relay） |
| `docs/specs/novel-generator-v2/08_agent-design.md` | エージェント設計 |
| `docs/specs/novel-generator-v2/09_migration.md` | 移行計画 |

## AoT（Atom of Thought）クイックガイド

**いつ使う？**（いずれかに該当）
- 判断ポイントが **2つ以上**
- 影響レイヤー/モジュールが **3つ以上**
- 有効な選択肢が **3つ以上**

**ワークフロー**
```
1. Decomposition: 議題を Atom に分解
2. Debate: 各 Atom で 3 Agents 議論
3. Synthesis: 統合結論 → 実装
```

**Atom テーブル形式**
```
| Atom | 内容 | 依存 | 並列可否(任意) |
```

## クイックリファレンス

**PLANNINGで実装を頼まれたら？**
→ 警告を表示し、3つの選択肢を提示

**成果物が完成したら？**
→ 承認を求めるメッセージを表示

**進捗を確認したい？**
→ `/project-status` を実行

**コンテキストが少なくなったら？**
→ `/quick-save` でセーブして `exit`

**次のセッションを始めるときは？**
→ `/full-load` で前回の状態を復元

**仕様書はどこ？**
→ `docs/specs/`

**ADRはどこ？**
→ `docs/adr/`

**Rulesはどこ？**
→ `.claude/rules/`
