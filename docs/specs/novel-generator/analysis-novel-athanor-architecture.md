# Novel-Athanor アーキテクチャ解析レポート

**Phase**: 1.1 アーキテクチャ解析
**対象**: `docs/Novel-Athanor-main/`
**日時**: 2026-01-24

---

## 1. 全体構造

### 1.1 ディレクトリ構成

```
Novel-Athanor/
├── CLAUDE.md                      # プロジェクト憲法（運用モード）
├── CLAUDE.dev.md                  # 開発モード用
├── pyproject.toml                 # Python依存管理
│
├── src/                           # ソースコード
│   └── analyzers/                 # 文体分析モジュール
│       ├── tokenizer.py           # 形態素解析
│       └── style_analyzer.py      # 文体定量分析
│
├── .claude/                       # Claude Code 設定
│   ├── agents/                    # サブエージェント（5個）
│   ├── commands/                  # スラッシュコマンド（9個）
│   ├── rules/                     # ガードレール（8個）
│   ├── skills/                    # テンプレート（2個）
│   ├── protocols/                 # プロトコル定義
│   ├── states/                    # 機能別状態管理
│   ├── current-phase.md           # 現在フェーズ
│   ├── CHEATSHEET.md              # クイックリファレンス
│   └── settings.json              # 権限設定
│
├── vault/                         # 作品データ（Obsidian形式）
│   ├── {作品名}/
│   │   ├── episodes/              # エピソード本文
│   │   ├── characters/            # キャラクター設定
│   │   ├── world/                 # 世界観設定
│   │   ├── _plot/                 # プロット（設計）
│   │   ├── _summary/              # サマリ（実績）
│   │   ├── _style_guides/         # 文体ガイド
│   │   └── _style_profiles/       # 文体プロファイル
│   └── templates/                 # ファイルテンプレート
│
└── docs/                          # ドキュメント
    ├── internal/                  # プロセス定義（00-07）
    ├── specs/                     # 仕様書
    ├── adr/                       # アーキテクチャ決定記録
    ├── tasks/                     # タスク管理
    └── memos/                     # ユーザーメモ
```

### 1.2 アーキテクチャ概念図

```
┌─────────────────────────────────────────────────────────────┐
│                    Living Architect Model                    │
│                  (プロジェクト統制レイヤー)                   │
├─────────────────────────────────────────────────────────────┤
│  CLAUDE.md (憲法)  ←→  .claude/rules/ (ガードレール)        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Execution Layer                           │
├───────────────┬─────────────────┬───────────────────────────┤
│  .claude/     │  .claude/       │  .claude/                 │
│  agents/      │  commands/      │  skills/                  │
│  (処理委譲)    │  (ユーザーI/F)  │  (テンプレート)            │
└───────────────┴─────────────────┴───────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
├───────────────────────────┬─────────────────────────────────┤
│  vault/ (作品データ)       │  src/analyzers/ (分析ツール)    │
│  ├─ episodes/             │  ├─ tokenizer.py              │
│  ├─ characters/           │  └─ style_analyzer.py         │
│  ├─ world/                │                                │
│  ├─ _plot/                │                                │
│  └─ _summary/             │                                │
└───────────────────────────┴─────────────────────────────────┘
```

---

## 2. コンポーネント一覧

### 2.1 エージェント（.claude/agents/）

| エージェント | 役割 | フェーズ | 推奨モデル |
|-------------|------|---------|-----------|
| `requirement-analyst` | 要件分析、曖昧さ解消 | PLANNING | Sonnet |
| `design-architect` | 設計、API/データモデル定義 | PLANNING | Sonnet |
| `task-decomposer` | タスク分割、1PR単位化 | PLANNING | Haiku |
| `tdd-developer` | TDD実装、Red-Green-Refactor | BUILDING | Sonnet |
| `quality-auditor` | 品質監査、改善提案 | AUDITING | Opus |

### 2.2 コマンド（.claude/commands/）

