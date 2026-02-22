"""
Configuration constants for Armenian Tutor App v20.

Base URLs, API keys, and app settings.
"""

# ============================================================================
# GITHUB REPOSITORY CONFIGURATION
# ============================================================================

GITHUB_USER = "SevvyV"
GITHUB_REPO = "ArmenianTutor"
GITHUB_BRANCH = "main"

# Base URLs for audio and images
BASE_AUDIO_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/ArmenianAITutor/audio_library"
BASE_IMAGE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/ArmenianAITutor/image_library"


# ============================================================================
# STREAMLIT APP CONFIGURATION
# ============================================================================

APP_TITLE = "HyeTutor v20"
APP_ICON = "🇦🇲"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"


# ============================================================================
# UI STYLING
# ============================================================================

# Card dimensions
CARD_HEIGHT = 380
IMAGE_HEIGHT = 230
EMOJI_SIZE = 150

# Colors (Western Armenian flag colors)
PRIMARY_COLOR = "#D90012"    # Red
SECONDARY_COLOR = "#0033A0"  # Blue
ACCENT_COLOR = "#F2A900"     # Orange/Gold


# ============================================================================
# AUDIO CONFIGURATION
# ============================================================================

# Available voices
AVAILABLE_VOICES = {
    "male": "🎙️ Male (Hayk)",
    "female": "🎙️ Female (Anahit)"
}

DEFAULT_VOICE = "male"


# ============================================================================
# AZURE TTS CONFIGURATION (for live translator)
# ============================================================================

# These should be set as Streamlit secrets in production
# Access via: st.secrets["AZURE_SPEECH_KEY"]
AZURE_REGION = "eastus"
AZURE_VOICES = {
    "male": "hy-AM-HaykNeural",
    "female": "hy-AM-AnahitNeural"
}


# ============================================================================
# FEATURE FLAGS
# ============================================================================

ENABLE_VERB_TOOL = True
ENABLE_LIVE_TRANSLATOR = True
ENABLE_VOICE_SELECTOR = True
ENABLE_SPEECH_PRACTICE = True


# ============================================================================
# SPEECH PRACTICE CONFIGURATION (OpenAI Whisper)
# ============================================================================

WHISPER_MODEL = "whisper-1"
WHISPER_LANGUAGE = "hy"
SPEECH_ACCURACY_THRESHOLD = 70

# Recording duration safeguards (seconds)
MAX_RECORDING_SECONDS = 15   # Reject recordings longer than this
MIN_RECORDING_SECONDS = 0.3  # Reject accidental taps shorter than this


# ============================================================================
# LESSON CONFIGURATION
# ============================================================================

# Total lessons in curriculum
TOTAL_LESSONS = 43
IMPLEMENTED_LESSONS = 43

# Lesson display format
LESSON_TITLE_FORMAT = "Lesson {num}: {title}"

# Level groupings for lesson navigation.
# Maps level label → (first_lesson_id, last_lesson_id) inclusive.
# Update these ranges as new lessons are added.
LESSON_LEVELS = {
    "A1 Beginner": ("lesson_01", "lesson_15"),
    "A2 Elementary": ("lesson_16", "lesson_30"),
    "B1 Intermediate": ("lesson_31", "lesson_43"),
}
