"""
HyeTutor v20 - Western Armenian Language Learning App

Main Streamlit application with:
- 43-lesson progressive curriculum (A1-B1)
- Dual voice support (male/female)
- Verb conjugation tool (50 verbs)
- Live English → Armenian translator
"""

import re
import streamlit as st
from config import (
    APP_TITLE, APP_ICON, LAYOUT, INITIAL_SIDEBAR_STATE,
    AVAILABLE_VOICES, DEFAULT_VOICE, ENABLE_VERB_TOOL, ENABLE_LIVE_TRANSLATOR,
    BASE_IMAGE_URL, ENABLE_SPEECH_PRACTICE
)
from lessons import LESSONS
from prayers import PRAYERS, list_prayers
from alphabet import WESTERN_ALPHABET, EASTERN_ALPHABET
from audio_manager import AudioManager
from renderers import render_verb_conjugation_tool, render_live_translator

if ENABLE_SPEECH_PRACTICE:
    from speech_analysis import render_mic_button


def get_image_url(english_text, lesson_id, prefix):
    """Build the GitHub-hosted image URL for a vocabulary or sentence item."""
    clean = ''.join(c for c in english_text if ord(c) < 128)
    clean = clean.strip().lower()
    clean = re.sub(r'[^\w\s]', '', clean)
    clean = re.sub(r'^\d+\s+', '', clean)
    clean = clean.replace('/', '').replace(' ', '_')
    filename = f"{lesson_id}_{prefix}_{clean}.png"
    return f"{BASE_IMAGE_URL}/{filename}"


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "voice" not in st.session_state:
    st.session_state.voice = DEFAULT_VOICE

if "current_view" not in st.session_state:
    st.session_state.current_view = "lesson"

if "current_lesson" not in st.session_state:
    st.session_state.current_lesson = "lesson_01"

if "current_prayer" not in st.session_state:
    st.session_state.current_prayer = "lords_prayer"


# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title(f"{APP_ICON} {APP_TITLE}")
    st.markdown("**Western Armenian Language Learning**")
    st.markdown("---")
    
    # Voice Selector
    st.markdown("### 🎙️ Voice Selection")
    voice_choice = st.radio(
        "Choose narrator voice:",
        options=list(AVAILABLE_VOICES.keys()),
        format_func=lambda x: AVAILABLE_VOICES[x],
        key="voice_selector",
        horizontal=True
    )
    st.session_state.voice = voice_choice
    
    st.markdown("---")
    
    # Main Navigation
    st.markdown("### 📚 Lessons")
    
    # Create lesson dropdown options
    lesson_options = []
    for lesson_id, lesson in sorted(LESSONS.items()):
        # Extract lesson number from ID (e.g., "lesson_01" → "1")
        lesson_num = lesson_id.split("_")[1].lstrip("0") or "0"
        # Extract title after "Lesson X: "
        if ":" in lesson.title:
            title = lesson.title.split(":", 1)[1].strip()
        else:
            title = lesson.title
        lesson_options.append((lesson_id, f"Lesson {lesson_num}: {title}"))
    
    # Lesson selector
    selected_lesson_display = st.selectbox(
        "Select a lesson:",
        options=[display for _, display in lesson_options],
        index=0,
        key="lesson_dropdown"
    )
    
    # Find the lesson_id from display text
    for lesson_id, display in lesson_options:
        if display == selected_lesson_display:
            st.session_state.current_lesson = lesson_id
            st.session_state.current_view = "lesson"
            break
    
    st.markdown("---")
    
    # Prayers Section
    st.markdown("### \U0001f64f Prayers")
    
    prayer_options = list_prayers()
    if prayer_options:
        selected_prayer_display = st.selectbox(
            "Select a prayer:",
            options=[title for _, title in prayer_options],
            index=0,
            key="prayer_dropdown"
        )
        
        # Find the prayer_id from display text
        for prayer_id, title in prayer_options:
            if title == selected_prayer_display:
                st.session_state.current_prayer = prayer_id
                break
    
    st.markdown("---")
    
    # Tools Section - Use radio for navigation
    st.markdown("### \U0001f527 Tools & Practice")
    
    tool_options = ["\U0001f4da Lessons", "\U0001f64f Prayers", "\U0001f524 Alphabet"]
    if ENABLE_VERB_TOOL:
        tool_options.append("\U0001f524 Verb Conjugation")
    if ENABLE_LIVE_TRANSLATOR:
        tool_options.append("\U0001f5e3\ufe0f Live Translator")
    
    # Set default index based on current view
    default_index = 0
    if st.session_state.current_view == "prayer":
        default_index = 1
    elif st.session_state.current_view == "alphabet":
        default_index = 2
    elif st.session_state.current_view == "verb_tool":
        default_index = 3
    elif st.session_state.current_view == "translator":
        default_index = 4
    
    selected_tool = st.radio(
        "Select activity:",
        options=tool_options,
        index=default_index,
        key="tool_selector",
        label_visibility="collapsed"
    )
    
    # Update view based on selection
    if selected_tool == "\U0001f4da Lessons":
        st.session_state.current_view = "lesson"
    elif selected_tool == "\U0001f64f Prayers":
        st.session_state.current_view = "prayer"
    elif selected_tool == "\U0001f524 Alphabet":
        st.session_state.current_view = "alphabet"
    elif selected_tool == "\U0001f524 Verb Conjugation":
        st.session_state.current_view = "verb_tool"
    elif selected_tool == "\U0001f5e3\ufe0f Live Translator":
        st.session_state.current_view = "translator"
    
    st.markdown("---")
    
    # Footer
    st.caption("💡 Tip: Click lesson cards to hear audio pronunciation!")
    st.caption("🎯 Use tools to practice verbs and translations")


