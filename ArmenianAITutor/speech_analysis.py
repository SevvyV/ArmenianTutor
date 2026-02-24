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
import wave
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher

import streamlit as st
from openai import OpenAI

from config import (
    WHISPER_MODEL, WHISPER_LANGUAGE, SPEECH_ACCURACY_THRESHOLD,
    MAX_RECORDING_SECONDS, MIN_RECORDING_SECONDS, DEBUG_SPEECH
)


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

# ── Consonant swap: convert Western Armenian spelling → Eastern Armenian ──
# Same swap used by TTS (generate_audio_dual.py). Applied to the EXPECTED
# text before comparing with Whisper output, so both sides are in Eastern form.
# Bidirectional: Բ↔Պ, Գ↔Կ, Դ↔Տ, Ծ↔Ձ, Ճ↔Ջ (plus lowercase).
WESTERN_TO_EASTERN_SWAP = str.maketrans(
    "ԲբՊպԳգԿկԴդՏտԾծՁձՃճՋջ",
    "ՊպԲբԿկԳգՏտԴդՁձԾծՋջՃճ",
)

# ── Sounds-alike normalization ──
# After converting expected to Eastern, Whisper may still use variant letters
# for similar sounds. These map all variants to a single canonical form.
SOUNDS_ALIKE_MAP = {
    # Ց(U+0551, Co/Tso) → Ծ(U+053E, Tsa) — both make TS sound
    'Ց': 'Ծ', 'ց': 'ծ',
    # Չ(U+0549, Cha) → Ճ(U+0543, Cha) — both make CH sound
    'Չ': 'Ճ', 'չ': 'ճ',
    # Փ(U+0553, Piwr) → Պ(U+054A, Peh) — both make P sound
    'Փ': 'Պ', 'փ': 'պ',
    # Ք(U+0554, Keh) → Կ(U+053F, Ken) — both make K sound
    'Ք': 'Կ', 'ք': 'կ',
    # Թ(U+0539, To) → Տ(U+054F, Tiwn) — both make T sound
    'Թ': 'Տ', 'թ': 'տ',
    # Ւ(U+0552, Yiwn) → Վ(U+054E, Vew) — both make V sound
    # Western uses Yiwn, Eastern uses Vew for "v" (e.g., Barev)
    'Ւ': 'Վ', 'ւ': 'վ',
}


def _normalize_sounds_alike(text: str) -> str:
    """Map variant letters that sound alike to a canonical form."""
    for variant, canonical in SOUNDS_ALIKE_MAP.items():
        text = text.replace(variant, canonical)
    return text


def _normalize_armenian(text: str) -> str:
    """
    Normalize Armenian text for fair comparison.

    Handles Unicode normalization, punctuation removal, apostrophe variants,
    Armenian-specific modifier marks, and sounds-alike consolidation.
    NOTE: Does NOT do consonant shifts — the expected text is converted to
    Eastern form before this function is called.
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
    # Apostrophes appear in Western Armenian contractions
    # but Whisper never produces them
    text = re.sub(r"[.,!?;:\-\"\(\)']", '', text)

    # Normalize sounds-alike variants (e.g., Whisper uses Փ where we expect Պ)
    text = _normalize_sounds_alike(text)

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

def _debug_print(msg: str):
    """Print debug message, handling Windows cp1252 encoding."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))


def _debug_codepoints(label: str, text: str):
    """Print Unicode codepoints for each character (debug helper)."""
    chars = ' '.join(f'U+{ord(c):04X}' for c in text)
    # Use Unicode escapes for the text repr to avoid Windows encoding issues
    safe_repr = ''.join(
        c if ord(c) < 128 else f'\\u{ord(c):04X}' for c in text
    )
    _debug_print(f"  {label}: \"{safe_repr}\"")
    _debug_print(f"    codepoints: {chars}")


