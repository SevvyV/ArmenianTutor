"""
Pimsleur Conversations tab renderer for Armenian Tutor.

Step-by-step mode showing each line styled by speaker type:
- instructor: info box with English text
- male/female: Armenian text + phonetic + English + audio player
- pause: "Your turn" practice prompt
- sfx: section divider
"""

import streamlit as st
from pimsleur_data import PIMSLEUR_LESSONS, PIMSLEUR_UNITS
from audio_manager import AudioManager
from config import ENABLE_SPEECH_PRACTICE

if ENABLE_SPEECH_PRACTICE:
    from speech_analysis import render_mic_button


def render_conversations(voice: str):
    """
    Main entry point called from app.py.

    Renders unit/lesson selectors and the selected conversation lesson.

    Args:
        voice: "male" or "female" - which voice to use for audio
    """
    # Initialize session state for conversation selection
    if "current_conversation" not in st.session_state:
        st.session_state.current_conversation = "pimsleur_01"

    # Build lesson list from registry
    all_conversations = []
    for lesson_id, lesson in sorted(PIMSLEUR_LESSONS.items()):
        all_conversations.append((lesson_id, lesson.unit, lesson.title))

    # Auto-detect which unit the current lesson belongs to
    current_id = st.session_state.current_conversation
    current_unit_idx = 0
    if current_id in PIMSLEUR_LESSONS:
        current_unit = PIMSLEUR_LESSONS[current_id].unit
        for idx, (unit_name, (start_id, end_id)) in enumerate(PIMSLEUR_UNITS.items()):
            s = int(start_id.split("_")[1])
            e = int(end_id.split("_")[1])
            lesson_num = int(current_id.split("_")[1])
            if s <= lesson_num <= e:
                current_unit_idx = idx
                break

    # Unit selector + Lesson selector
    unit_names = list(PIMSLEUR_UNITS.keys())

    col_unit, col_lesson = st.columns([1, 2])

    with col_unit:
        selected_unit = st.selectbox(
            "Unit:",
            options=unit_names,
            index=current_unit_idx,
            key="conversation_unit_dropdown"
        )

    # Filter lessons by selected unit
    start_id, end_id = PIMSLEUR_UNITS[selected_unit]
    start_num = int(start_id.split("_")[1])
    end_num = int(end_id.split("_")[1])

    filtered = [
        (lid, unit, title) for lid, unit, title in all_conversations
        if start_num <= int(lid.split("_")[1]) <= end_num
    ]

    with col_lesson:
        if filtered:
            lesson_options = [
                f"Lesson {int(lid.split('_')[1])}: {title}"
                for lid, _, title in filtered
            ]
            selected_display = st.selectbox(
                "Lesson:",
                options=lesson_options,
                index=0,
                key="conversation_lesson_dropdown"
            )

            # Update session state
            for lid, _, title in filtered:
                display = f"Lesson {int(lid.split('_')[1])}: {title}"
                if display == selected_display:
                    st.session_state.current_conversation = lid
                    break
        else:
            st.info("No lessons available in this unit yet.")
            return

    st.markdown("---")

    # Render the selected lesson
    lesson_id = st.session_state.current_conversation
    if lesson_id in PIMSLEUR_LESSONS:
        render_conversation_lesson(PIMSLEUR_LESSONS[lesson_id], voice)
    else:
        st.warning("This lesson is not yet available.")


def render_conversation_lesson(lesson, voice: str):
    """
    Render all lines in a conversation lesson sequentially.

    Args:
        lesson: ConversationLesson instance
        voice: "male" or "female"
    """
    st.header(f"Lesson {int(lesson.id.split('_')[1])}: {lesson.title}")

    # New vocabulary summary
    if lesson.new_vocabulary:
        with st.expander("New Vocabulary", expanded=False):
            for vocab in lesson.new_vocabulary:
                st.markdown(f"- **{vocab}**")

    st.markdown("---")

    # Render each line
    for i, line in enumerate(lesson.lines):
        render_conversation_line(line, lesson.id, voice, i)


def render_conversation_line(line, lesson_id: str, voice: str, index: int):
    """
    Render a single conversation line based on speaker type.

    Args:
        line: ConversationLine instance
        lesson_id: For building audio URLs
        voice: "male" or "female"
        index: Line index in the lesson
    """
    if line.speaker == "sfx":
        _render_sfx(line)
    elif line.speaker == "instructor":
        _render_instructor(line)
    elif line.speaker in ("male", "female"):
        _render_armenian_line(line, lesson_id, voice, index)
    elif line.speaker == "pause":
        _render_pause(line, index)


def _render_sfx(line):
    """Render a sound effect as a visual divider."""
    st.markdown("---")


def _render_instructor(line):
    """Render an instructor line as an info box."""
    st.info(f"**Instructor:** {line.text}")


def _render_armenian_line(line, lesson_id: str, voice: str, index: int):
    """Render a male/female Armenian line with text, phonetic, audio."""
    # Speaker color styling
    if line.speaker == "male":
        icon = "🔵"
        border_color = "#1E88E5"
    else:
        icon = "🟣"
        border_color = "#8E24AA"

    # Container with colored left border
    st.markdown(
        f"""<div style="border-left: 4px solid {border_color}; padding-left: 12px; margin: 8px 0;">
        <span style="font-size: 0.85em; color: gray;">{icon} {line.speaker.capitalize()}</span>
        </div>""",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        # Armenian text (large)
        st.markdown(f"### {line.text}")
        # Phonetic
        st.caption(f"*{line.phonetic}*")
        # English translation
        if line.english:
            st.markdown(f"**{line.english}**")

    with col2:
        # Audio player
        if line.audio_key:
            audio_url = AudioManager.get_conversation_url(
                line.audio_key, lesson_id, voice
            )
            st.audio(audio_url, format="audio/mp3")

    # Speech practice mic button
    if ENABLE_SPEECH_PRACTICE and line.text and line.speaker in ("male", "female"):
        render_mic_button(
            line.text,
            f"mic_{lesson_id}_conv_{index}"
        )

    st.markdown("")


def _render_pause(line, index: int):
    """Render a pause line as a 'Your turn' practice prompt."""
    st.markdown(
        f"""<div style="background-color: #FFF3E0; border-left: 4px solid #F57C00;
        padding: 12px 16px; margin: 8px 0; border-radius: 0 4px 4px 0;">
        <strong>Your turn:</strong> {line.text}
        <br><span style="font-size: 0.85em; color: #666;">({line.duration:.0f} seconds)</span>
        </div>""",
        unsafe_allow_html=True
    )
