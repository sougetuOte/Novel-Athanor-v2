"""Tests for VaultPathResolver."""

from pathlib import Path

from src.core.vault.path_resolver import VaultPathResolver


class TestVaultPathResolver:
    """VaultPathResolver のテスト."""

    def test_init(self) -> None:
        """初期化できる."""
        resolver = VaultPathResolver(Path("/vault"))

        assert resolver.vault_root == Path("/vault")

    def test_resolve_episode(self) -> None:
        """エピソードパスを解決できる."""
        resolver = VaultPathResolver(Path("/vault"))

        path = resolver.resolve_episode(1)

        assert path == Path("/vault/episodes/ep_0001.md")

    def test_resolve_episode_large_number(self) -> None:
        """大きなエピソード番号も正しくフォーマットされる."""
        resolver = VaultPathResolver(Path("/vault"))

        path = resolver.resolve_episode(1234)

        assert path == Path("/vault/episodes/ep_1234.md")

    def test_resolve_character(self) -> None:
        """キャラクターパスを解決できる."""
        resolver = VaultPathResolver(Path("/vault"))

        path = resolver.resolve_character("主人公")

        assert path == Path("/vault/characters/主人公.md")

    def test_resolve_world_setting(self) -> None:
        """世界観設定パスを解決できる."""
        resolver = VaultPathResolver(Path("/vault"))

        path = resolver.resolve_world_setting("魔法体系")

        assert path == Path("/vault/world/魔法体系.md")

    def test_resolve_plot_l1(self) -> None:
        """PlotL1 パスを解決できる."""
        resolver = VaultPathResolver(Path("/vault"))

        path = resolver.resolve_plot("L1")

        assert path == Path("/vault/_plot/L1_overall.md")

    def test_resolve_plot_l2(self) -> None:
        """PlotL2 パスを解決できる."""
        resolver = VaultPathResolver(Path("/vault"))

        path = resolver.resolve_plot("L2", chapter_number=1, chapter_name="旅立ち")

        assert path == Path("/vault/_plot/L2_chapters/01_旅立ち.md")

    def test_resolve_plot_l3(self) -> None:
        """PlotL3 パスを解決できる."""
        resolver = VaultPathResolver(Path("/vault"))

        path = resolver.resolve_plot(
            "L3", chapter_number=1, chapter_name="旅立ち", sequence_number=1
        )

        assert path == Path("/vault/_plot/L3_sequences/01_旅立ち/seq_001.md")

    def test_resolve_foreshadowing(self) -> None:
        """伏線レジストリパスを解決できる."""
        resolver = VaultPathResolver(Path("/vault"))

        path = resolver.resolve_foreshadowing()

        assert path == Path("/vault/_foreshadowing/registry.yaml")

    def test_resolve_summary_l1(self) -> None:
        """SummaryL1 パスを解決できる."""
        resolver = VaultPathResolver(Path("/vault"))

        path = resolver.resolve_summary("L1")

        assert path == Path("/vault/_summary/L1_overall.md")

    def test_resolve_summary_l2(self) -> None:
        """SummaryL2 パスを解決できる."""
        resolver = VaultPathResolver(Path("/vault"))

        path = resolver.resolve_summary("L2", chapter_number=1, chapter_name="旅立ち")

        assert path == Path("/vault/_summary/L2_chapters/01_旅立ち.md")

    def test_resolve_summary_l3(self) -> None:
        """SummaryL3 パスを解決できる."""
        resolver = VaultPathResolver(Path("/vault"))

        path = resolver.resolve_summary(
            "L3", chapter_number=1, chapter_name="旅立ち", sequence_number=1
        )

        assert path == Path("/vault/_summary/L3_sequences/01_旅立ち/seq_001.md")

    def test_exists_with_nonexistent_path(self, tmp_path: Path) -> None:
        """存在しないパスは False を返す."""
        resolver = VaultPathResolver(tmp_path)

        assert not resolver.exists(Path("nonexistent.md"))

    def test_exists_with_existing_path(self, tmp_path: Path) -> None:
        """存在するパスは True を返す."""
        resolver = VaultPathResolver(tmp_path)
        test_file = tmp_path / "test.md"
        test_file.write_text("test")

        assert resolver.exists(Path("test.md"))


