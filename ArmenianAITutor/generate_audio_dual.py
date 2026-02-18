"""
Azure TTS Dual-Voice Audio Generation Script - Complete Rebuild

Generates ALL audio files for Armenian Tutor app with:
- Male voice (Hayk) AND Female voice (Anahit)
- Western Armenian pronunciation hacks for Eastern TTS
- Organized folder structure

Total: ~590 MP3 files (295 per voice)

Usage:
    python generate_audio_dual.py --voice both
    python generate_audio_dual.py --voice male
    python generate_audio_dual.py --lesson greetings_01
"""

import os
import sys
import time
import argparse
import azure.cognitiveservices.speech as speechsdk
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from pathlib import Path
from lessons import LESSONS
from verb_conjugation import VERBS


# ============================================================================
# AZURE KEY VAULT CONFIGURATION
# ============================================================================

KEY_VAULT_URL = "https://kv-vartanian-prod.vault.azure.net/"
SPEECH_KEY_SECRET_NAME = "AzureKey1"


def get_speech_key_from_vault() -> str:
    """Retrieve Azure Speech API key from Key Vault using Azure CLI credentials."""
    try:
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)
        secret = client.get_secret(SPEECH_KEY_SECRET_NAME)
        print("Retrieved speech key from Key Vault")
        return secret.value
    except Exception as e:
        print(f"Failed to retrieve key from Key Vault: {e}")
        print("   Make sure you have run 'az login' and have access to the vault.")
        sys.exit(1)


# ============================================================================
# WESTERN ARMENIAN PRONUNCIATION HACKS
# ============================================================================
# GUIDE FOR IDENTIFYING WORDS THAT NEED HACKS:
# Azure TTS uses Eastern Armenian pronunciation. Western Armenian spelling
# patterns get mispronounced. Scan new lessons against these patterns.
#
# PATTERN A: Word-final այ sounds "ay" but should be "ah"
#   Fix: drop the final յ so Azure says "ah" not "ay"
#   Examples: Վրայ->"Վրա" (Vra), Ակռայ->Ակռա (Agra)
#   EXCEPTIONS: Հայ (Hay=Armenian) - "ay" IS correct, do NOT fix.
#   Also don't fix այի endings (the յ is pronounced before ի).
#   HOW TO SPOT: phonetic ends in "a" but Armenian text ends in այ
#
# PATTERN B: աւ sounds "aw" but should be "av"
#   Fix: replace աւ with ավ so Azure says "av"
#   Examples: Հաւ (Hav), Լաւ (Lav), Առաւօտ (Aravod)
#   HOW TO SPOT: phonetic shows "av" but Azure says "aw"
#
# PATTERN C: Word-final է in verb conjugations
#   Fix: replace է with ե for better pronunciation
#
# PATTERN D: Past tense աւ endings (same as B in verb context)
#
# WHEN ADDING NEW LESSONS:
#   1. Scan for words ending in այ (Pattern A)
#   2. Scan for words containing աւ (Pattern B)
#   3. Test-generate 2-3 flagged words and listen before bulk run
#   4. Add new problem words to WESTERN_TO_EASTERN_FIXES below
# ============================================================================

