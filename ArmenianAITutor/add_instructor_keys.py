"""
One-time script to add audio_key to all instructor ConversationLine entries
in pimsleur_data.py.

Each lesson gets sequential inst_001, inst_002, ... keys.
Only modifies instructor lines that don't already have an audio_key.

Usage:
    python add_instructor_keys.py
"""

import re


def add_instructor_keys():
    filepath = "pimsleur_data.py"

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Track which lesson we're in by finding lesson assignment patterns
    # e.g., _lesson_01 = ConversationLesson(
    # We process the file in order and track instructor line counts per lesson

    lines = content.split("\n")
    output_lines = []
    current_lesson_num = None
    instructor_counter = 0

    for line in lines:
        # Detect lesson start: _lesson_NN = ConversationLesson(
        lesson_match = re.match(r'^_lesson_(\d+)\s*=\s*ConversationLesson\(', line)
        if lesson_match:
            current_lesson_num = int(lesson_match.group(1))
            instructor_counter = 0

        # Detect instructor lines without audio_key
        # Pattern: ConversationLine(speaker="instructor", text="...")
        # These lines do NOT have audio_key= in them
        if 'speaker="instructor"' in line and 'audio_key=' not in line:
            instructor_counter += 1
            key = f"inst_{instructor_counter:03d}"
            # Insert audio_key before the closing paren
            # Handle both: ...text="blah"), and ...text="blah"),
            line = line.rstrip()
            if line.endswith("),"):
                line = line[:-2] + f', audio_key="{key}"),'
            elif line.endswith(")"):
                line = line[:-1] + f', audio_key="{key}")'

        output_lines.append(line)

    new_content = "\n".join(output_lines)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Done. Processed {filepath}")
    print(f"Added audio_key to instructor lines across all lessons.")


if __name__ == "__main__":
    add_instructor_keys()
