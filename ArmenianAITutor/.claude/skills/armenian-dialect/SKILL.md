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

**Pattern 6 — Word-initial Yi = "h" not "y" (U+0545/U+0575 → U+0540/U+0570):**
In Western Armenian, word-initial Yi (U+0545 uppercase, U+0575 lowercase) is pronounced "h", not "y" as in Eastern. The fix uses `re.sub(r'\bYi', 'Ho', text)` to replace at word boundaries only — mid-word Yi (e.g., in -ayi endings) is unaffected. Affects months (Hounvar, Hounis, Houlis), verbs (Hishel = "to remember"), adjectives (Hognadzadz = "tired"), and phrases (Hajoghoutyon = "success/luck").
- See `generate_audio_dual.py` in `apply_western_fixes()`, after the -tyoon fix

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

### Instructor TTS Pronunciation Fix Pipeline

Pimsleur instructor audio uses an **English voice** (en-US-JennyNeural) to narrate Armenian phonetic fragments. English TTS mispronounces certain Armenian phonetic clusters. Two fix mechanisms exist, tried in priority order:

**Priority 1 — SSML IPA Phonemes** (`ipa_phoneme_map.py`):
Armenian phonetic tokens are wrapped in `<phoneme alphabet="ipa" ph="...">` SSML tags, giving the TTS engine exact pronunciation via IPA transcription. The pipeline uses `wrap_instructor_text_ssml()` which scans instructor text for tokens in `ARMENIAN_IPA_MAP` and returns a complete SSML envelope, or `None` if no tokens match.

**Priority 2 — Regex Text Fixes** (`syllable_drill_agent.py`):
Fallback for instructor lines with no IPA-mapped tokens. Regex patterns in `apply_tts_fixes()` transform text (e.g., "tyoon" to "tee-yoon") before sending as plain text.

**en-US IPA Phone Set Limitations:**
Azure's en-US voice does NOT support all IPA symbols. Key gaps and approximations:

| Armenian Sound | True IPA | en-US Approximation | Strategy |
|---------------|----------|-------------------|----------|
| ts (affricate) | /ts/ | `ts` (two phones) | Sequential t+s |
| gh (uvular) | /ɣ/ | `g` | Closest voiced stop |
| kh (velar fricative) | /x/ | `k` | Closest voiceless stop |
| Aspirated t | /tʰ/ | `t` | Plain t (no aspiration marker) |
| zh (postalveolar) | /ʒ/ | `ʒ` | Natively supported |
| sh (postalveolar) | /ʃ/ | `ʃ` | Natively supported |

Supported en-US consonants: `b d f g h j k l m n ŋ p ɹ s ʃ t θ ð v w z ʒ tʃ dʒ`

**SSML structure** (same pattern as verb/prayer SSML in `generate_audio_dual.py`):
```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
  <voice name="en-US-JennyNeural">
    Say: <phoneme alphabet="ipa" ph="tjun">tyoon</phoneme>
  </voice>
</speak>
```
The `<voice>` tag in SSML overrides the voice set in SpeechConfig, so `synthesize_to_file_ssml()` can be called with a dummy voice key.

**Known IPA-mapped tokens** (in `ARMENIAN_IPA_MAP`):

| Token | IPA | Problem solved |
|-------|-----|---------------|
| tyoon | `tjun` | ty+vowel English "tie" |
| Tsedesutyoon | `tsɛdɛsʌtjun` | Ts onset + ty mid-word |
| Bzdik / Bz-dik | `bəzdɪk` | Bz impossible onset |
| Bdegh | `bdɛg` | Bd onset + uvular ending |
| Khntrem | `kəntɹɛm` | Khn triple consonant |
| Tsakh | `tsɑk` | Ts word-initial |
| Agheg / Agh-eg | `ɑgɛk` | gh uvular fricative |
| Yeghpayr | `jɛgpaɪɹ` | gh between vowels |
| Inknasharzh | `ɪnknəʃɑɹʒ` | zh ending + clusters |
| Sksel | `skəsɛl` | Sks onset |

