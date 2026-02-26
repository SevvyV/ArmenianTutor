"""
A/B Test Script for IPA Phoneme vs Regex TTS Fixes.

Generates audio pairs for each test word so you can listen and compare:
  - {token}_regex.mp3  -- old apply_tts_fixes() text hack
  - {token}_ssml.mp3   -- new SSML <phoneme> IPA approach

Output directory: audio_library/ab_test/

Usage:
    python test_ipa_phonemes.py                  # generate all pairs
    python test_ipa_phonemes.py --word tyoon      # one word only
    python test_ipa_phonemes.py --list            # show test words + IPA
    python test_ipa_phonemes.py --ssml-only       # only generate SSML variants
    python test_ipa_phonemes.py --regex-only      # only generate regex variants
"""

import os
import sys
import argparse

from ipa_phoneme_map import ARMENIAN_IPA_MAP, wrap_instructor_text_ssml
from syllable_drill_agent import apply_tts_fixes
from generate_audio_dual import DualVoiceTTS, get_speech_key_from_vault
from config import INSTRUCTOR_VOICE


# ============================================================================
# TEST WORDS
# ============================================================================

TEST_WORDS = [
    {
        "token": "tyoon",
        "instructor_text": "Say: tyoon",
        "lesson": "L1 drill",
        "problem": "ty -> English 'tie'",
    },
    {
        "token": "Tsedesutyoon",
        "instructor_text": "Now the whole word: Tse-de-su-tyoon",
        "lesson": "L1",
        "problem": "Ts onset + ty mid-word",
    },
    {
        "token": "Bzdik",
        "instructor_text": "Say: Bz-dik.",
        "lesson": "L19",
        "problem": "Bz onset impossible in English",
    },
    {
        "token": "Bdegh",
        "instructor_text": "Say: Bdegh.",
        "lesson": "L15",
        "problem": "Bd onset + egh uvular",
    },
    {
        "token": "Khntrem",
        "instructor_text": "Say: Khntrem",
        "lesson": "L3",
        "problem": "Khn triple consonant onset",
    },
    {
        "token": "Tsakh",
        "instructor_text": "Say: Tsakh.",
        "lesson": "L9",
        "problem": "Ts word-initial affricate",
    },
    {
        "token": "Agheg",
        "instructor_text": "Say: Agh-eg em",
        "lesson": "L2",
        "problem": "gh = uvular fricative",
    },
    {
        "token": "Yeghpayr",
        "instructor_text": "Say: Yegh-payr",
        "lesson": "L17",
        "problem": "gh between vowels",
    },
    {
        "token": "Inknasharzh",
        "instructor_text": "Say: Ink-na-sharzh",
        "lesson": "L10",
        "problem": "zh ending + complex clusters",
    },
    {
        "token": "Sksel",
        "instructor_text": "Say: Sksel.",
        "lesson": "N/A",
        "problem": "Sks onset, S sounds like 'uss'",
    },
]


OUTPUT_DIR = os.path.join("audio_library", "ab_test")


def _safe_print(text: str):
    """Print with UTF-8 encoding (Windows cp1252 can't handle IPA chars)."""
    sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()


def list_test_words():
    """Print test words with their IPA mappings."""
    _safe_print("=" * 70)
    _safe_print("A/B TEST WORDS")
    _safe_print("=" * 70)

    for i, tw in enumerate(TEST_WORDS, 1):
        token = tw["token"]
        # Find matching IPA entries
        ipa_entries = []
        for key, ipa in ARMENIAN_IPA_MAP.items():
            if key.lower() == token.lower():
                ipa_entries.append((key, ipa))

        _safe_print(f"\n  {i:2d}. {token}")
        _safe_print(f"      Lesson:    {tw['lesson']}")
        _safe_print(f"      Problem:   {tw['problem']}")
        _safe_print(f"      Text:      {tw['instructor_text']}")
        if ipa_entries:
            for key, ipa in ipa_entries:
                _safe_print(f"      IPA:       {ipa}")
        else:
            _safe_print(f"      IPA:       (no direct match -- may match hyphenated variant)")

    _safe_print(f"\n  Total: {len(TEST_WORDS)} test words")


