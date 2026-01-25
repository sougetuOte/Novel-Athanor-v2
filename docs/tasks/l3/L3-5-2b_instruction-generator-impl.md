# L3-5-2b: 伏線ステータス別指示生成

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-5-2b |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-5-2a |
| フェーズ | Phase E（伏線・Visibility 統合） |
| 参照仕様 | `docs/specs/novel-generator-v2/05_foreshadowing-system.md` |

## 概要

InstructionGenerator プロトコルの具象実装を作成する。
特定された伏線から、Ghost Writer に渡す指示書を生成。

## 受け入れ条件

- [ ] `InstructionGeneratorImpl` クラスが実装されている
- [ ] PLANT 指示を生成できる
- [ ] REINFORCE 指示を生成できる
- [ ] HINT 指示を生成できる
- [ ] subtlety_target を適切に設定できる
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/instruction_generator.py`（既存ファイルに追加）
- テスト: `tests/core/context/test_instruction_generator.py`（既存ファイルに追加）

### クラス定義

```python
from typing import Optional
from src.core.services.foreshadowing_manager import ForeshadowingManager
from .scene_identifier import SceneIdentifier
from .foreshadowing_identifier import ForeshadowingIdentifier, IdentifiedForeshadowing
from .foreshadow_instruction import (
    ForeshadowInstruction,
    ForeshadowInstructions,
    InstructionAction,
)

