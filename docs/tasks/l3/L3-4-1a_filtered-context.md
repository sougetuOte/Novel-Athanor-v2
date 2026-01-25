# L3-4-1a: FilteredContext データクラス定義

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-4-1a |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | なし |
| 並列実行 | Phase A グループ（他データクラスと並列可） |
| 参照仕様 | `docs/specs/novel-generator-v2/08_agent-design.md` Section 3.5 |

## 概要

フィルタリング済みのコンテキストを保持するデータクラスを定義する。
このクラスは L3 から L4（エージェントレイヤー）に渡される主要な出力形式となる。

## 受け入れ条件

- [ ] `FilteredContext` データクラスが定義されている
- [ ] Plot L1/L2/L3、Summary L1/L2/L3 フィールドが存在する
- [ ] characters, world_settings が dict 形式である
- [ ] style_guide フィールドが存在する
- [ ] メタ情報（scene_id, current_phase, warnings）が存在する
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/context_integrator.py`
- テスト: `tests/core/context/test_context_integrator.py`

### クラス定義

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class FilteredContext:
    """フィルタリング済みコンテキスト

    AI情報制御レイヤー（L2）とフェーズフィルタを通過した後の
    コンテキスト情報を保持する。このクラスは Ghost Writer に
    渡される主要な入力となる。

    Attributes:
        plot_l1: L1プロット（テーマ、全体方向性）
        plot_l2: L2プロット（章の目的、状態変化目標）
        plot_l3: L3プロット（シーン構成、場面リスト）
        summary_l1: L1サマリ（全体サマリ）
        summary_l2: L2サマリ（章サマリ）
        summary_l3: L3サマリ（直近のシーンサマリ）
        characters: キャラクター情報（名前→フェーズフィルタ済み情報）
        world_settings: 世界観設定（名前→フェーズフィルタ済み情報）
        style_guide: スタイルガイド
        scene_id: 対象シーンの識別子
        current_phase: 現在のフェーズ
        warnings: 処理中に発生した警告
    """

    # Plot 情報（階層構造）
    plot_l1: Optional[str] = None
    plot_l2: Optional[str] = None
    plot_l3: Optional[str] = None

    # Summary 情報（階層構造）
    summary_l1: Optional[str] = None
    summary_l2: Optional[str] = None
    summary_l3: Optional[str] = None

    # キャラクター情報（フェーズフィルタ済み）
    # key: キャラクター名, value: フィルタ済み設定テキスト
    characters: dict[str, str] = field(default_factory=dict)

    # 世界観設定（フェーズフィルタ済み）
    # key: 設定名, value: フィルタ済み設定テキスト
    world_settings: dict[str, str] = field(default_factory=dict)

    # スタイルガイド
    style_guide: Optional[str] = None

    # メタ情報
    scene_id: str = ""
    current_phase: Optional[str] = None
    warnings: list[str] = field(default_factory=list)

    def has_plot(self) -> bool:
        """プロット情報が存在するか"""
        return any([self.plot_l1, self.plot_l2, self.plot_l3])

    def has_summary(self) -> bool:
        """サマリ情報が存在するか"""
        return any([self.summary_l1, self.summary_l2, self.summary_l3])

    def get_character_names(self) -> list[str]:
        """キャラクター名のリストを取得"""
        return list(self.characters.keys())

    def add_warning(self, warning: str) -> None:
        """警告を追加"""
        self.warnings.append(warning)

    def to_prompt_dict(self) -> dict[str, str]:
        """プロンプト用の辞書形式に変換

        Ghost Writer に渡すためのフラットな辞書形式に変換する。
        """
        result = {}

        if self.plot_l1:
            result["plot_theme"] = self.plot_l1
        if self.plot_l2:
            result["plot_chapter"] = self.plot_l2
        if self.plot_l3:
            result["plot_scene"] = self.plot_l3

        if self.summary_l1:
            result["summary_overall"] = self.summary_l1
        if self.summary_l2:
            result["summary_chapter"] = self.summary_l2
        if self.summary_l3:
            result["summary_recent"] = self.summary_l3

        for name, info in self.characters.items():
            result[f"character_{name}"] = info

        for name, info in self.world_settings.items():
            result[f"world_{name}"] = info

        if self.style_guide:
            result["style_guide"] = self.style_guide

        return result
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | 空のFilteredContext生成 | デフォルト値で生成できる |
| 2 | 全フィールド指定 | 全フィールドを指定して生成 |
| 3 | has_plot() True | plot_l1 のみ設定時 |
| 4 | has_plot() False | 全て None 時 |
| 5 | has_summary() True | summary_l3 のみ設定時 |
| 6 | get_character_names() | キャラクター名リスト取得 |
| 7 | add_warning() | 警告追加の動作確認 |
| 8 | to_prompt_dict() | 辞書変換の動作確認 |

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
