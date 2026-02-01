"""Context integrator protocol for L3 context building.

This module defines protocols for collecting and integrating
various context elements (plot, summary, characters, etc.).
"""

from pathlib import Path
from typing import Any, Protocol

from .collectors.character_collector import CharacterContext
from .collectors.plot_collector import PlotContext
from .collectors.summary_collector import SummaryContext
from .collectors.world_setting_collector import WorldSettingContext
from .filtered_context import FilteredContext
from .scene_identifier import SceneIdentifier


class ContextCollector(Protocol):
    """Protocol for individual context collectors.

    Each collector is responsible for gathering one type of context
    (plot, summary, character, world setting, or style guide).

    Implementations should provide:
    - collect(): Returns a typed data class with structured data
    - collect_as_string(): Returns a formatted string for AI consumption
    """

    def collect_as_string(self, scene: SceneIdentifier) -> str | None:
        """Collect context as a formatted string.

        This is the primary method for integration with ContextIntegrator.

        Args:
            scene: The scene identifier.

        Returns:
            Collected context as formatted string, or None if not available.
        """
        ...


class ContextIntegrator(Protocol):
    """Protocol for integrating multiple context sources.

    Implementations combine outputs from various ContextCollectors
    into a unified FilteredContext.
    """

    def integrate(
        self,
        scene: SceneIdentifier,
        *,
        plot_collector: ContextCollector | None = None,
        summary_collector: ContextCollector | None = None,
        character_collector: ContextCollector | None = None,
        world_collector: ContextCollector | None = None,
        style_collector: ContextCollector | None = None,
    ) -> FilteredContext:
        """Integrate context from multiple collectors.

        Args:
            scene: The scene identifier.
            plot_collector: Collector for plot context (L1/L2/L3).
            summary_collector: Collector for summary context.
            character_collector: Collector for character context.
            world_collector: Collector for world setting context.
            style_collector: Collector for style guide context.

        Returns:
            Integrated FilteredContext.
        """
        ...

    def integrate_with_warnings(
        self,
        scene: SceneIdentifier,
        **collectors: Any,
    ) -> tuple[FilteredContext, list[str]]:
        """Integrate context and return warnings.

        Args:
            scene: The scene identifier.
            **collectors: Named collectors.

        Returns:
            Tuple of (FilteredContext, list of warning messages).
        """
        ...


