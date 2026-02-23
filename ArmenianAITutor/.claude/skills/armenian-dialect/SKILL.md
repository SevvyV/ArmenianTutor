---
name: mesrob
description: Western vs Eastern Armenian dialect rules, consonant shifts, phonetic conventions, TTS workarounds, and Whisper normalization. Named after Mesrob Mashtots, inventor of the Armenian alphabet (405 AD). Use whenever working on Armenian language content, audio generation, speech recognition, translations, or lesson data.
user-invocable: false
---

# Western Armenian Dialect Knowledge

This project teaches **Western Armenian**, but all available TTS engines and Whisper speech recognition use **Eastern Armenian**. This skill encodes the rules for bridging the two dialects.

## 1. Consonant Shift Pairs (5 Major Pairs)

Western and Eastern Armenian swap voicing on these consonant pairs:

| Letter | Western Sound | Eastern Sound | Unicode |
|--------|--------------|---------------|---------|
| Բ/բ    | **P** (pet)  | B (bat)       | U+0532/U+0562 |
| Պ/պ    | **B** (bat)  | P (pet)       | U+054A/U+057A |
| Գ/գ    | **K** (kite) | G (go)        | U+0533/U+0563 |
| Կ/կ    | **G** (go)   | K (kite)      | U+053F/U+056F |
| Դ/դ    | **T** (top)  | D (dog)       | U+0534/U+0564 |
| Տ/տ    | **D** (dog)  | T (top)       | U+054F/U+057F |
| Ծ/ծ    | **DZ**       | TS            | U+053E/U+056E |
| Ձ/ձ    | **TS**       | DZ            | U+0541/U+0571 |
| Ճ/ճ    | **J** (joy)  | CH (church)   | U+0543/U+0573 |
| Ջ/ջ    | **CH** (church) | J (joy)    | U+054B/U+057B |
| Չ/չ    | **CH** (soft)| CH            | U+0549/U+0579 |

**Rule:** When the user writes Armenian script, the letters represent Western sounds. When TTS or Whisper processes them, they interpret them as Eastern sounds. All bridging code must account for this.

## 2. TTS Consonant Swap

To make Azure TTS (Eastern Armenian engine) produce Western sounds, we swap consonants BEFORE sending to TTS:

```
Բ↔Պ, Գ↔Կ, Դ↔Տ, Ծ↔Ձ, Ճ↔Ջ (plus lowercase)
```

This is a **bidirectional swap** via `str.maketrans`. Example: "Բարev" (Western script, sounds like "Parev") becomes "Պարev" before TTS, so the Eastern engine says "Parev" instead of "Barev".

Implementation: `generate_audio_dual.py` → `WESTERN_CONSONANT_SWAP`

## 3. TTS Vowel/Semivowel Fixes

Beyond consonants, 4 pronunciation patterns need fixing for TTS. These are stored in `WESTERN_TO_EASTERN_FIXES` (140+ word mappings) in `generate_audio_dual.py`.

**Pattern A — Word-final silent Y (sounds "ah" not "ay"):**
Drop the final Y letter so Azure says "ah" instead of "ay".
- Vray -> Vra ("on top of"), Degha-y -> Degha ("boy")
- Exception: Hay ("Armenian") — the "ay" IS correct, do NOT fix
- Don't fix "-ayi" endings (the Y is pronounced before I)
- See `generate_audio_dual.py` lines 84-91

**Pattern B — AW digraph (sounds "av" not "aw"):**
Replace the digraph so Azure says "av" instead of "aw".
- Hav ("chicken"), Lav ("good"), Aravod ("morning"), Kavat ("cup")
- See `generate_audio_dual.py` lines 94-112

**Pattern 1 — Past tense verb endings (same AW->AV fix):**
55+ verbs: ekav (came), perav (brought), kerav (ate), tesav (saw), arav (took)
- See `generate_audio_dual.py` lines 114-150

**Pattern 2 — "UA" -> "VA" in wash verb conjugations:**
12 forms: luam -> lvam, luatsi -> lvatsi
- See `generate_audio_dual.py` lines 152-165

**Pattern 3 — Word-final silent Y in present/future verbs:**
30+ conjugations: k'ertay -> k'erta, ku gay -> ku ga
- See `generate_audio_dual.py` lines 167-200

**Pattern 4 — Word-final long-E -> short-E for natural TTS:**
Softens verb endings: k'uze, ke sire
- See `generate_audio_dual.py` lines 202-210

**Pattern 5 — "-tyoon" suffix split (theta-i-yiwn-nun → theta-i-vo-nun):**
The Western -tyoon suffix (U+0569 U+056B U+0582 U+0576) gets split by Azure TTS into "tye" + "oon" (two syllables). Fix: replace yiwn (U+0582) with vo (U+0578) in the suffix so TTS reads it as one fluid syllable. This is a general pattern replacement in `apply_western_fixes()`, affecting 12+ words (Tsedesutyoon, Shnorhagalutyoon, etc.). Audio files must be regenerated after this fix.

