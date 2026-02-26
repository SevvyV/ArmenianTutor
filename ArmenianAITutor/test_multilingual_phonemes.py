"""
Test multilingual phoneme borrowing for Armenian "gh" (uvular fricative).

Generates multiple SSML approaches to see if we can borrow the French [ʁ]
phone to construct Armenian words that the en-US phone set can't handle.

Test words:
    Agheg  (I'm well)  — gh between vowels
    Yeghpayr (brother) — gh between vowels
    Bdegh  (fruit)     — gh word-final

Output directory: audio_library/multilingual_test/

Usage:
    python test_multilingual_phonemes.py
"""

import os
import sys
import time
import azure.cognitiveservices.speech as speechsdk
from generate_audio_dual import DualVoiceTTS, get_speech_key_from_vault
from config import INSTRUCTOR_VOICE

OUTPUT_DIR = os.path.join("audio_library", "multilingual_test")

# French voices available on Azure
FR_VOICE = "fr-FR-DeniseNeural"
EN_VOICE = INSTRUCTOR_VOICE  # en-US-JennyNeural


def _safe_print(text: str):
    sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()


# ============================================================================
# TEST CASES
# ============================================================================
# Each test: (filename, description, ssml)
# We test multiple approaches for each word.

TESTS = [
    # ========================================================================
    # AGHEG — "I'm well" — target: ɑʁɛk
    # ========================================================================

    # Approach 1: <lang> tag mid-word (English voice, French phoneme island)
    (
        "agheg_1_lang_tag",
        "Agheg: <lang fr-FR> wrapping just the gh phone",
        f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{EN_VOICE}">
<phoneme alphabet="ipa" ph="ɑ">a</phoneme><lang xml:lang="fr-FR"><phoneme alphabet="ipa" ph="ʁ">r</phoneme></lang><phoneme alphabet="ipa" ph="ɛk">ek</phoneme>
</voice>
</speak>''',
    ),

    # Approach 2: Nested <voice> switch mid-word
    (
        "agheg_2_voice_switch",
        "Agheg: switch to French voice for gh phone only",
        f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{EN_VOICE}"><phoneme alphabet="ipa" ph="ɑ">a</phoneme></voice>
<voice name="{FR_VOICE}"><phoneme alphabet="ipa" ph="ʁ">r</phoneme></voice>
<voice name="{EN_VOICE}"><phoneme alphabet="ipa" ph="ɛk">ek</phoneme></voice>
</speak>''',
    ),

    # Approach 3: Use fr-FR phoneme set for the whole word
    (
        "agheg_3_full_french_ipa",
        "Agheg: entire word using French IPA (supports uvular r)",
        f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{EN_VOICE}">
<lang xml:lang="fr-FR"><phoneme alphabet="ipa" ph="ɑʁɛk">agheg</phoneme></lang>
</voice>
</speak>''',
    ),

    # Approach 4: Full French voice for the whole word
    (
        "agheg_4_french_voice_full",
        "Agheg: French voice speaks the full word with French IPA",
        f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="fr-FR">
<voice name="{FR_VOICE}">
<phoneme alphabet="ipa" ph="ɑʁɛk">agheg</phoneme>
</voice>
</speak>''',
    ),

    # Approach 5: Current en-US baseline (g approximation)
    (
        "agheg_5_baseline_en",
        "Agheg: current baseline with g approximation",
        f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{EN_VOICE}">
<phoneme alphabet="ipa" ph="ɑgɛk">agheg</phoneme>
</voice>
</speak>''',
    ),

    # Approach 6: en-US with English r approximation
    (
        "agheg_6_english_r",
        "Agheg: English r approximation instead of g",
        f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{EN_VOICE}">
<phoneme alphabet="ipa" ph="ɑɹɛk">agheg</phoneme>
</voice>
</speak>''',
    ),

    # ========================================================================
    # YEGHPAYR — "brother" — target: jɛʁpaɪɹ
    # ========================================================================

    # Approach 1: <lang> tag mid-word
    (
        "yeghpayr_1_lang_tag",
        "Yeghpayr: <lang fr-FR> wrapping just the gh phone",
        f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{EN_VOICE}">
<phoneme alphabet="ipa" ph="jɛ">ye</phoneme><lang xml:lang="fr-FR"><phoneme alphabet="ipa" ph="ʁ">r</phoneme></lang><phoneme alphabet="ipa" ph="paɪɹ">payr</phoneme>
</voice>
</speak>''',
    ),

    # Approach 2: Nested voice switch
    (
        "yeghpayr_2_voice_switch",
        "Yeghpayr: switch to French voice for gh phone only",
        f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{EN_VOICE}"><phoneme alphabet="ipa" ph="jɛ">ye</phoneme></voice>
<voice name="{FR_VOICE}"><phoneme alphabet="ipa" ph="ʁ">r</phoneme></voice>
<voice name="{EN_VOICE}"><phoneme alphabet="ipa" ph="paɪɹ">payr</phoneme></voice>
</speak>''',
    ),

    # Approach 3: Full French IPA
    (
        "yeghpayr_3_full_french_ipa",
        "Yeghpayr: entire word using French IPA",
        f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{EN_VOICE}">
<lang xml:lang="fr-FR"><phoneme alphabet="ipa" ph="jɛʁpajʁ">yeghpayr</phoneme></lang>
</voice>
</speak>''',
    ),

    # Approach 4: Full French voice
    (
        "yeghpayr_4_french_voice_full",
        "Yeghpayr: French voice with French IPA",
        f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="fr-FR">
<voice name="{FR_VOICE}">
<phoneme alphabet="ipa" ph="jɛʁpajʁ">yeghpayr</phoneme>
</voice>
</speak>''',
    ),

    # Approach 5: Current en-US baseline
    (
        "yeghpayr_5_baseline_en",
        "Yeghpayr: current baseline with g approximation",
        f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{EN_VOICE}">
<phoneme alphabet="ipa" ph="jɛgpaɪɹ">yeghpayr</phoneme>
</voice>
</speak>''',
    ),

    # Approach 6: en-US with English r approximation
    (
        "yeghpayr_6_english_r",
        "Yeghpayr: English r approximation instead of g",
        f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{EN_VOICE}">
<phoneme alphabet="ipa" ph="jɛɹpaɪɹ">yeghpayr</phoneme>
</voice>
</speak>''',
    ),

    # ========================================================================
    # BDEGH — "fruit" — target: bədɛʁ (gh at word end)
    # ========================================================================

    # Approach 1: <lang> tag for final gh
    (
        "bdegh_1_lang_tag",
        "Bdegh: <lang fr-FR> wrapping just the final gh",
        f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{EN_VOICE}">
<phoneme alphabet="ipa" ph="bədɛ">bde</phoneme><lang xml:lang="fr-FR"><phoneme alphabet="ipa" ph="ʁ">r</phoneme></lang>
</voice>
</speak>''',
    ),

    # Approach 3: Full French IPA
    (
        "bdegh_3_full_french_ipa",
        "Bdegh: entire word using French IPA",
        f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{EN_VOICE}">
<lang xml:lang="fr-FR"><phoneme alphabet="ipa" ph="bədɛʁ">bdegh</phoneme></lang>
</voice>
</speak>''',
    ),

    # Approach 5: Current en-US baseline
    (
        "bdegh_5_baseline_en",
        "Bdegh: current baseline with g approximation + schwa",
        f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{EN_VOICE}">
<phoneme alphabet="ipa" ph="b\u0259d\u025bg">bdegh</phoneme>
</voice>
</speak>''',
    ),

    # Approach 6: en-US with English r approximation
    (
        "bdegh_6_english_r",
        "Bdegh: English r approximation for final gh",
        f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{EN_VOICE}">
<phoneme alphabet="ipa" ph="b\u0259d\u025b\u0279">bdegh</phoneme>
</voice>
</speak>''',
    ),
]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    _safe_print("=" * 70)
    _safe_print("MULTILINGUAL PHONEME BORROWING TEST")
    _safe_print("=" * 70)
    _safe_print(f"\n  English voice: {EN_VOICE}")
    _safe_print(f"  French voice:  {FR_VOICE}")
    _safe_print(f"  Output:        {os.path.abspath(OUTPUT_DIR)}")
    _safe_print(f"  Tests:         {len(TESTS)}")
    _safe_print("")

    _safe_print("  Initializing Azure TTS...")
    api_key = get_speech_key_from_vault()
    region = os.environ.get("AZURE_SPEECH_REGION", "eastus")
    tts = DualVoiceTTS(api_key, region)
    _safe_print("  Ready.\n")

    ok = 0
    fail = 0

    for filename, desc, ssml in TESTS:
        output_path = os.path.join(OUTPUT_DIR, f"{filename}.mp3")

        # Delete existing
        if os.path.exists(output_path):
            os.remove(output_path)

        if tts.synthesize_to_file_ssml(ssml, output_path, "male"):
            _safe_print(f"  OK   {filename}")
            _safe_print(f"       {desc}")
            ok += 1
        else:
            _safe_print(f"  FAIL {filename}")
            _safe_print(f"       {desc}")
            fail += 1

    _safe_print(f"\n{'=' * 70}")
    _safe_print(f"DONE: {ok} OK, {fail} failed")
    _safe_print(f"Files: {os.path.abspath(OUTPUT_DIR)}")
    _safe_print("=" * 70)

    # Print listening guide
    _safe_print(f"\n{'=' * 70}")
    _safe_print("LISTENING GUIDE")
    _safe_print("=" * 70)
    _safe_print("""
  For each word, compare these approaches:
    *_1_lang_tag      = French <lang> island inside English voice
    *_2_voice_switch  = Swap to French voice mid-word
    *_3_full_french   = Whole word in French IPA (English voice + fr-FR lang)
    *_4_french_voice  = Whole word spoken by French voice
    *_5_baseline_en   = Current approach (g approximation)
    *_6_english_r     = English r approximation (no French borrowing)

  Listen for:
    - Does the "gh" sound throaty/uvular? (good = approaches 1-4)
    - Are there audible seams between language segments? (bad = approaches 1-2)
    - Does the overall word sound natural? (compare all)
""")


if __name__ == "__main__":
    main()
