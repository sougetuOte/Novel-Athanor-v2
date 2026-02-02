# HTMLプレゼンテーション作成計画

## 概要

Novel-Athanor-v2 プロジェクトのアーキテクチャと実装状況を説明する
視覚的なHTMLプレゼンテーションを作成する。

## 対象読者

- プロジェクトオーナー（自己理解）
- 他の開発者（オンボーディング、協力開発）

## 言語方針

- 説明テキスト: 日本語
- コード例・モジュール名: 英語

---

## 成果物構成

```
docs/presentations/architecture-overview/
├── plan.md              # 本ファイル（作成計画）
├── index.html           # メインプレゼンテーション
└── assets/
    └── styles.css       # スタイルシート
```

## スライド構成（予定）

| # | セクション | 内容 |
|---|-----------|------|
| 1 | タイトル | プロジェクト名、目的、キャッチコピー |
| 2 | プロジェクト背景 | 3つの解析対象プロジェクト、統合目標 |
| 3 | 差別化ポイント | AI情報制御、伏線管理、半自動ワークフロー |
| 4 | 5層アーキテクチャ全体図 | L1〜L5の概観（図） |
| 5 | L1: Data Layer | Vault構造、データモデル関係図 |
| 6 | L2: Context Builder | Lazy Loader、Phase Filter、Collectors |
| 7 | L3: AI Information Control | 4段階可視性、Expression Filter、Foreshadow Manager |
| 8 | L4: Agent Layer | The Relay ワークフロー（未実装を明示） |
| 9 | L5: Orchestration Layer | Chief Editor、Phase-Gate-Approval（未実装を明示） |
| 10 | 4段階AI可視性システム | Level 0〜3 の詳細図解 |
| 11 | 伏線管理システム | Chekhov's Gun Tracker、ライフサイクル |
| 12 | 実装状況サマリー | 実装済み/進行中/未着手の一覧 |
| 13 | 今後のロードマップ | Phase E〜G、L4/L5 実装予定 |
| 14 | 技術スタック | Python, Obsidian, Claude Code 等 |

---

## タスク分割（並列実行対応）

### Phase 1: 基盤準備（並列可能）

| Task ID | タスク名 | 依存 | 担当可能 |
|---------|---------|------|----------|
| T1 | HTMLテンプレート作成 | なし | 独立 |
| T2 | CSSスタイル設計 | なし | 独立 |
| T3 | 5層アーキテクチャ図のSVG/HTML作成 | なし | 独立 |

### Phase 2: コンテンツ作成（並列可能）

| Task ID | タスク名 | 依存 | 担当可能 |
|---------|---------|------|----------|
| T4 | スライド1-3: 導入セクション | T1 | 独立 |
| T5 | スライド4-5: L1/L2 レイヤー解説 | T1, T3 | 独立 |
| T6 | スライド6-7: L3 レイヤー解説 | T1, T3 | 独立 |
| T7 | スライド8-9: L4/L5 レイヤー解説 | T1, T3 | 独立 |
| T8 | スライド10: AI可視性システム詳細 | T1 | 独立 |
| T9 | スライド11: 伏線管理システム詳細 | T1 | 独立 |

### Phase 3: 統合・仕上げ

| Task ID | タスク名 | 依存 | 担当可能 |
|---------|---------|------|----------|
| T10 | スライド12-14: 状況・ロードマップ | T4-T9 | 順次 |
| T11 | 全体統合・動作確認 | T1-T10 | 順次 |
| T12 | レビュー・微調整 | T11 | 順次 |

---

## 技術仕様

### HTMLプレゼンテーション形式

- **Single Page Application**: 1つのHTMLファイルで完結
- **ナビゲーション**: キーボード（←→）またはクリックでスライド切り替え
- **レスポンシブ**: 様々な画面サイズに対応
- **印刷対応**: 必要に応じてPDF出力可能

### 図表作成方針

- **アーキテクチャ図**: HTML/CSS（flexbox/grid）またはSVG
- **フローチャート**: CSS Grid または SVG
- **データモデル図**: HTML table または SVG
- **アニメーション**: CSS transitions（控えめに）

### カラースキーム

| 要素 | 色 |
|------|-----|
| L5 Orchestration | #6366f1 (Indigo) |
| L4 Agent | #8b5cf6 (Violet) |
| L3 AI Control | #ec4899 (Pink) |
| L2 Context | #14b8a6 (Teal) |
| L1 Data | #f59e0b (Amber) |
| 実装済み | #22c55e (Green) |
| 進行中 | #eab308 (Yellow) |
| 未着手 | #94a3b8 (Gray) |

---

## 進捗管理

Claude Code の ToDo 機能を使用してタスク進捗を追跡する。

### 並列実行グループ

```
Group A (Phase 1): T1, T2, T3 → 同時実行可能
Group B (Phase 2): T4, T5, T6, T7, T8, T9 → T1完了後、同時実行可能
Group C (Phase 3): T10 → T11 → T12 → 順次実行
```

---

## 作成日

2026-02-02
