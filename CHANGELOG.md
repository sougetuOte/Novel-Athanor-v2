# Changelog

All notable changes to Novel-Athanor-v2 will be documented in this file.

## [v0.1.0] - 2026-01-24

### Added

- **Analysis**: 3プロジェクト解析完了
  - Novel-Athanor（ユーザー作）: 設定管理、フェーズ管理
  - NovelWriter: マルチエージェント、自動生成
  - 302_novel_writing: Web UI、多言語対応
- **Specification**: 統合仕様書策定完了（`docs/specs/novel-generator-v2/`）
  - 00_overview.md 〜 09_migration.md（全10ファイル）
  - AI情報制御（4段階可視性）
  - 伏線管理システム（Chekhov's Gun Tracker）
  - The Relay ワークフロー
  - エージェント設計（9種）
- **Framework**: Living Architect Model 開発フレームワーク導入
  - フェーズ制御（PLANNING/BUILDING/AUDITING）
  - 承認ゲートシステム
  - サブエージェント（5種）
- **Integration**: Antigravity（Google Gemini 3 Pro）との連携（`.exchange/`）

### Note

- 本プロジェクトは Living Architect Model テンプレートから派生
- 仕様策定完了、実装準備段階
