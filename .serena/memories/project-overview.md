# Novel-Athanor-v2 プロジェクト概要

## プロジェクト目的

AIとユーザーが協力して物語を作成する「半自動小説生成システム」の構築。

### 核心的価値
- 完全自動ではなく、ユーザーの創造性を活かした**協調的な創作**
- 伏線の発生・回収を含む**複層的なストーリー構造の管理**
- 段階的な**情報開示**（4段階AI可視性）

### 差別化ポイント
| 機能 | 説明 |
|------|------|
| AI情報制御 | 4段階可視性レベルによるネタバレ防止（業界初） |
| 伏線管理 | Chekhov's Gun Tracker（微細度スケール1-10付き） |
| 半自動ワークフロー | Phase-Gate-Approval + The Relay |

## ディレクトリ構成

```
Novel-Athanor-v2/
├── CLAUDE.md              # プロジェクト憲法
├── .claude/               # Claude Code用設定
│   ├── agents/            # サブエージェント定義
│   ├── commands/          # スラッシュコマンド
│   ├── rules/             # ガードレール（フェーズ別）
│   └── states/            # 状態管理JSON
├── src/                   # ソースコード（Python）
│   ├── core/              # コアモジュール
│   ├── agents/            # エージェント実装
│   └── cli/               # CLIインターフェース
├── tests/                 # テストコード
├── docs/
│   ├── specs/novel-generator-v2/  # 統合仕様書（00-09）← SSOT
│   ├── adr/               # アーキテクチャ決定記録（0001-0006）
│   ├── internal/          # プロジェクト運用ルール（00-07）
│   ├── tasks/             # タスク管理
│   ├── memos/             # ユーザーメモ・資料
│   └── [解析対象3プロジェクト]
├── vault/                 # 作品データ（Obsidian互換）
└── .exchange/             # 外部AI連携（Antigravity）
```

## 技術スタック

| カテゴリ | 技術 |
|---------|------|
| 実行環境 | Claude Code (CLI) |
| AI | Claude (Opus/Sonnet/Haiku) |
| データ形式 | Markdown + YAML frontmatter |
| 統合環境 | Obsidian (vault構造) |
| 言語 | Python 3.10+ |
| 形態素解析 | fugashi + unidic-lite |

## 現在のステータス

- 仕様書: **レビュー完了・実装準備完了**
- ADR: 6件確定（0001-0006）
- 実装: **未着手**

## 参照ドキュメント

| カテゴリ | 場所 |
|---------|------|
| プロジェクト憲法 | `CLAUDE.md` |
| 統合仕様書 | `docs/specs/novel-generator-v2/` |
| ADR | `docs/adr/` |
| 運用ルール SSOT | `docs/internal/` |
| ガードレール | `.claude/rules/` |