**Regex fallback patterns** (in `syllable_drill_agent.py`):

| Pattern | English TTS says | Fix | Example |
|---------|-----------------|-----|---------|
| `ty` + vowel (word start) | "tie-oon" | `tee-y` + vowel | tyoon to tee-yoon |
| `ty` + vowel (mid-word) | "tie-oon" | insert hyphen break | Tsedesutyoon to Tsedesu-tee-yoon |
| `Bz` at word start | splits "b-z" | `Buhz` | Bz-dik to Buhz-dik |

**Integration flow in `generate_pimsleur_audio.py`:**
1. Clean instructor text (strip trailing markers)
2. Try `wrap_instructor_text_ssml(clean_text, INSTRUCTOR_VOICE)` — returns SSML or None
3. If SSML: call `synthesize_to_file_ssml(ssml, path, "male")` (voice tag overrides)
4. If None: apply `apply_tts_fixes()` regex, then `synthesize_to_file_with_voice()`

**When adding new lessons or drill text:**
1. Write phonetic text naturally (e.g., "tyoon", "Bzdik") — this is what the student SEES
2. Check if the token needs IPA: add to `ARMENIAN_IPA_MAP` in `ipa_phoneme_map.py`
3. Run `python ipa_phoneme_map.py` to validate IPA entries use valid en-US phones
4. A/B test new entries: `python test_ipa_phonemes.py --word <token>`
5. Run `python regenerate_instructor_audio.py --scan` to see which lines use SSML vs regex
6. Run `python regenerate_instructor_audio.py` to regenerate affected audio files

**Regeneration script** (`regenerate_instructor_audio.py`):
```
python regenerate_instructor_audio.py --scan              # dry run — show SSML/regex per line
python regenerate_instructor_audio.py                     # delete + regenerate affected only
python regenerate_instructor_audio.py --lesson pimsleur_01  # specific lesson
python regenerate_instructor_audio.py --force             # ALL instructor audio
```

**A/B test script** (`test_ipa_phonemes.py`):
```
python test_ipa_phonemes.py                  # generate all A/B pairs
python test_ipa_phonemes.py --word tyoon     # one word only
python test_ipa_phonemes.py --list           # show test words + IPA
python test_ipa_phonemes.py --ssml-only      # SSML variants only
```
Output: `audio_library/ab_test/{token}_regex.mp3` and `{token}_ssml.mp3`

### Syllable Drill Agent (`syllable_drill_agent.py`)

Audits and generates Pimsleur-style syllable breakdown drills. Ensures three-layer alignment:
1. **display_text**: What the student SEES ("tyoon")
2. **tts_text**: What the English TTS SAYS ("tee-yoon") — via `apply_tts_fixes()`
3. **whisper_expected**: What Whisper CHECKS — Armenian script from the preceding speaker line

**Audit checks:** TTS mismatches, orphaned drills, fragment mismatches, progression errors, missing full-word steps.

**CLI usage:**
```
python syllable_drill_agent.py --audit                # audit all lessons
python syllable_drill_agent.py --audit pimsleur_01    # audit specific lesson
python syllable_drill_agent.py --report               # full drill report
```

### Audio Generation Functions (all in `generate_audio_dual.py`)

| Function | Output path | Count | Notes |
|----------|-------------|-------|-------|
| `generate_vocabulary_audio()` | `vocabulary/{lesson_id}/{voice}/` | ~698 | Uses `armenian_audio` or `armenian_display` |
| `generate_sentence_audio()` | `sentences/{lesson_id}/{voice}/` | ~300 | Same item field logic |
| `generate_verb_audio()` | `verbs/{voice}/verb_to_{key}_{tense}.mp3` | ~300 | SSML with 750ms pauses between pronoun conjugations |
| `generate_alphabet_audio()` | `alphabet/{voice}/alphabet_{pos:02d}{w\|e}.mp3` | 152 | Western: `apply_fixes=True`; Eastern: `apply_fixes=False` |
| `generate_prayer_audio()` | `prayers/{id}/{voice}/{audio_key}.mp3` | 34 | Lines + full recitation via SSML with 800ms pauses |
| `generate_all_audio()` | all of the above | ~1,484 | Master function; supports `--skip-verbs`, `--skip-alphabet`, `--skip-prayers` |

