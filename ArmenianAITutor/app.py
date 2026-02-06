"""
HyeTutor v20 - Western Armenian Language Learning App

Main Streamlit application with:
- 28-lesson progressive curriculum (15 implemented)
- Dual voice support (male/female)
- Verb conjugation tool (50 verbs)
- Live English → Armenian translator
"""

import streamlit as st
from config import (
    APP_TITLE, APP_ICON, LAYOUT, INITIAL_SIDEBAR_STATE,
    AVAILABLE_VOICES, DEFAULT_VOICE, ENABLE_VERB_TOOL, ENABLE_LIVE_TRANSLATOR,
    BASE_IMAGE_URL
)
from lessons import LESSONS
from audio_manager import AudioManager
from renderers import render_verb_conjugation_tool, render_live_translator


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
    
    # Tools Section - Use radio for navigation
    st.markdown("### 🔧 Tools & Practice")
    
    tool_options = ["📚 Lessons"]
    if ENABLE_VERB_TOOL:
        tool_options.append("🔤 Verb Conjugation")
    if ENABLE_LIVE_TRANSLATOR:
        tool_options.append("🗣️ Live Translator")
    
    selected_tool = st.radio(
        "Select activity:",
        options=tool_options,
        key="tool_selector",
        label_visibility="collapsed"
    )
    
    # Update view based on selection
    if selected_tool == "📚 Lessons":
        if st.session_state.current_view != "lesson":
            st.session_state.current_view = "lesson"
    elif selected_tool == "🔤 Verb Conjugation":
        if st.session_state.current_view != "verb_tool":
            st.session_state.current_view = "verb_tool"
    elif selected_tool == "🗣️ Live Translator":
        if st.session_state.current_view != "translator":
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
                        # Display image if available, otherwise emoji
                        if item.image:
                            image_url = f"{BASE_IMAGE_URL}/{item.image}"
                            st.image(image_url, use_container_width=True)
                        elif item.emoji:
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
                        
                        st.markdown("---")


def render_sentence_lesson(lesson):
    """Render a sentence lesson."""
    st.header(lesson.title)
    st.markdown(f"**{len(lesson.items)} practice sentences**")
    st.markdown("---")
    
    # Get current voice
    voice = st.session_state.voice
    
    # Display sentences in a list
    for item in lesson.items:
        with st.container():
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
# MAIN ROUTING
# ============================================================================

def main():
    """Main application router."""
    
    # Route to appropriate view
    if st.session_state.current_view == "lesson":
        render_lesson()
    
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
