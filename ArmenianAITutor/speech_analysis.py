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

# Western ↔ Eastern Armenian consonant shift pairs.
# Whisper transcribes in Eastern Armenian spelling, but the app uses Western.
# These pairs sound the same but are written with different letters.
# We normalize both sides to a canonical form so the comparison is fair.
CONSONANT_SHIFT_MAP = {
    # Պ/պ (B in Western) → Բ/բ (B in Eastern) — B/P pair
    'Պ': 'Բ', 'պ': 'բ',
    # Կ/կ (G in Western) → Գ/գ (G in Eastern) — G/K pair
    'Կ': 'Գ', 'կ': 'գ',
    # Տ/տ (D in Western) → Դ/դ (D in Eastern) — D/T pair
    'Տ': 'Դ', 'տ': 'դ',
    # Ձ/ձ (TS in Western) → Ծ/ծ (TS in Eastern) — TS/DZ pair
    'Ձ': 'Ծ', 'ձ': 'ծ',
    # Չ/չ (CH in Western) → Ճ/ճ (CH in Eastern) — CH/J pair
    'Չ': 'Ճ', 'չ': 'ճ',
}


def _normalize_consonants(text: str) -> str:
    """
    Normalize Western/Eastern Armenian consonant shifts.

    Maps paired consonants to a canonical form so that the same spoken
    sound matches regardless of which orthography was used.
    """
    for eastern, western in CONSONANT_SHIFT_MAP.items():
        text = text.replace(eastern, western)
    return text


def _normalize_armenian(text: str) -> str:
    """
    Normalize Armenian text for fair comparison.

    Handles Unicode normalization, punctuation removal, apostrophe variants,
    Armenian-specific modifier marks, and Western/Eastern consonant shifts.
    """
    # Unicode NFC normalization
    text = unicodedata.normalize('NFC', text)

    # Normalize apostrophe variants to ASCII apostrophe
    for apo in ['\u2019', '\u02BC', '\u2018', '\u02BB']:
        text = text.replace(apo, "'")

    # Remove Armenian-specific punctuation marks
    armenian_punctuation = '\u055E\u055C\u055B\u0589\u058A\u055D'
    text = re.sub(f'[{armenian_punctuation}]', '', text)

    # Remove ASCII punctuation and apostrophes
    # Apostrophes appear in Western Armenian contractions (e.g., Inding'delays)
    # but Whisper never produces them
    text = re.sub(r"[.,!?;:\-\"\(\)']", '', text)

    # Normalize consonant shifts (Western ↔ Eastern)
    text = _normalize_consonants(text)

    # Lowercase (Armenian has case: upper Ա-Ֆ, lower ա-ֆ)
    text = text.lower()

    # Collapse whitespace and strip
    text = ' '.join(text.split()).strip()

    return text


def _word_similarity(word1: str, word2: str) -> float:
    """Character-level similarity between two words (0.0 to 1.0)."""
    return SequenceMatcher(None, word1, word2).ratio()


def _contains_armenian(text: str) -> bool:
    """Check if text contains any Armenian Unicode characters."""
    return any('\u0530' <= c <= '\u058F' for c in text)


def _merge_short_prefixes(words: list) -> list:
    """
    Merge short Armenian prefix particles with the following word.

    The Western Armenian present tense prefix (կe/գe) is often written
    as a separate word, but Whisper consistently merges it with the verb.
    By merging prefixes on both sides before comparison, we ensure fair
    matching regardless of word boundary differences.

    Examples:
        ["ես", "գe", "տesnem"]  → ["ես", "գeտesnem"]
        ["ես", "գeտesnem"]      → ["ես", "գeտesnem"]  (no change)
    """
    if len(words) <= 1:
        return words

    merged = []
    i = 0
    while i < len(words):
        # If this word is 1-2 Armenian chars and there's a next word, merge them.
        # This handles prefixes like գe (ge/ke) that Whisper joins to the verb.
        if (i + 1 < len(words)
                and len(words[i]) <= 2
                and all('\u0530' <= c <= '\u058F' for c in words[i])):
            merged.append(words[i] + words[i + 1])
            i += 2
        else:
            merged.append(words[i])
            i += 1
    return merged


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

    Uses word-level comparison with:
    1. Consonant shift normalization (Western ↔ Eastern)
    2. Prefix merging (handles կe/գe present tense prefix)
    3. Fuzzy matching with length-aware thresholds
    4. Sentence-level character similarity as fallback
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

    # Merge short prefixes (e.g., կe/գe) with following word.
    # Whisper consistently merges the present tense prefix with the verb,
    # so we normalize both sides to match.
    t_words = _merge_short_prefixes(t_words)
    e_words = _merge_short_prefixes(e_words)

    # Fuzzy word matching: for each expected word, find best match
    # in transcribed words. Use length-aware threshold since short words
    # (3-4 chars) drop drastically with a single char difference.
    #   1-3 chars: 50% threshold (1 of 2 or 2 of 3 chars match)
    #   4-5 chars: 60% threshold
    #   6+  chars: 70% threshold
    used_t_indices = set()
    word_matches = []

    for e_word in e_words:
        best_sim = 0.0
        best_idx = -1

        for t_idx, t_word in enumerate(t_words):
            if t_idx in used_t_indices:
                continue
            sim = _word_similarity(e_word, t_word)
            if sim > best_sim:
                best_sim = sim
                best_idx = t_idx

        # Length-aware threshold
        word_len = len(e_word)
        if word_len <= 3:
            threshold = 0.50
        elif word_len <= 5:
            threshold = 0.60
        else:
            threshold = 0.70

        matched = best_sim >= threshold
        if matched and best_idx >= 0:
            used_t_indices.add(best_idx)

        word_matches.append((e_word, matched))

    matched_count = sum(1 for _, m in word_matches if m)
    word_accuracy = (matched_count / len(e_words)) * 100.0

    # Sentence-level fallback: compare joined strings character-by-character.
    # This handles cases where word boundaries differ but the overall
    # pronunciation is correct (e.g., Whisper merging prefix with verb).
    t_joined = ''.join(t_words)
    e_joined = ''.join(e_words)
    sentence_accuracy = SequenceMatcher(None, t_joined, e_joined).ratio() * 100.0

    # Use the better of word-level or sentence-level accuracy
    accuracy = max(word_accuracy, sentence_accuracy)

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