**When adding new lessons:** Scan for words with these patterns. Test-generate 2-3 flagged words and listen before bulk run. Add problem words to `WESTERN_TO_EASTERN_FIXES`.

Always refer to the source code for exact Unicode mappings — this skill describes patterns conceptually.

Implementation: `generate_audio_dual.py` -> `WESTERN_TO_EASTERN_FIXES` dict + `apply_western_fixes()` function.

## 4. Whisper Speech Recognition — Comparison Strategy

Whisper transcribes in **Eastern Armenian** spelling, but the app's expected text is in **Western Armenian** spelling. These are fundamentally different orthographies for the same words — not just consonant differences but also different letter choices (e.g., Yiwn U+0582 vs Vew U+057E for the "v" sound).

**Approach: Convert expected text to Eastern form, then compare.**

Before comparing, `compare_armenian_text()` in `speech_analysis.py`:
1. Applies `WESTERN_TO_EASTERN_SWAP` to the expected text (same consonant swap used for TTS) — this converts Western consonants to their Eastern equivalents
2. Both sides are now in Eastern-ish form
3. Applies `_normalize_armenian()` to both sides (punctuation removal, sounds-alike consolidation, case normalization)
4. Compares using fuzzy matching

**The UI still displays the original Western text** — the Eastern conversion is only for comparison.

**`_normalize_armenian()` performs 6 steps:**
1. Unicode NFC normalization
2. Apostrophe normalization (4 variants to ASCII)
3. Armenian punctuation removal (6 marks)
4. ASCII punctuation removal
5. Sounds-alike consolidation (SOUNDS_ALIKE_MAP) — maps variant letters to canonical forms
6. Lowercase + whitespace collapse

**SOUNDS_ALIKE_MAP handles Whisper's variant letter choices:**

| Variant | Canonical | Reason |
|---------|-----------|--------|
| Ց (U+0551, Co/Tso) | Ծ (U+053E, Tsa) | Both make TS sound |
| Չ (U+0549, Cha) | Ճ (U+0543, Cha) | Both make CH sound |
| Փ (U+0553, Piwr) | Պ (U+054A, Peh) | Both make P sound |
| Ք (U+0554, Keh) | Կ (U+053F, Ken) | Both make K sound |
| Թ (U+0539, To) | Տ (U+054F, Tiwn) | Both make T sound |
| Ւ (U+0552, Yiwn) | Վ (U+054E, Vew) | Both make V sound (Western vs Eastern spelling) |

**Debug mode:** Set `DEBUG_SPEECH = True` in `config.py` to print raw/normalized codepoints to the terminal for every comparison. Use `_debug_print()` for Windows-safe output (avoids cp1252 encoding crashes with Armenian text).

## 5. Phonetic Transliteration Conventions

When writing phonetic (Latin character) representations of Armenian words:

- Use **"oo"** for the ու sound (not "u"): Tsedesutyoon, Yergoo
- Use **"gh"** for Ղ: Yeghpayr, Degha
- Use **"kh"** for Խ: Khosil
- Use **"sh"** for Շ: Shnorhagal, Shapat
- Use **"ch"** for Չ/Ճ: Yech, Inch
- Use **"ts"** for Ծ/Ց: Tsedesutyoon
- Use **"dz"** for Ձ: Dzayn
- Double vowels for long sounds: Eellal (not Ellal)
- Western consonant sounds in phonetics: Pen (not Ben), Kal (not Gal), Degha (not Tegha)

## 6. Armenian Unicode Range

- Full block: U+0530 to U+058F
- Uppercase: Ա-Ֆ (U+0531-U+0556)
- Lowercase: ա-ֆ (U+0561-U+0586)
- Detection: `any('\u0530' <= c <= '\u058F' for c in text)`

## 7. Audio Architecture

- **TTS Engine:** Azure Speech SDK, Eastern Armenian voices
  - Male: `hy-AM-HaykNeural`
  - Female: `hy-AM-AnahitNeural`
- **CDN:** `https://raw.githubusercontent.com/SevvyV/ArmenianTutor/main/ArmenianAITutor/audio_library/...`
- **Whisper:** OpenAI `whisper-1`, language code `hy`
- **Accuracy threshold:** 70% to pass pronunciation check
- **Fuzzy matching thresholds:** 1-3 chars = 50%, 4-5 chars = 60%, 6+ chars = 70%
- **Recording limits:** 0.3s minimum, 15s maximum

## 8. Speech Comparison Logic

