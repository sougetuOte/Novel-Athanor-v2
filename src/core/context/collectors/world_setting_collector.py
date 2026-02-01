"""WorldSetting context collector for L3 context building (L3-4-2d).

This module collects WorldSetting contexts related to a scene,
applying Phase filtering to prevent spoilers.
"""

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from src.core.models.character import AIVisibilitySettings, Phase
from src.core.models.world_setting import WorldSetting
from src.core.parsers.frontmatter import parse_frontmatter_with_fallback
from src.core.parsers.markdown import extract_sections

from ..lazy_loader import FileLazyLoader, LoadPriority
from ..phase_filter import WorldSettingPhaseFilter
from ..scene_identifier import SceneIdentifier
from ..scene_resolver import SceneResolver


@dataclass
class WorldSettingContext:
    """WorldSetting context data.

    Attributes:
        settings: Setting name → filtered setting text.
        warnings: Collection warnings.
    """

    settings: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def get_names(self) -> list[str]:
        """Get list of setting names."""
        return list(self.settings.keys())

    def get_setting(self, name: str) -> str | None:
        """Get setting by name."""
        return self.settings.get(name)


class WorldSettingCollector:
    """WorldSetting context collector.

    Collects WorldSetting contexts related to a scene,
    applying Phase filtering.

    Attributes:
        vault_root: Vault root path.
        loader: Lazy loader for file loading.
        resolver: Scene resolver for path resolution.
        phase_filter: Phase filter for WorldSetting.
    """

    def __init__(
        self,
        vault_root: Path,
        loader: FileLazyLoader,
        resolver: SceneResolver,
        phase_filter: WorldSettingPhaseFilter,
    ):
        """Initialize WorldSettingCollector.

        Args:
            vault_root: Vault root directory.
            loader: Lazy loader instance.
            resolver: Scene resolver instance.
            phase_filter: WorldSetting phase filter instance.
        """
        self.vault_root = vault_root
        self.loader = loader
        self.resolver = resolver
        self.phase_filter = phase_filter

    def collect(self, scene: SceneIdentifier) -> WorldSettingContext:
        """Collect WorldSetting context.

        1. Identify setting files related to the scene.
        2. Load each setting file.
        3. Parse WorldSetting.
        4. Apply Phase filter.

        Args:
            scene: Scene identifier.

        Returns:
            Collected WorldSetting context.
        """
        context = WorldSettingContext()

        # Identify setting files
        setting_paths = self.resolver.identify_world_settings(scene)

        for path in setting_paths:
            try:
                # Load file
                result = self.loader.load(
                    str(path.relative_to(self.vault_root)),
                    LoadPriority.REQUIRED,
                )
                if not result.success or not result.data:
                    context.warnings.append(f"世界観設定読み込み失敗: {path}")
                    continue

                # Parse
                setting, parse_error = self._parse_world_setting(path, result.data)
                if not setting:
                    msg = f"世界観設定パース失敗: {path}"
                    if parse_error:
                        msg += f" - {parse_error}"
                    context.warnings.append(msg)
                    continue

                # Apply Phase filter
                if scene.current_phase:
                    filtered_str = self.phase_filter.to_context_string(
                        setting,
                        scene.current_phase,
                    )
                else:
                    # No phase specified, include all information
                    filtered_str = self._setting_to_string(setting)

                context.settings[setting.name] = filtered_str

            except Exception as e:
                context.warnings.append(f"世界観設定処理エラー: {path}: {e}")

        return context

    def _parse_world_setting(
        self, path: Path, content: str
    ) -> tuple[WorldSetting | None, str | None]:
        """Parse WorldSetting from file content.

        Args:
            path: File path.
            content: File content.

        Returns:
            Tuple of (parsed WorldSetting or None, error message or None).
        """
        try:
            parse_result = parse_frontmatter_with_fallback(content)

            if parse_result.result_type == "raw_text":
                return None, "Frontmatter parse failed"

            fm = parse_result.frontmatter or {}
            body = parse_result.body or ""

            # Extract sections
            sections_list = extract_sections(body)
            sections_dict = {s.title: s.content for s in sections_list}

            # Parse phases
            phases = []
            if "phases" in fm:
                for p in fm["phases"]:
                    phases.append(
                        Phase(
                            name=p.get("name", ""),
                            episodes=p.get("episodes", ""),
                        )
                    )

            # Parse AI visibility settings
            ai_vis = fm.get("ai_visibility", {})
            ai_visibility = AIVisibilitySettings(
                default=ai_vis.get("default", 0),
                hidden_section=ai_vis.get("hidden_section", 0),
            )

            # Create WorldSetting
            setting = WorldSetting(
                name=fm.get("name", path.stem),
                category=fm.get("category", ""),
                phases=phases,
                current_phase=fm.get("current_phase"),
                ai_visibility=ai_visibility,
                sections=sections_dict,
                created=self._parse_date(fm.get("created")),
                updated=self._parse_date(fm.get("updated")),
                tags=fm.get("tags", []),
            )

            return setting, None

        except Exception as e:
            return None, str(e)

    def _parse_date(self, value: Any) -> date:
        """Parse date from various formats."""
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            from datetime import datetime

            return datetime.strptime(value, "%Y-%m-%d").date()
        return date.today()

    def _setting_to_string(self, setting: WorldSetting) -> str:
        """Convert setting to string (no filtering).

        Args:
            setting: WorldSetting to convert.

        Returns:
            String representation.
        """
        lines = [f"# {setting.name}"]
        if setting.category:
            lines.append(f"Category: {setting.category}")

        for section_name, content in setting.sections.items():
            lines.append(f"\n## {section_name}")
            lines.append(content)

        return "\n".join(lines)

    def collect_as_string(self, scene: SceneIdentifier) -> str | None:
        """ContextCollector protocol method.

        Collect all settings and return as a single string.

        Args:
            scene: Scene identifier.

        Returns:
            Integrated world setting string, or None if no settings.
        """
        context = self.collect(scene)

        if not context.settings:
            return None

        parts = [f"## {name}\n{info}" for name, info in context.settings.items()]

        return "\n\n---\n\n".join(parts)
