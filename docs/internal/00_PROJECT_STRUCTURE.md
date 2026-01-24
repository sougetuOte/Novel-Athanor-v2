# Project Structure & Naming Conventions

本ドキュメントは、プロジェクトの物理的な構成（ディレクトリ構造）と、資産の配置ルールを定義する。
"Living Architect" は、この地図に従って情報を格納・検索しなければならない。

## 1. Directory Structure (ディレクトリ構成)

```
/
├── src/                    # ソースコード (実装)
│   ├── core/               # コアモジュール (Python)
│   ├── agents/             # エージェント実装
│   └── cli/                # CLIインターフェース
├── tests/                  # テストコード
├── docs/                   # ドキュメント資産
│   ├── specs/              # 要求仕様書 (Source of Truth)
│   ├── adr/                # アーキテクチャ決定記録 (Why)
│   ├── tasks/              # タスク管理 (Kanban/List)
│   ├── internal/           # プロジェクト運用ルール (本フォルダ)
│   ├── memos/              # [Input] ユーザーからの生メモ・資料
│   ├── Novel-Athanor-main/      # [解析対象] 設定管理プロジェクト
│   ├── NovelWriter-main/        # [解析対象] 自動生成プロジェクト
│   └── 302_novel_writing-main/  # [解析対象] Web UIプロジェクト
├── .claude/                # Claude Code用設定・コマンド
├── .exchange/              # 外部AI連携（Antigravity等）
└── CLAUDE.md               # プロジェクト憲法
```

### 解析対象プロジェクトについて

`docs/` 配下の `*-main/` ディレクトリは、解析・参照用のプロジェクトである。
これらは **読み取り専用** として扱い、直接編集しない。

| ディレクトリ | 出典 | 強み | 編集可否 |
|-------------|------|------|---------|
| `Novel-Athanor-main/` | ユーザー作 | 設定管理、フェーズ管理 | 読み取り専用 |
| `NovelWriter-main/` | [GitHub](https://github.com/EdwardAThomson/NovelWriter) | マルチエージェント、自動生成 | 読み取り専用 |
| `302_novel_writing-main/` | [GitHub](https://github.com/302ai/302_novel_writing) | Web UI、多言語対応 | 読み取り専用 |

### 仕様書ディレクトリ

| ディレクトリ | 内容 | ステータス |
|-------------|------|-----------|
| `docs/specs/novel-generator/` | 3プロジェクト解析結果 | 完了 |
| `docs/specs/novel-generator-v2/` | **統合仕様書（00-09）** | レビュー完了・実装準備完了 |

### 外部AI連携

| ディレクトリ | 用途 |
|-------------|------|
| `.exchange/` | Antigravity（Google Gemini 3 Pro）との情報交換 |

## 2. Asset Placement Rules (資産配置ルール)

### A. User Inputs (ユーザー入力)

- **Raw Ideas**: ユーザーからの未加工のアイデアやチャットログは `docs/memos/YYYY-MM-DD_topic.md` に保存する。
- **Reference Materials**: 参考資料（画像、PDF）は `docs/memos/assets/` に配置する。

### B. Specifications (仕様書)

- **Naming**: `docs/specs/{feature_name}.md` (ケバブケース)
- **Granularity**: 1 機能 = 1 ファイル。巨大になる場合はディレクトリを切る。

### C. ADR (Architectural Decision Records)

- **Naming**: `docs/adr/NNNN-kebab-case-title.md`（例: `0001-three-project-integration.md`）
- **Immutable**: 一度確定した ADR は原則変更せず、変更が必要な場合は新しい ADR を作成して "Supersedes" と明記する。

## 3. File Naming Conventions (命名規則)

- **Directories**: `snake_case` (例: `user_auth`)
- **Files (Code)**: 言語標準に従う (Python: `snake_case.py`, JS/TS: `PascalCase.tsx` or `camelCase.ts`)
- **Files (Docs)**: `snake_case.md` または `kebab-case.md` (プロジェクト内で統一)
