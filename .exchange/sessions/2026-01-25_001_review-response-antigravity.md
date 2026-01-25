# レビュー回答

## Meta

| 項目 | 値 |
|------|-----|
| Session ID | 2026-01-25_001 |
| 日時 | 2026-01-25 |
| レビュアー | Antigravity |
| 判定 | **A (Approve with minor fixes)** |

## 1. 問題点のリスト

実装されたコードは仕様書および設計要件を高いレベルで満たしており、非常に高品質です。
指摘事項は静的解析ツール（mypy, ruff）による軽微な型定義と構文の修正のみです。

### Critical (0件)
なし

### Warning (Must Fix) - 5件

依頼内容にあった mypy エラーと ruff 警告への対応が必要です。

1.  **src/core/models/ai_visibility.py:51**
    *   **Issue**: `UP007 Use X | Y for type annotations`
    *   **Fix**: `Union[str, AllowedExpression, dict]` を `str | AllowedExpression | dict` に変更してください。

2.  **src/core/repositories/foreshadowing.py:35**
    *   **Issue**: `Missing type parameters for generic type "dict"`
    *   **Fix**: `dict` を `dict[str, Any]` に変更してください。（`typing.Any` のインポートが必要です）

3.  **src/core/repositories/foreshadowing.py:45**
    *   **Issue**: `Missing type parameters for generic type "dict"`
    *   **Fix**: 同上。`data: dict[str, Any]`

4.  **src/core/repositories/foreshadowing.py:54**
    *   **Issue**: `Missing type parameters for generic type "dict"`
    *   **Fix**: 同上。`registry: dict[str, Any]`

### Info (Suggestion) - 2件

1.  **YAML保存時のキー順序 (src/core/repositories/foreshadowing.py:51)**
    *   `yaml.dump` はデフォルトで辞書のキー順序を保持しない場合があります（Pythonバージョン依存ですが、明示しておくと安全です）。`sort_keys=False` を指定することで、読み込み時の順序（あるいは挿入順）を維持しやすくなり、手動編集時の可読性が向上します。
    *   推奨: `yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)`

2.  **Obsidian Link Regex (src/core/parsers/obsidian_link.py:11)**
    *   現在の正規表現 `r"\[\[([^\]|#]+)(?:#(\^)?([^\]|]+))?(?:\|([^\]]+))?\]\]"` は標準的なケースを網羅していますが、パイプ `|` の後に `#` が来るようなエッジケース（表示名に `#` を含む場合など）は稀ですが、Obsidianの仕様上許容される場合があります。現状のスコープでは問題ありませんが、将来的にリンク記法が複雑化する場合は再考の余地があります。現状は **このままでOK** です。

## 2. リファクタリング提案

指摘された修正を適用するコード例です。

### src/core/repositories/foreshadowing.py

```python
from typing import Any  # 追加

# ...

    def _load_registry(self) -> dict[str, Any]:  # 修正
        """レジストリを読み込む."""
        # ...

    def _save_registry(self, data: dict[str, Any]) -> None:  # 修正
        """レジストリを保存する."""
        path = self._get_registry_path()
        path.parent.mkdir(parents=True, exist_ok=True)

        data["last_updated"] = date.today().isoformat()
        # sort_keys=False を追加推奨
        content = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        path.write_text(content, encoding="utf-8")

    def _find_index(self, registry: dict[str, Any], fs_id: str) -> int | None:  # 修正
        # ...
```

### src/core/models/ai_visibility.py

```python
    @field_validator("allowed_expressions", mode="before")
    @classmethod
    def coerce_expressions(
        cls, v: list[str | AllowedExpression | dict]  # Union を | に変更
    ) -> list[AllowedExpression]:
```

## 3. L2 レイヤー実装への推奨事項

今回の実装は L2（AI情報制御レイヤー）への接続を的確に見越した設計になっています。以下の点は特に良好であり、L2 実装時に活用すべきです。

1.  **Secret モデルの動的閾値**:
    *   `Secret.get_similarity_threshold()` は `Expression Filter` (L2-2) 実装時にそのまま利用してください。重要度に基づく検知感度の調整ロジックがモデル側にカプセル化されているのは良い設計です。

2.  **Allowed Expressions**:
    *   `AIVisibility` モデルの `allowed_expressions` は、L2-1 `Visibility Controller` が `Level 2 (KNOW)` のコンテキストを生成する際の「暗示推奨リスト」として機能します。プロンプトエンジニアリング時にこれを `system_prompt` に注入するロジックを忘れずに実装してください。

3.  **Foreshadowing Registry**:
    *   伏線情報が単一の YAML に集約されているため、`Foreshadowing Manager` (L2-3) はこのファイルを監視するだけで伏線状態の変更を検知できます。各エピソード生成前後のフックでこのレジストリをチェックし、`planted` や `reinforced` への状態遷移を自動化する仕組みを検討してください。

## 4. 総合評価

**Status**: **Approved** (修正後マージ可)

コード品質、設計品質ともに高く、テストカバレッジも十分です。
Pythonicな記述（Pydanticの活用、適切な型ヒント）がなされており、保守性も高いと判断します。
上記「Warning」の修正を行い次第、L2 フェーズへ進んでください。

お疲れ様でした！素晴らしい進捗です。
