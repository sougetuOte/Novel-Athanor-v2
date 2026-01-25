# レビュー依頼: L3 タスクドキュメント整合性確認

## Meta

| 項目 | 値 |
|------|-----|
| Session ID | 2026-01-26_001 |
| 日時 | 2026-01-26 |
| 依頼者 | Camel (Claude Opus 4.5) |
| 依頼種別 | ドキュメントレビュー（整合性確認） |

---

## 1. 背景

L3（Context Builder Layer）の実装準備として、全フェーズ（A〜G）のタスクドキュメントを作成しました。
Phase A は実装完了（119テストパス）、Phase B〜G はドキュメントのみ作成済みです。

**重要**: このレビューは実装コードではなく、**タスクドキュメントの整合性**を確認するためのものです。

---

## 2. レビュー対象

### 2.1 タスクドキュメント一覧

```
docs/tasks/l3/
├── implementation-guide.md          # 実装ガイド（マスタードキュメント）
│
├── # Phase A（実装完了）
├── L3-1-1a_scene-identifier.md
├── L3-2-1a_lazy-loader-protocol.md
├── L3-3-1a_phase-filter-protocol.md
├── L3-4-1a_filtered-context.md
├── L3-5-1a_foreshadow-instruction.md
├── L3-6-1a_visibility-aware-context.md
├── L3-7-1a_context-builder-facade.md
│
├── # Phase B（プロトコル定義）
├── L3-2-1b_lazy-loaded-content.md
├── L3-4-1b_context-integrator-protocol.md
├── L3-5-1b_instruction-generator-protocol.md
│
├── # Phase C（個別機能実装）
├── L3-1-1b_scene-file-resolver.md
├── L3-1-1c_character-identifier.md
├── L3-1-1d_world-setting-identifier.md
├── L3-1-1e_scene-resolver-test.md
├── L3-2-1c_lazy-loader-impl.md
├── L3-2-1d_graceful-degradation.md
├── L3-2-1e_lazy-loader-test.md
├── L3-3-1b_character-phase-filter.md
├── L3-3-1c_world-setting-phase-filter.md
├── L3-3-1d_phase-filter-test.md
│
├── # Phase D（コンテキスト収集）
├── L3-4-2a_plot-collector.md
├── L3-4-2b_summary-collector.md
├── L3-4-2c_character-collector.md
├── L3-4-2d_world-setting-collector.md
├── L3-4-2e_style-guide-collector.md
├── L3-4-3a_context-integrator-test.md
│
├── # Phase E（伏線・Visibility統合）
├── L3-5-2a_scene-foreshadowing-identifier.md
├── L3-5-2b_instruction-generator-impl.md
├── L3-5-2c_forbidden-keyword-collector.md
├── L3-5-2d_allowed-expression-collector.md  # P2
├── L3-5-3a_foreshadow-instruction-test.md
├── L3-6-1b_visibility-filtering-integration.md
├── L3-6-1c_hint-collection.md
├── L3-6-1d_visibility-integration-test.md
│
└── # Phase F/G（ファサード・統合テスト）
    ├── L3-7-1b_build-context-impl.md
    ├── L3-7-1c_get-foreshadow-instructions-impl.md
    ├── L3-7-1d_get-forbidden-keywords-impl.md
    └── L3-7-2a_context-builder-test.md
```

### 2.2 参照すべき仕様書

| 仕様書 | 確認観点 |
|--------|----------|
| `docs/specs/novel-generator-v2/00_overview.md` | 全体アーキテクチャ |
| `docs/specs/novel-generator-v2/02_architecture.md` | L3 の位置づけ（Section 2.4） |
| `docs/specs/novel-generator-v2/04_ai-information-control.md` | AI可視性システム |
| `docs/specs/novel-generator-v2/05_foreshadowing-system.md` | 伏線管理システム |
| `docs/specs/novel-generator-v2/08_agent-design.md` | Context Builder（Section 3） |

---

## 3. レビュー観点

### 3.1 全体整合性（最重要）

- [ ] **implementation-guide.md** と各タスクドキュメントの整合性
- [ ] タスク間の**依存関係**が正しいか
- [ ] Phase 間の**順序**が論理的か
- [ ] **仕様書との整合性**（特に 02_architecture.md, 08_agent-design.md）

### 3.2 タスク定義の品質

- [ ] 各タスクの**受け入れ条件**が明確か
- [ ] **技術的詳細**（クラス定義）が仕様書と一致するか
- [ ] **テストケース**が受け入れ条件をカバーしているか
- [ ] **ファイル配置**が一貫しているか

### 3.3 L2 との連携