def compare_armenian_text(transcribed: str, expected: str) -> ComparisonResult:
    """
    Compare transcribed text against expected Armenian text.

    Uses word-level comparison with:
    1. Consonant shift normalization (Western ↔ Eastern)
    2. Prefix merging (handles կe/գe present tense prefix)
    3. Fuzzy matching with length-aware thresholds
    4. Sentence-level character similarity as fallback
    """
    # Convert expected text from Western → Eastern consonants so both sides
    # are in the same orthography that Whisper uses. The UI still shows the
    # original Western text — this transform is only for comparison.
    expected_eastern = expected.translate(WESTERN_TO_EASTERN_SWAP)

    t_norm = _normalize_armenian(transcribed)
    e_norm = _normalize_armenian(expected_eastern)

    if DEBUG_SPEECH:
        _debug_print("\n=== SPEECH COMPARISON DEBUG ===")
        _debug_codepoints("Expected (raw Western)", expected)
        _debug_codepoints("Expected (Eastern swap)", expected_eastern)
        _debug_codepoints("Transcribed (raw)", transcribed)
        _debug_codepoints("Expected (normalized)", e_norm)
        _debug_codepoints("Transcribed (normalized)", t_norm)
        _debug_print(f"  Normalized match: {t_norm == e_norm}")

    t_words = t_norm.split()
    e_words = e_norm.split()

    # Keep original Western expected words for display in word_matches UI.
    # Strip punctuation so word count aligns with normalized version.
    orig_expected_words = re.sub(r"[.,!?;:\-\"\(\)']", '', expected).split()

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
    orig_expected_words = _merge_short_prefixes(orig_expected_words)

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

        # Use original Western word for display (if available), normalized for matching
        display_word = orig_expected_words[len(word_matches)] if len(word_matches) < len(orig_expected_words) else e_word
        word_matches.append((display_word, matched))

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

    if DEBUG_SPEECH:
        # Word matches may contain Armenian chars — make safe
        safe_matches = [
            (''.join(f'\\u{ord(c):04X}' if ord(c) > 127 else c for c in w), m)
            for w, m in word_matches
        ]
        _debug_print(f"  Word matches: {safe_matches}")
        _debug_print(f"  Word accuracy: {word_accuracy:.1f}%")
        _debug_print(f"  Sentence accuracy: {sentence_accuracy:.1f}%")
        _debug_print(f"  Final accuracy: {accuracy:.1f}%")
        _debug_print("=== END DEBUG ===\n")

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
# WEBM TRANSCRIPTION (for auto-record segment player component)
# ============================================================================

def transcribe_audio_webm(audio_bytes: bytes, api_key: str) -> str:
    """
    Send WebM/Opus audio to OpenAI Whisper and return Armenian transcription.

    The segment_player component captures audio as WebM/Opus via MediaRecorder.
    Whisper accepts WebM natively — no conversion needed.
    """
    try:
        client = OpenAI(api_key=api_key)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "recording.webm"

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


def analyze_pronunciation_b64(
    audio_b64: str,
    expected_armenian: str,
    api_key: str
) -> ComparisonResult:
    """
    Decode base64 WebM audio, transcribe, and compare against expected text.

    Used by the Pimsleur segment_player component which returns audio as base64.
    """
    import base64
    audio_bytes = base64.b64decode(audio_b64)
    transcribed = transcribe_audio_webm(audio_bytes, api_key)

    if not transcribed.strip():
        raise SpeechAnalysisError("No speech detected. Please try again.")

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


def _get_wav_duration(audio_bytes: bytes) -> float:
    """Get duration of WAV audio in seconds."""
    try:
        with wave.open(io.BytesIO(audio_bytes), 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            if rate == 0:
                return 0.0
            return frames / rate
    except Exception:
        return 0.0


def render_mic_button(expected_armenian: str, widget_key: str):
    """
    Render the microphone input widget and pronunciation feedback.
    Wrapped in an expander (collapsed by default) — for vocab/sentence tabs.

    Args:
        expected_armenian: The target armenian_display text
        widget_key: Unique Streamlit key for this widget instance
    """
    # Skip if no API key configured
    if "OPENAI_API_KEY" not in st.secrets:
        return

    with st.expander("🎤 Practice Speaking", expanded=False):
        _render_mic_core(expected_armenian, widget_key)


def render_mic_inline(expected_armenian: str, widget_key: str):
    """
    Render the microphone input widget INLINE (no expander).
    Used by the Pimsleur lesson player where the mic should be prominent.

    Args:
        expected_armenian: The target armenian_display text
        widget_key: Unique Streamlit key for this widget instance
    """
    if "OPENAI_API_KEY" not in st.secrets:
        st.info("Speech practice requires an OpenAI API key in Streamlit secrets.")
        return

    st.markdown("#### Record yourself:")
    _render_mic_core(expected_armenian, widget_key)


def _render_mic_core(expected_armenian: str, widget_key: str):
    """
    Core mic recording + Whisper analysis logic.
    Called by both render_mic_button (expander) and render_mic_inline (no expander).
    """
    audio_data = st.audio_input("Record yourself:", key=widget_key)

    if audio_data is not None:
        audio_bytes = audio_data.getvalue()
        duration = _get_wav_duration(audio_bytes)

        # Safeguard: reject recordings that are too short or too long
        if duration < MIN_RECORDING_SECONDS:
            st.warning("Recording too short. Please try again.")
            return
        if duration > MAX_RECORDING_SECONDS:
            st.warning(
                f"Recording too long ({duration:.0f}s). "
                f"Please keep recordings under {MAX_RECORDING_SECONDS}s."
            )
            return

        result_key = f"result_{widget_key}"
        audio_hash = hash(audio_bytes)
        hash_key = f"hash_{widget_key}"

        # Only call Whisper if this is a new recording
        if st.session_state.get(hash_key) != audio_hash:
            st.session_state[hash_key] = audio_hash
            try:
                api_key = st.secrets["OPENAI_API_KEY"]
                result = analyze_pronunciation(
                    audio_bytes,
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
