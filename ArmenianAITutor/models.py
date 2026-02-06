"""
Data models for Armenian Tutor App.

Unified structures for vocabulary, sentences, and lessons with type safety.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Literal


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
            clean_text = self.english
            
            # Strip leading emoji (emojis are typically unicode > 0x1F000)
            while clean_text and ord(clean_text[0]) > 0x1F000:
                clean_text = clean_text[1:].strip()
            
            # Remove invalid Windows filename characters: < > : " / \ | ? *
            invalid_chars = '<>:"/\\|?*'
            for char in invalid_chars:
                clean_text = clean_text.replace(char, '')
            
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
