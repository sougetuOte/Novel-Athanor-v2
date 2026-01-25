"""L3: Context Builder Layer.

This layer is responsible for building filtered context for AI agents.
It integrates L2 services (visibility control, expression filter, foreshadowing manager)
to construct the appropriate context for each scene.
"""

# Phase A: Data classes and protocols
from .scene_identifier import SceneIdentifier
from .lazy_loader import LazyLoader, LazyLoadResult, LoadPriority
from .phase_filter import PhaseFilter, PhaseFilterError, InvalidPhaseError
from .filtered_context import FilteredContext
from .foreshadow_instruction import (
    ForeshadowInstruction,
    ForeshadowInstructions,
    InstructionAction,
)
from .visibility_context import VisibilityAwareContext, VisibilityHint

__all__ = [
    # Scene identification
    "SceneIdentifier",
    # Lazy loading
    "LazyLoader",
    "LazyLoadResult",
    "LoadPriority",
    # Phase filtering
    "PhaseFilter",
    "PhaseFilterError",
    "InvalidPhaseError",
    # Context data
    "FilteredContext",
    # Foreshadowing
    "ForeshadowInstruction",
    "ForeshadowInstructions",
    "InstructionAction",
    # Visibility-aware context
    "VisibilityAwareContext",
    "VisibilityHint",
]
