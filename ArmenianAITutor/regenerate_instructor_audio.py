"""
Regenerate Instructor Audio with TTS Pronunciation Fixes.

Scans all Pimsleur instructor lines, identifies those where apply_tts_fixes()
would change the text OR where SSML IPA phonemes would be applied (meaning
the English TTS voice would mispronounce the original), deletes the old audio
files, and regenerates them.

This is the go-to script whenever:
  - A new TTS fix pattern is added to syllable_drill_agent.py
  - A new IPA entry is added to ipa_phoneme_map.py
  - Instructor drill text is corrected in pimsleur_data.py
  - You suspect instructor audio doesn't match the current data

Usage:
    python regenerate_instructor_audio.py                  # scan + regen all affected
    python regenerate_instructor_audio.py --scan           # scan only (dry run)
    python regenerate_instructor_audio.py --lesson pimsleur_01  # specific lesson
    python regenerate_instructor_audio.py --force          # regen ALL instructor audio
"""

import os
import argparse

from pimsleur_data import PIMSLEUR_LESSONS
from syllable_drill_agent import apply_tts_fixes
from ipa_phoneme_map import wrap_instructor_text_ssml
from generate_audio_dual import (
    DualVoiceTTS,
    get_speech_key_from_vault,
    print_statistics,
)
from config import INSTRUCTOR_VOICE


OUTPUT_DIR = "audio_library"


def scan_affected_lines(lesson_filter=None):
    """
    Scan all instructor lines and return those where apply_tts_fixes()
    changes the text OR where SSML IPA phonemes will be applied.

    Returns:
        List of (lesson_id, audio_key, original_text, fixed_text, method) tuples
        where method is "ssml" or "regex"
    """
    affected = []

    lessons = PIMSLEUR_LESSONS
    if lesson_filter:
        if lesson_filter not in lessons:
            print(f"Lesson '{lesson_filter}' not found!")
            print(f"Available: {', '.join(sorted(lessons.keys()))}")
            return affected
        lessons = {lesson_filter: lessons[lesson_filter]}

    for lesson_id in sorted(lessons.keys()):
        lesson = lessons[lesson_id]
        for line in lesson.lines:
            if line.speaker != "instructor" or not line.audio_key:
                continue
            if not line.text or not line.text.strip():
                continue

            # Clean text exactly like generate_pimsleur_audio.py does
            clean = line.text.rstrip().rstrip("-").rstrip()

            # Check SSML IPA path first (same priority as pipeline)
            ssml = wrap_instructor_text_ssml(clean)
            if ssml:
                affected.append((lesson_id, line.audio_key, clean, ssml[:80], "ssml"))
                continue

            # Then check regex path
            fixed = apply_tts_fixes(clean)
            if clean != fixed:
                affected.append((lesson_id, line.audio_key, clean, fixed, "regex"))

    return affected


def scan_missing_audio(lesson_filter=None):
    """
    Scan for instructor lines whose audio file doesn't exist at all.

    Returns:
        List of (lesson_id, audio_key) tuples
    """
    missing = []

    lessons = PIMSLEUR_LESSONS
    if lesson_filter:
        if lesson_filter not in lessons:
            return missing
        lessons = {lesson_filter: lessons[lesson_filter]}

    for lesson_id in sorted(lessons.keys()):
        lesson = lessons[lesson_id]
        for line in lesson.lines:
            if line.speaker != "instructor" or not line.audio_key:
                continue
            if not line.text or not line.text.strip():
                continue

            path = os.path.join(
                OUTPUT_DIR, "conversations", lesson_id, "instructor",
                f"{line.audio_key}.mp3"
            )
            if not os.path.exists(path):
                missing.append((lesson_id, line.audio_key))

    return missing


def delete_audio_files(affected):
    """Delete audio files for affected lines so they get regenerated."""
    deleted = 0
    for lesson_id, audio_key, *_ in affected:
        path = os.path.join(
            OUTPUT_DIR, "conversations", lesson_id, "instructor",
            f"{audio_key}.mp3"
        )
        if os.path.exists(path):
            os.remove(path)
            deleted += 1
    return deleted


