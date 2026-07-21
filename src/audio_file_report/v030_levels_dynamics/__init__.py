"""Version 0.3.0 workstream package."""

from .metrics import (
    ClippingEvent,
    GainPreview,
    LevelMetrics,
    SilenceRegion,
    StereoLevelComparison,
    compare_stereo_levels,
    compute_gain_preview,
    compute_level_metrics,
    compute_linked_stereo_gain_preview,
    compute_threshold_distribution,
    compute_windowed_rms,
    dbfs_from_linear,
    detect_clipping_events,
    detect_silence_regions,
    normalize_to_full_scale,
)
from .fundamental_amplitude import analyze_fundamental_amplitude
from .dynamic_envelope import analyze_dynamic_envelope
from .level_distribution import analyze_level_distribution
from .rms_crest_factor import analyze_rms_crest_factor

__all__ = [
    "ClippingEvent",
    "GainPreview",
    "LevelMetrics",
    "SilenceRegion",
    "StereoLevelComparison",
    "compare_stereo_levels",
    "compute_gain_preview",
    "compute_level_metrics",
    "compute_linked_stereo_gain_preview",
    "compute_threshold_distribution",
    "compute_windowed_rms",
    "dbfs_from_linear",
    "detect_clipping_events",
    "detect_silence_regions",
    "normalize_to_full_scale",
    "analyze_fundamental_amplitude",
    "analyze_dynamic_envelope",
    "analyze_level_distribution",
    "analyze_rms_crest_factor",
]
