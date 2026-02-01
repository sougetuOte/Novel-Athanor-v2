# L3-4-2c: Character コンテキスト収集（Phaseフィルタ適用）

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-4-2c |
| 優先度 | P1 |
| ステータス | ✅ done |
| 完了日 | 2026-02-01 |
| 依存タスク | L3-4-1b, L3-3-1b |
| フェーズ | Phase D（コンテキスト収集） |
| 参照仕様 | `docs/specs/novel-generator-v2/03_data-model.md` |

## 概要

キャラクター情報を収集し、Phase フィルタを適用するコレクターを実装する。
シーンに登場するキャラクターを特定し、現在フェーズに適切な情報のみを抽出。

## 受け入れ条件

- [x] `CharacterCollector` クラスが実装されている
- [x] シーンに関連するキャラクターを特定できる
- [x] CharacterPhaseFilter でフィルタリングできる
- [x] 複数キャラクターを収集できる
- [x] ContextCollector プロトコルに準拠
- [x] ユニットテストが存在する (12 tests, 100% pass)

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/collectors/character_collector.py`（新規）
- テスト: `tests/core/context/collectors/test_character_collector.py`（新規）

### クラス定義

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from src.core.models.character import Character
from ..scene_identifier import SceneIdentifier
from ..scene_resolver import SceneResolver
from ..lazy_loader import FileLazyLoader, LoadPriority
from ..phase_filter import CharacterPhaseFilter

@dataclass
class CharacterContext:
    """キャラクターコンテキスト

    Attributes:
        characters: キャラクター名 → フィルタ済み設定文字列
        warnings: 収集時の警告
    """
    characters: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def get_names(self) -> list[str]:
        """キャラクター名一覧"""
        return list(self.characters.keys())

    def get_character(self, name: str) -> Optional[str]:
        """指定キャラクターの設定を取得"""
        return self.characters.get(name)


class CharacterCollector:
    """キャラクターコンテキスト収集

    シーンに関連するキャラクターを特定し、
    Phase フィルタを適用して収集する。

    Attributes:
        vault_root: vault ルートパス
        loader: 遅延読み込みローダー
        resolver: シーン解決器
        phase_filter: フェーズフィルタ
    """

    def __init__(
        self,
        vault_root: Path,
        loader: FileLazyLoader,
        resolver: SceneResolver,
        phase_filter: CharacterPhaseFilter,
    ):
        self.vault_root = vault_root
        self.loader = loader
        self.resolver = resolver
        self.phase_filter = phase_filter

    def collect(self, scene: SceneIdentifier) -> CharacterContext:
        """キャラクターコンテキストを収集

        1. シーンに関連するキャラクターファイルを特定
        2. 各キャラクターを読み込み
        3. Phase フィルタを適用
        4. コンテキスト文字列に変換

        Args:
            scene: シーン識別子

        Returns:
            収集したキャラクターコンテキスト
        """
        context = CharacterContext()

        # キャラクターファイルを特定
        character_paths = self.resolver.identify_characters(scene)

        for path in character_paths:
            try:
                # ファイル読み込み
                result = self.loader.load(
                    str(path.relative_to(self.vault_root)),
                    LoadPriority.REQUIRED,
                )
                if not result.success or not result.data:
                    context.warnings.append(f"キャラクター読み込み失敗: {path}")
                    continue

                # パース
                character = self._parse_character(path, result.data)
                if not character:
                    context.warnings.append(f"キャラクターパース失敗: {path}")
                    continue

                # Phase フィルタ適用
                if scene.current_phase:
                    filtered_str = self.phase_filter.to_context_string(
                        character,
                        scene.current_phase,
                    )
                else:
                    # フェーズ指定なしの場合は全情報
                    filtered_str = self._character_to_string(character)

                context.characters[character.name] = filtered_str

            except Exception as e:
                context.warnings.append(f"キャラクター処理エラー: {path}: {e}")

        return context

    def _parse_character(self, path: Path, content: str) -> Optional[Character]:
        """ファイル内容から Character をパース

        Args:
            path: ファイルパス
            content: ファイル内容

        Returns:
            パースした Character、失敗時は None
        """
        # L1 の Character モデルのパーサーを使用
        # TODO: CharacterParser との統合
        ...

    def _character_to_string(self, character: Character) -> str:
        """キャラクターを文字列に変換（フィルタなし）"""
        lines = [f"# {character.name}"]
        if character.description:
            lines.append(character.description)
        return "\n".join(lines)

    def collect_as_string(self, scene: SceneIdentifier) -> Optional[str]:
        """ContextCollector プロトコル準拠メソッド

        全キャラクターを統合した文字列を返す。

        Args:
            scene: シーン識別子

        Returns:
            統合されたキャラクター文字列
        """
        context = self.collect(scene)

        if not context.characters:
            return None

        parts = [
            f"## {name}\n{info}"
            for name, info in context.characters.items()
        ]

        return "\n\n---\n\n".join(parts)
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | collect() 単一キャラ | 1キャラクター |
| 2 | collect() 複数キャラ | 複数キャラクター |
| 3 | collect() キャラなし | 空コンテキスト |
| 4 | collect() Phase適用 | フィルタ確認 |
| 5 | collect() Phase未指定 | 全情報 |
| 6 | _parse_character() | パース処理 |
| 7 | collect_as_string() | 統合文字列 |
| 8 | 読み込み失敗時 | warnings に記録 |
| 9 | パース失敗時 | warnings に記録 |

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
| 2026-02-01 | 実装完了（TDD: Red → Green → Refactor、12 tests pass、mypy clean） |
