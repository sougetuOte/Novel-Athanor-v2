"""Tests for scene resolver."""

from pathlib import Path

import pytest

from src.core.context.scene_identifier import SceneIdentifier
from src.core.context.scene_resolver import ResolvedPaths, SceneResolver


class TestResolvedPaths:
    """Test ResolvedPaths data class."""

    def test_create_empty(self) -> None:
        """Create empty ResolvedPaths."""
        paths = ResolvedPaths()
        assert paths.episode is None
        assert paths.plot_l1 is None
        assert paths.plot_l2 is None
        assert paths.plot_l3 is None
        assert paths.summary_l1 is None
        assert paths.summary_l2 is None
        assert paths.summary_l3 is None
        assert paths.style_guide is None

    def test_create_with_values(self) -> None:
        """Create ResolvedPaths with values."""
        paths = ResolvedPaths(
            episode=Path("episodes/010.md"),
            plot_l1=Path("_plot/l1_theme.md"),
            plot_l2=Path("_plot/l2_ch01.md"),
            summary_l1=Path("_summary/l1_overall.md"),
            style_guide=Path("_style_guides/default.md"),
        )
        assert paths.episode == Path("episodes/010.md")
        assert paths.plot_l1 == Path("_plot/l1_theme.md")
        assert paths.plot_l2 == Path("_plot/l2_ch01.md")
        assert paths.summary_l1 == Path("_summary/l1_overall.md")
        assert paths.style_guide == Path("_style_guides/default.md")


