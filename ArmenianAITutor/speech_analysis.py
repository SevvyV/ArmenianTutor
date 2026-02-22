"""
Speech Analysis Module for Armenian Tutor.

Handles:
- Audio recording via st.audio_input()
- Transcription via OpenAI Whisper (Armenian)
- Word-level comparison against expected text
- Color-coded feedback UI
"""

import io
import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher

import streamlit as st
from openai import OpenAI

from config import WHISPER_MODEL, WHISPER_LANGUAGE, SPEECH_ACCURACY_THRESHOLD


class SpeechAnalysisError(Exception):
    """Raised when speech analysis fails."""
    pass


@dataclass
class ComparisonResult:
    """Result of comparing transcribed vs expected Armenian text."""
    transcribed: str
    expected: str
    accuracy: float
    is_match: bool
    word_matches: list  # [(word, matched: bool), ...]


# ============================================================================
# TEXT NORMALIZATION
# ============================================================================

def _normalize_armenian(text: str) -> str:
    """
    Normalize Armenian text for fair comparison.

    Handles Unicode normalization, punctuation removal, apostrophe variants,
    and Armenian-specific modifier marks that Whisper will not produce.
    """
    # Unicode NFC normalization
    text = unicodedata.normalize('NFC', text)

    # Normalize apostrophe variants to ASCII apostrophe
    for apo in ['\u2019', '\u02BC', '\u2018', '\u02BB']:
        text = text.replace(apo, "'")

    # Remove Armenian-specific punctuation marks
    armenian_punctuation = '\u055E\u055C\u055B\u0589\u058A\u055D'
    text = re.sub(f'[{armenian_punctuation}]', '', text)

    # Remove ASCII punctuation
    text = re.sub(r'[.,!?;:\-\"\(\)]', '', text)

    # Lowercase (Armenian has case: upper Ա-Ֆ, lower ա-ֆ)
    text = text.lower()

    # Collapse whitespace and strip
    text = ' '.join(text.split()).strip()

    return text


def _contains_armenian(text: str) -> bool:
    """Check if text contains any Armenian Unicode characters."""
    return any('\u0530' <= c <= '\u058F' for c in text)


# ============================================================================
# TRANSCRIPTION
# ============================================================================

def transcribe_audio(audio_bytes: bytes, api_key: str) -> str:
    """
    Send audio to OpenAI Whisper and return Armenian transcription.

    Args:
        audio_bytes: Raw audio data from st.audio_input() (WAV format)
        api_key: OpenAI API key

    Returns:
        Transcribed Armenian text
    """
    try:
        client = OpenAI(api_key=api_key)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "recording.wav"

        response = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=audio_file,
            language=WHISPER_LANGUAGE
        )
        return response.text
    except Exception as e:
        error_type = type(e).__name__
        if "AuthenticationError" in error_type:
            raise SpeechAnalysisError("Invalid OpenAI API key.")
        elif "RateLimitError" in error_type:
            raise SpeechAnalysisError("API rate limit reached. Please wait and try again.")
        elif "APIConnectionError" in error_type:
            raise SpeechAnalysisError("Could not connect to OpenAI. Check your internet.")
        else:
            raise SpeechAnalysisError(f"Transcription failed: {str(e)}")


# ============================================================================
# COMPARISON
# ============================================================================

