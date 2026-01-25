# 解析対象3プロジェクト比較

## 概要

本プロジェクトは以下の3プロジェクトを解析し、長所を統合した新システムを構築する。

| プロジェクト | 場所 | 出典 | 編集可否 |
|-------------|------|------|---------|
| Novel-Athanor | `docs/Novel-Athanor-main/` | ユーザー作 | 読み取り専用 |
| NovelWriter | `docs/NovelWriter-main/` | GitHub (EdwardAThomson) | 読み取り専用 |
| 302_novel_writing | `docs/302_novel_writing-main/` | GitHub (302ai) | 読み取り専用 |

## 各プロジェクトの特徴

### Novel-Athanor（ユーザー作）

**強み**:
- 設定管理（キャラクター、世界観）
- フェーズ管理（current_phase による段階的開示）
- Obsidian 統合（vault構造、相互リンク）
- 人間介入を重視した設計思想

**採用要素**:
- フェーズ管理の概念 → 4段階可視性に発展
- Obsidian vault構造 → データレイヤーの基盤
- 設定管理パターン → キャラクター/世界観管理

### NovelWriter（EdwardAThomson）

**強み**:
- マルチエージェントアーキテクチャ
- 完全自動生成のワークフロー
- 品質管理システム

**採用要素**:
- マルチエージェント設計 → The Relay ワークフロー
- 品質スコアリング → Quality Agent
- エージェント間連携パターン

### 302_novel_writing（302ai）

**強み**:
- Web UI/UX 設計
- 多言語対応
- プロンプト設計パターン
- API 統合

**採用要素**:
- プロンプト設計手法
- ユーザー操作フロー
- 多言語対応の設計思想

## 統合分析

### Claude Code 解析（docs/specs/novel-generator/）

- Novel-Athanor: アーキテクチャ、データモデル、機能フロー
- NovelWriter: エージェントアーキテクチャ、品質管理
- 302_novel_writing: プロンプト設計、UI/UX

### Antigravity 解析（.exchange/sessions/）

- アーキテクチャ横断分析
- Chekhov's Gun Tracker 設計案
- Hybrid Parsing アプローチ
- The Relay ワークフロー

### クロスレビュー統合結果

| 採用元 | 採用要素 |
|--------|---------|
| Antigravity | subtlety_level、Reviewer Agent、Lazy Loading Context |
| Claude Code | AoT並列処理、Phase-Gate-Approval、ER図 |
| 両者共通 | 4段階可視性、L1/L2/L3階層、フェーズ管理 |

## 新規追加機能

既存3プロジェクトに**存在しなかった**機能:

| 機能 | 説明 |
|------|------|
| **伏線管理** | Chekhov's Gun Tracker（状態遷移 + 微細度スケール） |
| **AI可視性** | 4段階の情報制御（Level 0-3） |
| **Reviewer Agent** | 情報漏洩チェック専門エージェント |

## 参照ドキュメント

- `docs/specs/novel-generator/` - 各プロジェクト解析結果
- `docs/specs/novel-generator-v2/00_overview.md` - 統合仕様概要
- `.exchange/sessions/` - Antigravity 解析セッション