class TestSceneResolver:
    """Test SceneResolver class."""

    @pytest.fixture
    def vault_root(self, tmp_path: Path) -> Path:
        """Create test vault structure."""
        work = tmp_path / "test_work"
        (work / "episodes").mkdir(parents=True)
        (work / "_plot").mkdir()
        (work / "_summary").mkdir()
        (work / "_style_guides").mkdir()

        # Create test files
        (work / "episodes" / "010.md").write_text("Episode 10")
        (work / "_plot" / "l1_theme.md").write_text("Theme")
        (work / "_plot" / "l2_ch01.md").write_text("Chapter 1")
        (work / "_summary" / "l1_overall.md").write_text("Overall")
        (work / "_style_guides" / "default.md").write_text("Style")

        return work

    @pytest.fixture
    def resolver(self, vault_root: Path) -> SceneResolver:
        """Create SceneResolver instance."""
        return SceneResolver(vault_root)

    # Episode path resolution tests
    def test_resolve_episode_path_exists(self, resolver: SceneResolver) -> None:
        """Resolve existing episode path."""
        scene = SceneIdentifier(episode_id="010")
        path = resolver.resolve_episode_path(scene)
        assert path is not None
        assert path.name == "010.md"
        assert path.exists()

    def test_resolve_episode_path_not_exists(self, resolver: SceneResolver) -> None:
        """Resolve non-existing episode path."""
        scene = SceneIdentifier(episode_id="999")
        path = resolver.resolve_episode_path(scene)
        assert path is None

    def test_resolve_episode_path_with_chapter_subdirectory(
        self, vault_root: Path
    ) -> None:
        """Resolve episode in chapter subdirectory."""
        # Create chapter subdirectory structure
        (vault_root / "episodes" / "ch01").mkdir()
        (vault_root / "episodes" / "ch01" / "010.md").write_text("Episode 10 in ch01")

        resolver = SceneResolver(vault_root)
        scene = SceneIdentifier(episode_id="010", chapter_id="ch01")
        path = resolver.resolve_episode_path(scene)

        assert path is not None
        assert path == vault_root / "episodes" / "ch01" / "010.md"
        assert path.exists()

    # Plot paths resolution tests
    def test_resolve_plot_paths(self, resolver: SceneResolver) -> None:
        """Resolve plot paths."""
        scene = SceneIdentifier(episode_id="010", chapter_id="ch01")
        l1, l2, l3 = resolver.resolve_plot_paths(scene)

        assert l1 is not None  # l1_theme.md exists
        assert l1.name == "l1_theme.md"
        assert l2 is not None  # l2_ch01.md exists
        assert l2.name == "l2_ch01.md"
        assert l3 is None  # l3_010.md does not exist

    def test_resolve_plot_paths_without_chapter(self, resolver: SceneResolver) -> None:
        """Resolve plot paths without chapter ID."""
        scene = SceneIdentifier(episode_id="010")
        l1, l2, l3 = resolver.resolve_plot_paths(scene)

        assert l1 is not None
        assert l2 is None  # No chapter_id, so l2 should be None
        assert l3 is None

    def test_resolve_plot_paths_with_l3_exists(
        self, resolver: SceneResolver, vault_root: Path
    ) -> None:
        """Resolve plot paths when L3 plot exists."""
        # Create L3 plot file
        (vault_root / "_plot" / "l3_010.md").write_text("L3 plot for episode 010")

        scene = SceneIdentifier(episode_id="010")
        l1, l2, l3 = resolver.resolve_plot_paths(scene)

        assert l1 is not None
        assert l3 is not None
        assert l3.name == "l3_010.md"

    # Summary paths resolution tests
    def test_resolve_summary_paths(self, resolver: SceneResolver) -> None:
        """Resolve summary paths."""
        scene = SceneIdentifier(episode_id="010", chapter_id="ch01")
        l1, l2, l3 = resolver.resolve_summary_paths(scene)

        assert l1 is not None  # l1_overall.md exists
        assert l1.name == "l1_overall.md"
        assert l2 is None  # l2_ch01.md does not exist
        assert l3 is None  # l3_010.md does not exist

    def test_resolve_summary_paths_without_chapter(
        self, resolver: SceneResolver
    ) -> None:
        """Resolve summary paths without chapter ID."""
        scene = SceneIdentifier(episode_id="010")
        l1, l2, l3 = resolver.resolve_summary_paths(scene)

        assert l1 is not None
        assert l2 is None
        assert l3 is None

    def test_resolve_summary_paths_all_exist(
        self, resolver: SceneResolver, vault_root: Path
    ) -> None:
        """Resolve summary paths when all levels exist."""
        # Create L2 and L3 summary files
        (vault_root / "_summary" / "l2_ch01.md").write_text("Chapter 1 summary")
        (vault_root / "_summary" / "l3_010.md").write_text("Episode 010 summary")

        scene = SceneIdentifier(episode_id="010", chapter_id="ch01")
        l1, l2, l3 = resolver.resolve_summary_paths(scene)

        assert l1 is not None
        assert l2 is not None
        assert l2.name == "l2_ch01.md"
        assert l3 is not None
        assert l3.name == "l3_010.md"

    # Style guide path resolution tests
    def test_resolve_style_guide_path(self, resolver: SceneResolver) -> None:
        """Resolve style guide path."""
        path = resolver.resolve_style_guide_path()
        assert path is not None
        assert path.name == "default.md"
        assert path.exists()

    def test_resolve_style_guide_path_not_exists(self, vault_root: Path) -> None:
        """Resolve style guide path when it does not exist."""
        # Remove style guide file
        (vault_root / "_style_guides" / "default.md").unlink()

        resolver = SceneResolver(vault_root)
        path = resolver.resolve_style_guide_path()
        assert path is None

    # resolve_all tests
    def test_resolve_all(self, resolver: SceneResolver) -> None:
        """Resolve all paths for a scene."""
        scene = SceneIdentifier(episode_id="010", chapter_id="ch01")
        paths = resolver.resolve_all(scene)

        assert isinstance(paths, ResolvedPaths)
        assert paths.episode is not None
        assert paths.plot_l1 is not None
        assert paths.plot_l2 is not None
        assert paths.summary_l1 is not None
        assert paths.style_guide is not None

    def test_resolve_all_minimal(self, vault_root: Path) -> None:
        """Resolve all paths with minimal files."""
        # Create minimal vault
        minimal_vault = vault_root / "minimal"
        minimal_vault.mkdir()
        (minimal_vault / "episodes").mkdir()
        (minimal_vault / "_plot").mkdir()
        (minimal_vault / "_summary").mkdir()
        (minimal_vault / "_style_guides").mkdir()

        # Only create episode file
        (minimal_vault / "episodes" / "001.md").write_text("Episode 1")

        resolver = SceneResolver(minimal_vault)
        scene = SceneIdentifier(episode_id="001")
        paths = resolver.resolve_all(scene)

        assert paths.episode is not None
        assert paths.plot_l1 is None
        assert paths.plot_l2 is None
        assert paths.plot_l3 is None
        assert paths.summary_l1 is None
        assert paths.style_guide is None

    def test_resolve_all_comprehensive(self, vault_root: Path) -> None:
        """Resolve all paths when all files exist."""
        # Create all possible files
        (vault_root / "_plot" / "l2_ch01.md").write_text("L2 plot")
        (vault_root / "_plot" / "l3_010.md").write_text("L3 plot")
        (vault_root / "_summary" / "l2_ch01.md").write_text("L2 summary")
        (vault_root / "_summary" / "l3_010.md").write_text("L3 summary")

        resolver = SceneResolver(vault_root)
        scene = SceneIdentifier(episode_id="010", chapter_id="ch01")
        paths = resolver.resolve_all(scene)

        assert paths.episode is not None
        assert paths.plot_l1 is not None
        assert paths.plot_l2 is not None
        assert paths.plot_l3 is not None
        assert paths.summary_l1 is not None
        assert paths.summary_l2 is not None
        assert paths.summary_l3 is not None
        assert paths.style_guide is not None


