# L3-3-1c: WorldSetting Phase フィルタ

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-3-1c |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-3-1a, L1-2-3 |
| フェーズ | Phase C（個別機能実装） |
| 参照仕様 | `docs/specs/novel-generator-v2/03_data-model.md` |

## 概要

PhaseFilter プロトコルの世界観設定向け具象実装を作成する。
世界観設定の中から、現在のフェーズに適用可能な情報のみを抽出。

## 受け入れ条件

- [ ] `WorldSettingPhaseFilter` クラスが実装されている
- [ ] `filter_by_phase()` で指定フェーズまでの情報を抽出
- [ ] `get_available_phases()` で設定の全フェーズを取得
- [ ] L1 で定義した WorldSetting モデルと連携
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/phase_filter.py`（既存ファイルに追加）
- テスト: `tests/core/context/test_phase_filter.py`（既存ファイルに追加）

### クラス定義

```python
from typing import Optional
from src.core.models.world_setting import WorldSetting

class WorldSettingPhaseFilter:
    """世界観設定向け Phase フィルタ

    世界観設定をフェーズに基づいてフィルタリングする。
    指定されたフェーズまでの情報のみを抽出し、
    未来のフェーズの情報（ネタバレ）を除外する。

    Attributes:
        phase_order: フェーズの順序リスト（設定で定義）
    """

    def __init__(self, phase_order: list[str]):
        """
        Args:
            phase_order: フェーズの順序（例: ["initial", "arc_1", "arc_2", "finale"]）
        """
        self.phase_order = phase_order

    def filter_by_phase(
        self,
        setting: WorldSetting,
        phase: str,
    ) -> WorldSetting:
        """世界観設定をフェーズでフィルタリング

        指定されたフェーズまでの情報のみを含む設定を返す。

        Args:
            setting: フィルタ対象の世界観設定
            phase: 現在のフェーズ

        Returns:
            フィルタ済み世界観設定

        Raises:
            InvalidPhaseError: 無効なフェーズが指定された場合
        """
        if phase not in self.phase_order:
            raise InvalidPhaseError(
                f"Unknown phase: {phase}. "
                f"Available: {self.phase_order}"
            )

        # 現在フェーズのインデックスを取得
        phase_idx = self.phase_order.index(phase)
        applicable_phases = set(self.phase_order[:phase_idx + 1])

        # 設定の詳細をフィルタリング
        filtered_details = self._filter_details(
            setting.details,
            applicable_phases
        )

        # 新しい WorldSetting インスタンスを生成
        return WorldSetting(
            name=setting.name,
            category=setting.category,
            description=setting.description,
            details=filtered_details,
            visibility_overrides=setting.visibility_overrides,
        )

    def _filter_details(
        self,
        details: dict,
        applicable_phases: set[str],
    ) -> dict:
        """詳細情報をフィルタリング

        詳細情報の構造:
        {
            "overview": "魔法体系の概要...",
            "phases": {
                "initial": {"known_magic": "基本的な魔法"},
                "arc_2_reveal": {"forbidden_magic": "禁忌の魔法"},
            }
        }
        """
        result = {}

        for key, value in details.items():
            if key == "phases":
                # フェーズ依存の情報
                filtered_phases = {
                    p: v for p, v in value.items()
                    if p in applicable_phases
                }
                if filtered_phases:
                    result[key] = filtered_phases
            else:
                # 非フェーズ依存の情報はそのまま
                result[key] = value

        return result

    def get_available_phases(self, setting: WorldSetting) -> list[str]:
        """設定で利用可能なフェーズ一覧

        Args:
            setting: 対象の世界観設定

        Returns:
            フェーズ名のリスト（phase_order の順序を保持）
        """
        if "phases" not in setting.details:
            return []

        setting_phases = set(setting.details["phases"].keys())
        return [p for p in self.phase_order if p in setting_phases]

    def to_context_string(
        self,
        setting: WorldSetting,
        phase: str,
    ) -> str:
        """フィルタ済み設定をコンテキスト文字列に変換

        Args:
            setting: 世界観設定
            phase: 現在のフェーズ

        Returns:
            Ghost Writer に渡すコンテキスト文字列
        """
        filtered = self.filter_by_phase(setting, phase)

        lines = [f"# {filtered.name}"]
        if filtered.category:
            lines.append(f"Category: {filtered.category}")
        if filtered.description:
            lines.append(filtered.description)

        for key, value in filtered.details.items():
            if key == "phases":
                for p, phase_data in value.items():
                    lines.append(f"\n## Phase: {p}")
                    for k, v in phase_data.items():
                        lines.append(f"- {k}: {v}")
            else:
                lines.append(f"\n## {key}")
                lines.append(str(value))

        return "\n".join(lines)
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | filter_by_phase() initial | 最初のフェーズのみ |
| 2 | filter_by_phase() arc_2 | initial〜arc_2 |
| 3 | filter_by_phase() 無効フェーズ | InvalidPhaseError |
| 4 | get_available_phases() | フェーズ一覧取得 |
| 5 | get_available_phases() 空 | phases なし設定 |
| 6 | to_context_string() | 文字列変換 |
| 7 | 非フェーズ情報の保持 | overview 等 |
| 8 | category の保持 | カテゴリ情報 |

### 世界観設定の構造例

```yaml
# vault/world/魔法体系.md
---
name: 魔法体系
category: magic_system
description: この世界における魔法の仕組み
---

## 概要
魔法は精霊との契約によって発現する。

## phases

### initial
- known_magic: 基本的な精霊魔法（火、水、風、土）
- common_knowledge: 魔法は才能ある者のみが使える

### arc_2_reveal
- forbidden_magic: 古代に封印された禁忌の魔法
- secret_knowledge: 禁忌魔法は精霊を犠牲にする

### finale
- true_nature: 魔法の真の姿
- ultimate_secret: 精霊と人間の起源
```

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
