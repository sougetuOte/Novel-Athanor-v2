# L3-7-1c: get_foreshadow_instructions() 実装

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-7-1c |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-7-1b, L3-5-2a〜L3-5-2c |
| フェーズ | Phase F（ContextBuilder ファサード） |
| 参照仕様 | `docs/specs/novel-generator-v2/05_foreshadowing-system.md` |

## 概要

ContextBuilder の `get_foreshadow_instructions()` メソッドを実装する。
シーンに対する伏線指示書を取得する専用メソッド。

## 受け入れ条件

- [ ] `get_foreshadow_instructions()` メソッドが機能する
- [ ] キャッシュ機能（同一シーンで再計算しない）
- [ ] プロンプト形式への変換メソッド
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/context_builder.py`（既存ファイルに追加）
- テスト: `tests/core/context/test_context_builder.py`（既存ファイルに追加）

### メソッド定義

```python
# ContextBuilder クラスに追加

class ContextBuilder:
    # ... 既存コード ...

    def __init__(self, ...):
        # ... 既存コード ...
        # キャッシュ用
        self._instruction_cache: dict[str, ForeshadowInstructions] = {}

    def get_foreshadow_instructions(
        self,
        scene: SceneIdentifier,
        use_cache: bool = True,
    ) -> ForeshadowInstructions:
        """伏線指示書を取得

        シーンに対する伏線指示書を生成・取得する。
        キャッシュが有効な場合、同一シーンでは再計算しない。

        Args:
            scene: シーン識別子
            use_cache: キャッシュを使用するか

        Returns:
            伏線指示書
        """
        if not self.instruction_generator:
            return ForeshadowInstructions()

        cache_key = self._make_cache_key(scene)

        # キャッシュチェック
        if use_cache and cache_key in self._instruction_cache:
            return self._instruction_cache[cache_key]

        # 生成
        instructions = self.instruction_generator.generate(scene)

        # キャッシュ保存
        if use_cache:
            self._instruction_cache[cache_key] = instructions

        return instructions

    def get_foreshadow_instructions_as_prompt(
        self,
        scene: SceneIdentifier,
    ) -> str:
        """伏線指示書をプロンプト形式で取得

        Ghost Writer に渡す形式に変換。

        Args:
            scene: シーン識別子

        Returns:
            プロンプト形式の指示書
        """
        instructions = self.get_foreshadow_instructions(scene)
        return self._format_instructions_for_prompt(instructions)

    def _format_instructions_for_prompt(
        self,
        instructions: ForeshadowInstructions,
    ) -> str:
        """指示書をプロンプト形式に変換"""
        if not instructions.instructions:
            return ""

        lines = ["## 伏線指示\n"]

        # アクティブな指示（PLANT/REINFORCE/HINT）
        active = instructions.get_active_instructions()
        if active:
            lines.append("### このシーンで扱う伏線\n")
            for inst in active:
                action_label = self._action_to_label(inst.action)
                lines.append(f"#### {inst.foreshadowing_id} [{action_label}]")
                lines.append(f"- 巧妙さ目標: {inst.subtlety_target}/10")

                if inst.note:
                    lines.append(f"- 指示: {inst.note}")

                if inst.allowed_expressions:
                    lines.append("- 使用可能な表現:")
                    for expr in inst.allowed_expressions:
                        lines.append(f"  - 「{expr}」")

                if inst.forbidden_expressions:
                    lines.append("- 禁止表現:")
                    for expr in inst.forbidden_expressions:
                        lines.append(f"  - 「{expr}」")

                lines.append("")

        # NONE 指示（触れてはいけない伏線）
        none_insts = [
            i for i in instructions.instructions
            if i.action == InstructionAction.NONE
        ]
        if none_insts:
            lines.append("### 触れてはいけない伏線\n")
            for inst in none_insts:
                lines.append(f"- {inst.foreshadowing_id}")
                if inst.forbidden_expressions:
                    lines.append(f"  （禁止: {', '.join(inst.forbidden_expressions)}）")
            lines.append("")

        return "\n".join(lines)

    def _action_to_label(self, action: InstructionAction) -> str:
        """アクションをラベルに変換"""
        labels = {
            InstructionAction.PLANT: "初回設置",
            InstructionAction.REINFORCE: "強化",
            InstructionAction.HINT: "ヒント",
            InstructionAction.NONE: "触れない",
        }
        return labels.get(action, "不明")

    def _make_cache_key(self, scene: SceneIdentifier) -> str:
        """キャッシュキーを生成"""
        return f"{scene.episode_id}:{scene.chapter_id}:{scene.current_phase}"

    def clear_instruction_cache(self) -> None:
        """指示書キャッシュをクリア"""
        self._instruction_cache.clear()

    def get_active_foreshadowings(
        self,
        scene: SceneIdentifier,
    ) -> list[str]:
        """アクティブな伏線IDリストを取得

        このシーンで何らかのアクション（PLANT/REINFORCE/HINT）を
        行う伏線のIDリストを返す。

        Args:
            scene: シーン識別子

        Returns:
            伏線IDリスト
        """
        instructions = self.get_foreshadow_instructions(scene)
        return [
            inst.foreshadowing_id
            for inst in instructions.get_active_instructions()
        ]

    def get_foreshadowing_summary(
        self,
        scene: SceneIdentifier,
    ) -> dict[str, int]:
        """伏線サマリを取得

        アクション別の伏線数を返す。

        Args:
            scene: シーン識別子

        Returns:
            アクション → 件数 のマップ
        """
        instructions = self.get_foreshadow_instructions(scene)
        summary = {
            "PLANT": 0,
            "REINFORCE": 0,
            "HINT": 0,
            "NONE": 0,
        }

        for inst in instructions.instructions:
            key = inst.action.name
            summary[key] = summary.get(key, 0) + 1

        return summary
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | get_foreshadow_instructions() 正常 | 指示書取得 |
| 2 | get_foreshadow_instructions() キャッシュヒット | 再計算しない |
| 3 | get_foreshadow_instructions() キャッシュ無効 | 再計算する |
| 4 | get_foreshadow_instructions() 伏線無効時 | 空の指示書 |
| 5 | get_foreshadow_instructions_as_prompt() | プロンプト形式 |
| 6 | _format_instructions_for_prompt() PLANT | 初回設置形式 |
| 7 | _format_instructions_for_prompt() NONE | 禁止形式 |
| 8 | clear_instruction_cache() | キャッシュクリア |
| 9 | get_active_foreshadowings() | IDリスト |
| 10 | get_foreshadowing_summary() | サマリ |

### プロンプト出力例

```markdown
## 伏線指示

### このシーンで扱う伏線

#### FS-001 [初回設置]
- 巧妙さ目標: 4/10
- 指示: 王族の血筋を匂わせる
- 使用可能な表現:
  - 「気高い雰囲気」
  - 「見覚えのある光」
- 禁止表現:
  - 「王族」
  - 「血筋」

#### FS-002 [強化]
- 巧妙さ目標: 6/10
- 指示: 控えめに想起させてください

### 触れてはいけない伏線

- FS-003
  （禁止: 最終兵器, 世界の終末）
```

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