class TestSceneResolverCharacterIdentification:
    """Test character identification methods."""

    @pytest.fixture
    def vault_root(self, tmp_path: Path) -> Path:
        """Create test vault structure with characters."""
        work = tmp_path / "test_work"
        (work / "episodes").mkdir(parents=True)
        (work / "characters").mkdir()
        (work / "_plot").mkdir()

        # Create character files
        (work / "characters" / "アイラ.md").write_text("---\nname: アイラ\n---\n主人公")
        (work / "characters" / "ボブ.md").write_text("---\nname: ボブ\n---\n仲間")
        (work / "characters" / "villain.md").write_text("---\nname: villain\n---\n悪役")

        # Create episode with character references
        episode_content = """---
characters:
  - アイラ
  - ボブ
---
# Episode 010

アイラは窓の外を見つめていた。
[[characters/アイラ|アイラ]]が話しかける。
"""
        (work / "episodes" / "010.md").write_text(episode_content)

        # Create L3 plot with character references
        plot_content = """---
characters:
  - villain
---
## 登場人物
- [[characters/アイラ]]
- [[ボブ]]
"""
        (work / "_plot" / "l3_010.md").write_text(plot_content)

        return work

    @pytest.fixture
    def resolver(self, vault_root: Path) -> SceneResolver:
        """Create SceneResolver instance."""
        return SceneResolver(vault_root)

    def test_extract_character_references_wikilink_full(
        self, resolver: SceneResolver
    ) -> None:
        """Extract wikilink format [[characters/name]]."""
        content = "話の中で[[characters/アイラ]]が登場する。"
        refs = resolver._extract_character_references(content)
        assert "アイラ" in refs

    def test_extract_character_references_wikilink_with_alias(
        self, resolver: SceneResolver
    ) -> None:
        """Extract wikilink with alias [[characters/name|display]]."""
        content = "[[characters/アイラ|主人公アイラ]]が話す。"
        refs = resolver._extract_character_references(content)
        assert "アイラ" in refs

    def test_extract_character_references_short_form(
        self, resolver: SceneResolver
    ) -> None:
        """Extract short wikilink [[name]] (assumes characters/)."""
        content = "[[ボブ]]と話す。"
        refs = resolver._extract_character_references(content)
        assert "ボブ" in refs

    def test_extract_character_references_yaml_frontmatter(
        self, resolver: SceneResolver
    ) -> None:
        """Extract from YAML frontmatter characters list."""
        content = """---
characters:
  - アイラ
  - ボブ
---
本文
"""
        refs = resolver._extract_character_references(content)
        assert "アイラ" in refs
        assert "ボブ" in refs

    def test_extract_character_references_list_format(
        self, resolver: SceneResolver
    ) -> None:
        """Extract from '登場人物:' list format."""
        content = """## 登場人物
- アイラ
- ボブ
"""
        refs = resolver._extract_character_references(content)
        assert "アイラ" in refs
        assert "ボブ" in refs

    def test_resolve_character_path_exists(
        self, resolver: SceneResolver, vault_root: Path
    ) -> None:
        """Resolve character name to existing file path."""
        path = resolver._resolve_character_path("アイラ")
        assert path is not None
        assert path.exists()
        assert path.name == "アイラ.md"

    def test_resolve_character_path_not_exists(
        self, resolver: SceneResolver
    ) -> None:
        """Resolve non-existing character returns None."""
        path = resolver._resolve_character_path("存在しない")
        assert path is None

    def test_identify_characters_from_episode(
        self, resolver: SceneResolver, vault_root: Path
    ) -> None:
        """Identify characters from episode content."""
        scene = SceneIdentifier(episode_id="010")
        episode_content = (vault_root / "episodes" / "010.md").read_text()
        paths = resolver.identify_characters(scene, episode_content=episode_content)

        # Should find アイラ and ボブ
        names = [p.stem for p in paths]
        assert "アイラ" in names
        assert "ボブ" in names

    def test_identify_characters_from_plot(
        self, resolver: SceneResolver, vault_root: Path
    ) -> None:
        """Identify characters from L3 plot content."""
        scene = SceneIdentifier(episode_id="010")
        plot_content = (vault_root / "_plot" / "l3_010.md").read_text()
        paths = resolver.identify_characters(scene, plot_l3_content=plot_content)

        names = [p.stem for p in paths]
        assert "アイラ" in names
        assert "villain" in names

    def test_identify_characters_combined(
        self, resolver: SceneResolver, vault_root: Path
    ) -> None:
        """Identify characters from both episode and plot."""
        scene = SceneIdentifier(episode_id="010")
        episode_content = (vault_root / "episodes" / "010.md").read_text()
        plot_content = (vault_root / "_plot" / "l3_010.md").read_text()

        paths = resolver.identify_characters(
            scene, episode_content=episode_content, plot_l3_content=plot_content
        )

        names = [p.stem for p in paths]
        # Should find all three
        assert "アイラ" in names
        assert "ボブ" in names
        assert "villain" in names

    def test_list_all_characters(
        self, resolver: SceneResolver, vault_root: Path
    ) -> None:
        """List all character files in vault."""
        paths = resolver.list_all_characters()
        assert len(paths) == 3
        names = [p.stem for p in paths]
        assert "アイラ" in names
        assert "ボブ" in names
        assert "villain" in names