**Alphabet audio key insight:** Western alphabet letter names are written in Western Armenian script (e.g., letter 2 name is "Pen" spelled with Western letters). Since Azure TTS is Eastern, we must apply `apply_western_fixes()` (including consonant swap) so TTS produces Western sounds. Eastern alphabet names need NO fixes — TTS natively speaks Eastern.

**Prayer audio key insight:** Full prayer recitations use SSML with 800ms pauses between lines for natural cadence. Individual lines use `PrayerLine.armenian_audio` (falls back to `.armenian`) to honour any TTS pronunciation hacks defined in `prayers.py`.

**CLI usage:**
```
python generate_audio_dual.py --voice both                    # everything
python generate_audio_dual.py --type alphabet --voice both    # alphabet only
python generate_audio_dual.py --type prayers --voice both     # prayers only
python generate_audio_dual.py --skip-alphabet --skip-prayers  # vocab/sentences/verbs only
```

**Regeneration pattern:** To regenerate a category, delete its audio files first (the generators skip existing files), then run the appropriate command.

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
| `generate_audio_dual.py` | WESTERN_CONSONANT_SWAP, WESTERN_TO_EASTERN_FIXES, apply_western_fixes(), generate_alphabet_audio(), generate_prayer_audio(), all audio generation |
| `config.py` | WHISPER_MODEL, SPEECH_ACCURACY_THRESHOLD, AZURE_VOICES, DEBUG_SPEECH, recording limits |
| `alphabet.py` | 38 letters x 2 dialects with Western/Eastern phonetics, sounds, examples |
| `prayers.py` | PrayerLine/Prayer dataclasses, Lord's Prayer (12 lines), Meal Prayer (3 lines), PRAYERS registry |
| `lessons.py` | 43 lessons — vocabulary with Armenian script + phonetic + English |
| `verb_conjugation.py` | 50 verbs across present/past/future with pronouns |
| `pimsleur_data.py` | 20 conversation-based lesson segments with phrases |
| `syllable_drill_agent.py` | SyllableDrillAgent, apply_tts_fixes(), TTS_OVERRIDES, TTS_FIX_PATTERNS, drill auditing/generation |
| `ipa_phoneme_map.py` | ARMENIAN_IPA_MAP, wrap_instructor_text_ssml(), validate_ipa_phones() — SSML IPA phoneme pipeline |
| `test_ipa_phonemes.py` | A/B test script — generates regex vs SSML audio pairs in audio_library/ab_test/ |
| `regenerate_instructor_audio.py` | Scan + delete + regenerate instructor audio (IPA-aware: shows SSML vs regex per line) |
| `generate_pimsleur_audio.py` | Pimsleur conversation + instructor audio generation (SSML-first, regex fallback) |
| `pimsleur_renderer.py` | Streamlit renderer for Pimsleur lessons — drill classification, Whisper evaluation |
| `audio_manager.py` | AudioManager class — URL generation for all audio types (vocabulary, sentences, verbs, prayers, conversations) |

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
- **Phonetic for word-initial Yi:** When Yi starts a word, the phonetic transliteration must use "H" not "Y". Examples: Hognadzadz (tired), Hajoghoutun (good luck), Hounvar (January). Pattern 6 fixes TTS, but phonetics in `lessons.py` must also be updated manually.
- **Alphabet generator uses `apply_fixes=True` for Western, `apply_fixes=False` for Eastern.** This is intentional — Western letter names are written in Western script and need consonant swap. Eastern names are already native to the TTS engine.
- **Prayer full recitation uses SSML.** The full prayer audio joins all lines with 800ms breaks. Each line's text goes through `apply_western_fixes()` before insertion into SSML.
- **Generators skip existing files.** To force regeneration, delete the audio files first, then run the generator. This prevents accidental re-billing on Azure TTS.
- **Instructor audio uses an English voice (en-US-JennyNeural).** Armenian phonetic clusters like "ty" + vowel and word-initial "Bz" are mispronounced by this voice. Always use `apply_tts_fixes()` from `syllable_drill_agent.py` before sending instructor text to TTS. The fix is already integrated into `generate_pimsleur_audio.py`.
- **After adding TTS fix patterns**, run `python regenerate_instructor_audio.py` to find and regenerate all affected audio. Don't manually guess which files need updating — the script scans every instructor line automatically.
- **Pimsleur drill text stays human-readable.** Write "tyoon" in pimsleur_data.py (what the student sees), NOT "tee-yoon". The TTS fix pipeline handles the conversion at audio generation time. The display text and the TTS text are intentionally different.
- **Three-layer alignment in Pimsleur drills:** (1) display_text = what user sees, (2) tts_text = what TTS says (after apply_tts_fixes), (3) whisper_expected = Armenian script from preceding speaker line. Run `python syllable_drill_agent.py --audit` to verify all three layers are consistent.
- **SSML IPA phonemes take priority over regex fixes.** If a token is in `ARMENIAN_IPA_MAP`, the SSML path is used; regex `apply_tts_fixes()` only runs when `wrap_instructor_text_ssml()` returns None. Do not add the same token to both systems.
- **en-US IPA does NOT support ts, gh, kh, or aspirated t.** These must be approximated: ts as two separate phones `t`+`s`, gh/kh as `g`/`k`, aspirated t as plain `t`. Run `python ipa_phoneme_map.py` to validate entries.
- **SSML voice override pattern:** The `<voice name="en-US-JennyNeural">` tag in SSML overrides the voice set in SpeechConfig. This lets us call `synthesize_to_file_ssml(ssml, path, "male")` where "male" is a dummy — the SSML voice tag wins. Same pattern used for verb/prayer SSML.
- **XML escaping in SSML:** Instructor text may contain `&`, `<`, `>`, quotes, apostrophes (e.g., "Let's", "Hello & goodbye"). The `wrap_instructor_text_ssml()` function handles this via `xml.sax.saxutils.escape()` on non-phoneme text segments.
- **A/B test before deploying IPA changes.** Run `python test_ipa_phonemes.py` to generate regex vs SSML audio pairs in `audio_library/ab_test/`. Listen before running `regenerate_instructor_audio.py`.
- **Windows cp1252 cannot print IPA characters.** Use `_safe_print()` (UTF-8 buffer write) in any script that outputs IPA symbols. Both `ipa_phoneme_map.py` and `test_ipa_phonemes.py` handle this.

## 11. Armenian Text in Chat and Files — Garbling Prevention

**Problem:** When writing Armenian multi-character words inline with Latin text in chat messages, markdown files, or skill files, the text frequently garbles. Individual Armenian characters (Բ, Պ, Գ) render fine, but full Armenian words mixed with Latin text corrupt into nonsense like "Delays", "delays", "adeduction", etc.

**Rules to avoid garbling:**
1. **In chat messages:** Use transliterated Latin forms (e.g., "Parev" not "Բarev") when discussing Armenian words conversationally.
2. **In documentation/skill files:** Describe patterns conceptually with transliterations and reference source code line numbers for the actual Armenian Unicode text. Do NOT try to inline Armenian words in markdown prose.
3. **In source code (.py files):** Armenian Unicode strings work correctly in Python source files. Always write Armenian text directly in code — this is the safe place for it.
4. **Individual characters are safe:** Single Armenian letters (Բ, Պ, Ց) with Unicode codepoints render fine in tables and inline references. The issue is with multi-character Armenian words.
5. **When referencing Armenian words:** Prefer the format `Parev (see line 87)` over trying to write the Armenian script inline.
