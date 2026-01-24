# Novel-Athanor-v2 システム仕様書

## Meta

| 項目 | 値 |
|------|-----|
| バージョン | 2.0 |
| 作成日 | 2026-01-24 |
| 更新日 | 2026-01-24 |
| ステータス | レビュー完了・実装準備完了 |
| 作成者 | Claude Code + Antigravity クロスレビュー統合 |

---

## 1. エグゼクティブサマリー

### 1.1 プロジェクトビジョン

AIとユーザーが協力して物語を作成する「半自動小説生成システム」を構築する。

**核心的な価値**:
- 完全自動ではなく、ユーザーの創造性を活かした**協調的な創作**
- 伏線の発生・回収を含む**複層的なストーリー構造の管理**
- 段階的な**情報開示**（読者視点/書き手視点/AI制限視点/完全秘匿）

### 1.2 差別化ポイント

| 機能 | 説明 | 既存システムとの違い |
|------|------|---------------------|
| **AI情報制御** | 4段階可視性レベルによるネタバレ防止 | 業界初の本格実装 |
| **伏線管理** | Chekhov's Gun Trackerによる伏線追跡 | 微細度スケール（1-10）付き |
| **ハイブリッドワークフロー** | 自動化と人間判断のバランス | Phase-Gate-Approval統合 |

---

## 2. 仕様書構成

| No. | ドキュメント | 内容 |
|-----|-------------|------|
| 00 | overview.md（本文書） | システム概要、目次 |
| 01 | requirements.md | 機能/非機能要件、ユースケース |
| 02 | architecture.md | アーキテクチャ設計、コンポーネント構成 |
| 03 | data-model.md | エンティティ定義、ER図 |
| 04 | ai-information-control.md | AI情報制御システム詳細仕様 |
| 05 | foreshadowing-system.md | 伏線管理システム詳細仕様 |
| 06 | quality-management.md | 品質管理システム詳細仕様 |
| 07 | workflow.md | ワークフロー設計 |
| 08 | agent-design.md | エージェント設計 |
| 09 | migration.md | Novel-Athanorからの移行計画 |

---

## 3. 解析ベース

本仕様書は以下の解析を統合して作成された：

### 3.1 Claude Code 解析（docs/specs/novel-generator/）

- Novel-Athanor: アーキテクチャ、データモデル、機能フロー
- NovelWriter: エージェントアーキテクチャ、品質管理
- 302_novel_writing: プロンプト設計、UI/UX

### 3.2 Antigravity 解析（.exchange/sessions/）

- アーキテクチャ横断分析
- Chekhov's Gun Tracker 設計案
- Hybrid Parsing アプローチ
- The Relay ワークフロー

### 3.3 クロスレビュー統合

| 採用元 | 採用要素 |
|--------|---------|
| Antigravity | subtlety_level、Reviewer Agent、Lazy Loading Context |
| Claude Code | AoT並列処理、Phase-Gate-Approval、ER図 |
| 両者共通 | 4段階可視性、L1/L2/L3階層、フェーズ管理 |

### 3.4 追加解析（新角度）

- ユースケース分析（6ケース）
- 非機能要件分析
- リスク分析
- 移行分析
- トークン消費分析

---

## 4. 技術スタック

| カテゴリ | 技術 |
|---------|------|
| 実行環境 | Claude Code (CLI) |
| AI | Claude (Opus/Sonnet/Haiku) |
| データ形式 | Markdown + YAML frontmatter |
| 統合環境 | Obsidian (vault構造) |
| 言語 | Python 3.10+ (分析モジュール) |
| 形態素解析 | fugashi + unidic-lite |

---

## 5. 参照ドキュメント

- `docs/specs/novel-generator/` - Claude Code 解析結果
- `.exchange/sessions/2026-01-24_001_analysis-antigravity-architecture.md` - Antigravity 解析
- `docs/Novel-Athanor-main/` - 解析対象：Novel-Athanor
- `docs/NovelWriter-main/` - 解析対象：NovelWriter
- `docs/302_novel_writing-main/` - 解析対象：302_novel_writing
