# 移行計画書

## 1. 概要

### 1.1 目的

既存の Novel-Athanor プロジェクトから Novel-Athanor-v2 への移行パスを定義する。

### 1.2 移行方針

| 方針 | 説明 |
|------|------|
| **後方互換** | 既存データは最小限の変更で移行可能 |
| **段階的** | 新機能はオプトイン |
| **非破壊的** | 既存ファイルを破壊しない |

---

## 2. データ移行

### 2.1 移行対象

| データ種別 | 移行方法 | 追加作業 |
|-----------|---------|---------|
| **episodes/** | そのまま移行 | なし |
| **characters/** | そのまま移行 | `ai_visibility` 追加（オプション） |
| **world/** | そのまま移行 | `ai_visibility` 追加（オプション） |
| **_plot/** | そのまま移行 | 伏線テーブル抽出（オプション） |
| **_summary/** | そのまま移行 | なし |
| **_style_guides/** | そのまま移行 | なし |
| **_style_profiles/** | そのまま移行 | なし |

### 2.2 新規ディレクトリ

移行時に作成される新規ディレクトリ:

```
vault/{作品名}/
├── _foreshadowing/     # 新規: 伏線管理
│   ├── registry.yaml
│   └── timeline.yaml
└── _ai_control/        # 新規: AI情報制御
    └── visibility.yaml
```

### 2.3 `## 隠し設定` の移行

**移行前** (Novel-Athanor):
```markdown
## 隠し設定
<!-- このセクションはAIから参照されない -->

- 実は主人公は王族の血筋
```

**移行後** (Auto-Novel-Athanor):
```yaml
# _ai_control/visibility.yaml
entities:
  characters:
    主人公:
      sections:
        隠し設定: 0  # Level 0 = 完全秘匿

      secrets:
        - id: SEC-001
          content: "主人公は王族の血筋"
          visibility: 0  # または 2 で暗示可能に
          forbidden_keywords:
            - "王族"
            - "血筋"
```

**互換性**: `## 隠し設定` セクションは引き続き機能する（Level 0 として扱われる）

### 2.4 移行期の優先順位ルール（Secure by Default）

移行期間中、`## 隠し設定` セクションと `visibility.yaml` の両方に同じ情報が存在する場合、**より制限の厳しい方を採用する**（min原則）。

```python
def resolve_visibility_conflict(hidden_section_level, visibility_yaml_level):
    """
    Secure by Default: 競合時は安全側に倒す
    """
    return min(hidden_section_level, visibility_yaml_level)

# 例:
# hidden_section: Level 0 (完全秘匿)
# visibility.yaml: Level 2 (内容認識)
# → 結果: Level 0 が適用される
```

**ルール詳細**:

| 状況 | 適用ルール |
|------|-----------|
| `## 隠し設定` のみ存在 | Level 0 として処理 |
| `visibility.yaml` のみ存在 | 指定されたレベルを使用 |
| **両方存在**（競合） | `min(両者)` を適用 |

**理由**: 意図しない情報漏洩は、意図しない情報隠蔽より深刻な問題を引き起こすため。

### 2.5 混在期間の制限

移行期間は**最大1ヶ月**または**1巻分**を上限とする。
管理コストが倍増するため、期限を設けて完全移行を促進する。

```yaml
# _ai_control/visibility.yaml
migration:
  status: "in_progress"
  started_at: "2026-01-24"
  deadline: "2026-02-24"  # 1ヶ月後
  files_migrated: 15
  files_remaining: 5
```

---

## 3. 移行スクリプト

### 3.1 自動移行

```bash
# 移行スクリプト実行
python scripts/migrate_to_v2.py vault/{作品名}

# 処理内容:
# 1. _foreshadowing/ ディレクトリ作成
# 2. _ai_control/ ディレクトリ作成
# 3. _plot/ から伏線テーブルを抽出（オプション）
# 4. visibility.yaml の雛形を生成
# 5. バックアップ作成
```

### 3.2 移行スクリプト詳細

```python
def migrate_to_v2(vault_path):
    work_name = os.path.basename(vault_path)

    # 1. バックアップ作成
    backup_path = create_backup(vault_path)
    print(f"バックアップ作成: {backup_path}")

    # 2. 新規ディレクトリ作成
    create_directory(f"{vault_path}/_foreshadowing")
    create_directory(f"{vault_path}/_ai_control")

    # 3. registry.yaml 雛形作成
    create_registry_template(f"{vault_path}/_foreshadowing/registry.yaml")

    # 4. visibility.yaml 雛形作成
    visibility = generate_visibility_template(vault_path)
    write_yaml(f"{vault_path}/_ai_control/visibility.yaml", visibility)

    # 5. 伏線テーブル抽出（オプション）
    if has_foreshadowing_table(f"{vault_path}/_plot/L1_overall.md"):
        foreshadowing = extract_foreshadowing_table(vault_path)
        update_registry(f"{vault_path}/_foreshadowing/registry.yaml", foreshadowing)

    # 6. 移行レポート生成
    report = generate_migration_report(vault_path)
    print(report)

    return report
```

### 3.3 可視性設定テンプレート生成

```python
def generate_visibility_template(vault_path):
    template = {
        'version': '1.0',
        'default_visibility': 3,
        'entities': {
            'characters': {},
            'world_settings': {}
        }
    }

    # キャラクターファイルをスキャン
    for char_file in glob(f"{vault_path}/characters/*.md"):
        char_name = parse_character_name(char_file)
        has_hidden = has_hidden_section(char_file)

        template['entities']['characters'][char_name] = {
            'sections': {
                '基本情報': 3,
                '現在の状態': 3,
                'フェーズ別記録': 3,
                '隠し設定': 0 if has_hidden else None
            },
            'secrets': []  # 手動で追加
        }

    return template
```

---

## 4. 段階的移行

### 4.1 Phase 1: 基本移行

```
目標: 既存機能を維持したまま新ディレクトリ構造を追加

作業内容:
1. 新規ディレクトリ作成
2. 雛形ファイル配置
3. 既存ファイルは変更なし

結果: 既存機能はそのまま動作
```

### 4.2 Phase 2: AI情報制御有効化

```
目標: AI情報制御を有効化

作業内容:
1. visibility.yaml に秘密を登録
2. forbidden_keywords を設定
3. Continuity Director が visibility.yaml を参照開始

結果: AI情報制御が有効になる
```

### 4.3 Phase 3: 伏線管理有効化

```
目標: 伏線管理を有効化

作業内容:
1. registry.yaml に伏線を登録
2. 既存の伏線テーブルから移行
3. Foreshadowing Agent が管理開始

結果: 伏線管理が有効になる
```

### 4.4 Phase 4: 品質管理有効化

```
目標: 品質管理を有効化

作業内容:
1. quality_thresholds.yaml を設定
2. Quality Agent を有効化

結果: 自動品質スコアリングが有効になる
```

---

## 5. 互換性マトリクス

### 5.1 ファイル形式互換性

| ファイル | Novel-Athanor | Auto-Novel-Athanor | 互換性 |
|---------|--------------|-------------------|--------|
| episodes/*.md | ✅ | ✅ | 完全互換 |
| characters/*.md | ✅ | ✅ + ai_visibility | 上位互換 |
| world/*.md | ✅ | ✅ + ai_visibility | 上位互換 |
| _plot/*.md | ✅ | ✅ | 完全互換 |
| _summary/*.md | ✅ | ✅ | 完全互換 |
| _foreshadowing/ | - | ✅ | 新規 |
| _ai_control/ | - | ✅ | 新規 |

### 5.2 コマンド互換性

| コマンド | Novel-Athanor | Auto-Novel-Athanor |
|---------|--------------|-------------------|
| /draft-scene | ✅ | ✅（拡張） |
| /check-consistency | ✅ | ✅（拡張） |
| /extract-character | ✅ | ✅ |
| /extract-summary | ✅ | ✅ |
| /foreshadowing-* | - | ✅（新規） |
| /quality-report | - | ✅（新規） |
| /athanor | - | ✅（新規）単一エントリーポイント |
| /resume | - | ✅（新規）中断再開 |
| /athanor rollback | - | ✅（新規）チェックポイント復旧 |
| /athanor switch | - | ✅（新規）作品切替 |

---

## 6. ロールバック

### 6.1 ロールバック手順

```bash
# 1. バックアップから復元
python scripts/rollback.py vault/{作品名} --backup {backup_path}

# または、移行ロールバックコマンド（推奨）
/athanor rollback

# 2. 新規ディレクトリ削除（オプション）
rm -rf vault/{作品名}/_foreshadowing
rm -rf vault/{作品名}/_ai_control
```

### 6.2 移行失敗時の自動バックアップ

移行スクリプトは、変更前に自動的に `.bak` ファイルを作成する。

```python
def migrate_file_with_backup(file_path):
    # 1. .bak ファイル作成
    backup_path = f"{file_path}.bak"
    shutil.copy(file_path, backup_path)

    try:
        # 2. 移行処理
        migrate_content(file_path)
    except Exception as e:
        # 3. 失敗時は自動復元
        shutil.copy(backup_path, file_path)
        raise MigrationError(f"移行失敗: {e}。元ファイルを復元しました。")
```

### 6.3 部分ロールバック

特定機能のみ無効化:

```yaml
# _ai_control/visibility.yaml
enabled: false  # AI情報制御を無効化
```

```yaml
# _foreshadowing/registry.yaml
enabled: false  # 伏線管理を無効化
```

### 6.4 Dry Run（移行テスト）

本番移行前に、別ディレクトリで移行をシミュレーションする。

```bash
# Dry Run 実行
python scripts/migrate_to_v2.py vault/{作品名} --dry-run --output /tmp/migration_test

# Before/After 差分確認
diff -r vault/{作品名} /tmp/migration_test

# LLM による自動検証（オプション）
python scripts/validate_migration.py /tmp/migration_test
```

---

## 7. 移行チェックリスト

### 7.1 移行前

- [ ] 作品データのバックアップ
- [ ] 現在の機能動作確認
- [ ] 移行スクリプトのテスト（別ディレクトリで）

### 7.2 移行中

- [ ] 移行スクリプト実行
- [ ] 新規ディレクトリ確認
- [ ] 雛形ファイル確認
- [ ] エラーログ確認

### 7.3 移行後

- [ ] 既存機能の動作確認
- [ ] 新機能の設定
- [ ] テスト執筆
- [ ] 問題があればロールバック

### 7.4 大規模作品の移行

100エピソード以上の大規模作品は、Volume（巻）単位で段階的に移行する。

```
vault/{作品名}/
├── episodes/
│   ├── Vol.1/        # 移行済み
│   │   ├── EP-001.md
│   │   └── ...
│   ├── Vol.2/        # 移行中
│   └── Vol.3/        # 未移行
├── _ai_control/
│   └── visibility.yaml
└── _foreshadowing/
    └── registry.yaml
```

**移行ステータス管理**:

```yaml
# _settings/migration_status.yaml
volumes:
  Vol.1:
    status: "completed"
    migrated_at: "2026-01-20"
  Vol.2:
    status: "in_progress"
    started_at: "2026-01-24"
  Vol.3:
    status: "pending"
```

---

## 8. トラブルシューティング

### 8.1 よくある問題

| 問題 | 原因 | 解決策 |
|------|------|--------|
| 移行スクリプトエラー | パス不正 | 絶対パスで指定 |
| visibility.yaml 読み込みエラー | YAML構文エラー | yamlint で検証 |
| 伏線が認識されない | registry.yaml 未設定 | registry.yaml に登録 |
| AI情報制御が効かない | enabled: false | enabled: true に変更 |

### 8.2 サポート

```
1. docs/specs/novel-generator-v2/ を参照
2. .claude/rules/ のガードレールを確認
3. GitHub Issues で報告
```
