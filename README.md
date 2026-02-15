# Novel-Athanor-v2

**AIとユーザーが協力して物語を創る「半自動小説生成システム」**

## プロジェクト概要

Novel-Athanor-v2 は、完全自動ではなく、ユーザーの創造性を活かした**協調的な創作**を目指す小説執筆支援システムです。

### 差別化ポイント

| 機能 | 説明 |
|------|------|
| **AI情報制御** | 4段階可視性レベルによるネタバレ防止 |
| **伏線管理** | Chekhov's Gun Tracker による伏線追跡（微細度スケール1-10） |
| **ハイブリッドワークフロー** | 自動化と人間判断のバランス（Phase-Gate-Approval） |

### 4段階AI可視性

| Level | 名称 | AIの認識 |
|-------|------|---------|
| 0 | 完全秘匿 | 存在すら知らない |
| 1 | 認識のみ | 「何かある」と知る |
| 2 | 内容認識 | 内容を知るが文章に出さない |
| 3 | 使用可能 | 自由に使用可能 |

## 現在のステータス

**L4 エージェント層 実装中**

| フェーズ | 状態 |
|---------|------|
| 解析 | ✅ 完了 |
| 仕様策定 | ✅ 完了 |
| L1-L3 コア実装 | ✅ 完了（921 テスト） |
| L4 エージェント層 | 🔨 Phase A-E 完了 / Phase F-G 残 |

- テスト: **1103 件** (mypy: 0, ruff: 0)
- 実装済みエージェント: Ghost Writer, Reviewer, Quality Agent, Style Agent

## ドキュメント

### 仕様書

統合仕様書は `docs/specs/novel-generator-v2/` にあります：

| ファイル | 内容 |
|---------|------|
| `00_overview.md` | システム概要 |
| `01_requirements.md` | 機能/非機能要件 |
| `02_architecture.md` | アーキテクチャ設計 |
| `03_data-model.md` | データモデル |
| `04_ai-information-control.md` | AI情報制御（4段階可視性） |
| `05_foreshadowing-system.md` | 伏線管理システム |
| `06_quality-management.md` | 品質管理 |
| `07_workflow.md` | ワークフロー（The Relay） |
| `08_agent-design.md` | エージェント設計 |
| `09_migration.md` | 移行計画 |

### 解析対象プロジェクト

| プロジェクト | 出典 | 強み |
|-------------|------|------|
| Novel-Athanor | ユーザー作 | 設定管理、フェーズ管理 |
| NovelWriter | [GitHub](https://github.com/EdwardAThomson/NovelWriter) | マルチエージェント、自動生成 |
| 302_novel_writing | [GitHub](https://github.com/302ai/302_novel_writing) | Web UI、多言語対応 |

## 技術スタック

| カテゴリ | 技術 |
|---------|------|
| 実行環境 | Claude Code (CLI) |
| AI | Claude (Opus/Sonnet/Haiku) |
| データ形式 | Markdown + YAML frontmatter |
| 統合環境 | Obsidian (vault構造) |
| 言語 | Python 3.10+ |

## 開発手法

本プロジェクトは **Living Architect Model** を採用しています。

- フェーズ制御: `/planning` → `/building` → `/auditing`
- 承認ゲート: 各サブフェーズ完了時にユーザー承認必須
- 詳細: `CHEATSHEET.md`

## ライセンス

MIT License
