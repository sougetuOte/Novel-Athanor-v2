# L2 レイヤー実装ガイド

**作成日**: 2026-01-25
**前提**: L0/L1 完了済み（`implementation-backlog.md` 参照）
**フェーズ**: BUILDING
**対象仕様**: `docs/specs/novel-generator-v2/04_ai-information-control.md`

---

## 1. 概要

L2（AI情報制御レイヤー）の実装ガイド。
L1（データレイヤー）で定義したモデルを活用し、可視性制御とフィルタリング機能を実装する。

---

## 2. 実装範囲（P1 タスクのみ）

### スコープ内

| ID | タスク | 依存 | ステータス |
|----|--------|------|-----------|
| L2-1-1 | VisibilityLevel 列挙型 | - | ✅ 完了（AIVisibilityLevel） |
| L2-1-3 | HTMLコメント `<!-- ai_visibility: N -->` パーサー | - | ✅ |
| L2-1-2 | セクション単位可視性判定 | L2-1-3 | ✅ |
| L2-1-4 | 可視性フィルタリング関数 | L2-1-2 | ✅ |
| L2-1-5 | Visibility Controller テスト | L2-1-4 | ✅ |
| L2-2-1 | 禁止キーワードマッチャー | - | ✅ |
| L2-2-4 | Expression Filter テスト | L2-2-1 | ✅ |
| L2-3-1 | 伏線状態遷移ロジック | L1-2-6 | ✅ |
| L2-3-2 | Subtlety レベル管理 | L2-3-1 | ✅ |
| L2-3-3 | 伏線→可視性レベル自動マッピング | L2-3-1 | ✅ |
| L2-3-6 | Foreshadowing Manager テスト | L2-3-3 | ✅ |

### スコープ外（P2/P3 - 今回実装しない）

- L2-2-2: 類似度チェック（Embedding）
- L2-2-3: 許可表現リスト管理
- L2-3-4: 伏線タイムライン追跡
- L2-3-5: 回収期限アラート

---

## 3. 実装順序

```
並列グループ A:
├── L2-1-3 → L2-1-2 → L2-1-4 → L2-1-5 (Visibility Controller)
└── L2-2-1 → L2-2-4 (Expression Filter)

↓ 完了後

直列:
L2-3-1 → L2-3-2 → L2-3-3 → L2-3-6 (Foreshadowing Manager)
```

---

## 4. 各タスクの詳細

### 4.1 L2-1-3: HTMLコメントパーサー

**ファイル**: `src/core/parsers/visibility_comment.py`

**入力**:
```markdown
## 隠し設定
<!-- ai_visibility: 0 -->
- 秘密の内容...
```

**出力**:
```python
VisibilityMarker(level=0, line_number=2)
```

**テストケース**:
- 正常: `<!-- ai_visibility: 0 -->` → level=0
- 正常: `<!-- ai_visibility: 3 -->` → level=3
- 異常: `<!-- ai_visibility: 5 -->` → ValueError
- 異常: `<!-- ai_visibility: abc -->` → ValueError
- 空白許容: `<!--  ai_visibility:  2  -->` → level=2

---

### 4.2 L2-1-2/L2-1-4: 可視性フィルタリング

**ファイル**: `src/core/services/visibility_controller.py`

**主要関数**:
```python
def get_filtered_context(
    content: str,
    visibility_config: VisibilityConfig,
    current_level: AIVisibilityLevel = AIVisibilityLevel.USE
) -> FilteredContext
```

**FilteredContext 構造**:
```python
@dataclass
class FilteredContext:
    content: str           # フィルタ済みコンテンツ
    hints: list[str]       # Level 1/2 用のヒント
    forbidden_keywords: list[str]  # 禁止キーワードリスト
    excluded_sections: list[str]   # 除外されたセクション名
```

---

### 4.3 L2-2-1: 禁止キーワードマッチャー

**ファイル**: `src/core/services/expression_filter.py`

**主要関数**:
```python
def check_forbidden_keywords(
    text: str,
    forbidden_keywords: list[str]
) -> list[KeywordViolation]

@dataclass
class KeywordViolation:
    keyword: str
    positions: list[int]
    context: str  # 前後20文字
```