def delete_all_instructor_audio(lesson_filter=None):
    """Delete ALL instructor audio files (for --force mode)."""
    deleted = 0

    lessons = PIMSLEUR_LESSONS
    if lesson_filter:
        if lesson_filter not in lessons:
            return 0
        lessons = {lesson_filter: lessons[lesson_filter]}

    for lesson_id in sorted(lessons.keys()):
        lesson = lessons[lesson_id]
        for line in lesson.lines:
            if line.speaker != "instructor" or not line.audio_key:
                continue
            path = os.path.join(
                OUTPUT_DIR, "conversations", lesson_id, "instructor",
                f"{line.audio_key}.mp3"
            )
            if os.path.exists(path):
                os.remove(path)
                deleted += 1

    return deleted


def regenerate(lesson_filter=None):
    """
    Regenerate instructor audio using generate_pimsleur_audio.py's pipeline.

    This calls the same code path that generate_pimsleur_audio.py uses,
    which now includes apply_tts_fixes() for pronunciation correction.
    """
    from generate_pimsleur_audio import generate_instructor_audio

    api_key = get_speech_key_from_vault()
    region = os.environ.get("AZURE_SPEECH_REGION", "eastus")
    tts = DualVoiceTTS(api_key, region)

    stats = generate_instructor_audio(tts, lesson_filter, OUTPUT_DIR)
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate instructor audio with TTS pronunciation fixes"
    )
    parser.add_argument(
        "--scan", action="store_true",
        help="Scan only — show affected files without regenerating"
    )
    parser.add_argument(
        "--lesson",
        help="Process specific lesson only (e.g., 'pimsleur_01')"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Delete and regenerate ALL instructor audio, not just affected files"
    )
    args = parser.parse_args()

    # Step 1: Scan for affected lines
    print("=" * 70)
    print("SCANNING INSTRUCTOR LINES FOR TTS FIX TARGETS")
    print("=" * 70)

    affected = scan_affected_lines(args.lesson)
    missing = scan_missing_audio(args.lesson)

    if affected:
        ssml_count = sum(1 for *_, method in affected if method == "ssml")
        regex_count = sum(1 for *_, method in affected if method == "regex")
        print(f"\n  {len(affected)} lines need pronunciation fixes"
              f" ({ssml_count} SSML IPA, {regex_count} regex):\n")
        for lesson_id, audio_key, original, fixed, method in affected:
            path = os.path.join(
                OUTPUT_DIR, "conversations", lesson_id, "instructor",
                f"{audio_key}.mp3"
            )
            exists = "EXISTS" if os.path.exists(path) else "MISSING"
            tag = "SSML" if method == "ssml" else "REGEX"
            print(f"  [{exists}] [{tag:5s}] {lesson_id}/{audio_key}")
            print(f"           Original: {original[:80]}")
            if method == "regex":
                print(f"           Fixed:    {fixed[:80]}")
            else:
                print(f"           SSML:     (IPA phoneme tags applied)")
            print()
    else:
        print("\n  No TTS-affected instructor lines found.\n")

    if missing:
        print(f"  {len(missing)} instructor lines with missing audio files:\n")
        for lesson_id, audio_key in missing:
            print(f"  [MISSING] {lesson_id}/{audio_key}")
        print()

    # Scan-only mode stops here
    if args.scan:
        print("Scan complete. Use without --scan to regenerate.")
        return

    # Step 2: Delete old files
    if args.force:
        print("=" * 70)
        print("FORCE MODE: Deleting ALL instructor audio")
        print("=" * 70)
        deleted = delete_all_instructor_audio(args.lesson)
        print(f"  Deleted {deleted} files\n")
    elif affected:
        print("=" * 70)
        print("DELETING AFFECTED AUDIO FILES")
        print("=" * 70)
        deleted = delete_audio_files(affected)
        print(f"  Deleted {deleted} files\n")
    else:
        if not missing:
            print("Nothing to regenerate. All audio is up to date.")
            return

    # Step 3: Regenerate
    print("=" * 70)
    print("REGENERATING INSTRUCTOR AUDIO")
    print("=" * 70)
    stats = regenerate(args.lesson)
    print_statistics(stats)


if __name__ == "__main__":
    main()
