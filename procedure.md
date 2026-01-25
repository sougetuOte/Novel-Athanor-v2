# Novel-Athanor-v2 セットアップ手順書

このドキュメントは、別のPCでこのプロジェクトを展開する際の手順を説明します。
初心者でも分かりやすいようにステップバイステップで記載しています。

---

## 前提条件

以下がインストールされている必要があります：

| ツール | バージョン | 確認コマンド |
|--------|-----------|-------------|
| Python | 3.12 以上 | `python --version` |
| Git | 最新版推奨 | `git --version` |
| uv | 最新版推奨 | `uv --version` |

### uv のインストール（未インストールの場合）

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## セットアップ手順

### Step 1: リポジトリのクローン

```bash
git clone <リポジトリURL>
cd Novel-Athanor-v2
```

### Step 2: 仮想環境の作成

このプロジェクトは `uv` を使用して依存関係を管理しています。

```bash
# 仮想環境を作成（.venv ディレクトリが作成されます）
uv venv

# 仮想環境を有効化
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

### Step 3: 依存関係のインストール

```bash
# 開発用依存関係を含めてインストール
uv sync
```

これで `pyproject.toml` に記載された全ての依存関係がインストールされます。

### Step 4: インストール確認

```bash
# テストを実行して環境が正しくセットアップされたか確認
pytest

# 型チェック
mypy src/

# Lint チェック
ruff check src/
```

全てパスすれば、セットアップ完了です。

---

## ディレクトリ構成

```
Novel-Athanor-v2/
├── src/                    # ソースコード
│   └── core/               # コアモジュール
│       ├── models/         # L1: データモデル
│       ├── parsers/        # L1/L2: パーサー
│       ├── services/       # L2: サービス層
│       └── context/        # L3: コンテキストビルダー
├── tests/                  # テストコード
├── docs/                   # ドキュメント
│   ├── specs/              # 仕様書
│   ├── tasks/              # タスク定義
│   ├── internal/           # 内部プロセス定義
│   └── adr/                # 設計決定記録
├── .claude/                # Claude Code 設定
├── .exchange/              # AIエージェント間の通信記録
├── .serena/                # Serena MCP メモリ
├── pyproject.toml          # プロジェクト設定・依存関係
└── uv.lock                 # 依存関係ロックファイル
```

---

## 依存関係ファイルについて

| ファイル | 説明 |
|----------|------|
| `pyproject.toml` | プロジェクト設定と依存関係の定義 |
| `uv.lock` | 依存関係のバージョン固定（自動生成） |

`requirements.txt` は使用していません。`uv` が `pyproject.toml` を直接読み取ります。

---

## よく使うコマンド

### テスト実行

```bash
# 全テスト実行
pytest

# 特定のテストファイルを実行
pytest tests/core/context/test_scene_identifier.py

# カバレッジ付きで実行
pytest --cov=src --cov-report=html

# 失敗したテストのみ再実行
pytest --lf
```

### コード品質チェック

```bash
# 型チェック
mypy src/

# Lint
ruff check src/

# フォーマット
ruff format src/
```

### 依存関係の追加

```bash
# 本番用依存関係を追加
uv add <パッケージ名>

# 開発用依存関係を追加
uv add --dev <パッケージ名>

# 依存関係の更新
uv sync
```

---

## Claude Code での作業再開

このプロジェクトは Claude Code を使用して開発しています。

### 作業再開手順

1. ターミナルでプロジェクトディレクトリに移動
2. `claude` コマンドで Claude Code を起動
3. Serena のメモリを確認（現状と次のタスクが記録されています）

```bash
cd Novel-Athanor-v2
claude
```

### 現在の開発状況

- **L0/L1/L2**: 実装完了
- **L3**: Phase A 実装完了、Phase B〜G タスクドキュメント作成完了

詳細は `.serena/memories/` を確認してください。

---

## トラブルシューティング

### 仮想環境が有効化できない（Windows）

PowerShell の実行ポリシーを変更：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### uv sync でエラーが出る

Python バージョンを確認：

```bash
python --version  # 3.12 以上が必要
```

### テストが失敗する

依存関係を再インストール：

```bash
uv sync --reinstall
```

---

## 参考リンク

- [uv 公式ドキュメント](https://docs.astral.sh/uv/)
- [pytest 公式ドキュメント](https://docs.pytest.org/)
- [mypy 公式ドキュメント](https://mypy.readthedocs.io/)
- [ruff 公式ドキュメント](https://docs.astral.sh/ruff/)
