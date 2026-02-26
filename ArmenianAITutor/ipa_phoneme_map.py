"""
IPA Phoneme Map for Armenian Instructor TTS.

Maps Armenian phonetic tokens to IPA (International Phonetic Alphabet)
transcriptions for use with Azure TTS SSML <phoneme> tags. This gives
precise pronunciation control for the English instructor voice
(en-US-JennyNeural) when it reads Armenian phonetic fragments.

Architecture:
    Instructor text like "Say: tyoon" is scanned for tokens in
    ARMENIAN_IPA_MAP. Matched tokens get wrapped in SSML <phoneme> tags;
    unmatched text passes through unchanged. The result is a complete
    SSML envelope ready for speak_ssml_async().

    If no tokens match, wrap_instructor_text_ssml() returns None and the
    caller falls back to the regex-based apply_tts_fixes() pipeline.

en-US IPA Phone Set Limitations:
    Azure's en-US voice supports a SUBSET of IPA. Key phones NOT available:
        - ts (voiceless alveolar affricate) -- use t+s as two phones
        - gh/x (voiceless velar fricative) -- use k
        - tʰ (aspirated t) -- use plain t
        - ɣ (voiced velar/uvular fricative) -- use g

    Supported consonants:
        b d f g h j k l m n ŋ p ɹ s ʃ t θ ð v w z ʒ tʃ dʒ

    Supported vowels:
        i ɪ eɪ ɛ æ ɑ ɔ ʊ oʊ u ʌ aɪ aʊ ɔɪ ju ə
        + r-colored: ɪɹ ɛɹ ʊɹ aɪɹ aʊɹ ɔɹ ɑɹ ɝ ɚ

Usage:
    from ipa_phoneme_map import wrap_instructor_text_ssml, ARMENIAN_IPA_MAP

    ssml = wrap_instructor_text_ssml("Say: tyoon", "en-US-JennyNeural")
    if ssml:
        tts.synthesize_to_file_ssml(ssml, path, "male")  # voice tag overrides
    else:
        # fallback to regex
        text = apply_tts_fixes(text)
        tts.synthesize_to_file_with_voice(text, path, voice)
"""

import re
from typing import Dict, Optional, Set
from xml.sax.saxutils import escape as xml_escape


# ============================================================================
# VALID EN-US IPA PHONES (for validation)
# ============================================================================

VALID_EN_US_CONSONANTS: Set[str] = {
    "b", "d", "f", "g", "h", "j", "k", "l", "m", "n", "ŋ", "p",
    "ɹ", "s", "ʃ", "t", "θ", "ð", "v", "w", "z", "ʒ",
    # Affricates (two-char symbols treated as single phones by Azure)
    "tʃ", "dʒ",
}

VALID_EN_US_VOWELS: Set[str] = {
    "i", "ɪ", "eɪ", "ɛ", "æ", "ɑ", "ɔ", "ʊ", "oʊ", "u", "ʌ",
    "aɪ", "aʊ", "ɔɪ", "ju", "ə",
    # R-colored vowels
    "ɪɹ", "ɛɹ", "ʊɹ", "aɪɹ", "aʊɹ", "ɔɹ", "ɑɹ", "ɝ", "ɚ",
}

# Suprasegmentals allowed in IPA strings
VALID_SUPRASEGMENTALS: Set[str] = {
    "ˈ",  # primary stress
    "ˌ",  # secondary stress
    ".",   # syllable boundary
}


# ============================================================================
# ARMENIAN IPA PHONEME MAP
# ============================================================================
# Key:   Armenian phonetic token as it appears in instructor text
# Value: en-US IPA approximation
#
# Strategy for unsupported phones:
#   ts (affricate) → t + s as separate phones
#   tʰ (aspirated) → plain t (+ j for the ty glide)
#   ɣ/gh (uvular)  → g (closest voiced stop)
#   x/kh (velar)   → k (closest voiceless stop)
#   ə (schwa)      → inserted to break impossible English onset clusters