class InstructionGeneratorImpl:
    """伏線指示書生成の具象実装

    特定された伏線情報から、Ghost Writer に渡す
    具体的な指示書を生成する。

    Attributes:
        foreshadowing_manager: L2 の伏線マネージャー
        identifier: 伏線特定器
    """

    def __init__(
        self,
        foreshadowing_manager: ForeshadowingManager,
        identifier: ForeshadowingIdentifier,
    ):
        self.foreshadowing_manager = foreshadowing_manager
        self.identifier = identifier

    def generate(
        self,
        scene: SceneIdentifier,
    ) -> ForeshadowInstructions:
        """伏線指示書を生成

        Args:
            scene: シーン識別子

        Returns:
            生成された伏線指示書
        """
        # 1. 関連伏線を特定
        identified = self.identifier.identify(scene)

        # 2. 各伏線の指示を生成
        instructions = ForeshadowInstructions()

        for item in identified:
            instruction = self._generate_instruction(item)
            instructions.add_instruction(instruction)

        return instructions

    def _generate_instruction(
        self,
        identified: IdentifiedForeshadowing,
    ) -> ForeshadowInstruction:
        """個別の伏線指示を生成

        Args:
            identified: 特定された伏線情報

        Returns:
            伏線指示
        """
        # 伏線の詳細を取得
        fs_detail = self.foreshadowing_manager.get(identified.foreshadowing_id)

        # アクション別に指示を生成
        if identified.suggested_action == InstructionAction.PLANT:
            return self._generate_plant_instruction(fs_detail)
        elif identified.suggested_action == InstructionAction.REINFORCE:
            return self._generate_reinforce_instruction(fs_detail)
        elif identified.suggested_action == InstructionAction.HINT:
            return self._generate_hint_instruction(fs_detail)
        else:
            return self._generate_none_instruction(fs_detail)

    def _generate_plant_instruction(self, fs) -> ForeshadowInstruction:
        """PLANT 指示を生成

        初回設置なので、より明確に描写する。
        subtlety_target は低め（より分かりやすく）。
        """
        return ForeshadowInstruction(
            foreshadowing_id=fs.id,
            action=InstructionAction.PLANT,
            allowed_expressions=fs.allowed_expressions or [],
            forbidden_expressions=fs.forbidden_keywords or [],
            note=f"伏線の初回設置。{fs.plant_hint or '自然に描写してください。'}",
            subtlety_target=self._calculate_subtlety(fs, InstructionAction.PLANT),
        )

    def _generate_reinforce_instruction(self, fs) -> ForeshadowInstruction:
        """REINFORCE 指示を生成

        強化なので、既存の伏線を思い出させる程度に。
        subtlety_target は中程度。
        """
        return ForeshadowInstruction(
            foreshadowing_id=fs.id,
            action=InstructionAction.REINFORCE,
            allowed_expressions=fs.allowed_expressions or [],
            forbidden_expressions=fs.forbidden_keywords or [],
            note=f"伏線の強化。{fs.reinforce_hint or '控えめに想起させてください。'}",
            subtlety_target=self._calculate_subtlety(fs, InstructionAction.REINFORCE),
        )

    def _generate_hint_instruction(self, fs) -> ForeshadowInstruction:
        """HINT 指示を生成

        軽いヒントなので、最も控えめに。
        subtlety_target は高め（より巧妙に）。
        """
        return ForeshadowInstruction(
            foreshadowing_id=fs.id,
            action=InstructionAction.HINT,
            allowed_expressions=fs.allowed_expressions or [],
            forbidden_expressions=fs.forbidden_keywords or [],
            note="非常に控えめなヒントのみ。気づかなくても問題ない程度に。",
            subtlety_target=self._calculate_subtlety(fs, InstructionAction.HINT),
        )

    def _generate_none_instruction(self, fs) -> ForeshadowInstruction:
        """NONE 指示を生成（触れない）"""
        return ForeshadowInstruction(
            foreshadowing_id=fs.id,
            action=InstructionAction.NONE,
            forbidden_expressions=fs.forbidden_keywords or [],
            note="この伏線には今回触れないでください。",
            subtlety_target=10,
        )

    def _calculate_subtlety(
        self,
        fs,
        action: InstructionAction,
    ) -> int:
        """subtlety_target を計算

        アクションタイプと伏線の設定に基づいて決定。

        Args:
            fs: 伏線詳細
            action: アクションタイプ

        Returns:
            1-10 の subtlety 値
        """
        # 基本値（アクション別）
        base = {
            InstructionAction.PLANT: 4,
            InstructionAction.REINFORCE: 6,
            InstructionAction.HINT: 8,
            InstructionAction.NONE: 10,
        }

        subtlety = base.get(action, 5)

        # 伏線の重要度で調整
        if hasattr(fs, 'importance') and fs.importance == 'critical':
            subtlety = max(1, subtlety - 2)  # より分かりやすく
        elif hasattr(fs, 'importance') and fs.importance == 'minor':
            subtlety = min(10, subtlety + 1)  # より控えめに

        return subtlety

    def determine_action(
        self,
        foreshadowing: dict,
        scene: SceneIdentifier,
    ) -> InstructionAction:
        """伏線のアクションを決定（プロトコル準拠）"""
        # IdentifiedForeshadowing を作成して判定
        identified_list = self.identifier.identify(scene)

        for item in identified_list:
            if item.foreshadowing_id == foreshadowing.get('id'):
                return item.suggested_action

        return InstructionAction.NONE

    def collect_forbidden_keywords(
        self,
        instructions: ForeshadowInstructions,
    ) -> list[str]:
        """禁止キーワードを収集（プロトコル準拠）"""
        return instructions.get_all_forbidden()
```

### subtlety_target の目安

| 値 | 説明 | 例 |
|----|------|-----|
| 1-3 | 明確 | 読者が気づくべき伏線 |
| 4-6 | 中程度 | 注意深い読者なら気づく |
| 7-9 | 控えめ | 後から振り返って気づく程度 |
| 10 | 最小限 | ほぼ気づかない |

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | generate() PLANT | 初回設置指示 |
| 2 | generate() REINFORCE | 強化指示 |
| 3 | generate() HINT | ヒント指示 |
| 4 | generate() 複合 | 複数伏線 |
| 5 | _calculate_subtlety() PLANT | 4前後 |
| 6 | _calculate_subtlety() HINT | 8前後 |
| 7 | collect_forbidden_keywords() | 収集確認 |
| 8 | determine_action() | アクション決定 |

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
