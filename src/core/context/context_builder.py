"""ContextBuilder facade for L3 context building.

This module provides the unified entry point (facade) for the L3 Context Builder layer.
ContextBuilder orchestrates all L3 components to build complete context
for L4 agents (Continuity Director, Ghost Writer).

Usage:
    builder = ContextBuilder(vault_root=Path("vault"))
    result = builder.build_context(scene)
"""

from __future__ import annotations

import logging
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path

from src.core.repositories.foreshadowing import ForeshadowingRepository
from src.core.services.visibility_controller import VisibilityController

from .collectors.character_collector import CharacterCollector
from .collectors.plot_collector import PlotCollector
from .collectors.style_guide_collector import StyleGuideCollector
from .collectors.summary_collector import SummaryCollector
from .collectors.world_setting_collector import WorldSettingCollector
from .context_integrator import ContextIntegratorImpl
from .filtered_context import FilteredContext
from .forbidden_keyword_collector import (
    ForbiddenKeywordCollector,
    ForbiddenKeywordResult,
)
from .foreshadow_instruction import ForeshadowInstructions, InstructionAction
from .foreshadowing_identifier import ForeshadowingIdentifier
from .hint_collector import HintCollection, HintCollector
from .instruction_generator import InstructionGeneratorImpl
from .lazy_loader import FileLazyLoader
from .phase_filter import CharacterPhaseFilter, WorldSettingPhaseFilter
from .scene_identifier import SceneIdentifier
from .scene_resolver import SceneResolver
from .visibility_context import VisibilityAwareContext
from .visibility_filtering import VisibilityFilteringService