---

### 4.4 L2-3-1/L2-3-2/L2-3-3: Foreshadowing Manager

**ファイル**: `src/core/services/foreshadowing_manager.py`

**主要機能**:

1. **状態遷移**:
   ```
   registered → planted → reinforced → revealed
                    ↑         ↓
                    ←─────────
   ```

2. **Subtlety → Visibility マッピング**:
   | Subtlety | 推奨 Visibility |
   |----------|-----------------|
   | 1-3 | 2 (KNOW) |
   | 4-7 | 2 (KNOW) |
   | 8-10 | 1 (AWARE) |

3. **状態 → Visibility マッピング**:
   | Status | 推奨 Visibility |
   |--------|-----------------|
   | registered | 0 (HIDDEN) |
   | planted | 2 (KNOW) |
   | reinforced | 2 (KNOW) |
   | revealed | 3 (USE) |

---

## 5. ディレクトリ構成

### 既存構造（L0/L1 で作成済み）

```
src/core/
├── models/          # L1-2 で作成
│   ├── ai_visibility.py   # AIVisibilityLevel, AIVisibility
│   ├── foreshadowing.py   # Foreshadowing, ForeshadowingStatus
│   └── secret.py          # Secret
├── parsers/         # L1-1 で作成
│   ├── frontmatter.py
│   ├── markdown.py
│   └── obsidian_link.py
├── repositories/    # L1-4 で作成
│   └── foreshadowing.py
└── vault/           # L1-3 で作成
```

### L2 で追加する構造

```
src/core/
├── parsers/
│   └── visibility_comment.py   # L2-1-3 (新規)
└── services/                    # L2 で新規作成
    ├── __init__.py
    ├── visibility_controller.py  # L2-1-2, L2-1-4
    ├── expression_filter.py      # L2-2-1
    └── foreshadowing_manager.py  # L2-3-1, L2-3-2, L2-3-3

tests/core/
├── parsers/
│   └── test_visibility_comment.py  # 新規
└── services/                        # 新規
    ├── __init__.py
    ├── test_visibility_controller.py
    ├── test_expression_filter.py
    └── test_foreshadowing_manager.py
```

### 初期セットアップ手順

```bash
# services ディレクトリ作成
mkdir -p src/core/services tests/core/services
touch src/core/services/__init__.py tests/core/services/__init__.py
```

---

## 6. 終了条件

### 必須条件（全て満たすこと）

- [ ] 全 P1 タスク（11件中10件、L2-1-1は完了済み）の実装完了
- [ ] 全テストがパス
- [ ] mypy エラー 0 件
- [ ] ruff 警告 0 件
- [ ] 新規コードのテストカバレッジ 95% 以上

### 成果物チェックリスト

- [ ] `src/core/parsers/visibility_comment.py` 作成
- [ ] `src/core/services/visibility_controller.py` 作成
- [ ] `src/core/services/expression_filter.py` 作成
- [ ] `src/core/services/foreshadowing_manager.py` 作成
- [ ] 対応テストファイル 4 件作成
- [ ] バックログ更新（完了タスクを ✅ に）

### 品質基準

- 仕様書 `04_ai-information-control.md` との整合性
- L1 モデル（AIVisibilityLevel, Secret, Foreshadowing）の正しい活用
- 既存テストが壊れていないこと

---

## 7. 実装ルール

### TDD サイクル厳守

1. **Red**: 失敗するテストを先に書く
2. **Green**: テストを通す最小限のコード
3. **Refactor**: 設計改善

### 禁止事項

- テストなしでの本実装
- スコープ外タスクへの着手
- 仕様書にない機能の追加

### 疑問発生時

実装中に仕様の曖昧さや設計上の疑問が発生した場合:
1. **即座に作業を中断**
2. **ユーザーに相談**
3. **承認を得てから再開**

---

## 8. 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-25 | 初版作成 |
| 2026-01-25 | 全 P1 タスク完了（10/10） |
