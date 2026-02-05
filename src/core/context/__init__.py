"""L3: Context Builder Layer.

This layer is responsible for building filtered context for AI agents.
It integrates L2 services (visibility control, expression filter, foreshadowing manager)
to construct the appropriate context for each scene.
"""

# Phase F: Context Builder Facade
from .context_builder import ContextBuilder, ContextBuildResult

# Phase A: Data classes and protocols
from .context_integrator import ContextCollector, ContextIntegrator
from .filtered_context import FilteredContext
from .foreshadow_instruction import (
    ForeshadowInstruction,
    ForeshadowInstructions,
    InstructionAction,
)
from .foreshadowing_checker import (
    AlertSeverity,
    AlertType,
    ForeshadowingAlert,
    PayoffApproaching,
    PlantSuggestion,
    ReinforceSuggestion,
    SceneForeshadowingCheck,
    SceneForeshadowingChecker,
)
from .instruction_generator import InstructionGenerator
from .lazy_loader import (
    CacheEntry,
    ContentType,
    FileLazyLoader,
    GracefulLoader,
    GracefulLoadResult,
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

# Phase F: Write Facade
from .write_facade import (
    DependencyNotConfiguredError,
    WriteFacade,
    WriteFacadeError,
    WriteOperationError,
)

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
    "GracefulLoader",
    "GracefulLoadResult",
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
    # Foreshadowing checker (integrated check output)
    "AlertSeverity",
    "AlertType",
    "ForeshadowingAlert",
    "PayoffApproaching",
    "PlantSuggestion",
    "ReinforceSuggestion",
    "SceneForeshadowingCheck",
    "SceneForeshadowingChecker",
    # Visibility-aware context
    "VisibilityAwareContext",
    "VisibilityHint",
    # Context integration
    "ContextCollector",
    "ContextIntegrator",
    # Context Builder (L3-7 Facade)
    "ContextBuilder",
    "ContextBuildResult",
    # Write Facade (L3 Write Operations)
    "DependencyNotConfiguredError",
    "WriteFacade",
    "WriteFacadeError",
    "WriteOperationError",
]