ARMENIAN_IPA_MAP: Dict[str, str] = {
    # ---- tyoon family (ty + vowel → aspirated t + y-glide) ----
    "tyoon":             "tjun",
    "su-tyoon":          "sʌtjun",
    "de-su-tyoon":       "dɛsʌtjun",
    "Tse-de-su-tyoon":   "tsɛdɛsʌtjun",
    "Tsedesutyoon":      "tsɛdɛsʌtjun",

    # ---- Bz cluster (impossible English onset) ----
    "Bzdik":             "bəzdɪk",
    "bzdik":             "bəzdɪk",
    "Bz-dik":            "bəzdɪk",

    # ---- Bd cluster (impossible English onset → schwa insertion) ----
    "Bdegh":             "bədɛg",

    # ---- Khn triple consonant onset ----
    "Khntrem":           "kəntɹɛm",
    "Khntre-m":          "kəntɹɛm",

    # ---- Ts word-initial (affricate) ----
    "Tsakh":             "tsɑk",

    # ---- gh as uvular fricative ----
    "Agheg":             "ɑgɛk",
    "Agh-eg":            "ɑgɛk",

    # ---- gh between vowels ----
    "Yeghpayr":          "jɛgpaɪɹ",
    "Yegh-payr":         "jɛgpaɪɹ",

    # ---- zh ending + complex clusters (i = "ee" as in teen) ----
    "Inknasharzh":       "inknəʃɑɹʒ",
    "Ink-na-sharzh":     "inknəʃɑɹʒ",
    "sharzh":            "ʃɑɹʒ",
    "na-sharzh":         "nəʃɑɹʒ",

    # ---- Sks onset (schwa prefix to avoid "uss" onset) ----
    "Sksel":             "əskəsɛl",
}


# ============================================================================
# SSML WRAPPING
# ============================================================================

# SSML envelope template (matches existing pattern in generate_audio_dual.py)
SSML_TEMPLATE = (
    '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"'
    ' xml:lang="en-US">'
    '<voice name="{voice}">{body}</voice>'
    '</speak>'
)

PHONEME_TEMPLATE = '<phoneme alphabet="ipa" ph="{ipa}">{text}</phoneme>'


def wrap_instructor_text_ssml(
    text: str,
    voice_name: str = "en-US-JennyNeural",
    ipa_map: Dict[str, str] = None,
) -> Optional[str]:
    """
    Wrap instructor text in SSML with IPA phoneme tags for Armenian tokens.

    Scans `text` for tokens matching keys in the IPA map. Matched tokens
    are wrapped in <phoneme> SSML tags. Unmatched text is XML-escaped and
    left as plain text.

    Args:
        text: Full instructor line, e.g. "Say: tyoon"
        voice_name: Azure voice name for the <voice> tag
        ipa_map: Override IPA map (default: ARMENIAN_IPA_MAP)

    Returns:
        Complete SSML string if any tokens were wrapped.
        None if no tokens matched (caller should fall back to regex).
    """
    if ipa_map is None:
        ipa_map = ARMENIAN_IPA_MAP

    if not text or not text.strip():
        return None

    # Build regex pattern that matches any IPA map key (longest first to
    # avoid partial matches, e.g. "Tsedesutyoon" before "tyoon")
    sorted_keys = sorted(ipa_map.keys(), key=len, reverse=True)

    # Escape keys for regex and build alternation with word boundaries
    patterns = []
    for key in sorted_keys:
        escaped = re.escape(key)
        patterns.append(escaped)

    if not patterns:
        return None

    # Match case-insensitively, but preserve original case in output
    combined = "|".join(patterns)
    regex = re.compile(r"(?<!\w)(" + combined + r")(?!\w)", re.IGNORECASE)

    # Track whether we found any matches
    found_match = False

    def _replace(match):
        nonlocal found_match
        found_match = True
        matched_text = match.group(0)
        # Look up IPA (case-insensitive key search)
        for key, ipa in ipa_map.items():
            if key.lower() == matched_text.lower():
                return PHONEME_TEMPLATE.format(
                    ipa=ipa,
                    text=xml_escape(matched_text),
                )
        # Shouldn't happen, but fallback
        return xml_escape(matched_text)

    # Split text into parts: XML-escape non-matched segments, wrap matched ones
    # We can't just xml_escape the whole thing because that would escape the
    # phoneme tags too. Instead, use a two-pass approach:
    # 1. Replace IPA tokens with phoneme tags
    # 2. XML-escape the remaining segments

    # First, find all match positions
    parts = []
    last_end = 0
    for match in regex.finditer(text):
        # Add the text before this match (XML-escaped)
        if match.start() > last_end:
            parts.append(xml_escape(text[last_end:match.start()]))
        # Add the phoneme-wrapped token
        parts.append(_replace(match))
        last_end = match.end()

    # Add remaining text after last match
    if last_end < len(text):
        parts.append(xml_escape(text[last_end:]))

    if not found_match:
        return None

    body = "".join(parts)
    return SSML_TEMPLATE.format(voice=voice_name, body=body)


