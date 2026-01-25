"""Vault initialization utilities.

新規作品のディレクトリ構造とテンプレートファイルを作成する。
"""

from pathlib import Path


class VaultStructure:
    """Vault のディレクトリ構造定義."""

    # 必須ディレクトリ
    DIRECTORIES = [
        "episodes",
        "characters",
        "world",
        "_plot",
        "_summary",
        "_foreshadowing",
        "_ai_control",
        "_settings",
        "_style_guides",
        "_style_profiles",
    ]

    # サブディレクトリ
    SUBDIRECTORIES = [
        "_plot/L2_chapters",
        "_plot/L3_sequences",
        "_summary/L2_chapters",
        "_summary/L3_sequences",
    ]

    # テンプレートファイル
    TEMPLATE_FILES = {
        "_foreshadowing/registry.yaml": """# 伏線マスター登録簿
version: "1.0"
last_updated: null

foreshadowing: []
""",
        "_ai_control/visibility.yaml": """# AI情報制御設定
version: "1.0"

# デフォルト可視性（0: 秘匿, 1: 認識のみ, 2: 内容認識, 3: 使用可能）
default_visibility: 3

# エンティティ別可視性設定
entities:
  characters: {}
  world_settings: {}
  foreshadowing: {}
""",
        "_settings/pacing_profile.yaml": """# 作品ペース設定
version: "1.0"
profile: "medium"  # slow | medium | fast

# プリセット定義
presets:
  slow:
    payoff_reminder_episodes: 10
    long_silence_episodes: 20
    description: "ゆっくりとした伏線展開"

  medium:
    payoff_reminder_episodes: 5
    long_silence_episodes: 10
    description: "バランスの取れた伏線展開"

  fast:
    payoff_reminder_episodes: 3
    long_silence_episodes: 5
    description: "素早い伏線展開"

# カスタム設定（プリセットを上書き）
custom: null
""",
        "_settings/quality_thresholds.yaml": """# 品質閾値設定
version: "1.0"

thresholds:
  minimum_coherence: 0.6
  minimum_pacing: 0.6
  minimum_prose: 0.65
  minimum_character: 0.6
  minimum_style: 0.65
  minimum_overall: 0.65

warning_levels:
  critical: 0.4
  warning: 0.6
  good: 0.75

retry:
  enabled: false
  max_retries: 3
  conditional_retry:
    enabled: true
    auto_retry_conditions:
      - "forbidden_keyword"
      - "style_violation"
    user_judgment_conditions:
      - "low_excitement"
      - "pacing_issue"

learning_mode:
  enabled: true
  initial_threshold: 0.5
  target_threshold: 0.65
  increment_per_episode: 0.01
""",
    }


class VaultInitializer:
    """Vault の初期化を行うクラス."""

    def __init__(self, vault_path: Path, work_name: str) -> None:
        """VaultInitializer を初期化する.

        Args:
            vault_path: Vault のルートパス
            work_name: 作品名
        """
        self.vault_path = vault_path
        self.work_name = work_name

    def get_work_path(self) -> Path:
        """作品ディレクトリのパスを取得する.

        Returns:
            作品ディレクトリのパス
        """
        return self.vault_path / self.work_name

    def initialize(self) -> None:
        """Vault のディレクトリ構造とテンプレートファイルを作成する.

        既存のファイルは上書きしない（冪等性を保証）。
        """
        work_path = self.get_work_path()

        # 必須ディレクトリを作成
        for directory in VaultStructure.DIRECTORIES:
            dir_path = work_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)

        # サブディレクトリを作成
        for subdirectory in VaultStructure.SUBDIRECTORIES:
            subdir_path = work_path / subdirectory
            subdir_path.mkdir(parents=True, exist_ok=True)

        # テンプレートファイルを作成（既存ファイルは上書きしない）
        for file_path, content in VaultStructure.TEMPLATE_FILES.items():
            full_path = work_path / file_path
            if not full_path.exists():
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding="utf-8")
