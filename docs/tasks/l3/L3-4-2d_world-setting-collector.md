# L3-4-2d: WorldSetting コンテキスト収集（Phaseフィルタ適用）

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-4-2d |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-4-1b, L3-3-1c |
| フェーズ | Phase D（コンテキスト収集） |
| 参照仕様 | `docs/specs/novel-generator-v2/03_data-model.md` |

## 概要

世界観設定を収集し、Phase フィルタを適用するコレクターを実装する。
シーンに関連する設定を特定し、現在フェーズに適切な情報のみを抽出。

## 受け入れ条件

- [ ] `WorldSettingCollector` クラスが実装されている
- [ ] シーンに関連する世界観設定を特定できる
- [ ] WorldSettingPhaseFilter でフィルタリングできる
- [ ] 複数設定を収集できる
- [ ] ContextCollector プロトコルに準拠
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/collectors/world_setting_collector.py`（新規）
- テスト: `tests/core/context/collectors/test_world_setting_collector.py`（新規）

### クラス定義

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from src.core.models.world_setting import WorldSetting
from ..scene_identifier import SceneIdentifier
from ..scene_resolver import SceneResolver
from ..lazy_loader import FileLazyLoader, LoadPriority
from ..phase_filter import WorldSettingPhaseFilter

@dataclass
class WorldSettingContext:
    """世界観設定コンテキスト

    Attributes:
        settings: 設定名 → フィルタ済み設定文字列
        warnings: 収集時の警告
    """
    settings: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def get_names(self) -> list[str]:
        """設定名一覧"""
        return list(self.settings.keys())

    def get_setting(self, name: str) -> Optional[str]:
        """指定設定を取得"""
        return self.settings.get(name)


class WorldSettingCollector:
    """世界観設定コンテキスト収集

    シーンに関連する世界観設定を特定し、
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
        phase_filter: WorldSettingPhaseFilter,
    ):
        self.vault_root = vault_root
        self.loader = loader
        self.resolver = resolver
        self.phase_filter = phase_filter

    def collect(self, scene: SceneIdentifier) -> WorldSettingContext:
        """世界観設定コンテキストを収集

        1. シーンに関連する設定ファイルを特定
        2. 各設定を読み込み
        3. Phase フィルタを適用
        4. コンテキスト文字列に変換

        Args:
            scene: シーン識別子

        Returns:
            収集した世界観設定コンテキスト
        """
        context = WorldSettingContext()

        # 設定ファイルを特定
        setting_paths = self.resolver.identify_world_settings(scene)

        for path in setting_paths:
            try:
                # ファイル読み込み
                result = self.loader.load(
                    str(path.relative_to(self.vault_root)),
                    LoadPriority.REQUIRED,
                )
                if not result.success or not result.data:
                    context.warnings.append(f"世界観設定読み込み失敗: {path}")
                    continue

                # パース
                setting = self._parse_world_setting(path, result.data)
                if not setting:
                    context.warnings.append(f"世界観設定パース失敗: {path}")
                    continue

                # Phase フィルタ適用
                if scene.current_phase:
                    filtered_str = self.phase_filter.to_context_string(
                        setting,
                        scene.current_phase,
                    )
                else:
                    # フェーズ指定なしの場合は全情報
                    filtered_str = self._setting_to_string(setting)

                context.settings[setting.name] = filtered_str

            except Exception as e:
                context.warnings.append(f"世界観設定処理エラー: {path}: {e}")

        return context

    def _parse_world_setting(
        self, path: Path, content: str
    ) -> Optional[WorldSetting]:
        """ファイル内容から WorldSetting をパース

        Args:
            path: ファイルパス
            content: ファイル内容

        Returns:
            パースした WorldSetting、失敗時は None
        """
        # L1 の WorldSetting モデルのパーサーを使用
        # TODO: WorldSettingParser との統合
        ...

    def _setting_to_string(self, setting: WorldSetting) -> str:
        """設定を文字列に変換（フィルタなし）"""
        lines = [f"# {setting.name}"]
        if setting.category:
            lines.append(f"Category: {setting.category}")
        if setting.description:
            lines.append(setting.description)
        return "\n".join(lines)

    def collect_as_string(self, scene: SceneIdentifier) -> Optional[str]:
        """ContextCollector プロトコル準拠メソッド

        全設定を統合した文字列を返す。

        Args:
            scene: シーン識別子

        Returns:
            統合された世界観設定文字列
        """
        context = self.collect(scene)

        if not context.settings:
            return None

        parts = [
            f"## {name}\n{info}"
            for name, info in context.settings.items()
        ]

        return "\n\n---\n\n".join(parts)
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | collect() 単一設定 | 1設定 |
| 2 | collect() 複数設定 | 複数設定 |
| 3 | collect() 設定なし | 空コンテキスト |
| 4 | collect() Phase適用 | フィルタ確認 |
| 5 | collect() Phase未指定 | 全情報 |
| 6 | collect() サブディレクトリ | 階層対応 |
| 7 | _parse_world_setting() | パース処理 |
| 8 | collect_as_string() | 統合文字列 |
| 9 | 読み込み失敗時 | warnings に記録 |

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
