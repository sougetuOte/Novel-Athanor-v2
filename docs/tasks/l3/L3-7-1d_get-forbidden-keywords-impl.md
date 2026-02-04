# L3-7-1d: get_forbidden_keywords() 実装

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-7-1d |
| 優先度 | P1 |
| ステータス | done |
| 完了日 | 2026-02-04 |
| 依存タスク | L3-7-1b, L3-5-2c |
| フェーズ | Phase F（ContextBuilder ファサード） |
| 参照仕様 | `docs/specs/novel-generator-v2/04_ai-information-control.md` |

## 概要

ContextBuilder の `get_forbidden_keywords()` メソッドを実装する。
シーンで使用してはいけないキーワードを取得する専用メソッド。

## 受け入れ条件

- [ ] `get_forbidden_keywords()` メソッドが機能する
- [ ] 全ソースからの禁止キーワード統合
- [ ] プロンプト形式への変換メソッド
- [ ] デバッグ用ソース情報取得
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/context_builder.py`（既存ファイルに追加）
- テスト: `tests/core/context/test_context_builder.py`（既存ファイルに追加）

### メソッド定義

```python
# ContextBuilder クラスに追加

from .forbidden_keyword_collector import ForbiddenKeywordResult

class ContextBuilder:
    # ... 既存コード ...

    def __init__(self, ...):
        # ... 既存コード ...
        # 禁止キーワードキャッシュ
        self._forbidden_cache: dict[str, ForbiddenKeywordResult] = {}

    def get_forbidden_keywords(
        self,
        scene: SceneIdentifier,
        use_cache: bool = True,
    ) -> list[str]:
        """禁止キーワードを取得

        シーンで使用してはいけないキーワードのリストを返す。

        Args:
            scene: シーン識別子
            use_cache: キャッシュを使用するか

        Returns:
            禁止キーワードリスト（重複排除・ソート済み）
        """
        result = self._get_forbidden_result(scene, use_cache)
        return result.keywords

    def get_forbidden_keywords_with_sources(
        self,
        scene: SceneIdentifier,
    ) -> ForbiddenKeywordResult:
        """禁止キーワードをソース情報付きで取得

        デバッグ用。どのソースからキーワードが来たかを確認できる。

        Args:
            scene: シーン識別子

        Returns:
            ソース情報付き禁止キーワード結果
        """
        return self._get_forbidden_result(scene, use_cache=True)

    def _get_forbidden_result(
        self,
        scene: SceneIdentifier,
        use_cache: bool,
    ) -> ForbiddenKeywordResult:
        """禁止キーワード結果を取得（内部メソッド）"""
        if not self.forbidden_collector:
            return ForbiddenKeywordResult()

        cache_key = self._make_cache_key(scene)

        # キャッシュチェック
        if use_cache and cache_key in self._forbidden_cache:
            return self._forbidden_cache[cache_key]

        # 伏線指示書を取得（禁止キーワード収集に必要）
        instructions = self.get_foreshadow_instructions(scene, use_cache=True)

        # 収集
        result = self.forbidden_collector.collect(scene, instructions)

        # キャッシュ保存
        if use_cache:
            self._forbidden_cache[cache_key] = result

        return result

    def get_forbidden_keywords_as_prompt(
        self,
        scene: SceneIdentifier,
    ) -> str:
        """禁止キーワードをプロンプト形式で取得

        Ghost Writer に渡す形式に変換。

        Args:
            scene: シーン識別子

        Returns:
            プロンプト形式の禁止キーワード
        """
        keywords = self.get_forbidden_keywords(scene)
        return self._format_forbidden_for_prompt(keywords)

    def _format_forbidden_for_prompt(
        self,
        keywords: list[str],
    ) -> str:
        """禁止キーワードをプロンプト形式に変換"""
        if not keywords:
            return ""

        lines = ["## 禁止キーワード\n"]
        lines.append("以下の言葉は、このシーンで**絶対に使用しないでください**：\n")

        for keyword in keywords:
            lines.append(f"- 「{keyword}」")

        lines.append("")
        lines.append("これらの言葉を直接使うと、伏線やサプライズが台無しになります。")
        lines.append("別の表現で暗示することは許可されています。")

        return "\n".join(lines)

    def get_forbidden_by_source(
        self,
        scene: SceneIdentifier,
    ) -> dict[str, list[str]]:
        """ソース別禁止キーワードを取得

        どのソースから何のキーワードが来たかを確認。

        Args:
            scene: シーン識別子

        Returns:
            ソース → キーワードリスト
        """
        result = self._get_forbidden_result(scene, use_cache=True)
        return result.sources

    def check_text_for_forbidden(
        self,
        scene: SceneIdentifier,
        text: str,
    ) -> list[str]:
        """テキストに禁止キーワードが含まれるか確認

        生成されたテキストのバリデーション用。

        Args:
            scene: シーン識別子
            text: チェック対象テキスト

        Returns:
            見つかった禁止キーワードのリスト
        """
        keywords = self.get_forbidden_keywords(scene)
        found = []

        for keyword in keywords:
            if keyword in text:
                found.append(keyword)

        return found

    def is_text_clean(
        self,
        scene: SceneIdentifier,
        text: str,
    ) -> bool:
        """テキストが禁止キーワードを含まないか確認

        Args:
            scene: シーン識別子
            text: チェック対象テキスト

        Returns:
            禁止キーワードを含まなければ True
        """
        found = self.check_text_for_forbidden(scene, text)
        return len(found) == 0

    def clear_forbidden_cache(self) -> None:
        """禁止キーワードキャッシュをクリア"""
        self._forbidden_cache.clear()

    def clear_all_caches(self) -> None:
        """全キャッシュをクリア"""
        self.clear_instruction_cache()
        self.clear_forbidden_cache()
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | get_forbidden_keywords() 正常 | キーワード取得 |
| 2 | get_forbidden_keywords() キャッシュ | 再計算しない |
| 3 | get_forbidden_keywords() 収集なし | 空リスト |
| 4 | get_forbidden_keywords_with_sources() | ソース付き |
| 5 | get_forbidden_keywords_as_prompt() | プロンプト形式 |
| 6 | get_forbidden_by_source() | ソース別 |
| 7 | check_text_for_forbidden() 検出 | キーワード発見 |
| 8 | check_text_for_forbidden() なし | 空リスト |
| 9 | is_text_clean() True | クリーン |
| 10 | is_text_clean() False | 汚染あり |
| 11 | clear_forbidden_cache() | クリア |

### プロンプト出力例

```markdown
## 禁止キーワード

以下の言葉は、このシーンで**絶対に使用しないでください**：

- 「王族」
- 「血筋」
- 「禁忌の魔法」
- 「真の名前」
- 「最終兵器」

これらの言葉を直接使うと、伏線やサプライズが台無しになります。
別の表現で暗示することは許可されています。
```

### ソース別出力例

```python
{
    "foreshadowing": ["王族", "血筋", "禁忌の魔法"],
    "visibility": ["真の名前"],
    "global": ["最終兵器", "世界の終末"],
    "expression_filter": ["神の力"],
}
```

### バリデーション使用例

```python
# 生成されたテキストをチェック
generated_text = "彼女は王族の血を引いていた..."

found = builder.check_text_for_forbidden(scene, generated_text)
# found = ["王族"]

if not builder.is_text_clean(scene, generated_text):
    print(f"禁止キーワードが含まれています: {found}")
    # 再生成を要求
```

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