The comparison pipeline in `compare_armenian_text()`:
1. **Convert expected to Eastern:** `expected.translate(WESTERN_TO_EASTERN_SWAP)` — consonant swap so both sides use Eastern orthography
2. **Normalize both sides:** punctuation removal, sounds-alike consolidation, case + whitespace normalization
3. **Word-level matching:** fuzzy match each expected word against transcribed words with length-aware thresholds (1-3 chars: 50%, 4-5 chars: 60%, 6+ chars: 70%)
4. **Sentence-level fallback:** SequenceMatcher ratio on joined strings
5. **Final score:** `max(word_accuracy, sentence_accuracy)`
6. **Prefix merging:** Short Armenian prefixes (1-2 chars like present tense markers) get merged with following word before comparison, since Whisper merges them

**Critical:** The UI shows the original Western expected text. Only the comparison uses the Eastern-converted form.

## 9. Key Files

| File | Contains |
|------|----------|
| `speech_analysis.py` | WESTERN_TO_EASTERN_SWAP, SOUNDS_ALIKE_MAP, _normalize_armenian(), compare_armenian_text(), render_mic_inline() |
| `generate_audio_dual.py` | WESTERN_CONSONANT_SWAP, WESTERN_TO_EASTERN_FIXES, apply_western_fixes(), audio generation, -tyoon suffix fix |
| `config.py` | WHISPER_MODEL, SPEECH_ACCURACY_THRESHOLD, AZURE_VOICES, DEBUG_SPEECH, recording limits |
| `alphabet.py` | 38 letters with Western phonetics, sounds, examples |
| `lessons.py` | Vocabulary with Armenian script + phonetic + English |
| `verb_conjugation.py` | 50 verbs across present/past/future with pronouns |
| `pimsleur_data.py` | Conversation-based lesson segments with phrases |

## 10. Common Pitfalls

- **Never compare Western expected text directly against Whisper output.** They use different orthographies. Always convert expected to Eastern form first (via `WESTERN_TO_EASTERN_SWAP`), then normalize both sides.
- **The same consonant swap table is used for TTS AND Whisper comparison** — both need Western-to-Eastern conversion for different reasons.
- **Whisper uses variant letters** for similar sounds (Piwr instead of Peh for P, Vew instead of Yiwn for V). The SOUNDS_ALIKE_MAP handles these — expand it when new variants are discovered.
- **Ց (U+0551, "Ts") and Ձ (U+0541, "Dz/Ts")** are different letters. Both are handled via SOUNDS_ALIKE_MAP → canonical Ծ (U+053E).
- **Ւ (U+0552, Yiwn) and Վ (U+054E, Vew)** both represent "v" — Western vs Eastern orthographic convention. SOUNDS_ALIKE_MAP normalizes Yiwn → Vew.
- **Word-final յ** is often silent in Western Armenian. Whisper may or may not include it.
- **Present tense prefix** (ke/ge) appears as a separate word in written Western Armenian but Whisper merges it with the verb.
- **Windows terminal (cp1252) cannot print Armenian characters.** Use `_debug_print()` for safe output. Never use raw `print()` with Armenian text.
- **Azure TTS key** is in Azure Key Vault `kv-vartanian-prod` → `AzureKey1`
- **OpenAI key** for Whisper is in `.streamlit/secrets.toml` (gitignored), sourced from Key Vault → `OpenAI-HYE-Tutor`
- **When adding new vocabulary/lessons**, check for TTS patterns (word-final silent Y, AW digraph, -tyoon suffix). See Section 3.
- **Audio regeneration required** after TTS fix changes — code changes alone don't update the .mp3 files.

## 11. Armenian Text in Chat and Files — Garbling Prevention

**Problem:** When writing Armenian multi-character words inline with Latin text in chat messages, markdown files, or skill files, the text frequently garbles. Individual Armenian characters (Բ, Պ, Գ) render fine, but full Armenian words mixed with Latin text corrupt into nonsense like "Delays", "delays", "adeduction", etc.

**Rules to avoid garbling:**
1. **In chat messages:** Use transliterated Latin forms (e.g., "Parev" not "Բarev") when discussing Armenian words conversationally.
2. **In documentation/skill files:** Describe patterns conceptually with transliterations and reference source code line numbers for the actual Armenian Unicode text. Do NOT try to inline Armenian words in markdown prose.
3. **In source code (.py files):** Armenian Unicode strings work correctly in Python source files. Always write Armenian text directly in code — this is the safe place for it.
4. **Individual characters are safe:** Single Armenian letters (Բ, Պ, Ց) with Unicode codepoints render fine in tables and inline references. The issue is with multi-character Armenian words.
5. **When referencing Armenian words:** Prefer the format `Parev (see line 87)` over trying to write the Armenian script inline.
