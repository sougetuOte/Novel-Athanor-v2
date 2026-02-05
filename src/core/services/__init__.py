"""L2: Service Layer.

This layer provides core services for AI information control:
- Expression filtering and forbidden keyword detection
- Visibility-based content filtering
- Foreshadowing state management and visibility mapping
- Timeline indexing for cross-episode queries
"""

# Expression filter
from .expression_filter import (
    KeywordViolation,
    SafetyCheckResult,
    check_forbidden_keywords,
    check_text_safety,
)

# Foreshadowing manager
from .foreshadowing_manager import (
    STATUS_VISIBILITY_MAP,
    VALID_TRANSITIONS,
    ForeshadowingManager,
    get_recommended_visibility,
    get_visibility_from_subtlety,
    validate_status_transition,
)

# Timeline index
from .timeline_index import TimelineEvent, TimelineIndex

# Visibility controller
from .visibility_controller import (
    VisibilityController,
    VisibilityFilteredContent,
    filter_content_by_visibility,
    generate_level1_template,
    generate_level2_template,
)

__all__ = [
    # Expression filter
    "KeywordViolation",
    "SafetyCheckResult",
    "check_forbidden_keywords",
    "check_text_safety",
    # Visibility controller
    "VisibilityFilteredContent",
    "VisibilityController",
    "filter_content_by_visibility",
    "generate_level1_template",
    "generate_level2_template",
    # Foreshadowing manager
    "ForeshadowingManager",
    "VALID_TRANSITIONS",
    "STATUS_VISIBILITY_MAP",
    "validate_status_transition",
    "get_recommended_visibility",
    "get_visibility_from_subtlety",
    # Timeline index
    "TimelineEvent",
    "TimelineIndex",
]