# ============================================================================
# IPA VALIDATION
# ============================================================================

def validate_ipa_phones(ipa_map: Dict[str, str] = None) -> list:
    """
    Validate that all IPA strings in the map use only en-US supported phones.

    Returns a list of (token, ipa, bad_chars) tuples for any invalid entries.
    Empty list means all entries are valid.
    """
    if ipa_map is None:
        ipa_map = ARMENIAN_IPA_MAP

    # Build set of all valid characters (individual chars from multi-char phones)
    valid_chars = set()
    for phone_set in (VALID_EN_US_CONSONANTS, VALID_EN_US_VOWELS):
        for phone in phone_set:
            for char in phone:
                valid_chars.add(char)
    for sup in VALID_SUPRASEGMENTALS:
        valid_chars.add(sup)

    issues = []
    for token, ipa in ipa_map.items():
        bad_chars = set()
        for char in ipa:
            if char not in valid_chars:
                bad_chars.add(char)
        if bad_chars:
            issues.append((token, ipa, bad_chars))

    return issues


# ============================================================================
# CLI
# ============================================================================

def _safe_print(text: str):
    """Print with UTF-8 encoding (Windows cp1252 can't handle IPA chars)."""
    import sys
    sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()


def main():
    """Show IPA map and validate entries."""
    import sys

    _safe_print("=" * 70)
    _safe_print("ARMENIAN IPA PHONEME MAP")
    _safe_print("=" * 70)
    _safe_print(f"\n  {len(ARMENIAN_IPA_MAP)} entries:\n")

    for token, ipa in sorted(ARMENIAN_IPA_MAP.items(), key=lambda x: x[0].lower()):
        _safe_print(f"  {token:25s} -> {ipa}")

    # Validate
    _safe_print(f"\n{'=' * 70}")
    _safe_print("VALIDATION")
    _safe_print("=" * 70)

    issues = validate_ipa_phones()
    if issues:
        _safe_print(f"\n  {len(issues)} ISSUES FOUND:\n")
        for token, ipa, bad_chars in issues:
            _safe_print(f"  [FAIL] {token}: '{ipa}' contains unsupported chars: {bad_chars}")
    else:
        _safe_print(f"\n  All {len(ARMENIAN_IPA_MAP)} entries use valid en-US IPA phones.")

    # Demo SSML wrapping
    if "--demo" in sys.argv:
        _safe_print(f"\n{'=' * 70}")
        _safe_print("SSML DEMO")
        _safe_print("=" * 70)

        test_lines = [
            "Say: tyoon",
            "Say: su-tyoon",
            "Now the whole word: Tse-de-su-tyoon",
            "This means 'small' or 'young.' Say: Bz-dik.",
            "This means 'please.' Let's break it down. Say: Khntrem",
            "Hello, how are you?",  # No Armenian tokens — should return None
        ]

        for line in test_lines:
            ssml = wrap_instructor_text_ssml(line)
            if ssml:
                _safe_print(f"\n  Input:  {line}")
                _safe_print(f"  SSML:   {ssml}")
            else:
                _safe_print(f"\n  Input:  {line}")
                _safe_print(f"  SSML:   None (no IPA tokens -- uses regex fallback)")


if __name__ == "__main__":
    main()