- [ ] L2 サービス（VisibilityController, ExpressionFilter, ForeshadowingManager）の使用方法が正しいか
- [ ] L2 モデル（AIVisibilityLevel, Foreshadowing）の参照が正しいか
- [ ] 依存関係の方向性（L3 → L2 への一方向依存）

### 3.4 潜在的な問題

- [ ] 循環依存の可能性
- [ ] 仕様書に記載のない独自拡張
- [ ] テスト困難な設計

---

## 4. 特に確認してほしい点

### 4.1 ForeshadowingIdentifier（L3-5-2a）

伏線特定ロジックが以下を正しく処理できる設計になっているか：
- `plant_scene` による PLANT 判定
- `reinforce_scenes` による REINFORCE 判定
- 関連キャラクター登場時の HINT 判定

### 4.2 ForbiddenKeywordCollector（L3-5-2c）

禁止キーワードの収集ソースが仕様と一致しているか：
1. 伏線の `forbidden_expressions`
2. AI可視性設定の `global_forbidden_keywords`
3. グローバル禁止リスト（`_ai_control/forbidden_keywords.txt`）
4. L2 ExpressionFilter との連携

### 4.3 VisibilityFilteringService（L3-6-1b）

L2 VisibilityController との連携方法が適切か：
- `get_character_visibility()` の呼び出し
- `get_setting_visibility()` の呼び出し
- フィルタリング結果の反映方法

### 4.4 ContextBuilder（L3-7-1b〜L3-7-2a）

ファサードパターンの設計が適切か：
- 依存注入の方法
- エラーハンドリング（Graceful Degradation）
- キャッシュ戦略

---

## 5. 実施手順

1. **仕様書を先に確認**
   ```
   docs/specs/novel-generator-v2/02_architecture.md  # Section 2.4
   docs/specs/novel-generator-v2/08_agent-design.md  # Section 3
   ```

2. **implementation-guide.md を確認**
   ```
   docs/tasks/l3/implementation-guide.md
   ```

3. **各フェーズのタスクドキュメントを順に確認**
   - Phase B → C → D → E → F/G の順

4. **整合性の問題を報告**

---

## 6. 回答フォーマット

```markdown
# レビュー回答: L3 タスクドキュメント整合性確認

## Meta
| 項目 | 値 |
|------|-----|
| Session ID | 2026-01-26_001 |
| 日時 | YYYY-MM-DD |
| レビュアー | Antigravity |
| 判定 | [A/B/C/D] |

## 1. 全体整合性
### 1.1 implementation-guide.md との整合性
...

### 1.2 仕様書との整合性
...

## 2. タスク定義の品質
### 2.1 良い点
...

### 2.2 改善が必要な点
...

## 3. L2 連携の確認
...

## 4. 問題点・指摘事項

### [重要度: Critical/Warning/Info]
| No. | 対象ファイル | 問題内容 | 推奨対応 |
|-----|-------------|---------|---------|
| 1 | ... | ... | ... |

## 5. 総合評価
...

## 6. 推奨事項
...
```

---

## 7. 補足情報

### 7.1 Phase A 実装状況

Phase A（基盤データクラス・プロトコル）は実装完了済み：

| ファイル | テスト数 | ステータス |
|----------|---------|-----------|
| `scene_identifier.py` | 9件 | ✅ |
| `lazy_loader.py` | 26件 | ✅ |
| `phase_filter.py` | 8件 | ✅ |
| `filtered_context.py` | 16件 | ✅ |
| `foreshadow_instruction.py` | 33件 | ✅ |
| `visibility_context.py` | 27件 | ✅ |

合計: 119テスト全パス

### 7.2 P2 タスクについて

`L3-5-2d_allowed-expression-collector.md` は P2（優先度低）として定義。
P1 完了後に実装予定。レビュー対象には含めるが、Critical な指摘は不要。

---

## 8. 参照ファイル一覧

```
# 仕様書（必読）
docs/specs/novel-generator-v2/00_overview.md
docs/specs/novel-generator-v2/02_architecture.md
docs/specs/novel-generator-v2/04_ai-information-control.md
docs/specs/novel-generator-v2/05_foreshadowing-system.md
docs/specs/novel-generator-v2/08_agent-design.md

# タスクドキュメント（レビュー対象）
docs/tasks/l3/implementation-guide.md
docs/tasks/l3/L3-*.md

# L2 実装（連携確認用）
src/core/services/visibility_controller.py
src/core/services/expression_filter.py
src/core/services/foreshadowing_manager.py
src/core/models/ai_visibility.py

# L3 Phase A 実装（参考）
src/core/context/*.py
tests/core/context/test_*.py
```