WESTERN_TO_EASTERN_FIXES = {
    # ========================================================================
    # PATTERN A FIXES: Word-final այ -> ա (sounds "ah" not "ay")
    # Exception: Հայ (Hay=Armenian) is correct as-is
    # ========================================================================
    "Վրայ": "Վռա",              # on/on top of (Vra, not Vray)
    "վրայ": "վռա",              # on/on top of (lowercase)
    "Ակռայ": "Ակռա",          # tooth (Agra, not Agray)
    "չկայ": "չկա",              # doesn't exist (chga)
    "Տղայ": "Տղա",              # boy/son (Degha, not Deghay)

    # ========================================================================
    # PATTERN B FIXES: աւ -> ավ (sounds "av" not "aw") in vocabulary
    # ========================================================================
    "Հաւ": "Հավ",                    # chicken (Hav)
    "Հաւկիթ": "Հավկիթ",          # egg (Havgit)
    "Առաւօտ": "Առավօտ",          # morning (Aravod)
    "առաւօտ": "առավօտ",          # morning (lowercase)
    "Գաւաթ": "Գավաթ",          # cup (Kavat)
    "Տակաւին": "Տակավին",      # still/yet (Dagavin)
    "շաբաթաւերջ": "շաբաթավերջ",  # weekend
    "հրաւիրեմ": "հրավիրեմ",      # I invite
    "Շնորհաւոր": "Շնորհավոր",  # congratulations
    "Ձաւ": "Ձավ",                    # pain (Tsav)
    "Գլխացաւ": "Գլխացավ",      # headache
    "Լաւաշ": "Լավաշ",          # lavash
    "Լաւ": "Լավ",                    # good (Lav)
    "զաւակ": "զավակ",          # child (zavag)
    "մարեցաւ": "մարեցավ",      # died/went out (phone dead)
    "չեկաւ": "չեկավ",          # didn't come
    "չեղաւ": "չեղավ",          # didn't happen
    # ========================================================================
    # PATTERN 1: "աւ" → "ավ" in past tense verbs (very common!)
    # ========================================================================
    "ըրաւ": "ըրավ",          # did
    "եկաւ": "եկավ",          # came
    "բերաւ": "բերավ",        # brought
    "կերաւ": "կերավ",        # ate
    "տեսաւ": "տեսավ",        # saw
    "տուաւ": "տուավ",        # gave
    "առաւ": "առավ",          # took
    "գացաւ": "գացավ",        # went (but actual is գաց, not գացաւ)
    "դրաւ": "դրավ",          # put
    "բացաւ": "բացավ",        # opened
    "գոցաւ": "գոցավ",        # closed (but actual is գոցեց)
    "նստաւ": "նստավ",        # sat
    "քնացաւ": "քնացավ",      # slept
    "խօսեցաւ": "խօսեցավ",    # spoke
    "կայնեցաւ": "կայնեցավ",  # stood
    "սկսաւ": "սկսավ",        # started
    "ապրեցաւ": "ապրեցավ",    # lived
    "նայեցաւ": "նայեցավ",    # looked
    "սորվեցաւ": "սորվեցավ",  # learned
    "մոռցաւ": "մոռցավ",      # forgot
    
    # ========================================================================
    # PATTERN 2: "ուա" → "վա" in wash verb conjugations
    # ========================================================================
    "կը լուամ": "կը լվամ",
    "կը լուաս": "կը լվաս",
    "կը լուայ": "կը լվա",
    "կը լուանք": "կը լվանք",
    "կը լուաք": "կը լվաք",
    "կը լուան": "կը լվան",
    "լուացի": "լվացի",
    "լուացիր": "լվացիր",
    "լուաց": "լվաց",
    "լուացինք": "լվացինք",
    "լուացիք": "լվացիք",
    "լուացին": "լվացին",
    "պիտի լուամ": "պիտի լվամ",
    "պիտի լուաս": "պիտի լվաս",
    "պիտի լուայ": "պիտի լվա",
    "պիտի լուանք": "պիտի լվանք",
    "պիտի լուաք": "պիտի լվաք",
    "պիտի լուան": "պիտի լվան",
    
    # ========================================================================
    # PATTERN 3: Word-final "այ" → "ա" (drop silent յ) - KEEP THIS
    # NOTE: "կը նայի" should stay as "նայի" (pronounced "nayee")
    # Only fix word-final այ, not այի
    # ========================================================================
    "կ'արթննայ": "կ'արթննա",
    "կ'երթայ": "կ'երթա",
    "կու գայ": "կու գա",
    "կը տայ": "կը տա",
    "կը կարդայ": "կը կարդա",
    "կը խաղայ": "կը խաղա",
    "պիտի ըլլայ": "պիտի ըլլա",
    "պիտի երթայ": "պիտի երթա",
    "պիտի գայ": "պիտի գա",
    "պիտի տայ": "պիտի տա",
    "պիտի կարդայ": "պիտի կարդա",
    "պիտի խաղայ": "պիտի խաղա",
    "պիտի բանայ": "պիտի բանա",      # will open
    "կը բանայ": "կը բանա",            # opens
    "պիտի արթննայ": "պիտի արթննա",  # will wake up
    "պիտի քնանայ": "պիտի քնանա",    # will sleep
    "կը քնանայ": "կը քնանա",          # sleeps
    "պիտի ունենայ": "պիտի ունենա",  # will have
    "պիտի գիտնայ": "պիտի գիտնա",    # will know
    "պիտի մոռնայ": "պիտի մոռնա",    # will forget
    "պիտի հասկնայ": "պիտի հասկնա",  # will understand
    "կը մոռնայ": "կը մոռնա",          # forgets
    "կը հասկնայ": "կը հասկնա",        # understands
    
    # ========================================================================
    # PATTERN 4: "է" → "ե" for better TTS (word-final է can sound off)
    # ========================================================================
    "կ'ուզէ": "կ'ուզե",
    "կը սիրէ": "կը սիրե",
    "կը գրէ": "կը գրե",
    "կը բերէ": "կը բերե",
    "կ'ընէ": "կ'ընե",
    "կը տեսնէ": "կը տեսնե",
    "կը լսէ": "կը լսե",
    "կը խմէ": "կը խմե",
    "կ'ուտէ": "կ'ուտե",
    "կը դնէ": "կը դնե",
    "կ'առնէ": "կ'առնե",
    "կ'օգնէ": "կ'օգնե",
    "գիտէ": "գիտե",
    "ունի": "ունի",  # This one is already "ի" not "է"
}


