"""Context collectors for L3 context building.

This package contains collectors that gather various types of context
(plot, summary, character, world setting, style guide) for scene generation.
"""

from .character_collector import CharacterCollector, CharacterContext
from .plot_collector import PlotCollector, PlotContext
from .style_guide_collector import StyleGuideCollector, StyleGuideContext
from .summary_collector import SummaryCollector, SummaryContext
from .world_setting_collector import WorldSettingCollector, WorldSettingContext

__all__ = [
    "CharacterCollector",
    "CharacterContext",
    "PlotCollector",
    "PlotContext",
    "StyleGuideCollector",
    "StyleGuideContext",
    "SummaryCollector",
    "SummaryContext",
    "WorldSettingCollector",
    "WorldSettingContext",
]