class TestSceneResolverWorldSettingIdentification:
    """Test world setting identification methods."""

    @pytest.fixture
    def vault_root(self, tmp_path: Path) -> Path:
        """Create test vault structure with world settings."""
        work = tmp_path / "test_work"
        (work / "episodes").mkdir(parents=True)
        (work / "world").mkdir()
        (work / "world" / "地理").mkdir()
        (work / "world" / "組織").mkdir()
        (work / "_plot").mkdir()

        # Create world setting files
        (work / "world" / "魔法体系.md").write_text("---\nname: 魔法体系\n---")
        (work / "world" / "地理" / "王都.md").write_text("---\nname: 王都\n---")
        (work / "world" / "組織" / "騎士団.md").write_text("---\nname: 騎士団\n---")

        # Create episode with world references
        episode_content = """---
world_settings:
  - 魔法体系
  - 王都
---
# Episode 010

王都の中心には古い塔がそびえていた。
"""
        (work / "episodes" / "010.md").write_text(episode_content)

        # Create L3 plot with world references
        plot_content = """---
world_settings:
  - 騎士団
---
## 関連設定
- [[world/魔法体系]]
- [[world/地理/王都|王都]]
"""
        (work / "_plot" / "l3_010.md").write_text(plot_content)

        return work

    @pytest.fixture
    def resolver(self, vault_root: Path) -> SceneResolver:
        """Create SceneResolver instance."""
        return SceneResolver(vault_root)

    def test_extract_world_references_wikilink_full(
        self, resolver: SceneResolver
    ) -> None:
        """Extract wikilink format [[world/name]]."""
        content = "[[world/魔法体系]]について説明する。"
        refs = resolver._extract_world_references(content)
        assert "魔法体系" in refs

    def test_extract_world_references_subdirectory(
        self, resolver: SceneResolver
    ) -> None:
        """Extract wikilink with subdirectory [[world/category/name]]."""
        content = "[[world/地理/王都]]を訪れる。"
        refs = resolver._extract_world_references(content)
        assert "地理/王都" in refs or "王都" in refs

    def test_extract_world_references_with_alias(
        self, resolver: SceneResolver
    ) -> None:
        """Extract wikilink with alias [[world/name|display]]."""
        content = "[[world/地理/王都|首都王都]]に到着。"
        refs = resolver._extract_world_references(content)
        # Should extract 地理/王都 or 王都
        assert any("王都" in ref for ref in refs)

    def test_extract_world_references_yaml_frontmatter(
        self, resolver: SceneResolver
    ) -> None:
        """Extract from YAML frontmatter world_settings list."""
        content = """---
world_settings:
  - 魔法体系
  - 王都
---
本文
"""
        refs = resolver._extract_world_references(content)
        assert "魔法体系" in refs
        assert "王都" in refs

    def test_resolve_world_setting_path_top_level(
        self, resolver: SceneResolver, vault_root: Path
    ) -> None:
        """Resolve top-level world setting."""
        path = resolver._resolve_world_setting_path("魔法体系")
        assert path is not None
        assert path.exists()
        assert path.name == "魔法体系.md"

    def test_resolve_world_setting_path_subdirectory(
        self, resolver: SceneResolver, vault_root: Path
    ) -> None:
        """Resolve world setting in subdirectory."""
        path = resolver._resolve_world_setting_path("地理/王都")
        assert path is not None
        assert path.exists()

    def test_resolve_world_setting_path_by_name_only(
        self, resolver: SceneResolver, vault_root: Path
    ) -> None:
        """Resolve world setting by name only (search in subdirs)."""
        path = resolver._resolve_world_setting_path("王都")
        assert path is not None
        assert path.exists()
        assert path.name == "王都.md"

    def test_resolve_world_setting_path_not_exists(
        self, resolver: SceneResolver
    ) -> None:
        """Resolve non-existing world setting returns None."""
        path = resolver._resolve_world_setting_path("存在しない")
        assert path is None

    def test_identify_world_settings_from_episode(
        self, resolver: SceneResolver, vault_root: Path
    ) -> None:
        """Identify world settings from episode content."""
        scene = SceneIdentifier(episode_id="010")
        episode_content = (vault_root / "episodes" / "010.md").read_text()
        paths = resolver.identify_world_settings(scene, episode_content=episode_content)

        names = [p.stem for p in paths]
        assert "魔法体系" in names
        assert "王都" in names

    def test_identify_world_settings_from_plot(
        self, resolver: SceneResolver, vault_root: Path
    ) -> None:
        """Identify world settings from L3 plot content."""
        scene = SceneIdentifier(episode_id="010")
        plot_content = (vault_root / "_plot" / "l3_010.md").read_text()
        paths = resolver.identify_world_settings(scene, plot_l3_content=plot_content)

        names = [p.stem for p in paths]
        assert "魔法体系" in names
        assert "騎士団" in names

    def test_list_all_world_settings(
        self, resolver: SceneResolver, vault_root: Path
    ) -> None:
        """List all world setting files recursively."""
        paths = resolver.list_all_world_settings()
        assert len(paths) == 3
        names = [p.stem for p in paths]
        assert "魔法体系" in names
        assert "王都" in names
        assert "騎士団" in names


