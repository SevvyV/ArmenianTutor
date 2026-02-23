"""
HyeTutor v20 - Western Armenian Language Learning App

Main Streamlit application with:
- Tab-based navigation (Lessons, Prayers, Alphabet, Verbs, Translator)
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
    BASE_IMAGE_URL, ENABLE_SPEECH_PRACTICE, LESSON_LEVELS, ENABLE_CONVERSATIONS
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

# Custom CSS: push sidebar voice selector to bottom-left
st.markdown("""
<style>
    section[data-testid="stSidebar"] > div:first-child {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        justify-content: flex-end;
        padding-bottom: 2rem;
    }
    /* Larger, more prominent tab labels */
    button[data-baseweb="tab"] p {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
    }
    button[data-baseweb="tab"] {
        padding: 0.75rem 1.5rem !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "voice" not in st.session_state:
    st.session_state.voice = DEFAULT_VOICE

if "current_lesson" not in st.session_state:
    st.session_state.current_lesson = "lesson_01"

if "current_prayer" not in st.session_state:
    st.session_state.current_prayer = "lords_prayer"

if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = "pimsleur_01"


# ============================================================================
# SIDEBAR — Voice Selection (bottom-left)
# ============================================================================

with st.sidebar:
    st.markdown(f"**{APP_ICON} {APP_TITLE}**")
    st.markdown("---")
    st.markdown("🎙️ **Voice**")
    voice_choice = st.radio(
        "Choose narrator voice:",
        options=list(AVAILABLE_VOICES.keys()),
        format_func=lambda x: AVAILABLE_VOICES[x],
        key="voice_selector",
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state.voice = voice_choice

    # Pimsleur lesson player sidebar controls
    if ENABLE_CONVERSATIONS:
        from pimsleur_renderer import render_pimsleur_sidebar
        render_pimsleur_sidebar()


# ============================================================================
# LESSON RENDERERS
# ============================================================================

def render_vocabulary_lesson(lesson):
    """Render a vocabulary lesson with cards."""
    st.header(lesson.title)
    st.markdown(f"**{len(lesson.items)} vocabulary items**")
    st.markdown("---")

    voice = st.session_state.voice
    cols_per_row = 3
    items = lesson.items

    for i in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row)

        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(items):
                item = items[idx]

                with col:
                    with st.container():
                        # Image
                        image_url = get_image_url(item.english, lesson.id, lesson.prefix)
                        try:
                            st.image(image_url, use_container_width=True)
                        except:
                            if item.emoji:
                                st.markdown(f"<div style='text-align: center; font-size: 80px;'>{item.emoji}</div>",
                                          unsafe_allow_html=True)

                        # English (strip emoji)
                        english_clean = ''.join(c for c in item.english if ord(c) < 0x1F000).strip()
                        st.markdown(f"**{english_clean}**")

                        # Armenian
                        st.markdown(f"### {item.armenian_display}")

                        # Phonetic
                        st.caption(f"*{item.phonetic}*")

                        # Audio
                        audio_url = AudioManager.get_vocabulary_url(
                            item.audio_key, lesson.id, voice
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

    voice = st.session_state.voice

    for sent_idx, item in enumerate(lesson.items):
        with st.container():
            # Image
            image_url = get_image_url(item.english, lesson.id, lesson.prefix)
            try:
                st.image(image_url, width=300)
            except:
                pass

            col1, col2 = st.columns([3, 1])

            with col1:
                if hasattr(item, 'context') and item.context:
                    st.caption(f"📌 {item.context}")
                st.markdown(f"**English:** {item.english}")
                st.markdown(f"**Armenian:** {item.armenian_display}")
                st.caption(f"*Pronunciation: {item.phonetic}*")

            with col2:
                audio_url = AudioManager.get_sentence_url(
                    item.audio_key, lesson.id, voice
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
    with st.expander("View Full Prayer Text", expanded=False):
        for line in prayer.lines:
            st.markdown(f"**{line.armenian}**")
        st.markdown("---")
        if prayer.full_audio_key:
            st.markdown("**Listen to full prayer:**")
            full_audio_url = AudioManager.get_url(
                prayer.full_audio_key, "prayers", prayer.id, voice
            )
            st.audio(full_audio_url, format="audio/mp3")

    st.markdown("---")

    # Line-by-line breakdown
    st.subheader("Line-by-Line Study")
    st.markdown("*Click each line to study the pronunciation and meaning.*")
    st.markdown("")

    for line in prayer.lines:
        with st.expander(
            f"Line {line.line_number}: {line.armenian}",
            expanded=False
        ):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"## {line.armenian}")
                st.markdown(f"**Pronunciation:** *{line.phonetic}*")
                st.markdown(f"**English:** {line.english}")

            with col2:
                audio_url = AudioManager.get_url(
                    line.audio_key, "prayers", prayer.id, voice
                )
                st.markdown("**Listen:**")
                st.audio(audio_url, format="audio/mp3")

    st.markdown("---")

    # Build-up practice
    st.subheader("Build-Up Practice")
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

    base_audio_url = f"https://raw.githubusercontent.com/SevvyV/ArmenianTutor/main/ArmenianAITutor/audio_library/alphabet/{voice}"

    st.markdown("---")

    cols_per_row = 4

    for i in range(0, len(alphabet), cols_per_row):
        cols = st.columns(cols_per_row)

        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(alphabet):
                letter = alphabet[idx]

                with col:
                    with st.container():
                        image_filename = f"lesson_01_alphabet_{letter.position:02d}{suffix}.png"
                        image_url = f"{BASE_IMAGE_URL}/{image_filename}"
                        try:
                            st.image(image_url, use_container_width=True)
                        except:
                            st.markdown(f"### {letter.capital}  {letter.lowercase}")
                            st.markdown(f"**{letter.armenian_name}**")

                        audio_filename = f"alphabet_{letter.position:02d}{suffix}.mp3"
                        audio_url = f"{base_audio_url}/{audio_filename}"
                        st.audio(audio_url, format="audio/mp3")

                        st.markdown("---")


# ============================================================================
# MAIN — Tab-Based Navigation
# ============================================================================

def main():
    """Main application with tab-based navigation."""

    # App header
    st.title(f"{APP_ICON} {APP_TITLE}")
    st.caption("Western Armenian Language Learning")

    # Build tab list based on feature flags
    tab_names = ["📚 Lessons", "🙏 Prayers", "🔤 Alphabet"]
    tab_keys = ["lessons", "prayers", "alphabet"]

    if ENABLE_VERB_TOOL:
        tab_names.append("📝 Verbs")
        tab_keys.append("verbs")
    if ENABLE_CONVERSATIONS:
        tab_names.append("🗣️ Conversations")
        tab_keys.append("conversations")
    if ENABLE_LIVE_TRANSLATOR:
        tab_names.append("💬 Translator")
        tab_keys.append("translator")

    tabs = st.tabs(tab_names)
    tab_map = dict(zip(tab_keys, tabs))

    # --- LESSONS TAB ---
    with tab_map["lessons"]:
        # Build full lesson list with numeric keys for filtering
        all_lessons = []
        for lesson_id, lesson in sorted(LESSONS.items()):
            lesson_num = int(lesson_id.split("_")[1])
            if ":" in lesson.title:
                title = lesson.title.split(":", 1)[1].strip()
            else:
                title = lesson.title
            all_lessons.append((lesson_id, lesson_num, f"Lesson {lesson_num}: {title}"))

        # Auto-detect which level the current lesson belongs to
        current_num = int(st.session_state.current_lesson.split("_")[1])
        default_level_idx = 0
        for idx, (level_name, (start_id, end_id)) in enumerate(LESSON_LEVELS.items()):
            s = int(start_id.split("_")[1])
            e = int(end_id.split("_")[1])
            if s <= current_num <= e:
                default_level_idx = idx
                break

        # Level selector
        level_names = list(LESSON_LEVELS.keys())
        col_level, col_lesson = st.columns([1, 2])

        with col_level:
            selected_level = st.selectbox(
                "Level:",
                options=level_names,
                index=default_level_idx,
                key="level_dropdown"
            )

        # Filter lessons by selected level
        start_id, end_id = LESSON_LEVELS[selected_level]
        start_num = int(start_id.split("_")[1])
        end_num = int(end_id.split("_")[1])
        filtered = [
            (lid, num, display) for lid, num, display in all_lessons
            if start_num <= num <= end_num
        ]

        with col_lesson:
            selected_lesson_display = st.selectbox(
                "Lesson:",
                options=[display for _, _, display in filtered],
                index=0,
                key="lesson_dropdown"
            )

        for lesson_id, _, display in filtered:
            if display == selected_lesson_display:
                st.session_state.current_lesson = lesson_id
                break

        st.markdown("---")
        render_lesson()

    # --- PRAYERS TAB ---
    with tab_map["prayers"]:
        prayer_options = list_prayers()
        if prayer_options:
            selected_prayer_display = st.selectbox(
                "Select a prayer:",
                options=[title for _, title in prayer_options],
                index=0,
                key="prayer_dropdown"
            )

            for prayer_id, title in prayer_options:
                if title == selected_prayer_display:
                    st.session_state.current_prayer = prayer_id
                    break

        st.markdown("---")
        render_prayer()

    # --- ALPHABET TAB ---
    with tab_map["alphabet"]:
        render_alphabet()

    # --- CONVERSATIONS TAB ---
    if "conversations" in tab_map:
        with tab_map["conversations"]:
            from pimsleur_renderer import render_conversations
            render_conversations(st.session_state.voice)

    # --- VERBS TAB ---
    if "verbs" in tab_map:
        with tab_map["verbs"]:
            render_verb_conjugation_tool(st.session_state.voice)

    # --- TRANSLATOR TAB ---
    if "translator" in tab_map:
        with tab_map["translator"]:
            render_live_translator(st.session_state.voice)


# ============================================================================
# RUN APP
# ============================================================================

if __name__ == "__main__":
    main()
