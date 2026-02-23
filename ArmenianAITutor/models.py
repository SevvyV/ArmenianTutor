"""
Data models for Armenian Tutor App.

Unified structures for vocabulary, sentences, and lessons with type safety.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Literal, Tuple


@dataclass
class VocabItem:
    """
    Represents a single vocabulary word or phrase.
    
    Attributes:
        english: English translation
        armenian_display: Western Armenian (shown to user)
        phonetic: Pronunciation guide
        armenian_audio: Eastern-compatible text for TTS (optional, defaults to display)
        emoji: Optional emoji for visual representation
        image: Optional image filename (in image_library/)
        audio_key: Audio filename without extension (auto-generated if empty)
    """
    english: str
    armenian_display: str
    phonetic: str
    armenian_audio: str = ""  # For TTS workarounds (Eastern dialect hacks)
    emoji: Optional[str] = None
    image: Optional[str] = None
    audio_key: str = ""
    
    def __post_init__(self):
        """Auto-generate audio_key and set defaults."""
        # If no audio hack specified, use display version
        if not self.armenian_audio:
            self.armenian_audio = self.armenian_display
        
        # Auto-generate audio key from English text if not provided
        if not self.audio_key:
            # Remove emoji and clean text for filename
            import re
            clean_text = self.english
            
            # Remove ALL non-ASCII characters (emojis, symbols, combining marks)
            # This catches all emojis including number emojis, flags, symbols, etc.
            clean_text = ''.join(c for c in clean_text if ord(c) < 128)
            clean_text = clean_text.strip()
            
            # NOTE: Do NOT remove leading digits - audio files include them
            # e.g. "1 One" -> "1_one" -> with prefix "numbers_1_one.mp3"
            
            # Remove invalid Windows filename characters and punctuation
            invalid_chars = '<>:"/\\|?*.,!;\''
            for char in invalid_chars:
                clean_text = clean_text.replace(char, '')
            
            # Remove slashes (for items like "cup/mug" -> "cupmug")
            clean_text = clean_text.replace('/', '')
            
            # Convert to lowercase, replace spaces with underscores
            self.audio_key = clean_text.lower().replace(" ", "_")


@dataclass
class Sentence:
    """
    Represents a sentence or phrase with context.
    
    Attributes:
        english: English translation
        armenian_display: Western Armenian (shown to user)
        phonetic: Pronunciation guide
        audio_key: Audio filename without extension
        armenian_audio: Eastern-compatible text for TTS (optional)
        context: Optional context (e.g., "Early morning", "At dinner")
    """
    english: str
    armenian_display: str
    phonetic: str
    audio_key: str
    armenian_audio: str = ""
    context: Optional[str] = None
    
    def __post_init__(self):
        """Set defaults for audio workarounds."""
        if not self.armenian_audio:
            self.armenian_audio = self.armenian_display


@dataclass
class Lesson:
    """
    Represents a complete lesson with multiple items.
    
    Attributes:
        id: Unique lesson identifier (e.g., "greetings", "family")
        title: Display title (e.g., "Lesson 1: Greetings")
        lesson_type: Type of content ("vocabulary" or "sentences")
        items: List of VocabItem or Sentence objects
        prefix: Audio filename prefix for this lesson (e.g., "family", "sent")
    """
    id: str
    title: str
    lesson_type: Literal["vocabulary", "sentences"]
    items: List  # List[VocabItem] or List[Sentence]
    prefix: str = ""  # Audio prefix (empty for vocabulary without prefix)
    
    def __post_init__(self):
        """Apply prefix to all items' audio keys if specified."""
        if self.prefix:
            for item in self.items:
                # Only add prefix if not already present
                if not item.audio_key.startswith(self.prefix):
                    item.audio_key = f"{self.prefix}_{item.audio_key}"


# ============================================================================
# PIMSLEUR CONVERSATION MODELS
# ============================================================================

@dataclass
class ConversationLine:
    """A single line in a Pimsleur conversation script."""
    speaker: str              # "instructor", "male", "female", "pause", "sfx"
    text: str                 # The spoken text (English for instructor, Armenian for male/female)
    phonetic: str = ""        # Pronunciation guide (for Armenian lines)
    english: str = ""         # English translation (for Armenian lines)
    duration: float = 0.0     # Pause duration in seconds (for pause lines)
    audio_key: str = ""       # e.g., "line_003" — used for audio file lookup


@dataclass
class ConversationLesson:
    """A complete Pimsleur-style conversation lesson."""
    id: str                   # e.g., "pimsleur_01"
    title: str                # e.g., "Hello & Goodbye"
    unit: int                 # 1-4 (for grouping)
    lines: List[ConversationLine] = field(default_factory=list)
    new_vocabulary: List[str] = field(default_factory=list)