def apply_western_fixes(armenian_text: str) -> str:
    """
    Apply Western → Eastern pronunciation hacks for better TTS.
    
    Args:
        armenian_text: Original Western Armenian text
    
    Returns:
        Modified text optimized for Azure TTS
    """
    text = armenian_text
    
    # Apply known fixes
    for western, eastern in WESTERN_TO_EASTERN_FIXES.items():
        text = text.replace(western, eastern)
    
    return text


# ============================================================================
# DUAL-VOICE TTS ENGINE
# ============================================================================

class DualVoiceTTS:
    """
    Handles text-to-speech for both male and female voices.
    """
    
    VOICES = {
        "male": "hy-AM-HaykNeural",
        "female": "hy-AM-AnahitNeural",
    }
    
    def __init__(self, subscription_key: str, region: str = "eastus"):
        """
        Initialize Azure Speech SDK.
        
        Args:
            subscription_key: Azure Speech API key
            region: Azure region
        """
        self.subscription_key = subscription_key
        self.region = region
    
    def synthesize_to_file_ssml(
        self, 
        ssml_text: str, 
        output_path: str, 
        voice: str = "male",
        delay: float = 1.0
    ) -> bool:
        """
        Generate audio file from SSML (for pauses, emphasis, etc).
        
        Args:
            ssml_text: SSML text with markup (e.g., <speak>text<break time="500ms"/>more</speak>)
            output_path: Full path where MP3 should be saved
            voice: "male" or "female"
            delay: Delay in seconds after each API call
        
        Returns:
            True if successful, False otherwise
        """
        # Convert path to absolute and normalize for Windows
        output_path = os.path.abspath(output_path)
        
        # Create parent directory
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Verify directory was created
        if not os.path.exists(os.path.dirname(output_path)):
            print(f"   ❌ Failed to create directory: {os.path.dirname(output_path)}")
            return False
        
        # Configure voice
        speech_config = speechsdk.SpeechConfig(
            subscription=self.subscription_key,
            region=self.region
        )
        speech_config.speech_synthesis_voice_name = self.VOICES[voice]
        
        # Configure audio output
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        
        # Create synthesizer
        try:
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
        except Exception as e:
            print(f"   ❌ Synthesizer creation failed: {str(e)}")
            return False
        
        # Synthesize using SSML
        result = synthesizer.speak_ssml_async(ssml_text).get()
        
        # Add delay to prevent rate limiting
        time.sleep(delay)
        
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return True
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            print(f"   ❌ Failed: {cancellation.reason}")
            if cancellation.error_details:
                print(f"      Error: {cancellation.error_details}")
            return False
        else:
            return False
    
    def synthesize_to_file(
        self, 
        text: str, 
        output_path: str, 
        voice: str = "male",
        apply_fixes: bool = True,
        delay: float = 1.0
    ) -> bool:
        """
        Generate audio file from Armenian text.
        
        Args:
            text: Armenian text (Western spelling)
            output_path: Full path where MP3 should be saved
            voice: "male" or "female"
            apply_fixes: Whether to apply Western→Eastern pronunciation hacks
            delay: Delay in seconds after each API call (prevents rate limiting)
        
        Returns:
            True if successful, False otherwise
        """
        # Apply pronunciation fixes
        if apply_fixes:
            tts_text = apply_western_fixes(text)
        else:
            tts_text = text
        
        # Convert path to absolute and normalize for Windows
        output_path = os.path.abspath(output_path)
        
        # Create parent directory
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Verify directory was created
        if not os.path.exists(os.path.dirname(output_path)):
            print(f"   ❌ Failed to create directory: {os.path.dirname(output_path)}")
            return False
        
        # Configure voice
        speech_config = speechsdk.SpeechConfig(
            subscription=self.subscription_key,
            region=self.region
        )
        speech_config.speech_synthesis_voice_name = self.VOICES[voice]
        
        # Configure audio output - use absolute path
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        
        # Create synthesizer
        try:
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
        except Exception as e:
            print(f"   ❌ Synthesizer creation failed: {str(e)}")
            return False
        
        # Synthesize
        result = synthesizer.speak_text_async(tts_text).get()
        
        # Add delay to prevent rate limiting
        time.sleep(delay)
        
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return True
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            print(f"   ❌ Failed: {cancellation.reason}")
            if cancellation.error_details:
                print(f"      Error: {cancellation.error_details}")
            return False
        else:
            return False


