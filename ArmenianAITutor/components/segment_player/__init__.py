"""
Bidirectional Streamlit component for Pimsleur lesson segments.

Combines audio playback with auto-recording and silence detection.
Returns structured data to Python via Streamlit.setComponentValue().
"""

import os
import streamlit.components.v1 as components

_COMPONENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

_component_func = components.declare_component(
    "segment_player",
    path=_COMPONENT_DIR,
)


def segment_player(
    audio_urls: list,
    has_pause: bool,
    practice_text: str = "",
    practice_phonetic: str = "",
    practice_english: str = "",
    segment_index: int = 0,
    audio_gap_ms: int = 400,
    silence_threshold_db: float = -45.0,
    silence_duration_ms: int = 1000,
    recording_delay_ms: int = 800,
    skip_audio: bool = False,
    key: str = None,
) -> dict | None:
    """
    Render the segment player component.

    Returns None while playing/recording.
    Returns dict when an event occurs:
      - {"type": "segment_complete"}
      - {"type": "practice_audio", "audio_b64": "...", "duration": float}
      - {"type": "error", "message": "..."}
    """
    return _component_func(
        audio_urls=audio_urls,
        has_pause=has_pause,
        practice_text=practice_text,
        practice_phonetic=practice_phonetic,
        practice_english=practice_english,
        segment_index=segment_index,
        audio_gap_ms=audio_gap_ms,
        silence_threshold_db=silence_threshold_db,
        silence_duration_ms=silence_duration_ms,
        recording_delay_ms=recording_delay_ms,
        skip_audio=skip_audio,
        key=key,
        default=None,
    )
