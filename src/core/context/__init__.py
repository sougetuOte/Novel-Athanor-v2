"""L3: Context Builder Layer.

This layer is responsible for building filtered context for AI agents.
It integrates L2 services (visibility control, expression filter, foreshadowing manager)
to construct the appropriate context for each scene.
"""

# Phase A: Data classes and protocols
from .context_integrator import ContextCollector, ContextIntegrator
from .filtered_context import FilteredContext
from .foreshadow_instruction import (
    ForeshadowInstruction,
    ForeshadowInstructions,
    InstructionAction,
)
from .instruction_generator import InstructionGenerator
from .lazy_loader import (
    CacheEntry,
    ContentType,
    FileLazyLoader,
    LazyLoadedContent,
    LazyLoader,
    LazyLoadResult,
    LoadPriority,
)
from .phase_filter import (
    CharacterPhaseFilter,
    InvalidPhaseError,
    PhaseFilter,
    PhaseFilterError,
    WorldSettingPhaseFilter,
)
from .scene_identifier import SceneIdentifier
from .scene_resolver import ResolvedPaths, SceneResolver
from .visibility_context import VisibilityAwareContext, VisibilityHint

__all__ = [
    # Scene identification
    "SceneIdentifier",
    # Scene resolution
    "ResolvedPaths",
    "SceneResolver",
    # Lazy loading
    "CacheEntry",
    "ContentType",
    "FileLazyLoader",
    "LazyLoadedContent",
    "LazyLoader",
    "LazyLoadResult",
    "LoadPriority",
    # Phase filtering
    "PhaseFilter",
    "PhaseFilterError",
    "InvalidPhaseError",
    "CharacterPhaseFilter",
    "WorldSettingPhaseFilter",
    # Context data
    "FilteredContext",
    # Foreshadowing
    "ForeshadowInstruction",
    "ForeshadowInstructions",
    "InstructionAction",
    "InstructionGenerator",
    # Visibility-aware context
    "VisibilityAwareContext",
    "VisibilityHint",
    # Context integration
    "ContextCollector",
    "ContextIntegrator",
]