# ============================================================================
# AUDIO GENERATION FUNCTIONS
# ============================================================================

def generate_vocabulary_audio(tts: DualVoiceTTS, voices: list, output_dir: str = "audio_library"):
    """Generate audio for all vocabulary lessons."""
    
    print("\n" + "="*70)
    print("📚 GENERATING VOCABULARY AUDIO")
    print("="*70)
    
    stats = {"total": 0, "success": 0, "failed": 0, "skipped": 0}
    
    for lesson_id, lesson in LESSONS.items():
        if lesson.lesson_type != "vocabulary":
            continue
        
        print(f"\n📖 {lesson.title}")
        print(f"   Items: {len(lesson.items)}")
        
        for voice in voices:
            print(f"   Voice: {voice.capitalize()}")
            
            # Build output path: vocabulary/{lesson_id}/{voice}/
            voice_dir = f"{output_dir}/vocabulary/{lesson_id}/{voice}"
            
            for item in lesson.items:
                stats["total"] += 1
                output_path = f"{voice_dir}/{item.audio_key}.mp3"
                
                # Skip if exists
                if os.path.exists(output_path):
                    stats["skipped"] += 1
                    continue
                
                # Get text (use armenian_audio if present, else armenian_display)
                text = (item.armenian_audio if hasattr(item, 'armenian_audio') and item.armenian_audio 
                       else item.armenian_display)
                
                # Generate
                if tts.synthesize_to_file(text, output_path, voice):
                    print(f"      ✅ {item.audio_key}.mp3")
                    stats["success"] += 1
                else:
                    print(f"      ❌ {item.audio_key}.mp3 FAILED")
                    stats["failed"] += 1
    
    return stats


