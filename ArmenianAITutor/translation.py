"""
Live Translation Feature for Armenian Tutor App

English → Armenian translation with Azure TTS pronunciation.
Includes caching to minimize API costs.
"""

import streamlit as st
from deep_translator import GoogleTranslator
import azure.cognitiveservices.speech as speechsdk
import io


# ============================================================================
# CONVENIENCE FUNCTION FOR STREAMLIT APP
# ============================================================================

def translate_and_speak(english_text: str, azure_key: str, azure_region: str = "eastus", voice: str = "male"):
    """
    Convenience function for Streamlit app.
    Translates English to Armenian and generates audio.
    
    Args:
        english_text: Text to translate
        azure_key: Azure Speech API key
        azure_region: Azure region
        voice: "male" or "female"
    
    Returns:
        Tuple of (armenian_text, audio_bytes)
    """
    # Translate text
    translator = GoogleTranslator(source='en', target='hy')
    armenian_text = translator.translate(english_text)
    
    # Configure TTS
    speech_config = speechsdk.SpeechConfig(subscription=azure_key, region=azure_region)
    
    # Select voice
    if voice == "female":
        speech_config.speech_synthesis_voice_name = "hy-AM-AnahitNeural"
    else:
        speech_config.speech_synthesis_voice_name = "hy-AM-HaykNeural"
    
    # Use stream output instead of speaker or file
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )
    
    # Create synthesizer with null output (returns audio data directly)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
    
    result = synthesizer.speak_text_async(armenian_text).get()
    
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        # Return audio bytes
        return armenian_text, result.audio_data
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        raise Exception(f"TTS failed: {cancellation.reason} - {cancellation.error_details}")
    else:
        raise Exception(f"TTS failed: {result.reason}")


class LiveTranslator:
    """
    Handles English → Armenian translation with Azure TTS.
    
    Uses Google Translate for text translation (free, instant).
    Uses Azure TTS for audio generation (costs credits, cached).
    """
    
    def __init__(self, azure_key: str, azure_region: str = "eastus"):
        """
        Initialize translator with Azure credentials.
        
        Args:
            azure_key: Azure Speech API key
            azure_region: Azure region (default: "eastus")
        """
        self.speech_config = speechsdk.SpeechConfig(
            subscription=azure_key,
            region=azure_region
        )
        # Use Eastern Armenian voice
        self.speech_config.speech_synthesis_voice_name = "hy-AM-HaykNeural"
        
        # Initialize Google Translator
        try:
            self.translator = GoogleTranslator(source='en', target='hy')
        except Exception as e:
            st.error(f"Translation service initialization failed: {str(e)}")
            self.translator = None
    
    def translate_text(self, english_text: str) -> str:
        """
        Translate English to Armenian.
        
        Note: Google Translate gives Eastern Armenian.
        For Western Armenian, you'd need a specialized translator.
        
        Args:
            english_text: English text to translate
        
        Returns:
            Armenian translation or error message
        """
        if not self.translator:
            return "Translation service unavailable"
        
        try:
            armenian = self.translator.translate(english_text)
            return armenian
        except Exception as e:
            return f"Translation error: {str(e)}"
    
    def synthesize_speech(self, armenian_text: str) -> bytes:
        """
        Generate audio for Armenian text using Azure TTS.
        
        Args:
            armenian_text: Armenian text to speak
        
        Returns:
            Audio data as bytes, or None if failed
        """
        try:
            # Create synthesizer (returns audio bytes, doesn't play)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None  # Return bytes instead of playing
            )
            
            # Synthesize
            result = synthesizer.speak_text_async(armenian_text).get()
            
            # Check result
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                st.error(f"❌ Audio generation failed: {cancellation.reason}")
                if cancellation.error_details:
                    st.error(f"Details: {cancellation.error_details}")
                return None
            else:
                st.error(f"❌ Unknown error in audio generation")
                return None
                
        except Exception as e:
            st.error(f"❌ Audio synthesis error: {str(e)}")
            return None


# ============================================================================
# CACHING UTILITIES
# ============================================================================

def get_cached_translation(english_text: str):
    """
    Get cached translation if it exists.
    
    Uses Streamlit session_state as cache.
    Returns tuple: (armenian_text, audio_data) or None
    """
    cache_key = f"translation_{english_text}"
    return st.session_state.get(cache_key)


def cache_translation(english_text: str, armenian_text: str, audio_data: bytes):
    """
    Cache translation and audio for future use.
    
    Reduces Azure API calls by 80-90% for common phrases.
    """
    cache_key = f"translation_{english_text}"
    st.session_state[cache_key] = (armenian_text, audio_data)


def get_cache_stats():
    """Return statistics about cached translations."""
    translation_keys = [k for k in st.session_state.keys() if k.startswith("translation_")]
    return {
        "cached_phrases": len(translation_keys),
        "estimated_api_calls_saved": len(translation_keys),
    }


# ============================================================================
# COMMON PHRASES (Pre-cached to avoid API calls)
# ============================================================================

COMMON_PHRASES = {
    "hello": ("Բարեւ", "common/hello.mp3"),
    "thank you": ("Շնորհակալ եմ", "common/thank_you.mp3"),
    "goodbye": ("Ցտեսութիւն", "common/goodbye.mp3"),
    "how are you": ("Ինչպէ՞ս ես", "common/how_are_you.mp3"),
    "i am well": ("Լաւ եմ", "common/i_am_well.mp3"),
    # Add more common phrases as needed
}


def is_common_phrase(english_text: str) -> bool:
    """Check if text is a pre-defined common phrase."""
    return english_text.lower().strip() in COMMON_PHRASES


def get_common_phrase(english_text: str):
    """
    Get common phrase translation without using API.
    
    Returns tuple: (armenian_text, None) - no audio data since we'd use existing files
    """
    phrase_data = COMMON_PHRASES.get(english_text.lower().strip())
    if phrase_data:
        return (phrase_data[0], None)  # Return Armenian text, no audio (use existing file)
    return None