class ContextIntegratorImpl:
    """Implementation of ContextIntegrator protocol.

    Integrates multiple context collectors into a unified FilteredContext.

    Attributes:
        vault_root: Root path of the vault.
    """

    def __init__(self, vault_root: Path) -> None:
        """Initialize ContextIntegratorImpl.

        Args:
            vault_root: Root path of the vault.
        """
        self.vault_root = vault_root

    def integrate(
        self,
        scene: SceneIdentifier,
        *,
        plot_collector: ContextCollector | None = None,
        summary_collector: ContextCollector | None = None,
        character_collector: ContextCollector | None = None,
        world_collector: ContextCollector | None = None,
        style_collector: ContextCollector | None = None,
    ) -> FilteredContext:
        """Integrate context from multiple collectors.

        Args:
            scene: The scene identifier.
            plot_collector: Collector for plot context.
            summary_collector: Collector for summary context.
            character_collector: Collector for character context.
            world_collector: Collector for world setting context.
            style_collector: Collector for style guide context.

        Returns:
            Integrated FilteredContext.
        """
        ctx = FilteredContext(
            scene_id=scene.episode_id,
            current_phase=scene.current_phase,
        )

        # Collect plot context
        if plot_collector is not None:
            self._integrate_plot(ctx, plot_collector, scene)

        # Collect summary context
        if summary_collector is not None:
            self._integrate_summary(ctx, summary_collector, scene)

        # Collect character context
        if character_collector is not None:
            self._integrate_character(ctx, character_collector, scene)

        # Collect world setting context
        if world_collector is not None:
            self._integrate_world_setting(ctx, world_collector, scene)

        # Collect style guide context
        if style_collector is not None:
            ctx.style_guide = style_collector.collect_as_string(scene)

        return ctx

    def _integrate_plot(
        self,
        ctx: FilteredContext,
        collector: ContextCollector,
        scene: SceneIdentifier,
    ) -> None:
        """Integrate plot context into FilteredContext.

        Args:
            ctx: The FilteredContext to update.
            collector: The plot collector.
            scene: The scene identifier.
        """
        # Check if collector has collect method returning PlotContext
        if hasattr(collector, "collect") and callable(collector.collect):
            result = collector.collect(scene)
            if isinstance(result, PlotContext):
                ctx.plot_l1 = result.l1_theme
                ctx.plot_l2 = result.l2_chapter
                ctx.plot_l3 = result.l3_scene
                return

        # Fallback to collect_as_string
        content = collector.collect_as_string(scene)
        if content:
            ctx.plot_l1 = content

    def _integrate_summary(
        self,
        ctx: FilteredContext,
        collector: ContextCollector,
        scene: SceneIdentifier,
    ) -> None:
        """Integrate summary context into FilteredContext.

        Args:
            ctx: The FilteredContext to update.
            collector: The summary collector.
            scene: The scene identifier.
        """
        # Check if collector has collect method returning SummaryContext
        if hasattr(collector, "collect") and callable(collector.collect):
            result = collector.collect(scene)
            if isinstance(result, SummaryContext):
                ctx.summary_l1 = result.l1_overall
                ctx.summary_l2 = result.l2_chapter
                ctx.summary_l3 = result.l3_recent
                return

        # Fallback to collect_as_string
        content = collector.collect_as_string(scene)
        if content:
            ctx.summary_l1 = content

    def _integrate_character(
        self,
        ctx: FilteredContext,
        collector: ContextCollector,
        scene: SceneIdentifier,
    ) -> None:
        """Integrate character context into FilteredContext.

        Args:
            ctx: The FilteredContext to update.
            collector: The character collector.
            scene: The scene identifier.
        """
        # Check if collector has collect method returning CharacterContext
        if hasattr(collector, "collect") and callable(collector.collect):
            result = collector.collect(scene)
            if isinstance(result, CharacterContext):
                # Store each character with its own key
                for char_name, char_content in result.characters.items():
                    ctx.characters[char_name] = char_content
                # Collect warnings
                ctx.warnings.extend(result.warnings)
                return

        # Fallback to collect_as_string
        fallback_content = collector.collect_as_string(scene)
        if fallback_content is not None:
            ctx.characters["_all"] = fallback_content

    def _integrate_world_setting(
        self,
        ctx: FilteredContext,
        collector: ContextCollector,
        scene: SceneIdentifier,
    ) -> None:
        """Integrate world setting context into FilteredContext.

        Args:
            ctx: The FilteredContext to update.
            collector: The world setting collector.
            scene: The scene identifier.
        """
        # Check if collector has collect method returning WorldSettingContext
        if hasattr(collector, "collect") and callable(collector.collect):
            result = collector.collect(scene)
            if isinstance(result, WorldSettingContext):
                # Store each setting with its own key
                for setting_name, setting_content in result.settings.items():
                    ctx.world_settings[setting_name] = setting_content
                # Collect warnings
                ctx.warnings.extend(result.warnings)
                return

        # Fallback to collect_as_string
        fallback_content = collector.collect_as_string(scene)
        if fallback_content is not None:
            ctx.world_settings["_all"] = fallback_content

    def integrate_with_warnings(
        self,
        scene: SceneIdentifier,
        **collectors: Any,
    ) -> tuple[FilteredContext, list[str]]:
        """Integrate context and return warnings.

        Args:
            scene: The scene identifier.
            **collectors: Named collectors.

        Returns:
            Tuple of (FilteredContext, list of warning messages).
        """
        warnings: list[str] = []

        ctx = self.integrate(
            scene,
            plot_collector=collectors.get("plot_collector"),
            summary_collector=collectors.get("summary_collector"),
            character_collector=collectors.get("character_collector"),
            world_collector=collectors.get("world_collector"),
            style_collector=collectors.get("style_collector"),
        )

        # Collect warnings from context
        warnings.extend(ctx.warnings)

        return ctx, warnings
