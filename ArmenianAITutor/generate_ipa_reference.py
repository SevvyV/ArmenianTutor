"""
Generate reference audio files for every en-US IPA phone Azure TTS supports.

Creates one MP3 per phoneme so you can listen to each sound individually.
Consonants are placed in an "ah-{C}-ah" carrier context for audibility.
Vowels and diphthongs are generated standalone.

Output directory: audio_library/ipa_reference/

Usage:
    python generate_ipa_reference.py           # generate all
    python generate_ipa_reference.py --list    # list all phones (no audio)
"""

import os
import sys
import argparse

from generate_audio_dual import DualVoiceTTS, get_speech_key_from_vault
from config import INSTRUCTOR_VOICE


# ============================================================================
# PHONE CATALOG
# ============================================================================
# (ipa, filename, example_word, description, category)

CONSONANTS = [
    ("b",  "b",            "boy",     "voiced bilabial stop"),
    ("d",  "d",            "dog",     "voiced alveolar stop"),
    ("f",  "f",            "fan",     "voiceless labiodental fricative"),
    ("g",  "g",            "go",      "voiced velar stop"),
    ("h",  "h",            "hat",     "voiceless glottal fricative"),
    ("j",  "j_glide",      "yes",     "palatal glide (y-sound)"),
    ("k",  "k",            "cat",     "voiceless velar stop"),
    ("l",  "l",            "leg",     "lateral approximant"),
    ("m",  "m",            "man",     "bilabial nasal"),
    ("n",  "n",            "no",      "alveolar nasal"),
    ("ŋ",  "ng",           "sing",    "velar nasal"),
    ("p",  "p",            "pen",     "voiceless bilabial stop"),
    ("ɹ",  "r",            "red",     "alveolar approximant"),
    ("s",  "s",            "sun",     "voiceless alveolar fricative"),
    ("ʃ",  "sh",           "ship",    "voiceless postalveolar fricative"),
    ("t",  "t",            "top",     "voiceless alveolar stop"),
    ("θ",  "th_voiceless", "think",   "voiceless dental fricative"),
    ("ð",  "th_voiced",    "this",    "voiced dental fricative"),
    ("v",  "v",            "van",     "voiced labiodental fricative"),
    ("w",  "w",            "win",     "labial-velar glide"),
    ("z",  "z",            "zoo",     "voiced alveolar fricative"),
    ("ʒ",  "zh",           "measure", "voiced postalveolar fricative"),
    ("tʃ", "ch",           "chip",    "voiceless postalveolar affricate"),
    ("dʒ", "dj",           "judge",   "voiced postalveolar affricate"),
]

VOWELS = [
    ("i",  "ee",       "teen",   "close front unrounded (long e)"),
    ("ɪ",  "ih",       "bit",    "near-close front unrounded (short i)"),
    ("eɪ", "ay",       "say",    "diphthong"),
    ("ɛ",  "eh",       "bet",    "open-mid front unrounded"),
    ("æ",  "ae",       "cat",    "near-open front unrounded"),
    ("ɑ",  "ah",       "father", "open back unrounded"),
    ("ɔ",  "aw",       "law",    "open-mid back rounded"),
    ("ʊ",  "oo_short", "book",   "near-close back rounded"),
    ("oʊ", "oh",       "go",     "diphthong"),
    ("u",  "oo",       "moon",   "close back rounded"),
    ("ʌ",  "uh",       "but",    "open-mid back unrounded"),
    ("aɪ", "eye",      "my",     "diphthong"),
    ("aʊ", "ow",       "cow",    "diphthong"),
    ("ɔɪ", "oy",       "boy",    "diphthong"),
    ("ju", "yoo",      "use",    "diphthong"),
    ("ə",  "schwa",    "about",  "mid central (unstressed)"),
]

R_COLORED = [
    ("ɪɹ", "ir",           "ear",    "r-colored near-close front"),
    ("ɛɹ", "air",          "air",    "r-colored open-mid front"),
    ("ʊɹ", "oor",          "tour",   "r-colored near-close back"),
    ("aɪɹ", "ire",         "fire",   "r-colored diphthong"),
    ("aʊɹ", "our",         "hour",   "r-colored diphthong"),
    ("ɔɹ", "or",           "or",     "r-colored open-mid back"),
    ("ɑɹ", "ar",           "car",    "r-colored open back"),
    ("ɝ",  "er_stressed",  "bird",   "r-colored mid central (stressed)"),
    ("ɚ",  "er_unstressed", "butter", "r-colored mid central (unstressed)"),
]

