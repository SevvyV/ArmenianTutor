"""
Syllable Drill Agent for Armenian Tutor.

Generates Pimsleur-style syllable breakdown drills with proper phonetic
alignment between display text, TTS pronunciation, and Whisper evaluation.

Pimsleur Method:
    Start from the LAST syllable of a word and progressively prepend
    syllables until the full word is spoken:
        "Tsedesutyoon" → tyoon → su-tyoon → de-su-tyoon → Tse-de-su-tyoon

Three-Layer Alignment:
    1. display_text:     What the user SEES    ("tyoon")
    2. tts_text:         What the TTS SAYS     ("tee-yoon")  — English-friendly
    3. whisper_expected:  What Whisper CHECKS   ("Ցտdelays") — Armenian script

TTS Problem:
    Instructor audio uses en-US-JennyNeural (English voice).  When it reads
    Armenian phonetic clusters like "tyoon", it applies English rules:
        "tyoon" → "tye-oon" (WRONG — should be "tee-oon")
        "dzer"  → "dzer" (may split into "d-zer")
    The tts_override map provides English-friendly spellings.

Usage:
    from syllable_drill_agent import SyllableDrillAgent

    agent = SyllableDrillAgent()

    # Generate a drill sequence
    drills = agent.generate_drill("Մայրիկ", "Mayrig", "Mother")
    for d in drills:
        print(d)

    # Audit an existing lesson
    issues = agent.audit_lesson("pimsleur_16")
    for issue in issues:
        print(issue)
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict


# ============================================================================
# TTS PRONUNCIATION OVERRIDES
# ============================================================================
# Map: phonetic fragment → TTS-safe English spelling
# These fix cases where the English TTS voice mispronounces Armenian phonetics.
#
# Rules:
#   - "ty" before a vowel: English reads as "tie" → use "tee-y"
#   - "dz" at start: English may split → use "dz" with hyphen guide
#   - "ts" at start: English may read as two letters → "ts" stays
#   - "gh" cluster: English reads as "g-h" → use "gh" (guttural hint)
#   - "kh" cluster: may read as "k-h" → stays (close enough)
#   - "bz" cluster: unusual in English → add slight vowel "buhz"

TTS_OVERRIDES: Dict[str, str] = {
    # Clusters where English TTS consistently fails
    "tyoon": "tee-yoon",
    "tyan": "tee-yan",
    "tyen": "tee-yen",
    "tyoo": "tee-yoo",
    "tyoun": "tee-yoon",
    "tyun": "tee-yoon",
    # Generic pattern: any "ty" + vowel
    # (handled dynamically in _apply_tts_fixes)
}

# Regex patterns for dynamic TTS fixes (applied in order)
TTS_FIX_PATTERNS: List[Tuple[str, str]] = [
    # "ty" before a vowel → "tee-y" + vowel
    (r'\bty([aeiou])', r'tee-y\1'),
    # "Bz" at word start → "Buhz"
    (r'\bBz', 'Buhz'),
    (r'\bbz', 'buhz'),
]


# ============================================================================
# STANDALONE TTS FIX FUNCTION (for use by audio generation pipeline)
# ============================================================================

def apply_tts_fixes(text: str) -> str:
    """
    Apply TTS-safe pronunciation fixes to instructor narration text.

    Call this before sending instructor text to Azure TTS (English voice).
    Converts Armenian phonetic clusters that English TTS mispronounces
    into English-friendly spellings.

    The regex patterns use word boundaries (\\b) so they only match
    Armenian phonetic fragments, not English words:
      - "tyoon" → "tee-yoon"  (but "type" is untouched — no vowel after "ty")
      - "Bz-dik" → "Buhz-dik" (no English word starts with "Bz")

    Args:
        text: Full instructor line text, e.g.
              "This means 'goodbye.' Say: tyoon"

    Returns:
        TTS-safe text: "This means 'goodbye.' Say: tee-yoon"
    """
    result = text
    # Apply exact overrides for known fragments
    for original, replacement in TTS_OVERRIDES.items():
        # Case-insensitive search with word boundary
        pattern = r'\b' + re.escape(original) + r'\b'
        # Preserve original capitalization
        def _replace(m, repl=replacement):
            matched = m.group(0)
            if matched[0].isupper():
                return repl[0].upper() + repl[1:]
            return repl
        result = re.sub(pattern, _replace, result, flags=re.IGNORECASE)

    # Apply dynamic regex patterns for clusters not in the exact map
    for pattern, replacement in TTS_FIX_PATTERNS:
        result = re.sub(pattern, replacement, result)

    return result


# ============================================================================
# ARMENIAN PHONETIC SYLLABLE RULES
# ============================================================================

# Consonant digraphs that should never be split
DIGRAPHS = {"sh", "ch", "gh", "kh", "dz", "ts", "zh", "ph", "th"}

# Armenian vowels in phonetic representation
VOWELS = set("aeiouAEIOU")

# Common vowel combinations that count as one nucleus
VOWEL_CLUSTERS = {"oo", "ee", "ou", "ey", "ay", "oy", "ui"}


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class DrillStep:
    """A single step in a syllable breakdown drill."""
    display_text: str          # What user sees: "tyoon", "su-tyoon", etc.
    tts_text: str              # What English TTS should say (may differ)
    is_full_word: bool         # True only for the final complete-word step
    whisper_expected: str      # Armenian script for Whisper (empty if partial)
    instructor_prefix: str     # "Say:" or "Now the whole word:"

    @property
    def instructor_text(self) -> str:
        """Full instructor line text for display and TTS."""
        return f"{self.instructor_prefix} {self.display_text}"

    @property
    def instructor_tts_text(self) -> str:
        """Full instructor line text optimized for TTS."""
        return f"{self.instructor_prefix} {self.tts_text}"


@dataclass
class DrillSequence:
    """Complete syllable drill for one word/phrase."""
    armenian: str              # Armenian script: "Մայրիկ"
    phonetic: str              # Full phonetic: "Mayrig"
    english: str               # English meaning: "Mother"
    syllables: List[str]       # Split syllables: ["May", "rig"]
    steps: List[DrillStep]     # Progressive drill steps
    intro_text: str = ""       # Optional intro: "This means 'mother.'"

    def __repr__(self):
        steps_str = "\n".join(
            f"  {'*' if s.is_full_word else 'o'} {s.instructor_text}"
            f"{'  [TTS: ' + s.tts_text + ']' if s.tts_text != s.display_text else ''}"
            for s in self.steps
        )
        return (
            f"DrillSequence({self.phonetic} → {self.armenian})\n"
            f"  Syllables: {self.syllables}\n"
            f"{steps_str}"
        )


@dataclass
class AuditIssue:
    """An issue found during drill audit."""
    lesson_id: str
    line_number: int
    severity: str              # "error", "warning", "info"
    category: str              # "tts_mismatch", "missing_drill", "wrong_classification"
    message: str
    instructor_text: str = ""
    expected: str = ""
    actual: str = ""

    def __repr__(self):
        return (
            f"[{self.severity.upper()}] {self.lesson_id} line {self.line_number}: "
            f"{self.message}"
        )


# ============================================================================
# SYLLABLE DRILL AGENT
# ============================================================================

class SyllableDrillAgent:
    """
    Generates and audits Pimsleur-style syllable breakdown drills.

    Handles three alignment layers:
      - Display text (user sees)
      - TTS text (English voice speaks)
      - Whisper expected (Armenian script for speech recognition)
    """

    def __init__(self, tts_overrides: Dict[str, str] = None):
        self.tts_overrides = {**TTS_OVERRIDES, **(tts_overrides or {})}

    # ----------------------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------------------

    def syllabify(self, phonetic: str) -> List[str]:
        """
        Split a phonetic Armenian word into syllables.

        Uses hyphens if present; otherwise applies Armenian phonetic rules.

        Args:
            phonetic: Phonetic string, e.g. "Mayrig" or "Tse-de-su-tyoon"

        Returns:
            List of syllables: ["May", "rig"] or ["Tse", "de", "su", "tyoon"]
        """
        # If already hyphenated, respect author's syllable boundaries
        if "-" in phonetic:
            return [s.strip() for s in phonetic.split("-") if s.strip()]

        # Otherwise, apply algorithmic syllabification
        return self._auto_syllabify(phonetic)

    def generate_drill(
        self,
        armenian: str,
        phonetic: str,
        english: str,
        intro_text: str = "",
        min_syllables_for_drill: int = 2,
    ) -> Optional[DrillSequence]:
        """
        Generate a complete Pimsleur-style syllable drill.

        Args:
            armenian: Armenian script text, e.g. "Մայրիկ"
            phonetic: Phonetic pronunciation, e.g. "Mayrig"
            english: English translation, e.g. "Mother"
            intro_text: Optional intro line, e.g. "This means 'mother.'"
            min_syllables_for_drill: Minimum syllables to warrant a drill (default 2)

        Returns:
            DrillSequence or None if word is too short for a drill
        """
        syllables = self.syllabify(phonetic)

        if len(syllables) < min_syllables_for_drill:
            return None

        steps = []
        for i in range(len(syllables)):
            # Build from last syllable forward: [-1], [-2:-1], [-3:-1], ... [all]
            start_idx = len(syllables) - 1 - i
            fragment_parts = syllables[start_idx:]
            display_text = "-".join(fragment_parts)

            # Capitalize first letter of the full word step
            if i == len(syllables) - 1:
                display_text = display_text[0].upper() + display_text[1:]

            is_full = (i == len(syllables) - 1)
            tts_text = self._get_tts_text(display_text)
            whisper_expected = armenian if is_full else ""
            prefix = "Now the whole word:" if is_full and len(syllables) > 2 else "Say:"

            steps.append(DrillStep(
                display_text=display_text,
                tts_text=tts_text,
                is_full_word=is_full,
                whisper_expected=whisper_expected,
                instructor_prefix=prefix,
            ))

        return DrillSequence(
            armenian=armenian,
            phonetic=phonetic,
            english=english,
            syllables=syllables,
            steps=steps,
            intro_text=intro_text,
        )

    def generate_phrase_drill(
        self,
        armenian: str,
        phonetic: str,
        english: str,
        intro_text: str = "",
    ) -> Optional[DrillSequence]:
        """
        Generate a drill for a multi-word phrase.

        For phrases, drills build word-by-word from the end rather than
        syllable-by-syllable. Individual long words within the phrase
        may get their own sub-drills.

        Args:
            armenian: Armenian script, e.g. "Իdelays մayrig"
            phonetic: Phonetic, e.g. "Im mayrig"
            english: English, e.g. "My mother"
            intro_text: Optional intro line

        Returns:
            DrillSequence or None
        """
        words = phonetic.split()
        if len(words) < 2:
            # Single word — use syllable drill
            return self.generate_drill(armenian, phonetic, english, intro_text)

        steps = []
        for i in range(len(words)):
            start_idx = len(words) - 1 - i
            fragment = " ".join(words[start_idx:])
            is_full = (i == len(words) - 1)
            tts_text = self._get_tts_text(fragment)

            steps.append(DrillStep(
                display_text=fragment,
                tts_text=tts_text,
                is_full_word=is_full,
                whisper_expected=armenian if is_full else "",
                instructor_prefix="Say:",
            ))

        return DrillSequence(
            armenian=armenian,
            phonetic=phonetic,
            english=english,
            syllables=words,
            steps=steps,
            intro_text=intro_text,
        )

    def get_tts_safe_text(self, phonetic_fragment: str) -> str:
        """
        Get TTS-safe version of a phonetic fragment.

        Public method for use by audio generation scripts.

        Args:
            phonetic_fragment: e.g. "tyoon", "Bz-dik"

        Returns:
            TTS-safe version: e.g. "tee-yoon", "Buhz-dik"
        """
        return self._get_tts_text(phonetic_fragment)

    def classify_drill_step(
        self,
        instructor_say_text: str,
        last_armenian_phonetic: str,
        last_armenian_text: str,
    ) -> Tuple[bool, str]:
        """
        Classify whether a "Say: X" drill is partial or full-word.

        This replicates the logic in pimsleur_renderer.py but with
        additional validation.

        Args:
            instructor_say_text: The text after "Say:" e.g. "rig" or "May-rig"
            last_armenian_phonetic: The full phonetic of the word being drilled
            last_armenian_text: The Armenian script of the word being drilled

        Returns:
            Tuple of (is_full_word, whisper_expected)
        """
        override_norm = instructor_say_text.replace("-", "").lower().strip()
        phonetic_norm = last_armenian_phonetic.replace("-", "").lower().strip()
        is_full_word = override_norm == phonetic_norm
        whisper_expected = last_armenian_text if is_full_word else ""
        return is_full_word, whisper_expected

    def audit_lesson(self, lesson_id: str) -> List[AuditIssue]:
        """
        Audit a lesson's syllable drills for issues.

        Checks:
        1. TTS pronunciation mismatches (display ≠ what TTS will say)
        2. Partial vs full-word classification correctness
        3. Missing whisper_expected on full-word drills
        4. Orphaned drills (no preceding Armenian word)
        5. Syllable progression correctness (right-to-left build-up)

        Args:
            lesson_id: e.g. "pimsleur_16"

        Returns:
            List of AuditIssue objects
        """
        from pimsleur_data import PIMSLEUR_LESSONS

        if lesson_id not in PIMSLEUR_LESSONS:
            return [AuditIssue(
                lesson_id=lesson_id, line_number=0, severity="error",
                category="missing_lesson",
                message=f"Lesson '{lesson_id}' not found",
            )]

        lesson = PIMSLEUR_LESSONS[lesson_id]
        issues = []
        last_armenian_text = ""
        last_armenian_phonetic = ""
        last_armenian_english = ""
        last_armenian_line_num = 0
        # Track drill sequences for progression validation
        current_drill_group: List[Tuple[int, str]] = []  # (line_num, say_text)

        say_pattern = re.compile(
            r'^(?:Say|Now (?:say|the whole (?:word|phrase))):\s*(.+)',
            re.IGNORECASE,
        )

        for line_idx, line in enumerate(lesson.lines):
            line_num = line_idx + 1  # 1-indexed for user display

            if line.speaker in ("male", "female") and line.audio_key:
                # New Armenian word resets drill context
                if current_drill_group:
                    # Validate the completed drill group
                    issues.extend(self._validate_drill_group(
                        lesson_id, current_drill_group,
                        last_armenian_phonetic, last_armenian_text,
                    ))
                    current_drill_group = []

                last_armenian_text = line.text
                last_armenian_phonetic = getattr(line, "phonetic", "")
                last_armenian_english = getattr(line, "english", "")
                last_armenian_line_num = line_num

            elif line.speaker == "instructor" and line.audio_key:
                match = say_pattern.match(line.text)
                if match:
                    say_text = match.group(1).strip().rstrip(".")
                    current_drill_group.append((line_num, say_text))

                    # Check 1: TTS pronunciation
                    tts_safe = self._get_tts_text(say_text)
                    if tts_safe.lower() != say_text.lower():
                        issues.append(AuditIssue(
                            lesson_id=lesson_id,
                            line_number=line_num,
                            severity="warning",
                            category="tts_mismatch",
                            message=(
                                f"TTS will mispronounce '{say_text}' "
                                f"→ should use '{tts_safe}' for audio"
                            ),
                            instructor_text=line.text,
                            expected=tts_safe,
                            actual=say_text,
                        ))

                    # Check 2: Orphaned drill (no preceding Armenian word)
                    if not last_armenian_text:
                        issues.append(AuditIssue(
                            lesson_id=lesson_id,
                            line_number=line_num,
                            severity="error",
                            category="orphaned_drill",
                            message=(
                                f"'Say: {say_text}' has no preceding "
                                f"Armenian word to drill against"
                            ),
                            instructor_text=line.text,
                        ))
                    else:
                        # Check 3: Classification correctness
                        is_full, whisper = self.classify_drill_step(
                            say_text, last_armenian_phonetic, last_armenian_text,
                        )
                        if is_full:
                            # Full word should be the final step
                            pass  # Validated in _validate_drill_group
                        else:
                            # Partial: verify it's a valid suffix of the phonetic
                            fragment_norm = say_text.replace("-", "").lower()
                            phonetic_norm = last_armenian_phonetic.replace("-", "").lower()
                            if fragment_norm not in phonetic_norm:
                                issues.append(AuditIssue(
                                    lesson_id=lesson_id,
                                    line_number=line_num,
                                    severity="warning",
                                    category="fragment_mismatch",
                                    message=(
                                        f"Fragment '{say_text}' ('{fragment_norm}') "
                                        f"not found in phonetic '{last_armenian_phonetic}' "
                                        f"('{phonetic_norm}')"
                                    ),
                                    instructor_text=line.text,
                                    expected=last_armenian_phonetic,
                                    actual=say_text,
                                ))

            elif line.speaker == "pause":
                # Pause after a drill — this is where the student practices
                pass

        # Validate any remaining drill group
        if current_drill_group:
            issues.extend(self._validate_drill_group(
                lesson_id, current_drill_group,
                last_armenian_phonetic, last_armenian_text,
            ))

        return issues

    def audit_all_lessons(self) -> Dict[str, List[AuditIssue]]:
        """
        Audit all 20 Pimsleur lessons.

        Returns:
            Dict mapping lesson_id → list of AuditIssue
        """
        from pimsleur_data import PIMSLEUR_LESSONS

        results = {}
        for lesson_id in sorted(PIMSLEUR_LESSONS.keys()):
            issues = self.audit_lesson(lesson_id)
            if issues:
                results[lesson_id] = issues
        return results

    def print_audit_report(self, results: Dict[str, List[AuditIssue]] = None):
        """Print a formatted audit report."""
        if results is None:
            results = self.audit_all_lessons()

        total_issues = sum(len(v) for v in results.values())
        errors = sum(1 for v in results.values() for i in v if i.severity == "error")
        warnings = sum(1 for v in results.values() for i in v if i.severity == "warning")

        print("=" * 70)
        print("SYLLABLE DRILL AUDIT REPORT")
        print("=" * 70)
        print(f"Total issues: {total_issues} ({errors} errors, {warnings} warnings)")
        print()

        if not results:
            print("All lessons pass — no issues found.")
            return

        for lesson_id, issues in sorted(results.items()):
            lesson_num = int(lesson_id.split("_")[1])
            print(f"\n  Lesson {lesson_num} ({lesson_id}):")
            for issue in issues:
                icon = "[ERR]" if issue.severity == "error" else "[WARN]"
                print(f"    {icon} Line {issue.line_number}: {issue.message}")
                if issue.expected and issue.actual:
                    print(f"       Expected: {issue.expected}")
                    print(f"       Actual:   {issue.actual}")

    def generate_all_drills_report(self):
        """
        Scan all lessons and print every syllable drill with alignment info.
        """
        from pimsleur_data import PIMSLEUR_LESSONS

        say_pattern = re.compile(
            r'^(?:Say|Now (?:say|the whole (?:word|phrase))):\s*(.+)',
            re.IGNORECASE,
        )

        print("=" * 70)
        print("ALL SYLLABLE DRILLS — THREE-LAYER ALIGNMENT REPORT")
        print("=" * 70)

        for lesson_id in sorted(PIMSLEUR_LESSONS.keys()):
            lesson = PIMSLEUR_LESSONS[lesson_id]
            lesson_num = int(lesson_id.split("_")[1])
            last_armenian = {"text": "", "phonetic": "", "english": ""}
            drills_in_lesson = []

            for line in lesson.lines:
                if line.speaker in ("male", "female") and line.audio_key:
                    last_armenian = {
                        "text": line.text,
                        "phonetic": getattr(line, "phonetic", ""),
                        "english": getattr(line, "english", ""),
                    }
                elif line.speaker == "instructor" and line.audio_key:
                    match = say_pattern.match(line.text)
                    if match:
                        say_text = match.group(1).strip().rstrip(".")
                        is_full, whisper = self.classify_drill_step(
                            say_text,
                            last_armenian["phonetic"],
                            last_armenian["text"],
                        )
                        tts_safe = self._get_tts_text(say_text)
                        tts_mismatch = tts_safe.lower() != say_text.lower()

                        drills_in_lesson.append({
                            "say_text": say_text,
                            "tts_text": tts_safe,
                            "tts_mismatch": tts_mismatch,
                            "is_full": is_full,
                            "whisper": whisper,
                            "target_armenian": last_armenian["text"],
                            "target_phonetic": last_armenian["phonetic"],
                            "target_english": last_armenian["english"],
                        })

            if drills_in_lesson:
                print(f"\n  Lesson {lesson_num}: {lesson.title}")
                print(f"  {'-' * 60}")
                for d in drills_in_lesson:
                    full_tag = "FULL *" if d["is_full"] else "PARTIAL"
                    tts_tag = " <<TTS>>" if d["tts_mismatch"] else ""
                    print(
                        f"    [{full_tag:8s}] Say: {d['say_text']:25s}"
                        f"  -> {d['target_phonetic']} ({d['target_armenian']})"
                        f"{tts_tag}"
                    )
                    if d["tts_mismatch"]:
                        print(
                            f"              TTS should say: \"{d['tts_text']}\""
                        )
                    if d["is_full"]:
                        print(
                            f"              Whisper checks: {d['whisper']}"
                        )

    # ----------------------------------------------------------------
    # INTERNAL HELPERS
    # ----------------------------------------------------------------

    def _get_tts_text(self, phonetic_fragment: str) -> str:
        """
        Convert a phonetic fragment to TTS-safe English spelling.

        Applies:
        1. Exact overrides from TTS_OVERRIDES dict
        2. Dynamic pattern-based fixes from TTS_FIX_PATTERNS
        """
        # Check exact override first (case-insensitive key)
        lower = phonetic_fragment.lower().strip()
        if lower in self.tts_overrides:
            # Preserve original capitalization pattern
            result = self.tts_overrides[lower]
            if phonetic_fragment[0].isupper():
                result = result[0].upper() + result[1:]
            return result

        # Apply dynamic regex patterns
        result = phonetic_fragment
        for pattern, replacement in TTS_FIX_PATTERNS:
            result = re.sub(pattern, replacement, result)

        return result

    def _auto_syllabify(self, phonetic: str) -> List[str]:
        """
        Algorithmically split a phonetic word into syllables.

        Armenian phonetic syllable rules:
        1. Each syllable has exactly one vowel nucleus
        2. Consonant digraphs (sh, ch, gh, kh, dz, ts) stay together
        3. Single consonants between vowels go with the following vowel
        4. Consonant clusters are split, keeping digraphs intact
        """
        if not phonetic:
            return []

        # Tokenize into units (digraphs or single chars)
        tokens = self._tokenize(phonetic)

        # Identify vowel positions
        vowel_positions = []
        i = 0
        while i < len(tokens):
            token = tokens[i].lower()
            # Check for vowel clusters (oo, ee, ou, etc.)
            if i + 1 < len(tokens):
                pair = token + tokens[i + 1].lower()
                if pair in VOWEL_CLUSTERS:
                    vowel_positions.append((i, i + 1))
                    i += 2
                    continue
            if token in VOWELS or token.lower() in VOWELS:
                vowel_positions.append((i, i))
                i += 1
            else:
                i += 1

        if not vowel_positions:
            # No vowels found — return as single syllable
            return [phonetic]

        if len(vowel_positions) == 1:
            return [phonetic]

        # Build syllables by splitting at consonants between vowels
        syllables = []
        prev_end = 0

        for idx in range(len(vowel_positions) - 1):
            curr_vowel_end = vowel_positions[idx][1]
            next_vowel_start = vowel_positions[idx + 1][0]

            # Consonants between current vowel end and next vowel start
            cons_start = curr_vowel_end + 1
            cons_end = next_vowel_start

            if cons_start >= cons_end:
                # No consonants between vowels — split before next vowel
                split_at = next_vowel_start
            elif cons_end - cons_start == 1:
                # Single consonant — goes with next syllable
                split_at = cons_start
            else:
                # Multiple consonants — split after first
                split_at = cons_start + 1

            syllable = "".join(tokens[prev_end:split_at])
            if syllable:
                syllables.append(syllable)
            prev_end = split_at

        # Add remaining tokens as last syllable
        last = "".join(tokens[prev_end:])
        if last:
            syllables.append(last)

        return syllables

    def _tokenize(self, phonetic: str) -> List[str]:
        """
        Tokenize phonetic string into digraphs and single characters.

        "Shadd" → ["Sh", "a", "d", "d"]
        "ghost" → ["gh", "o", "s", "t"]
        """
        tokens = []
        i = 0
        while i < len(phonetic):
            if i + 1 < len(phonetic):
                pair = phonetic[i:i+2].lower()
                if pair in DIGRAPHS:
                    tokens.append(phonetic[i:i+2])
                    i += 2
                    continue
            tokens.append(phonetic[i])
            i += 1
        return tokens

    def _validate_drill_group(
        self,
        lesson_id: str,
        drill_group: List[Tuple[int, str]],
        full_phonetic: str,
        full_armenian: str,
    ) -> List[AuditIssue]:
        """
        Validate a sequence of drill steps for a single word.

        Checks:
        1. Steps should progressively grow (right-to-left)
        2. Final step should be the full word
        3. Each step should be a suffix of the full phonetic
        """
        issues = []
        if not drill_group or not full_phonetic:
            return issues

        phonetic_norm = full_phonetic.replace("-", "").lower()

        # Check progression: each step should be longer than the previous
        prev_len = 0
        for line_num, say_text in drill_group:
            fragment_norm = say_text.replace("-", "").lower()
            curr_len = len(fragment_norm)

            if curr_len <= prev_len and len(drill_group) > 1:
                issues.append(AuditIssue(
                    lesson_id=lesson_id,
                    line_number=line_num,
                    severity="warning",
                    category="progression_error",
                    message=(
                        f"Drill step '{say_text}' ({curr_len} chars) is not "
                        f"longer than previous step ({prev_len} chars)"
                    ),
                    instructor_text=f"Say: {say_text}",
                    expected=f">{prev_len} chars",
                    actual=f"{curr_len} chars",
                ))

            # Check that fragment is a suffix of the full phonetic
            if not phonetic_norm.endswith(fragment_norm):
                # Could be a phrase drill or different pattern — lower severity
                # Check if it's contained at all
                if fragment_norm not in phonetic_norm:
                    issues.append(AuditIssue(
                        lesson_id=lesson_id,
                        line_number=line_num,
                        severity="info",
                        category="non_suffix_fragment",
                        message=(
                            f"Fragment '{say_text}' is not a suffix of "
                            f"'{full_phonetic}' — may be a phrase drill"
                        ),
                        instructor_text=f"Say: {say_text}",
                        expected=f"suffix of '{full_phonetic}'",
                        actual=say_text,
                    ))

            prev_len = curr_len

        # Check that the last step in the group is the full word
        if drill_group:
            last_text = drill_group[-1][1]
            is_full, _ = self.classify_drill_step(
                last_text, full_phonetic, full_armenian
            )
            if not is_full and len(drill_group) >= 2:
                issues.append(AuditIssue(
                    lesson_id=lesson_id,
                    line_number=drill_group[-1][0],
                    severity="warning",
                    category="missing_full_word",
                    message=(
                        f"Drill group ends with '{last_text}' which is not "
                        f"the full word '{full_phonetic}' — student never "
                        f"practices the complete word with Whisper evaluation"
                    ),
                    instructor_text=f"Say: {last_text}",
                    expected=full_phonetic,
                    actual=last_text,
                ))

        return issues


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    """Run audit and drill report from command line."""
    import sys

    agent = SyllableDrillAgent()

    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        agent.generate_all_drills_report()
    elif len(sys.argv) > 1 and sys.argv[1] == "--audit":
        lesson_filter = sys.argv[2] if len(sys.argv) > 2 else None
        if lesson_filter:
            issues = agent.audit_lesson(lesson_filter)
            agent.print_audit_report({lesson_filter: issues} if issues else {})
        else:
            results = agent.audit_all_lessons()
            agent.print_audit_report(results)
    elif len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Demo: generate drills for sample words
        demos = [
            ("Մայریკ", "Mayrig", "Mother"),
            ("Հայریک", "Hayrig", "Father"),
            (" Delays", "Untanick", "Family"),
            ("Ցdelays", "Tsedesutyoon", "Goodbye"),
            ("Yelays", "Yegeghertsi", "Church"),
            ("Inks", "Inknacharj", "Car"),
        ]
        for arm, phon, eng in demos:
            drill = agent.generate_drill(arm, phon, eng)
            if drill:
                print(drill)
                print()
    else:
        print("Syllable Drill Agent")
        print("Usage:")
        print("  python syllable_drill_agent.py --report    Show all drills alignment")
        print("  python syllable_drill_agent.py --audit     Audit all lessons")
        print("  python syllable_drill_agent.py --audit pimsleur_16  Audit one lesson")
        print("  python syllable_drill_agent.py --demo      Demo drill generation")


if __name__ == "__main__":
    main()