class TestVaultPathResolverWithVolumes:
    """VaultPathResolver のボリューム対応テスト."""

    def test_detect_volume_structure(self, tmp_path: Path) -> None:
        """ボリューム構造を検出できる."""
        # ボリュームディレクトリを作成
        (tmp_path / "vol01").mkdir()
        (tmp_path / "vol02").mkdir()

        resolver = VaultPathResolver(tmp_path)

        assert resolver.has_volume_structure()

    def test_no_volume_structure_when_flat(self, tmp_path: Path) -> None:
        """フラット構造の場合はボリューム構造なしと判定される."""
        (tmp_path / "episodes").mkdir()

        resolver = VaultPathResolver(tmp_path)

        assert not resolver.has_volume_structure()

    def test_resolve_episode_with_volumes(self, tmp_path: Path) -> None:
        """ボリューム構造がある場合、エピソードパスを正しく解決できる."""
        # ボリューム構造を作成
        vol01 = tmp_path / "vol01"
        vol01.mkdir()

        resolver = VaultPathResolver(tmp_path)

        # エピソード1-25は vol01 に配置される
        path = resolver.resolve_episode(1)
        assert path == tmp_path / "vol01" / "ep_0001.md"

        path = resolver.resolve_episode(25)
        assert path == tmp_path / "vol01" / "ep_0025.md"

    def test_resolve_episode_across_volumes(self, tmp_path: Path) -> None:
        """複数ボリュームにまたがるエピソードを解決できる."""
        vol01 = tmp_path / "vol01"
        vol02 = tmp_path / "vol02"
        vol01.mkdir()
        vol02.mkdir()

        resolver = VaultPathResolver(tmp_path)

        # エピソード26は vol02 に配置される
        path = resolver.resolve_episode(26)
        assert path == tmp_path / "vol02" / "ep_0026.md"

        path = resolver.resolve_episode(50)
        assert path == tmp_path / "vol02" / "ep_0050.md"

    def test_resolve_episode_flat_structure_backward_compatible(
        self, tmp_path: Path
    ) -> None:
        """ボリュームがない場合は従来のフラット構造で解決される."""
        episodes_dir = tmp_path / "episodes"
        episodes_dir.mkdir()

        resolver = VaultPathResolver(tmp_path)

        path = resolver.resolve_episode(1)
        assert path == tmp_path / "episodes" / "ep_0001.md"

    def test_resolve_volume_directory(self, tmp_path: Path) -> None:
        """ボリュームディレクトリのパスを解決できる."""
        vol01 = tmp_path / "vol01"
        vol01.mkdir()

        resolver = VaultPathResolver(tmp_path)

        path = resolver.resolve_volume(1)
        assert path == tmp_path / "vol01"

    def test_resolve_volume_with_two_digit_number(self, tmp_path: Path) -> None:
        """2桁のボリューム番号を解決できる."""
        vol10 = tmp_path / "vol10"
        vol10.mkdir()

        resolver = VaultPathResolver(tmp_path)

        path = resolver.resolve_volume(10)
        assert path == tmp_path / "vol10"

    def test_episode_at_volume_boundary(self, tmp_path: Path) -> None:
        """ボリューム境界のエピソードを正しく解決できる."""
        vol01 = tmp_path / "vol01"
        vol02 = tmp_path / "vol02"
        vol01.mkdir()
        vol02.mkdir()

        resolver = VaultPathResolver(tmp_path)

        # エピソード25（vol01の最後）
        path = resolver.resolve_episode(25)
        assert path == tmp_path / "vol01" / "ep_0025.md"

        # エピソード26（vol02の最初）
        path = resolver.resolve_episode(26)
        assert path == tmp_path / "vol02" / "ep_0026.md"