ALL_PHONES = (
    [(*c, "consonant") for c in CONSONANTS]
    + [(*v, "vowel") for v in VOWELS]
    + [(*r, "r-colored") for r in R_COLORED]
)


# ============================================================================
# SSML
# ============================================================================

SSML_TEMPLATE = (
    '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"'
    ' xml:lang="en-US">'
    '<voice name="{voice}">'
    '<phoneme alphabet="ipa" ph="{ipa}">{display}</phoneme>'
    '</voice>'
    '</speak>'
)

OUTPUT_DIR = os.path.join("audio_library", "ipa_reference")


def _safe_print(text: str):
    sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()


def list_phones():
    """Print all phones grouped by category."""
    _safe_print("=" * 70)
    _safe_print("EN-US IPA PHONES SUPPORTED BY AZURE TTS")
    _safe_print("=" * 70)

    for label, group in [("CONSONANTS", CONSONANTS), ("VOWELS", VOWELS), ("R-COLORED VOWELS", R_COLORED)]:
        _safe_print(f"\n  {label} ({len(group)}):")
        _safe_print(f"  {'IPA':<8} {'File':<18} {'Example':<10} Description")
        _safe_print(f"  {'-'*8} {'-'*18} {'-'*10} {'-'*30}")
        for ipa, fname, example, desc in group:
            _safe_print(f"  {ipa:<8} {fname:<18} {example:<10} {desc}")

    total = len(CONSONANTS) + len(VOWELS) + len(R_COLORED)
    _safe_print(f"\n  Total: {total} phones")


def generate_phone_audio(tts, ipa, filename, example, desc, category, voice):
    """Generate one MP3 for a single IPA phone."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    output_path = os.path.join(OUTPUT_DIR, f"{filename}.mp3")

    # For consonants, sandwich in "ah-C-ah" context so they're audible.
    # For vowels/diphthongs, generate standalone.
    if category == "consonant":
        # "ah" + consonant + "ah" gives clear audibility
        carrier_ipa = f"ɑ.{ipa}.ɑ"
        display_text = f"ah-{filename}-ah"
    else:
        carrier_ipa = ipa
        display_text = filename

    ssml = SSML_TEMPLATE.format(
        voice=voice,
        ipa=carrier_ipa,
        display=display_text,
    )

    # Delete existing to force regeneration
    if os.path.exists(output_path):
        os.remove(output_path)

    if tts.synthesize_to_file_ssml(ssml, output_path, "male"):
        _safe_print(f"  OK   {filename:<18}  /{ipa}/  ({example}: {desc})")
        return True
    else:
        _safe_print(f"  FAIL {filename:<18}  /{ipa}/  ({example}: {desc})")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate reference audio for all en-US IPA phones"
    )
    parser.add_argument("--list", action="store_true", help="List phones only (no audio)")
    parser.add_argument("--category", choices=["consonant", "vowel", "r-colored"],
                        help="Generate only one category")
    args = parser.parse_args()

    if args.list:
        list_phones()
        return

    _safe_print("=" * 70)
    _safe_print("GENERATING IPA REFERENCE AUDIO")
    _safe_print("=" * 70)

    phones = ALL_PHONES
    if args.category:
        phones = [p for p in ALL_PHONES if p[4] == args.category]

    _safe_print(f"\n  Voice:  {INSTRUCTOR_VOICE}")
    _safe_print(f"  Output: {os.path.abspath(OUTPUT_DIR)}")
    _safe_print(f"  Phones: {len(phones)}")
    _safe_print(f"\n  Consonants are generated in 'ah-C-ah' carrier context.")
    _safe_print(f"  Vowels and diphthongs are generated standalone.\n")

    _safe_print("  Initializing Azure TTS...")
    api_key = get_speech_key_from_vault()
    region = os.environ.get("AZURE_SPEECH_REGION", "eastus")
    tts = DualVoiceTTS(api_key, region)
    _safe_print("  Ready.\n")

    ok_count = 0
    fail_count = 0

    for ipa, fname, example, desc, category in phones:
        if generate_phone_audio(tts, ipa, fname, example, desc, category, INSTRUCTOR_VOICE):
            ok_count += 1
        else:
            fail_count += 1

    _safe_print(f"\n{'=' * 70}")
    _safe_print(f"DONE: {ok_count} OK, {fail_count} failed")
    _safe_print(f"Files: {os.path.abspath(OUTPUT_DIR)}")
    _safe_print("=" * 70)


if __name__ == "__main__":
    main()
