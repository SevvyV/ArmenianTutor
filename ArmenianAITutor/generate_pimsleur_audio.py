"""
Azure TTS Audio Generation for Pimsleur Conversations

Generates per-line MP3 files for male/female speaker lines only.
Reuses DualVoiceTTS and WESTERN_TO_EASTERN_FIXES from generate_audio_dual.py.

Output structure:
  audio_library/conversations/{lesson_id}/{voice}/{audio_key}.mp3

Usage:
    python generate_pimsleur_audio.py --voice both
    python generate_pimsleur_audio.py --voice male --lesson pimsleur_01
    python generate_pimsleur_audio.py --lesson pimsleur_05 --voice female
"""

import os
import argparse
from generate_audio_dual import (
    DualVoiceTTS,
    apply_western_fixes,
    get_speech_key_from_vault,
    print_statistics,
)
from pimsleur_data import PIMSLEUR_LESSONS


def generate_conversation_audio(
    tts: DualVoiceTTS,
    voices: list,
    lesson_filter: str = None,
    output_dir: str = "audio_library",
):
    """
    Generate audio for Pimsleur conversation lines.

    Only generates for male/female speaker lines (not instructor/pause/sfx).

    Args:
        tts: Initialized DualVoiceTTS instance
        voices: List of voices to generate ("male", "female", or both)
        lesson_filter: If set, only generate for this lesson ID
        output_dir: Base output directory
    """
    print("\n" + "=" * 70)
    print("GENERATING PIMSLEUR CONVERSATION AUDIO")
    print("=" * 70)

    stats = {"total": 0, "success": 0, "failed": 0, "skipped": 0}

    lessons = PIMSLEUR_LESSONS
    if lesson_filter:
        if lesson_filter not in lessons:
            print(f"Lesson '{lesson_filter}' not found!")
            print(f"Available: {', '.join(sorted(lessons.keys()))}")
            return stats
        lessons = {lesson_filter: lessons[lesson_filter]}

    for lesson_id in sorted(lessons.keys()):
        lesson = lessons[lesson_id]
        armenian_lines = [
            line for line in lesson.lines
            if line.speaker in ("male", "female") and line.audio_key
        ]

        print(f"\n  Lesson {int(lesson_id.split('_')[1])}: {lesson.title}")
        print(f"  Armenian lines: {len(armenian_lines)}")

        for voice in voices:
            print(f"  Voice: {voice.capitalize()}")
            voice_dir = os.path.join(
                output_dir, "conversations", lesson_id, voice
            )

            for line in armenian_lines:
                stats["total"] += 1
                output_path = os.path.join(voice_dir, f"{line.audio_key}.mp3")

                # Skip if exists
                if os.path.exists(output_path):
                    stats["skipped"] += 1
                    continue

                # Use Armenian text for TTS
                text = line.text
                if not text or not any(
                    0x0530 <= ord(c) <= 0x058F for c in text
                ):
                    # No Armenian text available, skip
                    print(f"    -- {line.audio_key} (no Armenian text, skipped)")
                    stats["skipped"] += 1
                    continue

                # Generate audio with Western->Eastern fixes
                if tts.synthesize_to_file(text, output_path, voice):
                    print(f"    OK {line.audio_key}.mp3")
                    stats["success"] += 1
                else:
                    print(f"    FAIL {line.audio_key}.mp3")
                    stats["failed"] += 1

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Generate Pimsleur conversation audio files"
    )
    parser.add_argument(
        "--voice",
        choices=["male", "female", "both"],
        default="both",
        help="Which voice(s) to generate (default: both)",
    )
    parser.add_argument(
        "--lesson",
        help="Generate specific lesson only (e.g., 'pimsleur_01')",
    )
    parser.add_argument(
        "--output",
        default="audio_library",
        help="Output directory (default: audio_library)",
    )

    args = parser.parse_args()

    # Get Azure credentials from Key Vault
    api_key = get_speech_key_from_vault()
    region = os.getenv("AZURE_SPEECH_REGION", "eastus")

    # Determine voices
    if args.voice == "both":
        voices = ["male", "female"]
    else:
        voices = [args.voice]

    # Initialize TTS
    tts = DualVoiceTTS(api_key, region)

    # Generate audio
    stats = generate_conversation_audio(tts, voices, args.lesson, args.output)
    print_statistics(stats)


if __name__ == "__main__":
    main()
