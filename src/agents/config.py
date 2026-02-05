"""L4 Agent pipeline configuration constants.

パイプライン実行時の定数と閾値を定義する。
ランタイム変更可能な設定は PipelineConfig モデルを使用すること。
"""

from __future__ import annotations

# --- Review Settings ---
MAX_REVIEW_RETRIES: int = 3
"""レビューリトライ最大回数。超過時は Human Fallback。"""

HUMAN_FALLBACK_ENABLED: bool = True
"""Human Fallback の有効/無効。"""

# --- Quality Thresholds ---
QUALITY_THRESHOLD_EXCELLENT: float = 0.85
"""Excellent 評価の閾値。"""

QUALITY_THRESHOLD_GOOD: float = 0.70
"""Good 評価の閾値。"""

QUALITY_THRESHOLD_ACCEPTABLE: float = 0.50
"""Acceptable 評価の閾値（これ未満は needs_improvement）。"""

# まとめて dict でも提供
QUALITY_THRESHOLDS: dict[str, float] = {
    "excellent": QUALITY_THRESHOLD_EXCELLENT,
    "good": QUALITY_THRESHOLD_GOOD,
    "acceptable": QUALITY_THRESHOLD_ACCEPTABLE,
}

# --- Default Scene Settings ---
DEFAULT_WORD_COUNT: int = 3000
"""デフォルトのシーン語数目標。"""

DEFAULT_POV: str = "三人称限定視点"
"""デフォルトの視点。"""


# --- Utility Functions ---
def get_assessment(overall_score: float) -> str:
    """overall スコアから QualityAssessment 文字列を判定する.

    Args:
        overall_score: 0.0-1.0 の品質スコア

    Returns:
        "excellent", "good", "acceptable", or "needs_improvement"

    Raises:
        ValueError: overall_score が 0.0-1.0 の範囲外の場合
    """
    if not 0.0 <= overall_score <= 1.0:
        msg = f"Score must be between 0.0 and 1.0, got {overall_score}"
        raise ValueError(msg)
    if overall_score >= QUALITY_THRESHOLD_EXCELLENT:
        return "excellent"
    if overall_score >= QUALITY_THRESHOLD_GOOD:
        return "good"
    if overall_score >= QUALITY_THRESHOLD_ACCEPTABLE:
        return "acceptable"
    return "needs_improvement"
