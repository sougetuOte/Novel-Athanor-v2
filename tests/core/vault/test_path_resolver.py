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
