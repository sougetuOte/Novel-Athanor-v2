# Novel-Athanor-v2 開発計画スナップショット

**作成日**: 2026-03-11
**目的**: LAM 4.1.0 移行作業中に元の開発コンテキストを保持し、移行後にスムーズに復帰するためのファイル。

---

## 現在の状態

- **ブランチ**: main (9599593)
- **フェーズ**: BUILDING (L4 Phase A-F 完了、Full Review 完了)
- **テスト**: 1101 passed (1 flaky excluded via @pytest.mark.slow) / ruff: 0 / mypy: 0
- **State file**: `.claude/states/novel-generator.json`

## 完了済み Phase

| Phase | 内容 | タスク数 | テスト数 | 完了日 |
|:-----:|------|:--------:|:--------:|--------|
| A | エージェント基盤 (models, config, CLI, context tool) | 6 | 58 | 2026-02-05 |
| B | Ghost Writer (prompt formatter + agent MD) | 4 | 13 | 2026-02-06 |
| C | Reviewer (formatter + parser + tool + agent MD) | 6 | 42 | 2026-02-06 |
| D | Quality Agent (formatter + parser + agent MD) | 4 | 22 | 2026-02-06 |
| E | Style Agent (formatter + parser + tool + text_stats) | 7 | 47 | 2026-02-06 |
| F | パイプライン統合 (/draft-scene + test vault) | 4 | - | 2026-03-07 |
| **FR** | Full Review #1 + #2 (Critical 5, Warning 30+修正) | - | - | 2026-03-07 |

## 未完了タスク

### Phase G: M1 運用マニュアル (次の開発ターゲット)

| ID | タスク | 成果物 |
|----|--------|--------|
| G-1 | M1-1: 新作開始ガイド | `docs/presentations/getting-started/` |
| G-2 | M1-2: 毎エピソード作成フロー | `docs/presentations/workflow-guide/` |
| G-3 | M1-3: L1設定変更ガイド | `docs/presentations/settings-guide/` |
| G-4 | M1-4: キャラ・世界観設定変更 | `docs/presentations/entity-guide/` |
| G-5 | M1-5: 伏線運用ガイド | `docs/presentations/foreshadowing-guide/` |
| G-6 | M1-6: トラブルシューティング | `docs/presentations/troubleshooting/` |
| G-7 | M1-7: AI可視性設定ガイド | `docs/presentations/visibility-guide/` |

### 未解決 Issue

| ID | 内容 | 対応時期 |
|----|------|----------|
| TC-6 | FR番号追記 | Phase G |
| SC-7 | Plot/Summary Repository DRY | Phase F/G の合間 |
| F-4 残り | /draft-scene 実行デバッグ・調整 | Phase G 前 |

## 主要参照ファイル

| 種別 | パス |
|------|------|
| Phase計画 | `docs/tasks/l4-phase-plan.md` |
| 設計書 | `docs/memos/2026-02-05-l4-core-design.md` |
| E2Eテスト手順 | `docs/memos/l4-e2e-test-plan.md` |
| M1目次 | `docs/memos/2026-02-05-m1-manual-outline.md` |
| テスト vault | `tests/fixtures/test_vault/` |
| 仕様書 | `docs/specs/novel-generator-v2/` |

## Full Review 教訓 (ルール化済み)

R-7〜R-12, S-2, A-5〜A-6 を `.claude/rules/building-checklist.md` と
`.claude/rules/audit-fix-policy.md` に反映済み。詳細は MEMORY.md 参照。

## 復帰手順

1. `git checkout main` でメインブランチに戻る
2. SESSION_STATE.md を確認
3. このファイルで全体像を把握
4. F-4 残り（/draft-scene デバッグ）or Phase G から再開