def generate_pair(
    tts: DualVoiceTTS,
    test_word: dict,
    do_regex: bool = True,
    do_ssml: bool = True,
):
    """Generate regex and/or SSML audio for a single test word."""
    token = test_word["token"]
    text = test_word["instructor_text"]

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results = {"token": token, "regex": None, "ssml": None}

    # --- Regex variant ---
    if do_regex:
        regex_path = os.path.join(OUTPUT_DIR, f"{token}_regex.mp3")
        # Delete existing to force regeneration
        if os.path.exists(regex_path):
            os.remove(regex_path)

        regex_text = apply_tts_fixes(text)
        _safe_print(f"  [REGEX] {token}")
        _safe_print(f"          Text: '{regex_text}'")

        if tts.synthesize_to_file_with_voice(regex_text, regex_path, INSTRUCTOR_VOICE):
            _safe_print(f"          OK -> {regex_path}")
            results["regex"] = regex_path
        else:
            _safe_print(f"          FAILED")

    # --- SSML variant ---
    if do_ssml:
        ssml_path = os.path.join(OUTPUT_DIR, f"{token}_ssml.mp3")
        if os.path.exists(ssml_path):
            os.remove(ssml_path)

        ssml = wrap_instructor_text_ssml(text, INSTRUCTOR_VOICE)
        if ssml:
            _safe_print(f"  [SSML]  {token}")
            _safe_print(f"          SSML: {ssml[:120]}...")

            # Use synthesize_to_file_ssml with "male" as dummy key;
            # the <voice name="en-US-JennyNeural"> in SSML overrides it
            if tts.synthesize_to_file_ssml(ssml, ssml_path, "male"):
                _safe_print(f"          OK -> {ssml_path}")
                results["ssml"] = ssml_path
            else:
                _safe_print(f"          FAILED")
        else:
            _safe_print(f"  [SSML]  {token} -- no IPA match, skipped")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="A/B test: IPA phoneme SSML vs regex TTS fixes"
    )
    parser.add_argument(
        "--word",
        help="Generate pair for specific word only (e.g., 'tyoon')"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List test words and IPA mappings"
    )
    parser.add_argument(
        "--ssml-only", action="store_true",
        help="Only generate SSML variants"
    )
    parser.add_argument(
        "--regex-only", action="store_true",
        help="Only generate regex variants"
    )
    args = parser.parse_args()

    if args.list:
        list_test_words()
        return

    # Filter test words if --word specified
    words = TEST_WORDS
    if args.word:
        words = [tw for tw in TEST_WORDS if tw["token"].lower() == args.word.lower()]
        if not words:
            _safe_print(f"Word '{args.word}' not found in test list.")
            _safe_print(f"Available: {', '.join(tw['token'] for tw in TEST_WORDS)}")
            return

    do_regex = not args.ssml_only
    do_ssml = not args.regex_only

    # Initialize TTS
    _safe_print("=" * 70)
    _safe_print("A/B TEST: IPA PHONEME SSML vs REGEX TTS FIXES")
    _safe_print("=" * 70)
    _safe_print(f"\n  Voice: {INSTRUCTOR_VOICE}")
    _safe_print(f"  Output: {os.path.abspath(OUTPUT_DIR)}")
    _safe_print(f"  Words: {len(words)}")
    _safe_print(f"  Variants: {'regex' if do_regex else ''} {'ssml' if do_ssml else ''}")

    _safe_print("\n  Initializing Azure TTS...")
    api_key = get_speech_key_from_vault()
    region = os.environ.get("AZURE_SPEECH_REGION", "eastus")
    tts = DualVoiceTTS(api_key, region)
    _safe_print("  Ready.\n")

    # Generate pairs
    all_results = []
    for tw in words:
        _safe_print(f"\n{'─' * 50}")
        results = generate_pair(tts, tw, do_regex=do_regex, do_ssml=do_ssml)
        all_results.append(results)

    # Summary
    _safe_print(f"\n{'=' * 70}")
    _safe_print("SUMMARY")
    _safe_print("=" * 70)

    regex_ok = sum(1 for r in all_results if r["regex"])
    ssml_ok = sum(1 for r in all_results if r["ssml"])
    _safe_print(f"\n  Regex generated: {regex_ok}/{len(words)}")
    _safe_print(f"  SSML  generated: {ssml_ok}/{len(words)}")
    _safe_print(f"\n  Files in: {os.path.abspath(OUTPUT_DIR)}")
    _safe_print(f"\n  Listen and compare each pair:")
    for r in all_results:
        token = r["token"]
        rx = "OK" if r["regex"] else "--"
        sm = "OK" if r["ssml"] else "--"
        _safe_print(f"    {token:25s}  regex={rx}  ssml={sm}")


if __name__ == "__main__":
    main()