| コマンド | 機能 | ガードレール |
|---------|------|-------------|
| `/planning` | PLANNINGフェーズ開始 | コード生成禁止 |
| `/building` | BUILDINGフェーズ開始 | 仕様なし実装禁止 |
| `/auditing` | AUDITINGフェーズ開始 | 修正直接禁止 |
| `/status` | 進捗状況表示 | - |
| `/focus` | タスク集中モード | - |
| `/daily` | 日次振り返り | - |
| `/adr-create` | ADR作成支援 | - |
| `/security-review` | セキュリティレビュー | - |
| `/impact-analysis` | 変更影響分析 | - |

### 2.3 ルール（.claude/rules/）

| ルール | 内容 |
|--------|------|
| `core-identity.md` | Living Architect 行動規範 |
| `phase-planning.md` | PLANNINGガードレール |
| `phase-building.md` | BUILDINGガードレール |
| `phase-auditing.md` | AUDITINGガードレール |
| `decision-making.md` | 3 Agents Model + AoT |
| `model-selection.md` | モデル選定ガイド |
| `security-commands.md` | コマンド実行安全基準 |
| `self-modification.md` | プロジェクト自己改造ルール |

### 2.4 スキル（.claude/skills/）

| スキル | 用途 |
|--------|------|
| `spec-template` | 仕様書作成テンプレート |
| `adr-template` | ADR作成テンプレート |

### 2.5 分析モジュール（src/analyzers/）

| モジュール | 機能 | 依存 |
|-----------|------|------|
| `tokenizer.py` | 形態素解析 | fugashi, unidic-lite |
| `style_analyzer.py` | 文体定量分析 | tokenizer.py |

**分析機能一覧**:
- `analyze_sentence_length()` - 文長分析
- `analyze_dialogue_ratio()` - 会話比率分析
- `analyze_vocabulary()` - 語彙豊富度（TTR）
- `analyze_pos_ratio()` - 品詞比率分析
- `analyze_frequent_words()` - 頻出語分析
- `generate_profile()` - 統合プロファイル生成

---

## 3. 特徴的な設計パターン

### 3.1 Phase-Gate-Approval Model（3段階承認ゲート）

```
PLANNING
  ├─ requirements → [承認] ✅
  ├─ design → [承認] ✅
  └─ tasks → [承認] ✅
      ↓
BUILDING
  └─ implementation → [テストパス] ✅
      ↓
AUDITING
  └─ review → [承認] ✅ → 完了
```

**特徴**:
- ユーザーが「承認」と言うまで次に進まない
- `.claude/states/<feature>.json` で進捗を永続化

### 3.2 3 Agents Model（多視点意思決定）

| Agent | ペルソナ | フォーカス |
|-------|---------|-----------|
| **Affirmative** | 推進者 | Value, Speed, Innovation |
| **Critical** | 批判者 | Risk, Security, Debt |
| **Mediator** | 調停者 | Synthesis, Balance |

### 3.3 Atom of Thought（AoT）

**適用条件**:
- 判断ポイント ≥ 2
- 影響レイヤー ≥ 3
- 選択肢 ≥ 3

**Atom の要件**:
- 自己完結性
- インターフェース契約
- エラー隔離

### 3.4 Vault Structure（Obsidian形式データ管理）

```
vault/{作品名}/
├── episodes/           # 本文（Markdown）
├── characters/         # キャラクター（YAML frontmatter + Markdown）
├── world/              # 世界観（YAML frontmatter + Markdown）
├── _plot/              # プロット（L1/L2/L3 階層）
├── _summary/           # サマリ（L1/L2/L3 階層）
├── _style_guides/      # 文体ガイド（定性）
└── _style_profiles/    # 文体プロファイル（定量）
```

---

## 4. データフロー

### 4.1 文体分析フロー

```
エピソードファイル (.md)
    ↓
tokenize() [形態素解析]
    ↓
┌─────────────────────────────────────┐
│ 並列分析                              │
├─────────────────────────────────────┤
│ analyze_sentence_length()           │
│ analyze_dialogue_ratio()            │
│ analyze_vocabulary()                │
│ analyze_pos_ratio()                 │
│ analyze_frequent_words()            │
└─────────────────────────────────────┘
    ↓
generate_profile() [Markdown統合]
    ↓
_style_profiles/{作品名}.md
```

