# L1-2-10: モデルバリデーションテスト

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L1-2-10 |
| 優先度 | P0 |
| ステータス | 🔲 backlog |
| 依存タスク | L1-2-1, L1-2-2, L1-2-3, L1-2-4, L1-2-5 |
| 参照仕様 | `docs/internal/02_DEVELOPMENT_FLOW.md` Phase 2 |

## 概要

全データモデルの包括的なバリデーションテストを作成する。

## 受け入れ条件

- [ ] 全モデルの正常系テストが PASS する
- [ ] 全モデルの異常系テストが PASS する
- [ ] モデル間の関連テストが存在する
- [ ] カバレッジ 90% 以上

## テストケース

### Episode

| ケース | 入力 | 期待結果 |
|--------|------|---------|
| 正常 | 有効なデータ | インスタンス生成 |
| episode_number < 1 | 0 | ValidationError |
| 無効な status | "unknown" | ValidationError |

### Character / WorldSetting

| ケース | 入力 | 期待結果 |
|--------|------|---------|
| 正常（フェーズあり） | phases + current_phase | インスタンス生成 |
| current_phase が phases に存在しない | 不一致 | 警告 or エラー |
| ai_visibility 範囲外 | level=5 | ValidationError |

### Plot / Summary

| ケース | 入力 | 期待結果 |
|--------|------|---------|
| 正常（L1） | 有効な PlotL1 | インスタンス生成 |
| 階層不整合 | L2 に存在しない章番号 | 警告 |

### 統合テスト

| ケース | 説明 |
|--------|------|
| 相互参照 | Episode から Character への参照が解決可能 |
| JSON 往復 | model -> JSON -> model が等価 |
| YAML 往復 | model -> YAML -> model が等価 |

### ファイル配置

- `tests/core/models/test_episode.py`
- `tests/core/models/test_character.py`
- `tests/core/models/test_world_setting.py`
- `tests/core/models/test_plot.py`
- `tests/core/models/test_summary.py`
- `tests/core/models/test_integration.py`

## 実装メモ

（実装時に記録）

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
