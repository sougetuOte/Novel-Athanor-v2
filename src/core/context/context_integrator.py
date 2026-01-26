"""Context integrator protocol for L3 context building.

This module defines protocols for collecting and integrating
various context elements (plot, summary, characters, etc.).
"""

from typing import Any, Protocol

from .filtered_context import FilteredContext
from .scene_identifier import SceneIdentifier


class ContextCollector(Protocol):
    """Protocol for individual context collectors.

    Each collector is responsible for gathering one type of context
    (plot, summary, character, world setting, or style guide).
    """

    def collect(self, scene: SceneIdentifier) -> str | None:
        """Collect context for the given scene.

        Args:
            scene: The scene identifier.

        Returns:
            Collected context string, or None if not available.
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