### 4.2 創作支援フロー

```
ユーザー入力
    ↓
エージェント選択（自然言語で呼び出し）
    ↓
┌─────────────────────────────────────┐
│ 参照データ                            │
├─────────────────────────────────────┤
│ characters/ (current_phase)         │
│ world/ (current_phase)              │
│ _plot/ (L1/L2/L3)                   │
│ _style_guides/                      │
└─────────────────────────────────────┘
    ↓
生成物（下書き、設定抽出、整合性チェック等）
    ↓
vault/ に保存
```

---

## 5. 技術スタック

| カテゴリ | 技術 |
|---------|------|
| 言語 | Python 3.10+ |
| 形態素解析 | fugashi + unidic-lite |
| テスト | pytest |
| AI | Claude Code (Opus/Sonnet/Haiku) |
| データ形式 | Markdown + YAML frontmatter |
| 統合環境 | Obsidian (vault構造) |

---

## 6. 強みと活用ポイント

### 6.1 設定管理の強み

| 機能 | 説明 | 活用ポイント |
|------|------|-------------|
| **フェーズ管理** | キャラクター/世界観の状態変化を追跡 | 時系列整合性の維持 |
| **隠し設定** | `## 隠し設定` セクションはAI参照対象外 | ネタバレ防止 |
| **L1/L2/L3階層** | プロット/サマリの3階層構造 | 粒度別の管理 |

### 6.2 品質管理の強み

| 機能 | 説明 | 活用ポイント |
|------|------|-------------|
| **整合性チェック** | Plot/Summary/設定間の矛盾検出 | 自動品質ゲート |
| **3 Agents Model** | 多視点レビュー | バイアス排除 |
| **Definition of Ready** | 着手前チェックリスト | 手戻り防止 |

### 6.3 新システムへの示唆

| 学ぶべき点 | 詳細 |
|-----------|------|
| Phase-Gate-Approval | 承認ゲートによる品質担保 |
| 状態ファイル管理 | JSON による進捗永続化 |
| Vault構造 | Markdown + YAML による柔軟なデータ管理 |
| フェーズ管理 | 時系列での状態変化追跡 |
| 隠し設定 | 情報階層の実装例 |

---

## 7. 伏線管理観点の評価

### 7.1 現状

| 観点 | 評価 | 詳細 |
|------|------|------|
| 伏線の定義 | ❌ 未実装 | 伏線専用のデータ構造なし |
| 発生と回収 | ❌ 未実装 | 追跡機能なし |
| 情報階層 | ⚠️ 部分実装 | `## 隠し設定` で一部実現 |
| 整合性 | ⚠️ 部分実装 | 整合性チェックに伏線は含まれず |

### 7.2 拡張の可能性

```
vault/{作品名}/
└── _foreshadowing/              # 新規追加
    ├── active/                  # 未回収の伏線
    │   └── {伏線ID}.md
    ├── resolved/                # 回収済みの伏線
    │   └── {伏線ID}.md
    └── _index.md                # 伏線一覧・状態
```

**伏線ファイル構造案**:
```yaml
---
id: FS-001
title: 主人公の出生の秘密
status: active  # active / resolved / abandoned
planted_episode: EP-003
resolved_episode: null
visibility:
  reader: false
  writer: true
  ai: limited  # full / limited / none
related_characters:
  - アイラ
  - マスター
---

## 伏線内容
...

## 回収計画
...
```

---

## 8. 次のステップ

- [x] Phase 1.1: アーキテクチャ解析 ✅
- [ ] Phase 1.2: データモデル解析（vault/構造の詳細）
- [ ] Phase 1.3: 機能フロー解析（agents/commands/skillsの詳細）

---

## 9. 参照

- `docs/Novel-Athanor-main/README_ja.md`
- `docs/Novel-Athanor-main/CLAUDE.md`
- `docs/Novel-Athanor-main/docs/internal/`