def generate_sentence_audio(tts: DualVoiceTTS, voices: list, output_dir: str = "audio_library"):
    """Generate audio for all sentence lessons."""
    
    print("\n" + "="*70)
    print("💬 GENERATING SENTENCE AUDIO")
    print("="*70)
    
    stats = {"total": 0, "success": 0, "failed": 0, "skipped": 0}
    
    for lesson_id, lesson in LESSONS.items():
        if lesson.lesson_type != "sentences":
            continue
        
        print(f"\n📝 {lesson.title}")
        print(f"   Items: {len(lesson.items)}")
        
        for voice in voices:
            print(f"   Voice: {voice.capitalize()}")
            
            # Build output path: sentences/{lesson_id}/{voice}/
            voice_dir = f"{output_dir}/sentences/{lesson_id}/{voice}"
            
            for item in lesson.items:
                stats["total"] += 1
                output_path = f"{voice_dir}/{item.audio_key}.mp3"
                
                # Skip if exists
                if os.path.exists(output_path):
                    stats["skipped"] += 1
                    continue
                
                # Get text
                text = (item.armenian_audio if hasattr(item, 'armenian_audio') and item.armenian_audio 
                       else item.armenian_display)
                
                # Generate
                if tts.synthesize_to_file(text, output_path, voice):
                    print(f"      ✅ {item.audio_key}.mp3")
                    stats["success"] += 1
                else:
                    print(f"      ❌ {item.audio_key}.mp3 FAILED")
                    stats["failed"] += 1
    
    return stats