# ============================================================================
# MAIN CONTENT AREA
# ============================================================================

def render_vocabulary_lesson(lesson):
    """Render a vocabulary lesson with cards."""
    st.header(lesson.title)
    st.markdown(f"**{len(lesson.items)} vocabulary items**")
    st.markdown("---")
    
    # Get current voice
    voice = st.session_state.voice
    
    # Create grid layout (3 columns)
    cols_per_row = 3
    items = lesson.items
    
    for i in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(items):
                item = items[idx]
                
                with col:
                    # Card container
                    with st.container():
                        # Try to display image
                        image_url = get_image_url(item.english, lesson.id, lesson.prefix)
                        try:
                            st.image(image_url, use_container_width=True)
                        except:
                            # Fallback to emoji if image fails
                            if item.emoji:
                                st.markdown(f"<div style='text-align: center; font-size: 80px;'>{item.emoji}</div>",
                                          unsafe_allow_html=True)
                        
                        # English
                        # Remove emoji from display if present
                        english_clean = ''.join(c for c in item.english if ord(c) < 0x1F000).strip()
                        st.markdown(f"**{english_clean}**")
                        
                        # Armenian
                        st.markdown(f"### {item.armenian_display}")
                        
                        # Phonetic
                        st.caption(f"*{item.phonetic}*")
                        
                        # Audio button
                        audio_url = AudioManager.get_vocabulary_url(
                            item.audio_key,
                            lesson.id,
                            voice
                        )
                        st.audio(audio_url, format="audio/mp3")

                        # Speech practice
                        if ENABLE_SPEECH_PRACTICE:
                            render_mic_button(
                                item.armenian_display,
                                f"mic_{lesson.id}_vocab_{idx}"
                            )

                        st.markdown("---")


def render_sentence_lesson(lesson):
    """Render a sentence lesson."""
    st.header(lesson.title)
    st.markdown(f"**{len(lesson.items)} practice sentences**")
    st.markdown("---")
    
    # Get current voice
    voice = st.session_state.voice
    
    # Display sentences in a list
    for sent_idx, item in enumerate(lesson.items):
        with st.container():
            # Try to display image
            image_url = get_image_url(item.english, lesson.id, lesson.prefix)
            try:
                st.image(image_url, width=300)
            except:
                pass

            col1, col2 = st.columns([3, 1])

            with col1:
                # Context label if present
                if hasattr(item, 'context') and item.context:
                    st.caption(f"📌 {item.context}")

                # English
                st.markdown(f"**English:** {item.english}")

                # Armenian
                st.markdown(f"**Armenian:** {item.armenian_display}")

                # Phonetic
                st.caption(f"*Pronunciation: {item.phonetic}*")

            with col2:
                # Audio
                audio_url = AudioManager.get_sentence_url(
                    item.audio_key,
                    lesson.id,
                    voice
                )
                st.audio(audio_url, format="audio/mp3")

            # Speech practice
            if ENABLE_SPEECH_PRACTICE:
                render_mic_button(
                    item.armenian_display,
                    f"mic_{lesson.id}_sent_{sent_idx}"
                )

            st.markdown("---")


def render_lesson():
    """Render the currently selected lesson."""
    lesson_id = st.session_state.current_lesson
    
    if lesson_id not in LESSONS:
        st.error(f"Lesson '{lesson_id}' not found!")
        return
    
    lesson = LESSONS[lesson_id]
    
    # Render based on lesson type
    if lesson.lesson_type == "vocabulary":
        render_vocabulary_lesson(lesson)
    elif lesson.lesson_type == "sentences":
        render_sentence_lesson(lesson)
    else:
        st.error(f"Unknown lesson type: {lesson.lesson_type}")


# ============================================================================
# PRAYER RENDERER
# ============================================================================

