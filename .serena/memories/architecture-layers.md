# システムアーキテクチャ レイヤー構成

## 概要図

```
┌─────────────────────────────────────────────────────────────────┐
│                      Claude Code CLI                             │
├─────────────────────────────────────────────────────────────────┤
│  L5: Orchestration Layer（統制レイヤー）                         │
│      Chief Editor, Commands, Phase-Gate-Approval                 │
├─────────────────────────────────────────────────────────────────┤
│  L4: Agent Layer（エージェントレイヤー）"The Relay"              │
│      Continuity Director → Ghost Writer → Reviewer → Quality    │
├─────────────────────────────────────────────────────────────────┤
│  L3: AI Information Control Layer（AI情報制御レイヤー）          │
│      Visibility Controller, Expression Filter, Foreshadow Mgr   │
├─────────────────────────────────────────────────────────────────┤
│  L2: Context Builder（コンテキスト構築レイヤー）                 │
│      Lazy Loader, Phase Filter, AoT Parallel Collector          │
├─────────────────────────────────────────────────────────────────┤
│  L1: Data Layer（データレイヤー）"Vault"                         │
│      Episodes, Characters, World, Plot, Foreshadow, AI Control  │
└─────────────────────────────────────────────────────────────────┘
```

## 各レイヤー詳細

### L5: Orchestration Layer（統制レイヤー）

| コンポーネント | 責務 | 実装場所 |
|--------------|------|---------|
| Chief Editor | 全体統括、タスク分解、結果統合 | Main System Prompt |
| Commands | ユーザーインターフェース | `.claude/commands/` |
| Phase-Gate-Approval | 承認ゲート管理、状態永続化 | `.claude/states/` |

### L4: Agent Layer（エージェントレイヤー）

"The Relay" ワークフローによる協調処理:

| エージェント | 責務 | 入力 → 出力 |
|-------------|------|------------|
| Continuity Director | コンテキスト構築、情報フィルタリング | シーン指定 → フィルタ済みコンテキスト |
| Ghost Writer | 実テキスト生成 | コンテキスト → 下書き |
| Reviewer Agent | 情報漏洩チェック | 下書き → 承認/警告 |
| Quality Agent | 品質スコアリング | 下書き → 品質レポート |

### L3: AI Information Control Layer（AI情報制御レイヤー）

| コンポーネント | 責務 |
|--------------|------|
| Visibility Controller | Level 0-3 の可視性判定 |
| Expression Filter | 禁止キーワード、類似度チェック |
| Foreshadowing Manager | 伏線ライフサイクル管理 |

**4段階可視性レベル**:
| Level | 名称 | AIの認識 | AIの行動 |
|-------|------|---------|---------|
| 0 | 完全秘匿 | 存在すら知らない | 言及不可 |
| 1 | 認識のみ | 「何かある」と知る | 匂わせのみ |
| 2 | 内容認識 | 内容を知っている | 直接言及禁止 |
| 3 | 使用可能 | 完全に把握 | 自由に使用 |

### L2: Context Builder（コンテキスト構築レイヤー）

| コンポーネント | 責務 |
|--------------|------|
| Lazy Loader | 必要最小限のデータ読み込み |
| Phase Filter | current_phase に基づくフィルタ |
| AoT Parallel Collector | 並列コンテキスト収集 |

**AoT 並列収集の Atom 構成**:
```
Atom 1: Plot L1     → テーマ、全体方向性
Atom 2: Plot L2     → 章の目的
Atom 3: Plot L3     → シーン構成
Atom 4: Summary     → これまでの流れ
Atom 5: Characters  → current_phase 状態
Atom 6: WorldSetting→ current_phase 状態
Atom 7: StyleGuide  → 声、対話パターン
Atom 8: Foreshadow  → 伏線指示（Level別）
```

### L1: Data Layer（データレイヤー）

Obsidian vault 構造:
```
vault/{作品名}/
├── episodes/           # エピソード本文
├── characters/         # キャラクター設定（フェーズ管理）
├── world/              # 世界観設定（フェーズ管理）
├── _plot/              # L1/L2/L3 プロット
├── _summary/           # L1/L2/L3 サマリ
├── _foreshadowing/     # 伏線管理 【新規】
├── _ai_control/        # AI制御設定 【新規】
├── _settings/          # 作品設定
├── _style_guides/      # 文体ガイド
└── _style_profiles/    # 文体プロファイル
```

## 設計原則

| 原則 | 説明 |
|------|------|
| 情報制御優先 | 全データアクセスはAI Control Layer経由 |
| ツール強制 | 重要処理は必須ツール呼び出しで制御 |
| 人間最終判断 | 自動化は提案まで、最終判断は人間 |
| 段階的実装 | Level 2 から開始、段階的に拡張 |
| LLM非依存コア | コアロジック（Python）はLLM非依存 |

## 参照ドキュメント

- `docs/specs/novel-generator-v2/02_architecture.md` - 詳細仕様