def generate_verb_audio(tts: DualVoiceTTS, voices: list, output_dir: str = "audio_library"):
    """Generate audio for all verb conjugations with pronouns and pauses."""
    
    print("\n" + "="*70)
    print("🔤 GENERATING VERB CONJUGATION AUDIO")
    print("="*70)
    
    # Western Armenian pronouns
    PRONOUNS = ["Ես", "Դուն", "Անիկա", "Մենք", "Դուք", "Անոնք"]
    
    stats = {"total": 0, "success": 0, "failed": 0, "skipped": 0}
    
    for voice in voices:
        print(f"\n   Voice: {voice.capitalize()}")
        voice_dir = f"{output_dir}/verbs/{voice}"
        
        for verb_key, verb in VERBS.items():
            for tense in ["present", "past", "future"]:
                stats["total"] += 1
                
                # Filename: verb_to_{verb_key}_{tense}.mp3
                output_path = f"{voice_dir}/verb_to_{verb.verb_key}_{tense}.mp3"
                
                # Skip if exists
                if os.path.exists(output_path):
                    stats["skipped"] += 1
                    continue
                
                # Get conjugations for this tense
                conjugations = verb.conjugations[tense]
                
                # Build SSML with pronouns and pauses
                # Format: "Ես եմ <break time="750ms"/> Դուն ես <break time="750ms"/> ..."
                ssml_parts = []
                for pronoun, conjugation in zip(PRONOUNS, conjugations):
                    # Apply pronunciation fixes to each conjugation
                    fixed_conjugation = apply_western_fixes(conjugation)
                    ssml_parts.append(f"{pronoun} {fixed_conjugation}")
                
                # Join with pauses (750ms between each)
                ssml_text = '<break time="750ms"/>'.join(ssml_parts)
                
                # Get voice name for SSML
                voice_name = tts.VOICES[voice]
                
                # Wrap in SSML speak tag with voice declaration
                ssml_full = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hy-AM">
                    <voice name="{voice_name}">{ssml_text}</voice>
                </speak>'''
                
                # Generate using SSML
                if tts.synthesize_to_file_ssml(ssml_full, output_path, voice):
                    print(f"      ✅ verb_to_{verb.verb_key}_{tense}.mp3")
                    stats["success"] += 1
                else:
                    print(f"      ❌ verb_to_{verb.verb_key}_{tense}.mp3 FAILED")
                    stats["failed"] += 1
    
    return stats


def generate_single_lesson(
    lesson_id: str, 
    tts: DualVoiceTTS, 
    voices: list, 
    output_dir: str = "audio_library"
):
    """Generate audio for a single lesson only."""
    
    if lesson_id not in LESSONS:
        print(f"❌ Lesson '{lesson_id}' not found!")
        print(f"Available lessons: {', '.join(LESSONS.keys())}")
        return
    
    lesson = LESSONS[lesson_id]
    print(f"\n🎯 Generating audio for: {lesson.title}")
    
    # Route to appropriate generator
    if lesson.lesson_type == "vocabulary":
        # Temporarily filter
        temp_lessons = {lesson_id: lesson}
        original = LESSONS.copy()
        LESSONS.clear()
        LESSONS.update(temp_lessons)
        
        stats = generate_vocabulary_audio(tts, voices, output_dir)
        
        LESSONS.clear()
        LESSONS.update(original)
    
    elif lesson.lesson_type == "sentences":
        temp_lessons = {lesson_id: lesson}
        original = LESSONS.copy()
        LESSONS.clear()
        LESSONS.update(temp_lessons)
        
        stats = generate_sentence_audio(tts, voices, output_dir)
        
        LESSONS.clear()
        LESSONS.update(original)
    
    print_statistics(stats)


def generate_all_audio(tts: DualVoiceTTS, voices: list, output_dir: str = "audio_library"):
    """Generate ALL audio files."""
    
    print("\n" + "="*70)
    print("🎙️  ARMENIAN TUTOR - DUAL-VOICE AUDIO GENERATION")
    print("="*70)
    print(f"Output directory: {output_dir}/")
    print(f"Voices: {', '.join([v.capitalize() for v in voices])}")
    print("="*70)
    
    # Generate all types
    vocab_stats = generate_vocabulary_audio(tts, voices, output_dir)
    sentence_stats = generate_sentence_audio(tts, voices, output_dir)
    verb_stats = generate_verb_audio(tts, voices, output_dir)
    
    # Combine statistics
    total_stats = {
        "total": vocab_stats["total"] + sentence_stats["total"] + verb_stats["total"],
        "success": vocab_stats["success"] + sentence_stats["success"] + verb_stats["success"],
        "failed": vocab_stats["failed"] + sentence_stats["failed"] + verb_stats["failed"],
        "skipped": vocab_stats["skipped"] + sentence_stats["skipped"] + verb_stats["skipped"],
    }
    
    print_statistics(total_stats)


def print_statistics(stats: dict):
    """Print generation statistics."""
    print("\n" + "="*70)
    print("📊 GENERATION COMPLETE")
    print("="*70)
    print(f"Total files:    {stats['total']}")
    print(f"✅ Generated:   {stats['success']}")
    print(f"⏭️  Skipped:     {stats['skipped']} (already exist)")
    print(f"❌ Failed:      {stats['failed']}")
    
    if stats['success'] > 0:
        print(f"\n💡 Next steps:")
        print(f"1. Test audio files locally")
        print(f"2. Upload to GitHub: audio_library/")
        print(f"3. Commit and push to main branch")
    
    if stats['failed'] > 0:
        print(f"\n⚠️  Some files failed to generate. Check errors above.")


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate Armenian audio files with dual voice support"
    )
    parser.add_argument(
        "--voice",
        choices=["male", "female", "both"],
        default="both",
        help="Which voice(s) to generate (default: both)"
    )
    parser.add_argument(
        "--lesson",
        help="Generate specific lesson only (e.g., 'lesson_01')"
    )
    parser.add_argument(
        "--output",
        default="audio_library",
        help="Output directory (default: audio_library)"
    )
    parser.add_argument(
        "--skip-verbs",
        action="store_true",
        help="Skip verb conjugation generation"
    )
    
    args = parser.parse_args()
    
    # Get Azure credentials from Key Vault
    api_key = get_speech_key_from_vault()
    region = os.getenv("AZURE_SPEECH_REGION", "eastus")
    
    # Determine voices to generate
    voices = []
    if args.voice == "both":
        voices = ["male", "female"]
    else:
        voices = [args.voice]
    
    # Initialize TTS
    tts = DualVoiceTTS(api_key, region)
    
    # Generate audio
    if args.lesson:
        generate_single_lesson(args.lesson, tts, voices, args.output)
    else:
        generate_all_audio(tts, voices, args.output)


if __name__ == "__main__":
    main()
