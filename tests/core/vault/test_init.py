"""Tests for Vault initialization."""

from pathlib import Path

from src.core.vault.init import VaultInitializer, VaultStructure


class TestVaultStructure:
    """VaultStructure 定数のテスト."""

    def test_required_directories(self) -> None:
        """必須ディレクトリが定義されている."""
        assert "episodes" in VaultStructure.DIRECTORIES
        assert "characters" in VaultStructure.DIRECTORIES
        assert "world" in VaultStructure.DIRECTORIES
        assert "_plot" in VaultStructure.DIRECTORIES
        assert "_summary" in VaultStructure.DIRECTORIES
        assert "_foreshadowing" in VaultStructure.DIRECTORIES
        assert "_ai_control" in VaultStructure.DIRECTORIES
        assert "_settings" in VaultStructure.DIRECTORIES

    def test_required_subdirectories(self) -> None:
        """サブディレクトリが定義されている."""
        assert "_plot/L2_chapters" in VaultStructure.SUBDIRECTORIES
        assert "_plot/L3_sequences" in VaultStructure.SUBDIRECTORIES
        assert "_summary/L2_chapters" in VaultStructure.SUBDIRECTORIES
        assert "_summary/L3_sequences" in VaultStructure.SUBDIRECTORIES

    def test_template_files(self) -> None:
        """テンプレートファイルが定義されている."""
        assert "_foreshadowing/registry.yaml" in VaultStructure.TEMPLATE_FILES
        assert "_ai_control/visibility.yaml" in VaultStructure.TEMPLATE_FILES


class TestVaultInitializer:
    """VaultInitializer クラスのテスト."""

    def test_init(self, tmp_path: Path) -> None:
        """VaultInitializer を初期化できる."""
        vault_path = tmp_path / "test_vault"
        initializer = VaultInitializer(vault_path, "テスト作品")
        assert initializer.vault_path == vault_path
        assert initializer.work_name == "テスト作品"

    def test_initialize_creates_directories(self, tmp_path: Path) -> None:
        """initialize() がディレクトリを作成する."""
        vault_path = tmp_path / "test_vault"
        initializer = VaultInitializer(vault_path, "テスト作品")
        initializer.initialize()

        # 作品ディレクトリが作成される
        work_path = vault_path / "テスト作品"
        assert work_path.exists()

        # 必須ディレクトリが作成される
        assert (work_path / "episodes").exists()
        assert (work_path / "characters").exists()
        assert (work_path / "world").exists()
        assert (work_path / "_plot").exists()
        assert (work_path / "_summary").exists()
        assert (work_path / "_foreshadowing").exists()
        assert (work_path / "_ai_control").exists()
        assert (work_path / "_settings").exists()

    def test_initialize_creates_subdirectories(self, tmp_path: Path) -> None:
        """initialize() がサブディレクトリを作成する."""
        vault_path = tmp_path / "test_vault"
        initializer = VaultInitializer(vault_path, "テスト作品")
        initializer.initialize()

        work_path = vault_path / "テスト作品"
        assert (work_path / "_plot" / "L2_chapters").exists()
        assert (work_path / "_plot" / "L3_sequences").exists()
        assert (work_path / "_summary" / "L2_chapters").exists()
        assert (work_path / "_summary" / "L3_sequences").exists()

    def test_initialize_creates_template_files(self, tmp_path: Path) -> None:
        """initialize() がテンプレートファイルを作成する."""
        vault_path = tmp_path / "test_vault"
        initializer = VaultInitializer(vault_path, "テスト作品")
        initializer.initialize()

        work_path = vault_path / "テスト作品"
        assert (work_path / "_foreshadowing" / "registry.yaml").exists()
        assert (work_path / "_ai_control" / "visibility.yaml").exists()

    def test_initialize_idempotent(self, tmp_path: Path) -> None:
        """initialize() は冪等である（複数回実行しても問題ない）."""
        vault_path = tmp_path / "test_vault"
        initializer = VaultInitializer(vault_path, "テスト作品")

        # 2回実行
        initializer.initialize()
        initializer.initialize()

        work_path = vault_path / "テスト作品"
        assert (work_path / "episodes").exists()

    def test_initialize_preserves_existing_files(self, tmp_path: Path) -> None:
        """initialize() は既存ファイルを上書きしない."""
        vault_path = tmp_path / "test_vault"
        initializer = VaultInitializer(vault_path, "テスト作品")
        initializer.initialize()

        # 既存ファイルを変更
        registry_path = vault_path / "テスト作品" / "_foreshadowing" / "registry.yaml"
        registry_path.write_text("# Custom content\nforeshadowing: []")

        # 再度 initialize
        initializer.initialize()

        # ファイル内容が保持される
        content = registry_path.read_text()
        assert "# Custom content" in content

    def test_get_work_path(self, tmp_path: Path) -> None:
        """get_work_path() が作品パスを返す."""
        vault_path = tmp_path / "test_vault"
        initializer = VaultInitializer(vault_path, "テスト作品")
        assert initializer.get_work_path() == vault_path / "テスト作品"

    def test_template_file_content_valid_yaml(self, tmp_path: Path) -> None:
        """テンプレートファイルの内容が有効な YAML である."""
        import yaml

        vault_path = tmp_path / "test_vault"
        initializer = VaultInitializer(vault_path, "テスト作品")
        initializer.initialize()

        work_path = vault_path / "テスト作品"

        # registry.yaml
        registry_content = (work_path / "_foreshadowing" / "registry.yaml").read_text(
            encoding="utf-8"
        )
        registry_data = yaml.safe_load(registry_content)
        assert "version" in registry_data
        assert "foreshadowing" in registry_data

        # visibility.yaml
        visibility_content = (work_path / "_ai_control" / "visibility.yaml").read_text(
            encoding="utf-8"
        )
        visibility_data = yaml.safe_load(visibility_content)
        assert "version" in visibility_data
        assert "default_visibility" in visibility_data
