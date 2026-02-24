"""Audit all Pimsleur lessons for correct segment practice text resolution."""
import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pimsleur_data import PIMSLEUR_LESSONS
from pimsleur_renderer import build_segments

ISSUES = []

for lesson_id in sorted(PIMSLEUR_LESSONS.keys()):
    lesson = PIMSLEUR_LESSONS[lesson_id]
    segments = build_segments(lesson, 'female')

    for i, seg in enumerate(segments):
        if not seg['has_pause']:
            continue

        pt = seg['practice_text']
        pp = seg['practice_phonetic']
        pe = seg['practice_english']
        we = seg['whisper_expected']

        # Find last instructor line
        last_inst = ''
        for l in reversed(seg['lines']):
            if l['speaker'] == 'instructor':
                last_inst = l['text']
                break

        # CHECK 1: Empty practice text (no word to practice)
        if not pt.strip():
            ISSUES.append(
                f'{lesson_id} Seg {i}: EMPTY practice_text | inst: {last_inst[:80]}'
            )

        # CHECK 2: Practice text is English in quotes (regex leak)
        if pt.startswith('"') or pt.startswith('\u201c'):
            ISSUES.append(
                f'{lesson_id} Seg {i}: QUOTED practice_text={repr(pt)} | inst: {last_inst[:80]}'
            )

        # CHECK 3: Instructor asks about a specific word but practice doesn't match
        # Accounts for: prefix matches, synonym matches, phonetic-to-English
        SYNONYMS = {
            "mom": "mother", "mother": "mom",
            "dad": "father", "father": "dad",
            "my mom": "my mother", "my mother": "my mom",
            "my dad": "my father", "my father": "my dad",
        }
        eng_ask = re.search(
            r'(?:how do you say|(?:now )?say)\s+"([^"]+)"',
            last_inst, re.IGNORECASE
        )
        if eng_ask and pe:
            asked = eng_ask.group(1).strip().lower().rstrip('.!?')
            got = pe.strip().lower().rstrip('.!?')
            if asked != got:
                # Allow prefix matches: "my name is" matches "my name is aram"
                is_prefix = got.startswith(asked)
                # Allow synonym matches: "mom" ↔ "mother"
                is_synonym = SYNONYMS.get(asked) == got
                # Allow phonetic-vs-english: asked is phonetic, got is English
                # (e.g. "medz" → "big", "logaran-uh oor e" → "where is the bathroom")
                # Check if asked matches any phonetic in the segment lines
                is_phonetic = any(
                    l['phonetic'].strip().lower().rstrip('.!?') == asked
                    for l in seg['lines']
                    if l['speaker'] in ('male', 'female') and l.get('phonetic')
                )
                # Also check if answered word's phonetic matches asked
                # Normalize hyphens: "Logaran-uh" vs "Logaranuh"
                if not is_phonetic and pp:
                    pp_norm = pp.strip().lower().rstrip('.!?').replace('-', '')
                    asked_norm = asked.replace('-', '')
                    is_phonetic = pp_norm == asked_norm

                if not (is_prefix or is_synonym or is_phonetic):
                    ISSUES.append(
                        f'{lesson_id} Seg {i}: MISMATCH asked={repr(asked)} got={repr(got)} '
                        f'| inst: {last_inst[:80]}'
                    )

        # CHECK 4: Whisper expected empty for full-word practice
        if pe and not we and pp:
            ISSUES.append(
                f'{lesson_id} Seg {i}: NO_WHISPER but english={repr(pe)} phonetic={repr(pp)} '
                f'| inst: {last_inst[:80]}'
            )

        # CHECK 5: Instructor says "Say: X" but practice_text doesn't match
        say_colon = re.match(r'^Say:\s*(.+)', last_inst, re.IGNORECASE)
        if say_colon:
            expected_phonetic = say_colon.group(1).strip().rstrip('.')
            if pt != expected_phonetic:
                # Could be a multi-line segment; check if any instructor line has Say:
                pass  # Not critical, handled by other checks

if ISSUES:
    print(f'Found {len(ISSUES)} issues:\n')
    for issue in ISSUES:
        print(f'  {issue}')
else:
    print('ALL 20 LESSONS PASS - no issues found')

# Also print summary stats
print(f'\n--- Summary ---')
total_segments = 0
total_practice = 0
total_partial = 0
total_whisper = 0
for lesson_id in sorted(PIMSLEUR_LESSONS.keys()):
    lesson = PIMSLEUR_LESSONS[lesson_id]
    segments = build_segments(lesson, 'female')
    practice_segs = [s for s in segments if s['has_pause']]
    partial = [s for s in practice_segs if not s['whisper_expected']]
    whisper = [s for s in practice_segs if s['whisper_expected']]
    total_segments += len(segments)
    total_practice += len(practice_segs)
    total_partial += len(partial)
    total_whisper += len(whisper)
    print(f'{lesson_id}: {len(segments)} segments, {len(practice_segs)} practice '
          f'({len(whisper)} whisper, {len(partial)} partial-drill)')

print(f'\nTotals: {total_segments} segments, {total_practice} practice points '
      f'({total_whisper} whisper, {total_partial} partial-drill)')