def render_prayer():
    """Render the currently selected prayer with line-by-line breakdown."""
    prayer_id = st.session_state.current_prayer
    
    if prayer_id not in PRAYERS:
        st.error(f"Prayer '{prayer_id}' not found!")
        return
    
    prayer = PRAYERS[prayer_id]
    voice = st.session_state.voice
    
    # Header
    st.header(f"\U0001f64f {prayer.title}")
    st.markdown(f"### {prayer.armenian_title}")
    st.markdown(f"*{prayer.description}*")
    st.markdown("---")
    
    # Full prayer text
    with st.expander("\U0001f4dc View Full Prayer Text", expanded=False):
        for line in prayer.lines:
            st.markdown(f"**{line.armenian}**")
        st.markdown("---")
        # Full prayer audio
        if prayer.full_audio_key:
            st.markdown("**\U0001f50a Listen to full prayer:**")
            full_audio_url = AudioManager.get_url(
                prayer.full_audio_key, "prayers", prayer.id, voice
            )
            st.audio(full_audio_url, format="audio/mp3")
    
    st.markdown("---")
    
    # Line-by-line breakdown
    st.markdown("### \U0001f4d6 Line-by-Line Study")
    st.markdown("*Click each line to study the pronunciation and meaning.*")
    st.markdown("")
    
    for line in prayer.lines:
        with st.expander(
            f"**Line {line.line_number}:** {line.armenian}",
            expanded=False
        ):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Armenian text (large)
                st.markdown(f"## {line.armenian}")
                
                # Phonetic pronunciation
                st.markdown(f"**Pronunciation:** *{line.phonetic}*")
                
                # English translation
                st.markdown(f"**English:** {line.english}")
            
            with col2:
                # Audio for this line
                audio_url = AudioManager.get_url(
                    line.audio_key, "prayers", prayer.id, voice
                )
                st.markdown("**\U0001f50a Listen:**")
                st.audio(audio_url, format="audio/mp3")
    
    st.markdown("---")
    
    # Build-up practice section
    st.markdown("### \U0001f3af Build-Up Practice")
    st.markdown("*Practice reciting the prayer progressively, adding one line at a time.*")
    st.markdown("")
    
    num_lines = st.slider(
        "How many lines to practice:",
        min_value=1,
        max_value=len(prayer.lines),
        value=3,
        key="prayer_buildup_slider"
    )
    
    st.markdown("---")
    
    for line in prayer.lines[:num_lines]:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{line.armenian}**")
            st.caption(f"{line.phonetic}  \u2014  {line.english}")
        with col2:
            audio_url = AudioManager.get_url(
                line.audio_key, "prayers", prayer.id, voice
            )
            st.audio(audio_url, format="audio/mp3")


# ============================================================================
# ALPHABET RENDERER
# ============================================================================

def render_alphabet():
    """Render the Armenian alphabet with Western/Eastern toggle and audio."""

    st.header("\U0001f524 Armenian Alphabet")
    st.markdown("**38 Letters of the Armenian Alphabet**")
    st.markdown("---")
    
    # Toggle between Western and Eastern
    dialect = st.radio(
        "Select pronunciation style:",
        options=["Western Armenian", "Eastern Armenian"],
        horizontal=True,
        key="alphabet_dialect"
    )
    
    is_western = dialect == "Western Armenian"
    alphabet = WESTERN_ALPHABET if is_western else EASTERN_ALPHABET
    suffix = "w" if is_western else "e"
    voice = st.session_state.voice
    
    # Base audio URL
    base_audio_url = f"https://raw.githubusercontent.com/SevvyV/ArmenianTutor/main/ArmenianAITutor/audio_library/alphabet/{voice}"
    
    st.markdown("---")
    
    # Display in grid (4 columns)
    cols_per_row = 4
    
    for i in range(0, len(alphabet), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(alphabet):
                letter = alphabet[idx]
                
                with col:
                    with st.container():
                        # Image
                        image_filename = f"lesson_01_alphabet_{letter.position:02d}{suffix}.png"
                        image_url = f"{BASE_IMAGE_URL}/{image_filename}"
                        try:
                            st.image(image_url, use_container_width=True)
                        except:
                            st.markdown(f"### {letter.capital}  {letter.lowercase}")
                            st.markdown(f"**{letter.armenian_name}**")
                        
                        # Audio
                        audio_filename = f"alphabet_{letter.position:02d}{suffix}.mp3"
                        audio_url = f"{base_audio_url}/{audio_filename}"
                        st.audio(audio_url, format="audio/mp3")
                        
                        st.markdown("---")


# ============================================================================
# MAIN ROUTING
# ============================================================================

def main():
    """Main application router."""
    
    # Route to appropriate view
    if st.session_state.current_view == "lesson":
        render_lesson()
    
    elif st.session_state.current_view == "prayer":
        render_prayer()
    
    elif st.session_state.current_view == "alphabet":
        render_alphabet()
    
    elif st.session_state.current_view == "verb_tool":
        render_verb_conjugation_tool(st.session_state.voice)
    
    elif st.session_state.current_view == "translator":
        render_live_translator(st.session_state.voice)
    
    else:
        st.error(f"Unknown view: {st.session_state.current_view}")


# ============================================================================
# RUN APP
# ============================================================================

if __name__ == "__main__":
    main()