class TestReferencePatternConfig:
    """Test configurable reference patterns from _settings/."""

    @pytest.fixture
    def vault_root(self, tmp_path: Path) -> Path:
        """Create test vault with _settings directory."""
        work = tmp_path / "test_work"
        (work / "episodes").mkdir(parents=True)
        (work / "characters").mkdir()
        (work / "world").mkdir()
        (work / "_settings").mkdir()

        # Create character files
        (work / "characters" / "Hero.md").write_text("---\nname: Hero\n---")
        (work / "characters" / "Villain.md").write_text("---\nname: Villain\n---")

        return work

    @pytest.fixture
    def default_config_yaml(self) -> str:
        """Default reference pattern config."""
        return """# Reference Pattern Configuration
character_patterns:
  # Wikilink patterns for characters
  wikilinks:
    - pattern: '\\[\\[characters/([^\\]|]+)(?:\\|[^\\]]+)?\\]\\]'
      description: "Full character wikilink"
    - pattern: '\\[\\[([^\\]/|]+)(?:\\|[^\\]]+)?\\]\\]'
      exclude_prefixes: ["world", "_", "episodes"]
      description: "Short wikilink (assumes characters/)"

  # YAML frontmatter patterns
  yaml:
    - pattern: '^characters:\\s*\\n((?:\\s+-\\s*.+\\n?)+)'
      description: "YAML characters list"

  # Japanese list patterns
  list_headers:
    - "登場人物"
    - "登場キャラクター"

world_patterns:
  wikilinks:
    - pattern: '\\[\\[world/([^\\]|]+)(?:\\|[^\\]]+)?\\]\\]'
      description: "World setting wikilink"

  yaml:
    - pattern: '^world_settings:\\s*\\n((?:\\s+-\\s*.+\\n?)+)'
      description: "YAML world_settings list"

  list_headers:
    - "関連設定"
    - "世界観設定"
"""

    def test_load_default_patterns_when_no_config(
        self, vault_root: Path
    ) -> None:
        """Use default patterns when no config file exists."""
        from src.core.context.scene_resolver import SceneResolver

        resolver = SceneResolver(vault_root)
        config = resolver.get_reference_patterns()

        # Should have default patterns
        assert "character_patterns" in config
        assert "world_patterns" in config
        assert len(config["character_patterns"]["list_headers"]) >= 2

    def test_load_patterns_from_settings_file(
        self, vault_root: Path, default_config_yaml: str
    ) -> None:
        """Load patterns from _settings/reference_patterns.yaml."""
        from src.core.context.scene_resolver import SceneResolver

        # Create config file
        config_path = vault_root / "_settings" / "reference_patterns.yaml"
        config_path.write_text(default_config_yaml)

        resolver = SceneResolver(vault_root)
        config = resolver.get_reference_patterns()

        assert "character_patterns" in config
        assert "登場人物" in config["character_patterns"]["list_headers"]
        assert "登場キャラクター" in config["character_patterns"]["list_headers"]

    def test_custom_list_header_patterns(
        self, vault_root: Path
    ) -> None:
        """Use custom list header patterns from config."""
        from src.core.context.scene_resolver import SceneResolver

        # Create config with custom headers
        custom_config = """character_patterns:
  list_headers:
    - "キャラ一覧"
    - "出演者"

world_patterns:
  list_headers:
    - "設定一覧"
"""
        config_path = vault_root / "_settings" / "reference_patterns.yaml"
        config_path.write_text(custom_config)

        resolver = SceneResolver(vault_root)

        # Test with custom format
        content = """## キャラ一覧
- Hero
- Villain
"""
        refs = resolver._extract_character_references(content)
        assert "Hero" in refs
        assert "Villain" in refs

    def test_patterns_cached_after_first_load(
        self, vault_root: Path, default_config_yaml: str
    ) -> None:
        """Patterns should be cached after first load."""
        from src.core.context.scene_resolver import SceneResolver

        config_path = vault_root / "_settings" / "reference_patterns.yaml"
        config_path.write_text(default_config_yaml)

        resolver = SceneResolver(vault_root)

        # First call loads from file
        config1 = resolver.get_reference_patterns()

        # Modify file
        config_path.write_text("character_patterns:\n  list_headers: ['Changed']")

        # Second call should return cached version
        config2 = resolver.get_reference_patterns()

        assert config1 is config2  # Same object (cached)
        assert "登場人物" in config1["character_patterns"]["list_headers"]

    def test_reload_patterns(
        self, vault_root: Path, default_config_yaml: str
    ) -> None:
        """Force reload patterns from file."""
        from src.core.context.scene_resolver import SceneResolver

        config_path = vault_root / "_settings" / "reference_patterns.yaml"
        config_path.write_text(default_config_yaml)

        resolver = SceneResolver(vault_root)
        config1 = resolver.get_reference_patterns()

        # Modify file
        config_path.write_text("character_patterns:\n  list_headers:\n    - 'NewHeader'")

        # Force reload
        config2 = resolver.get_reference_patterns(force_reload=True)

        assert config1 is not config2
        assert "NewHeader" in config2["character_patterns"]["list_headers"]

    def test_invalid_yaml_falls_back_to_defaults(
        self, tmp_path: Path
    ) -> None:
        """Invalid YAML config falls back to defaults."""
        from src.core.context.scene_resolver import SceneResolver

        # Create fresh vault with invalid YAML
        work = tmp_path / "invalid_yaml_test"
        (work / "_settings").mkdir(parents=True)
        config_path = work / "_settings" / "reference_patterns.yaml"
        config_path.write_text("invalid: yaml: : : content [[[")

        resolver = SceneResolver(work)
        config = resolver.get_reference_patterns()

        # Should fallback to defaults
        assert "character_patterns" in config
        assert len(config["character_patterns"]["list_headers"]) >= 2

    def test_extract_with_config_patterns(
        self, vault_root: Path
    ) -> None:
        """Extract references using configured patterns."""
        from src.core.context.scene_resolver import SceneResolver

        config = """character_patterns:
  list_headers:
    - "メインキャラ"
    - "サブキャラ"

world_patterns:
  list_headers:
    - "舞台設定"
"""
        config_path = vault_root / "_settings" / "reference_patterns.yaml"
        config_path.write_text(config)

        resolver = SceneResolver(vault_root)

        content = """## メインキャラ
- Hero
- Villain

## サブキャラ
- Support
"""
        refs = resolver._extract_character_references(content)
        assert "Hero" in refs
        assert "Villain" in refs
        assert "Support" in refs
