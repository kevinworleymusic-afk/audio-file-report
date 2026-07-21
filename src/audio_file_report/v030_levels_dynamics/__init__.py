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
from .clipping_limiting_indicators import analyze_clipping_limiting_indicators
from .dc_waveform_center_measurements import analyze_dc_waveform_center_measurements
from .dynamic_envelope import analyze_dynamic_envelope
from .gain_normalization_information import analyze_gain_normalization_information
from .level_distribution import analyze_level_distribution
from .rms_crest_factor import analyze_rms_crest_factor
from .silence_dropout_analysis import analyze_silence_dropout_analysis

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
    "analyze_clipping_limiting_indicators",
    "analyze_dc_waveform_center_measurements",
    "analyze_dynamic_envelope",
    "analyze_gain_normalization_information",
    "analyze_level_distribution",
    "analyze_rms_crest_factor",
    "analyze_silence_dropout_analysis",
]