@dataclass
class ContextBuildResult:
    """Result of a complete context build operation.

    Contains all context information needed by L4 agents, including
    the base context, visibility-filtered context, foreshadowing instructions,
    forbidden keywords, and collected hints.

    Attributes:
        context: Base filtered context from context integration.
        visibility_context: Visibility-filtered context (None if no controller).
        foreshadow_instructions: Generated foreshadowing instructions.
        forbidden_keywords: Aggregated forbidden keywords from all sources.
        hints: Collected hints from visibility and foreshadowing.
        success: Whether the build completed successfully.
        errors: List of error messages.
        warnings: List of warning messages.
    """

    context: FilteredContext
    visibility_context: VisibilityAwareContext | None
    foreshadow_instructions: ForeshadowInstructions
    forbidden_keywords: list[str]
    hints: HintCollection
    success: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def has_errors(self) -> bool:
        """Check if any errors occurred during build.

        Returns:
            True if there are errors.
        """
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if any warnings were generated during build.

        Returns:
            True if there are warnings.
        """
        return len(self.warnings) > 0


logger = logging.getLogger(__name__)


class ContextBuilder:
    """Unified facade for L3 context building.

    This is the single entry point for the L3 Context Builder layer.
    It orchestrates all internal components (collectors, integrator,
    foreshadowing, visibility, forbidden keywords, hints) to build
    complete context for L4 agents.

    Args:
        vault_root: Root path of the Obsidian vault.
        work_name: Name of the work (for foreshadowing repository).
        visibility_controller: Optional L2 visibility controller.
        foreshadowing_repository: Optional foreshadowing repository.

    Examples:
        >>> builder = ContextBuilder(vault_root=Path("vault"))
        >>> scene = SceneIdentifier(episode_id="ep010", sequence_id="seq_01")
        >>> result = builder.build_context(scene)
    """

    # Default phase order used when none is specified
    _DEFAULT_PHASE_ORDER: list[str] = [
        "initial",
        "development",
        "climax",
        "resolution",
    ]

    # Maximum number of cache entries per cache type
    _MAX_CACHE_SIZE: int = 128

    def __init__(
        self,
        vault_root: Path,
        *,
        work_name: str = "",
        visibility_controller: VisibilityController | None = None,
        foreshadowing_repository: ForeshadowingRepository | None = None,
        phase_order: list[str] | None = None,
    ) -> None:
        """Initialize ContextBuilder with all components.

        Args:
            vault_root: Root path of the Obsidian vault.
            work_name: Name of the work (for foreshadowing).
            visibility_controller: Optional L2 visibility controller.
            foreshadowing_repository: Optional foreshadowing repository.
            phase_order: Ordered list of narrative phases. Uses defaults if None.
        """
        self._vault_root = vault_root
        self._work_name = work_name
        self._phase_order = phase_order or self._DEFAULT_PHASE_ORDER

        # Core infrastructure
        self._loader = FileLazyLoader(vault_root)
        self._resolver = SceneResolver(vault_root)

        # Phase filters
        character_phase_filter = CharacterPhaseFilter(self._phase_order)
        world_phase_filter = WorldSettingPhaseFilter(self._phase_order)

        # Collectors
        self._plot_collector = PlotCollector(vault_root, self._loader)
        self._summary_collector = SummaryCollector(vault_root, self._loader)
        self._character_collector = CharacterCollector(
            vault_root, self._loader, self._resolver, character_phase_filter
        )
        self._world_collector = WorldSettingCollector(
            vault_root, self._loader, self._resolver, world_phase_filter
        )
        self._style_collector = StyleGuideCollector(vault_root, self._loader)

        # Context integrator
        self._integrator = ContextIntegratorImpl(vault_root)

        # Hint collector
        self._hint_collector = HintCollector()

        # Forbidden keyword collector
        self._forbidden_keyword_collector = ForbiddenKeywordCollector(
            vault_root, self._loader
        )

        # Visibility (optional L2 dependency)
        self._visibility_controller = visibility_controller
        self._visibility_filtering_service: VisibilityFilteringService | None = None
        if visibility_controller is not None:
            self._visibility_filtering_service = VisibilityFilteringService(
                visibility_controller
            )

        # Foreshadowing (optional L2 dependency)
        self._foreshadowing_repository = foreshadowing_repository
        self._foreshadowing_identifier: ForeshadowingIdentifier | None = None
        self._instruction_generator: InstructionGeneratorImpl | None = None
        if foreshadowing_repository is not None:
            self._foreshadowing_identifier = ForeshadowingIdentifier(
                foreshadowing_repository
            )
            self._instruction_generator = InstructionGeneratorImpl(
                foreshadowing_repository, self._foreshadowing_identifier
            )

        # Caches (OrderedDict for LRU eviction with size limit)
        self._instruction_cache: OrderedDict[str, ForeshadowInstructions] = OrderedDict()
        self._forbidden_cache: OrderedDict[str, list[str]] = OrderedDict()
        self._forbidden_result_cache: OrderedDict[str, ForbiddenKeywordResult] = (
            OrderedDict()
        )

    def _cache_put(self, cache: OrderedDict, key: str, value: object) -> None:  # type: ignore[type-arg]
        """Insert into a bounded cache, evicting oldest entry if full.

        Args:
            cache: The OrderedDict cache to insert into.
            key: Cache key.
            value: Value to cache.
        """
        if key in cache:
            cache.move_to_end(key)
        cache[key] = value
        while len(cache) > self._MAX_CACHE_SIZE:
            cache.popitem(last=False)

    def build_context(self, scene: SceneIdentifier) -> ContextBuildResult:
        """Build complete context for a scene.

        Orchestrates all components to produce a complete ContextBuildResult.
        This is the primary method called by L4 agents.

        Args:
            scene: The scene identifier.

        Returns:
            Complete build result with context, instructions, and metadata.
        """
        warnings: list[str] = []
        errors: list[str] = []
        logger.debug("Building context for scene %s:%s", scene.episode_id, scene.sequence_id)

        # 1. Context integration (collect all context data)
        try:
            context, integration_warnings = self._integrator.integrate_with_warnings(
                scene,
                plot_collector=self._plot_collector,
                summary_collector=self._summary_collector,
                character_collector=self._character_collector,
                world_collector=self._world_collector,
                style_collector=self._style_collector,
            )
            warnings.extend(integration_warnings)
        except (OSError, ValueError, KeyError, TypeError) as e:
            logger.error("Context integration failed: %s", e)
            errors.append(f"Context integration failed: {e}")
            context = FilteredContext()

        # 2. Foreshadowing instructions (optional)
        foreshadow_instructions = self.get_foreshadow_instructions(scene)

        # 3. Forbidden keywords (uses cache via get_forbidden_keywords)
        try:
            forbidden_keywords = self.get_forbidden_keywords(scene)
        except (OSError, ValueError, KeyError, TypeError) as e:
            logger.warning("Forbidden keyword collection failed: %s", e)
            warnings.append(f"Forbidden keyword collection failed: {e}")
            forbidden_keywords = []

        # 4. Visibility filtering (optional)
        visibility_context: VisibilityAwareContext | None = None
        if self._visibility_filtering_service is not None:
            try:
                visibility_context = (
                    self._visibility_filtering_service.filter_context(context)
                )
            except (OSError, ValueError, KeyError, TypeError) as e:
                logger.warning("Visibility filtering failed: %s", e)
                warnings.append(f"Visibility filtering failed: {e}")

        # 5. Hint collection
        hints = self._hint_collector.collect_all(
            visibility_context=visibility_context,
            foreshadow_instructions=foreshadow_instructions,
        )

        success = len(errors) == 0
        if success:
            logger.debug("Context build succeeded for %s:%s", scene.episode_id, scene.sequence_id)
        else:
            logger.warning("Context build completed with %d error(s)", len(errors))

        return ContextBuildResult(
            context=context,
            visibility_context=visibility_context,
            foreshadow_instructions=foreshadow_instructions,
            forbidden_keywords=forbidden_keywords,
            hints=hints,
            success=success,
            errors=errors,
            warnings=warnings,
        )

    def build_context_simple(self, scene: SceneIdentifier) -> FilteredContext:
        """Build context and return only the FilteredContext.

        A convenience method that returns just the base context
        without visibility filtering, instructions, or hints.

        Args:
            scene: The scene identifier.

        Returns:
            The base FilteredContext.
        """
        result = self.build_context(scene)
        return result.context

    def get_foreshadow_instructions(
        self, scene: SceneIdentifier, *, use_cache: bool = True
    ) -> ForeshadowInstructions:
        """Get foreshadowing instructions for a scene.

        Args:
            scene: The scene identifier.
            use_cache: Whether to use cached instructions. Default is True.

        Returns:
            Foreshadowing instructions.
        """
        cache_key = f"{scene.episode_id}:{scene.sequence_id}"

        if use_cache and cache_key in self._instruction_cache:
            logger.debug("Instruction cache hit for %s", cache_key)
            return self._instruction_cache[cache_key]

        if self._instruction_generator is None:
            instructions = ForeshadowInstructions()
        else:
            try:
                instructions = self._instruction_generator.generate(scene)
            except (OSError, ValueError, KeyError, TypeError) as e:
                logger.warning("Instruction generation failed for %s: %s", cache_key, e)
                instructions = ForeshadowInstructions()
                self._last_instruction_error = e

        self._cache_put(self._instruction_cache, cache_key, instructions)
        return instructions

    def get_forbidden_keywords(
        self, scene: SceneIdentifier, *, use_cache: bool = True
    ) -> list[str]:
        """Get forbidden keywords for a scene.

        Args:
            scene: The scene identifier.
            use_cache: Whether to use cached results. Default is True.

        Returns:
            List of forbidden keywords.
        """
        cache_key = f"{scene.episode_id}:{scene.sequence_id}"

        if use_cache and cache_key in self._forbidden_cache:
            logger.debug("Forbidden keyword cache hit for %s", cache_key)
            return self._forbidden_cache[cache_key]

        # Get foreshadowing instructions for forbidden expressions
        foreshadow_instructions = self.get_foreshadow_instructions(scene)

        # Collect forbidden keywords from all sources
        result = self._forbidden_keyword_collector.collect(scene, foreshadow_instructions)
        keywords = result.keywords
        logger.debug("Collected %d forbidden keywords for %s", len(keywords), cache_key)

        self._cache_put(self._forbidden_cache, cache_key, keywords)
        self._cache_put(self._forbidden_result_cache, cache_key, result)
        return keywords

    def get_foreshadow_instructions_as_prompt(self, scene: SceneIdentifier) -> str:
        """Get foreshadowing instructions formatted as a prompt.

        Args:
            scene: The scene identifier.

        Returns:
            Formatted string for prompt injection.
        """
        instructions = self.get_foreshadow_instructions(scene)
        return self._format_instructions_for_prompt(instructions)

    def get_active_foreshadowings(self, scene: SceneIdentifier) -> list[str]:
        """Get list of active foreshadowing IDs for a scene.

        Args:
            scene: The scene identifier.

        Returns:
            List of foreshadowing IDs that require action.
        """
        instructions = self.get_foreshadow_instructions(scene)
        return [inst.foreshadowing_id for inst in instructions.get_active_instructions()]

    def get_foreshadowing_summary(self, scene: SceneIdentifier) -> dict[InstructionAction, int]:
        """Get summary of foreshadowing instructions by action type.

        Args:
            scene: The scene identifier.

        Returns:
            Dictionary mapping action types to their counts.
        """
        instructions = self.get_foreshadow_instructions(scene)
        return instructions.count_by_action()

    def clear_instruction_cache(self) -> None:
        """Clear the instruction cache.

        This forces regeneration of instructions on the next call.
        """
        self._instruction_cache.clear()

    def _format_instructions_for_prompt(self, instructions: ForeshadowInstructions) -> str:
        """Format foreshadowing instructions for prompt injection.

        Args:
            instructions: The foreshadowing instructions.

        Returns:
            Formatted string suitable for LLM prompt.
        """
        active = instructions.get_active_instructions()
        if not active:
            return ""

        _ACTION_LABELS = {
            InstructionAction.PLANT: "設置",
            InstructionAction.REINFORCE: "強化",
            InstructionAction.HINT: "ヒント",
        }

        lines = ["## 伏線指示書\n"]
        for inst in active:
            label = _ACTION_LABELS.get(inst.action, str(inst.action.value))
            lines.append(f"### {inst.foreshadowing_id} [{label}]")
            if inst.note:
                lines.append(f"- 指示: {inst.note}")
            if inst.allowed_expressions:
                lines.append(f"- 使用可能な表現: {', '.join(inst.allowed_expressions)}")
            if inst.forbidden_expressions:
                lines.append(f"- 禁止表現: {', '.join(inst.forbidden_expressions)}")
            lines.append(f"- 繊細さ: {inst.subtlety_target}/10")
            lines.append("")

        return "\n".join(lines)

    # ---- Forbidden keyword methods (L3-7-1d) ----

    def get_forbidden_keywords_with_sources(
        self, scene: SceneIdentifier
    ) -> ForbiddenKeywordResult:
        """Get forbidden keywords with source information.

        Args:
            scene: The scene identifier.

        Returns:
            ForbiddenKeywordResult with keywords and source mapping.
        """
        cache_key = f"{scene.episode_id}:{scene.sequence_id}"
        if cache_key not in self._forbidden_result_cache:
            self.get_forbidden_keywords(scene)
        return self._forbidden_result_cache[cache_key]

    def get_forbidden_keywords_as_prompt(self, scene: SceneIdentifier) -> str:
        """Get forbidden keywords formatted as a prompt section.

        Args:
            scene: The scene identifier.

        Returns:
            Formatted string for prompt injection, or empty string if none.
        """
        keywords = self.get_forbidden_keywords(scene)
        if not keywords:
            return ""

        lines = [
            "## 禁止キーワード\n",
            "以下のキーワードは生成テキストに含めないでください：\n",
        ]
        for kw in keywords:
            lines.append(f"- {kw}")
        return "\n".join(lines)

    def get_forbidden_by_source(
        self, scene: SceneIdentifier
    ) -> dict[str, list[str]]:
        """Get forbidden keywords grouped by source.

        Args:
            scene: The scene identifier.

        Returns:
            Dictionary mapping source name to keywords from that source.
        """
        result = self.get_forbidden_keywords_with_sources(scene)
        return dict(result.sources)

    def check_text_for_forbidden(
        self, scene: SceneIdentifier, text: str
    ) -> list[str]:
        """Check text for forbidden keywords.

        Args:
            scene: The scene identifier.
            text: The text to check.

        Returns:
            List of forbidden keywords found in the text.
        """
        keywords = self.get_forbidden_keywords(scene)
        return [kw for kw in keywords if kw in text]

    def is_text_clean(self, scene: SceneIdentifier, text: str) -> bool:
        """Check if text contains no forbidden keywords.

        Args:
            scene: The scene identifier.
            text: The text to check.

        Returns:
            True if text contains no forbidden keywords.
        """
        return len(self.check_text_for_forbidden(scene, text)) == 0

    # ---- Cache management ----

    def clear_forbidden_cache(self) -> None:
        """Clear the forbidden keyword cache."""
        self._forbidden_cache.clear()
        self._forbidden_result_cache.clear()

    def clear_all_caches(self) -> None:
        """Clear all caches (instructions and forbidden keywords)."""
        self.clear_instruction_cache()
        self.clear_forbidden_cache()