def compare_armenian_text(transcribed: str, expected: str) -> ComparisonResult:
    """
    Compare transcribed text against expected Armenian text.

    Uses word-level comparison via SequenceMatcher for meaningful
    language learning feedback.
    """
    t_norm = _normalize_armenian(transcribed)
    e_norm = _normalize_armenian(expected)

    t_words = t_norm.split()
    e_words = e_norm.split()

    if not e_words:
        accuracy = 100.0 if not t_words else 0.0
        return ComparisonResult(
            transcribed=transcribed,
            expected=expected,
            accuracy=accuracy,
            is_match=accuracy >= SPEECH_ACCURACY_THRESHOLD,
            word_matches=[]
        )

    # Find matching words using SequenceMatcher
    matcher = SequenceMatcher(None, e_words, t_words)
    matched_indices = set()
    for block in matcher.get_matching_blocks():
        for i in range(block.size):
            matched_indices.add(block.a + i)

    word_matches = [(e_words[i], i in matched_indices) for i in range(len(e_words))]
    accuracy = (len(matched_indices) / len(e_words)) * 100.0

    return ComparisonResult(
        transcribed=transcribed,
        expected=expected,
        accuracy=accuracy,
        is_match=accuracy >= SPEECH_ACCURACY_THRESHOLD,
        word_matches=word_matches
    )


def analyze_pronunciation(
    audio_bytes: bytes,
    expected_armenian: str,
    api_key: str
) -> ComparisonResult:
    """
    Transcribe audio and compare against expected Armenian text.
    """
    transcribed = transcribe_audio(audio_bytes, api_key)

    if not transcribed.strip():
        raise SpeechAnalysisError(
            "No speech detected. Please try again."
        )

    if not _contains_armenian(transcribed):
        raise SpeechAnalysisError(
            "Could not recognize Armenian speech. "
            "Try speaking more clearly or closer to the microphone."
        )

    return compare_armenian_text(transcribed, expected_armenian)


# ============================================================================
# UI RENDERING
# ============================================================================

def render_speech_feedback(result: ComparisonResult):
    """Render color-coded pronunciation feedback."""
    # Accuracy indicator
    if result.accuracy >= 90:
        st.success(f"Excellent! {result.accuracy:.0f}% accuracy")
    elif result.accuracy >= SPEECH_ACCURACY_THRESHOLD:
        st.warning(f"Good try! {result.accuracy:.0f}% accuracy")
    else:
        st.error(f"Keep practicing! {result.accuracy:.0f}% accuracy")

    # Expected vs heard
    st.markdown(f"**Expected:** {result.expected}")
    st.markdown(f"**You said:** {result.transcribed}")

    # Word-by-word color-coded breakdown
    if result.word_matches:
        colored_words = []
        for word, matched in result.word_matches:
            if matched:
                colored_words.append(
                    f'<span style="color: green; font-weight: bold;">{word}</span>'
                )
            else:
                colored_words.append(
                    f'<span style="color: red; text-decoration: underline;">{word}</span>'
                )
        st.markdown(
            "**Word Match:** " + " ".join(colored_words),
            unsafe_allow_html=True
        )


def render_mic_button(expected_armenian: str, widget_key: str):
    """
    Render the microphone input widget and pronunciation feedback.

    Args:
        expected_armenian: The target armenian_display text
        widget_key: Unique Streamlit key for this widget instance
    """
    # Skip if no API key configured
    if "OPENAI_API_KEY" not in st.secrets:
        return

    with st.expander("🎤 Practice Speaking", expanded=False):
        audio_data = st.audio_input("Record yourself:", key=widget_key)

        if audio_data is not None:
            result_key = f"result_{widget_key}"
            audio_hash = hash(audio_data.getvalue())
            hash_key = f"hash_{widget_key}"

            # Only call Whisper if this is a new recording
            if st.session_state.get(hash_key) != audio_hash:
                st.session_state[hash_key] = audio_hash
                try:
                    api_key = st.secrets["OPENAI_API_KEY"]
                    result = analyze_pronunciation(
                        audio_data.getvalue(),
                        expected_armenian,
                        api_key
                    )
                    st.session_state[result_key] = result
                except SpeechAnalysisError as e:
                    st.session_state[result_key] = None
                    st.error(str(e))
                except Exception as e:
                    st.session_state[result_key] = None
                    st.error(f"An error occurred: {str(e)}")

            # Display cached result
            if st.session_state.get(result_key):
                render_speech_feedback(st.session_state[result_key])
