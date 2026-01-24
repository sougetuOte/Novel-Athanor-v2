# L0-1-3: pytest 環境セットアップ

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L0-1-3 |
| 優先度 | P0 |
| ステータス | ✅ done |
| 依存タスク | L0-1-1 |
| 参照仕様 | `docs/internal/02_DEVELOPMENT_FLOW.md` Phase 2 |

## 概要

TDD サイクルを回すための pytest 環境をセットアップする。

## 受け入れ条件

- [ ] `pytest.ini` または `pyproject.toml` に pytest 設定が存在する
- [ ] `pytest` コマンドが正常に実行できる
- [ ] `pytest --cov=src` でカバレッジレポートが生成できる
- [ ] サンプルテストが PASS する

## 技術的詳細

### pyproject.toml への追記

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/__init__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
]
```

### サンプルテスト

```python
# tests/test_sample.py
def test_sample():
    """セットアップ確認用のサンプルテスト"""
    assert 1 + 1 == 2
```

## 実装メモ

- 2026-01-24: pyproject.toml に coverage 設定追加
- tests/test_sample.py 作成（基本テスト + import テスト）
- pytest / pytest --cov=src ともに終了コード 0 で成功

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
