"""
Audio management with dual-voice support for Armenian Tutor v20.

Handles URL generation for the new nested audio structure:
- audio_library/vocabulary/{lesson_id}/{voice}/{file}.mp3
- audio_library/sentences/{lesson_id}/{voice}/{file}.mp3
- audio_library/verbs/{voice}/{file}.mp3
"""

from config import BASE_AUDIO_URL, DEFAULT_VOICE


class AudioManager:
    """
    Manages audio file URL generation with dual-voice support.
    
    New folder structure:
    - Vocabulary: audio_library/vocabulary/lesson_01/male/hello.mp3
    - Sentences: audio_library/sentences/lesson_05/male/sent_be_present.mp3
    - Verbs: audio_library/verbs/male/verb_to_be_present.mp3
    """
    
    @classmethod
    def get_url(
        cls,
        audio_key: str,
        lesson_type: str,
        lesson_id: str,
        voice: str = None
    ) -> str:
        """
        Generate full GitHub URL for an audio file.
        
        Args:
            audio_key: Filename without extension (e.g., "hello", "verb_to_be_present")
            lesson_type: "vocabulary", "sentences", or "verbs"
            lesson_id: Lesson identifier (e.g., "lesson_01")
            voice: "male" or "female" (defaults to DEFAULT_VOICE if not specified)
        
        Returns:
            Full URL to the .mp3 file
        
        Examples:
            >>> AudioManager.get_url("hello", "vocabulary", "lesson_01", "male")
            'https://.../audio_library/vocabulary/lesson_01/male/hello.mp3'
            
            >>> AudioManager.get_url("verb_to_be_present", "verbs", "", "female")
            'https://.../audio_library/verbs/female/verb_to_be_present.mp3'
        """
        # Use default voice if not specified
        if voice is None:
            voice = DEFAULT_VOICE
        
        # Build path based on lesson type
        if lesson_type == "verbs":
            # Flat structure for verbs: verbs/{voice}/{file}.mp3
            path = f"verbs/{voice}/{audio_key}.mp3"
        else:
            # Nested structure for vocab/sentences: {type}/{lesson_id}/{voice}/{file}.mp3
            path = f"{lesson_type}/{lesson_id}/{voice}/{audio_key}.mp3"
        
        return f"{BASE_AUDIO_URL}/{path}"
    
    @classmethod
    def get_vocabulary_url(cls, audio_key: str, lesson_id: str, voice: str = None) -> str:
        """
        Convenience method for vocabulary audio.
        
        Args:
            audio_key: Filename without extension
            lesson_id: Lesson identifier (e.g., "lesson_01")
            voice: "male" or "female"
        
        Returns:
            Full URL to vocabulary MP3
        """
        return cls.get_url(audio_key, "vocabulary", lesson_id, voice)
    
    @classmethod
    def get_sentence_url(cls, audio_key: str, lesson_id: str, voice: str = None) -> str:
        """
        Convenience method for sentence audio.
        
        Args:
            audio_key: Filename without extension
            lesson_id: Lesson identifier (e.g., "lesson_05")
            voice: "male" or "female"
        
        Returns:
            Full URL to sentence MP3
        """
        return cls.get_url(audio_key, "sentences", lesson_id, voice)
    
    @classmethod
    def get_verb_url(cls, verb_key: str, tense: str, voice: str = None) -> str:
        """
        Convenience method for verb conjugation audio.
        
        Args:
            verb_key: Verb identifier (e.g., "be", "have", "go")
            tense: "present", "past", or "future"
            voice: "male" or "female"
        
        Returns:
            Full URL to verb MP3
        
        Example:
            >>> AudioManager.get_verb_url("be", "present", "male")
            'https://.../audio_library/verbs/male/verb_to_be_present.mp3'
        """
        audio_key = f"verb_to_{verb_key}_{tense}"
        return cls.get_url(audio_key, "verbs", "", voice)
    
    @classmethod
    def get_conversation_url(cls, audio_key: str, lesson_id: str, voice: str = None) -> str:
        """
        Convenience method for Pimsleur conversation audio.

        Path: audio_library/conversations/{lesson_id}/{voice}/{audio_key}.mp3

        Args:
            audio_key: Filename without extension (e.g., "line_004")
            lesson_id: Lesson identifier (e.g., "pimsleur_01")
            voice: "male" or "female"

        Returns:
            Full URL to conversation MP3
        """
        if voice is None:
            voice = DEFAULT_VOICE
        return f"{BASE_AUDIO_URL}/conversations/{lesson_id}/{voice}/{audio_key}.mp3"

    @classmethod
    def validate_voice(cls, voice: str) -> str:
        """
        Validate voice parameter and return valid voice.
        
        Args:
            voice: Voice string to validate
        
        Returns:
            Valid voice ("male" or "female")
        """
        if voice in ["male", "female"]:
            return voice
        return DEFAULT_VOICE
