# L1-3-2: ファイルパス解決ユーティリティ

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L1-3-2 |
| 優先度 | P0 |
| ステータス | 🔲 backlog |
| 依存タスク | L0-1-2 |
| 参照仕様 | `docs/specs/novel-generator-v2/02_architecture.md` Section 2.5, `03_data-model.md` Section 5 |

## 概要

Vault 内のファイルパスを解決するユーティリティを実装する。

## 受け入れ条件

- [ ] `VaultPathResolver` クラスが存在する
- [ ] vault ルートからの相対パスを解決できる
- [ ] エンティティ種別ごとのパス規則を適用できる
- [ ] パスの正規化ができる
- [ ] ユニットテストが存在する

## 技術的詳細

### クラス定義

```python
from pathlib import Path

class VaultPathResolver:
    def __init__(self, vault_root: Path):
        self.vault_root = vault_root

    def resolve_episode(self, episode_number: int) -> Path:
        """エピソードファイルのパスを解決"""
        return self.vault_root / "episodes" / f"ep_{episode_number:04d}.md"

    def resolve_character(self, name: str) -> Path:
        """キャラクターファイルのパスを解決"""
        return self.vault_root / "characters" / f"{name}.md"

    def resolve_world_setting(self, name: str) -> Path:
        """世界観設定ファイルのパスを解決"""
        return self.vault_root / "world" / f"{name}.md"

    def resolve_plot(self, level: str, **kwargs) -> Path:
        """プロットファイルのパスを解決"""
        ...

    def resolve_foreshadowing(self) -> Path:
        """伏線レジストリのパスを解決"""
        return self.vault_root / "_foreshadowing" / "registry.yaml"

    def exists(self, path: Path) -> bool:
        """ファイルが存在するか確認"""
        return (self.vault_root / path).exists()
```

### パス規則（仕様書より）

| エンティティ | パス形式 |
|-------------|---------|
| Episode | `episodes/ep_{XXXX}.md` |
| Character | `characters/{name}.md` |
| WorldSetting | `world/{name}.md` |
| Plot L1 | `_plot/L1_overall.md` |
| Plot L2 | `_plot/L2_chapters/{章番号}_{章名}.md` |
| Plot L3 | `_plot/L3_sequences/{章番号}_{章名}/seq_{番号}.md` |
| Foreshadowing | `_foreshadowing/registry.yaml` |

### ファイル配置

- `src/core/vault/path_resolver.py`
- `tests/core/vault/test_path_resolver.py`

## 実装メモ

（実装時に記録）

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
