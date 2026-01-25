# L3-5-2a: シーン→関連伏線特定

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-5-2a |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-5-1b, L2-3-1 |
| フェーズ | Phase E（伏線・Visibility 統合） |
| 参照仕様 | `docs/specs/novel-generator-v2/05_foreshadowing-system.md` |

## 概要

シーンに関連する伏線を特定するロジックを実装する。
L2 の ForeshadowingManager と連携し、該当シーンで触れるべき伏線を抽出。

## 受け入れ条件

- [ ] `ForeshadowingIdentifier` クラスが実装されている
- [ ] シーンで PLANT すべき伏線を特定できる
- [ ] シーンで REINFORCE すべき伏線を特定できる
- [ ] シーンで HINT すべき伏線を特定できる
- [ ] L2 ForeshadowingManager との連携
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/foreshadowing_identifier.py`（新規）
- テスト: `tests/core/context/test_foreshadowing_identifier.py`（新規）

### クラス定義

```python
from dataclasses import dataclass, field
from typing import Optional

from src.core.services.foreshadowing_manager import ForeshadowingManager
from .scene_identifier import SceneIdentifier
from .foreshadow_instruction import InstructionAction

@dataclass
class IdentifiedForeshadowing:
    """特定された伏線情報

    Attributes:
        foreshadowing_id: 伏線ID（FS-XXX形式）
        suggested_action: 推奨アクション
        status: 現在のステータス
        relevance_reason: 関連理由
    """
    foreshadowing_id: str
    suggested_action: InstructionAction
    status: str  # registered, planted, reinforced, revealed
    relevance_reason: str


class ForeshadowingIdentifier:
    """シーン→関連伏線特定

    シーンに関連する伏線を特定し、
    推奨アクションを決定する。

    Attributes:
        foreshadowing_manager: L2 の伏線マネージャー
    """

    def __init__(self, foreshadowing_manager: ForeshadowingManager):
        self.foreshadowing_manager = foreshadowing_manager

    def identify(
        self, scene: SceneIdentifier
    ) -> list[IdentifiedForeshadowing]:
        """シーンに関連する伏線を特定

        Args:
            scene: シーン識別子

        Returns:
            特定された伏線のリスト
        """
        results = []

        # 1. このシーンで PLANT すべき伏線
        plant_targets = self._find_plant_targets(scene)
        results.extend(plant_targets)

        # 2. このシーンで REINFORCE すべき伏線
        reinforce_targets = self._find_reinforce_targets(scene)
        results.extend(reinforce_targets)

        # 3. HINT 候補（planted だが reinforce/reveal ではない）
        hint_targets = self._find_hint_candidates(scene, results)
        results.extend(hint_targets)

        return results

    def _find_plant_targets(
        self, scene: SceneIdentifier
    ) -> list[IdentifiedForeshadowing]:
        """PLANT すべき伏線を検索

        plant_scene がこのシーンと一致する伏線を検索。
        """
        all_foreshadowings = self.foreshadowing_manager.list_all()
        results = []

        for fs in all_foreshadowings:
            if fs.status == "registered":
                if self._matches_scene(fs.plant_scene, scene):
                    results.append(IdentifiedForeshadowing(
                        foreshadowing_id=fs.id,
                        suggested_action=InstructionAction.PLANT,
                        status=fs.status,
                        relevance_reason=f"plant_scene が {scene.episode_id} に設定",
                    ))

        return results

    def _find_reinforce_targets(
        self, scene: SceneIdentifier
    ) -> list[IdentifiedForeshadowing]:
        """REINFORCE すべき伏線を検索

        reinforce_scenes にこのシーンが含まれる伏線を検索。
        """
        all_foreshadowings = self.foreshadowing_manager.list_all()
        results = []

        for fs in all_foreshadowings:
            if fs.status == "planted":
                if self._scene_in_list(scene, fs.reinforce_scenes):
                    results.append(IdentifiedForeshadowing(
                        foreshadowing_id=fs.id,
                        suggested_action=InstructionAction.REINFORCE,
                        status=fs.status,
                        relevance_reason=f"reinforce_scenes に {scene.episode_id} が含まれる",
                    ))

        return results

    def _find_hint_candidates(
        self,
        scene: SceneIdentifier,
        already_identified: list[IdentifiedForeshadowing],
    ) -> list[IdentifiedForeshadowing]:
        """HINT 候補を検索

        planted 状態で、まだ特定されていない伏線を
        HINT 候補として返す。
        """
        already_ids = {f.foreshadowing_id for f in already_identified}
        all_foreshadowings = self.foreshadowing_manager.list_all()
        results = []

        for fs in all_foreshadowings:
            if fs.id not in already_ids and fs.status == "planted":
                # 関連キャラクターがシーンに登場するかチェック
                if self._is_relevant_to_scene(fs, scene):
                    results.append(IdentifiedForeshadowing(
                        foreshadowing_id=fs.id,
                        suggested_action=InstructionAction.HINT,
                        status=fs.status,
                        relevance_reason="関連キャラクター登場のためHINT候補",
                    ))

        return results

    def _matches_scene(
        self, target_scene: Optional[str], scene: SceneIdentifier
    ) -> bool:
        """シーン指定が一致するか"""
        if not target_scene:
            return False
        return target_scene == scene.episode_id

    def _scene_in_list(
        self, scene: SceneIdentifier, scene_list: list[str]
    ) -> bool:
        """シーンがリストに含まれるか"""
        return scene.episode_id in scene_list

    def _is_relevant_to_scene(self, fs, scene: SceneIdentifier) -> bool:
        """伏線がシーンに関連するか

        関連キャラクターやタグベースで判定。
        TODO: より洗練された関連性判定
        """
        # 簡易実装: related_characters がシーンの characters と重複するか
        # 実際の実装では SceneResolver と連携
        return False  # デフォルトでは HINT しない
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | identify() PLANT検出 | plant_scene 一致 |
| 2 | identify() REINFORCE検出 | reinforce_scenes 含む |
| 3 | identify() HINT検出 | 関連キャラ登場 |
| 4 | identify() 複合 | PLANT + REINFORCE |
| 5 | identify() 該当なし | 空リスト |
| 6 | _matches_scene() True | 一致 |
| 7 | _matches_scene() False | 不一致 |
| 8 | _scene_in_list() | リスト内検索 |

## 伏線ライフサイクルとの対応

| ステータス | シーンとの関係 | アクション |
|-----------|--------------|-----------|
| registered | plant_scene 一致 | PLANT |
| planted | reinforce_scenes 含む | REINFORCE |
| planted | それ以外で関連 | HINT |
| revealed | - | NONE |

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
