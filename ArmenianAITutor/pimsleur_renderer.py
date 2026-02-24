"""
Interactive Pimsleur Lesson Player for Armenian Tutor.

Hands-free, auto-recording lesson flow:

1. User taps "Start Lesson" (also grants mic permission)
2. Audio plays automatically, segment by segment
3. At practice points: auto-records with silence detection
4. Whisper analyzes pronunciation, shows color-coded feedback
5. Auto-advances on good score, retry option on poor score

Architecture:
- Lessons are split into "segments" at pause boundaries
- Each segment uses a bidirectional Streamlit component (segment_player)
  that handles audio playback + auto-recording + silence detection
- State machine: IDLE -> SEGMENT -> FEEDBACK -> SEGMENT -> ... -> COMPLETE
"""

import re
import time
import streamlit as st
import streamlit.components.v1 as components

from pimsleur_data import PIMSLEUR_LESSONS, PIMSLEUR_UNITS
from audio_manager import AudioManager
from config import (
    ENABLE_SPEECH_PRACTICE,
    AUDIO_GAP_MS,
    SILENCE_THRESHOLD_DB,
    SILENCE_DURATION_MS,
    RECORDING_DELAY_MS,
    AUTO_ADVANCE_SECONDS,
    SPEECH_ACCURACY_THRESHOLD,
)

try:
    from components.segment_player import segment_player
except ImportError:
    segment_player = None

if ENABLE_SPEECH_PRACTICE:
    try:
        from speech_analysis import (
            analyze_pronunciation_b64,
            render_speech_feedback,
            SpeechAnalysisError,
        )
    except ImportError:
        ENABLE_SPEECH_PRACTICE = False


# ============================================================================
# SEGMENT DATA STRUCTURE (plain dicts for session state compatibility)
# ============================================================================

def build_segments(lesson, voice: str) -> list:
    """
    Split a lesson into playable segments at pause boundaries.

    Each segment is a plain dict (not a dataclass) so it survives
    Streamlit session state serialization across reruns.
    """
    segments = []
    current_lines = []
    current_urls = []
    last_armenian_text = ""
    last_armenian_phonetic = ""
    last_armenian_english = ""
    # Track instructor "Say: X" overrides for partial-word drills
    instructor_say_override = ""
    # Track instructor "how do you say X?" prompts
    instructor_english_prompt = ""

    # Build English→Armenian lookup from all speaker lines in this lesson
    english_to_armenian = {}
    for line in lesson.lines:
        if line.speaker in ("male", "female") and getattr(line, "english", ""):
            eng_key = line.english.strip().lower().rstrip(".!?")
            if eng_key not in english_to_armenian:
                english_to_armenian[eng_key] = {
                    "text": line.text,
                    "phonetic": getattr(line, "phonetic", ""),
                    "english": line.english,
                }

    for line in lesson.lines:
        if line.speaker == "pause":
            # Priority 1: instructor "Say: tyoon" overrides (partial drills)
            if instructor_say_override:
                practice_text = instructor_say_override
                practice_phonetic = ""  # Override text is already phonetic
                practice_english = ""
                # Partial drills (syllables) can't be compared by Whisper
                # Full word drills ("Now the whole word: X") CAN be compared
                override_norm = instructor_say_override.replace("-", "").lower()
                phonetic_norm = last_armenian_phonetic.replace("-", "").lower()
                is_full_word = override_norm == phonetic_norm
                whisper_expected = last_armenian_text if is_full_word else ""
            # Priority 2: instructor "how do you say hello?" prompts
            elif instructor_english_prompt:
                lookup = english_to_armenian.get(instructor_english_prompt)
                if lookup:
                    practice_text = lookup["text"]
                    practice_phonetic = lookup["phonetic"]
                    practice_english = lookup["english"]
                    whisper_expected = lookup["text"]
                else:
                    # Fallback to last Armenian if lookup fails
                    practice_text = last_armenian_text
                    practice_phonetic = last_armenian_phonetic
                    practice_english = last_armenian_english
                    whisper_expected = last_armenian_text
            else:
                practice_text = last_armenian_text
                practice_phonetic = last_armenian_phonetic
                practice_english = last_armenian_english
                whisper_expected = last_armenian_text
            segments.append({
                "index": len(segments),
                "lines": [_line_to_dict(l) for l in current_lines],
                "audio_urls": list(current_urls),
                "has_pause": True,
                "pause_text": line.text,
                "practice_text": practice_text,
                "practice_phonetic": practice_phonetic,
                "practice_english": practice_english,
                "whisper_expected": whisper_expected,
            })
            current_lines = []
            current_urls = []
            instructor_say_override = ""
            instructor_english_prompt = ""
        else:
            current_lines.append(line)
            if line.speaker == "instructor" and line.audio_key:
                current_urls.append(
                    AudioManager.get_instructor_url(line.audio_key, lesson.id)
                )
                # Detect "Say: X" or "Now the whole word: X" patterns
                say_match = re.match(
                    r'^(?:Say|Now (?:say|the whole word))[:\s]+(.+)',
                    line.text, re.IGNORECASE
                )
                if say_match:
                    instructor_say_override = say_match.group(1).strip()

                # Detect "how do you say X?" / "say X." / "Now say X."
                # patterns that reference an English word
                eng_match = re.search(
                    r'(?:how do you say|(?:now )?say)\s+"?([^"?.]+)"?',
                    line.text, re.IGNORECASE
                )
                if eng_match and not say_match:
                    eng_word = eng_match.group(1).strip().lower().rstrip(".!?")
                    if eng_word in english_to_armenian:
                        instructor_english_prompt = eng_word
            elif line.speaker in ("male", "female") and line.audio_key:
                current_urls.append(
                    AudioManager.get_conversation_url(
                        line.audio_key, lesson.id, voice
                    )
                )
                last_armenian_text = line.text
                last_armenian_phonetic = line.phonetic
                last_armenian_english = line.english
                instructor_say_override = ""  # Reset on new Armenian word
                instructor_english_prompt = ""

    # Trailing segment after the last pause (closing lines)
    if current_lines:
        segments.append({
            "index": len(segments),
            "lines": [_line_to_dict(l) for l in current_lines],
            "audio_urls": list(current_urls),
            "has_pause": False,
            "pause_text": "",
            "practice_text": "",
            "practice_phonetic": "",
            "practice_english": "",
            "whisper_expected": "",
        })

    return segments


def _line_to_dict(line) -> dict:
    """Convert a ConversationLine to a plain dict for session state storage."""
    return {
        "speaker": line.speaker,
        "text": line.text,
        "phonetic": getattr(line, "phonetic", ""),
        "english": getattr(line, "english", ""),
        "audio_key": getattr(line, "audio_key", ""),
    }


# ============================================================================
# COMPACT LINE RENDERERS
# ============================================================================

def _render_line_transcript(line):
    """Compact line rendering for the playing transcript. Accepts dict or object."""
    speaker = line.get("speaker", "") if isinstance(line, dict) else getattr(line, "speaker", "")
    text = line.get("text", "") if isinstance(line, dict) else getattr(line, "text", "")
    phonetic = line.get("phonetic", "") if isinstance(line, dict) else getattr(line, "phonetic", "")
    english = line.get("english", "") if isinstance(line, dict) else getattr(line, "english", "")

    if speaker == "instructor":
        st.markdown(
            f'<div style="padding: 6px 12px; margin: 4px 0; color: #555; '
            f'font-style: italic; font-size: 0.95em;">'
            f'{text}</div>',
            unsafe_allow_html=True,
        )
    elif speaker in ("male", "female"):
        color = "#1E88E5" if speaker == "male" else "#8E24AA"
        st.markdown(
            f'<div style="border-left: 3px solid {color}; padding: 6px 12px; margin: 4px 0;">'
            f'<span style="font-size: 1.3em; font-weight: bold;">{text}</span>'
            f'<br><span style="color: #888; font-size: 0.9em;">{phonetic}</span>'
            f' &mdash; <span style="color: #666;">{english}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    elif speaker == "sfx":
        pass  # Silent visual marker, skip in transcript


# ============================================================================
# MAIN RENDERER (Entry Point)
# ============================================================================

def render_conversations(voice: str):
    """
    Main entry point called from app.py.

    Routes to the appropriate rendering mode based on pimsleur_state:
    - IDLE: Lesson selector + Start button
    - SEGMENT: Combined audio playback + auto-recording
    - FEEDBACK: Whisper analysis results + auto-advance or retry
    - COMPLETE: Congratulations + next lesson
    """
    # Initialize session state
    if "current_conversation" not in st.session_state:
        st.session_state.current_conversation = "pimsleur_01"
    if "pimsleur_state" not in st.session_state:
        st.session_state.pimsleur_state = "IDLE"
    if "pimsleur_segment" not in st.session_state:
        st.session_state.pimsleur_segment = 0
    if "pimsleur_segments" not in st.session_state:
        st.session_state.pimsleur_segments = []
    if "pimsleur_practice_audio" not in st.session_state:
        st.session_state.pimsleur_practice_audio = None
    if "pimsleur_practice_expected" not in st.session_state:
        st.session_state.pimsleur_practice_expected = ""
    if "pimsleur_retry_count" not in st.session_state:
        st.session_state.pimsleur_retry_count = 0
    if "pimsleur_skip_audio" not in st.session_state:
        st.session_state.pimsleur_skip_audio = False

    state = st.session_state.pimsleur_state

    if state == "IDLE":
        _render_idle(voice)
    elif state == "SEGMENT":
        _render_segment(voice)
    elif state == "FEEDBACK":
        _render_feedback(voice)
    elif state == "COMPLETE":
        _render_complete(voice)
    else:
        st.session_state.pimsleur_state = "IDLE"
        st.rerun()


# ============================================================================
# IDLE MODE — Lesson selection + Start
# ============================================================================

def _render_idle(voice: str):
    """Lesson selector with Start Lesson button."""

    # Build lesson list
    all_conversations = []
    for lesson_id, lesson in sorted(PIMSLEUR_LESSONS.items()):
        all_conversations.append((lesson_id, lesson.unit, lesson.title))

    # Auto-detect current unit
    current_id = st.session_state.current_conversation
    current_unit_idx = 0
    if current_id in PIMSLEUR_LESSONS:
        for idx, (unit_name, (start_id, end_id)) in enumerate(PIMSLEUR_UNITS.items()):
            s = int(start_id.split("_")[1])
            e = int(end_id.split("_")[1])
            lesson_num = int(current_id.split("_")[1])
            if s <= lesson_num <= e:
                current_unit_idx = idx
                break

    # Unit + Lesson selectors
    unit_names = list(PIMSLEUR_UNITS.keys())
    col_unit, col_lesson = st.columns([1, 2])

    with col_unit:
        selected_unit = st.selectbox(
            "Unit:", options=unit_names, index=current_unit_idx,
            key="conversation_unit_dropdown"
        )

    # Filter lessons by unit
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
                "Lesson:", options=lesson_options, index=0,
                key="conversation_lesson_dropdown"
            )
            for lid, _, title in filtered:
                display = f"Lesson {int(lid.split('_')[1])}: {title}"
                if display == selected_display:
                    st.session_state.current_conversation = lid
                    break
        else:
            st.info("No lessons available in this unit yet.")
            return

    st.markdown("---")

    # Show lesson info
    lesson_id = st.session_state.current_conversation
    if lesson_id not in PIMSLEUR_LESSONS:
        st.warning("Lesson not available.")
        return

    lesson = PIMSLEUR_LESSONS[lesson_id]
    num = int(lesson.id.split("_")[1])

    st.markdown(f"## Lesson {num}: {lesson.title}")

    # Vocabulary preview
    if lesson.new_vocabulary:
        with st.expander("New Vocabulary", expanded=True):
            cols = st.columns(min(len(lesson.new_vocabulary), 3))
            for i, vocab in enumerate(lesson.new_vocabulary):
                with cols[i % len(cols)]:
                    st.markdown(f"**{vocab}**")

    # Lesson stats
    segments = build_segments(lesson, voice)
    total_audio = sum(len(s["audio_urls"]) for s in segments)
    practice_points = sum(1 for s in segments if s["has_pause"])

    st.caption(
        f"{len(lesson.lines)} steps | {len(segments)} segments | "
        f"{practice_points} practice pauses | {total_audio} audio clips"
    )

    st.markdown("")

    # Mic permission primer: piggybacks on the Start Lesson click gesture
    # to pre-authorize getUserMedia. Hidden iframe, 0 height.
    components.html("""
    <script>
    document.addEventListener('click', function initMic() {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({audio: true})
                .then(function(stream) { stream.getTracks().forEach(function(t) { t.stop(); }); })
                .catch(function() {});
        }
        document.removeEventListener('click', initMic);
    }, {once: true});
    </script>
    """, height=0)

    # START BUTTON
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "Start Lesson",
            type="primary",
            use_container_width=True,
            key="start_lesson_btn",
        ):
            st.session_state.pimsleur_state = "SEGMENT"
            st.session_state.pimsleur_segment = 0
            st.session_state.pimsleur_segments = segments
            st.session_state.pimsleur_lesson_id = lesson_id
            st.session_state.pimsleur_practice_audio = None
            st.rerun()


# ============================================================================
# SEGMENT MODE — Combined audio playback + auto-recording
# ============================================================================

def _render_segment(voice: str):
    """Play current segment's audio. If practice point, auto-record."""

    segments = st.session_state.pimsleur_segments
    seg_idx = st.session_state.pimsleur_segment
    lesson_id = st.session_state.get("pimsleur_lesson_id", "")
    total_segments = len(segments)

    if not segments or seg_idx >= total_segments:
        st.session_state.pimsleur_state = "COMPLETE"
        st.rerun()
        return

    segment = segments[seg_idx]
    lesson = PIMSLEUR_LESSONS.get(lesson_id)
    num = int(lesson_id.split("_")[1]) if lesson_id else 0

    # Header with progress
    st.markdown(f"### Lesson {num}: {lesson.title if lesson else ''}")
    st.progress(
        seg_idx / total_segments,
        text=f"Segment {seg_idx + 1} of {total_segments}"
    )

    # Show transcript of current segment
    st.markdown("---")
    for line in segment["lines"]:
        _render_line_transcript(line)

    st.markdown("")

    # Render the bidirectional segment_player component
    if segment_player is not None:
        skip_audio = st.session_state.get("pimsleur_skip_audio", False)
        st.session_state.pimsleur_skip_audio = False  # Reset after reading

        result = segment_player(
            audio_urls=segment["audio_urls"],
            has_pause=segment["has_pause"],
            practice_text=segment.get("practice_text", ""),
            practice_phonetic=segment.get("practice_phonetic", ""),
            practice_english=segment.get("practice_english", ""),
            segment_index=seg_idx,
            audio_gap_ms=AUDIO_GAP_MS,
            silence_threshold_db=SILENCE_THRESHOLD_DB,
            silence_duration_ms=SILENCE_DURATION_MS,
            recording_delay_ms=RECORDING_DELAY_MS,
            skip_audio=skip_audio,
            key=f"seg_player_{lesson_id}_{seg_idx}_{st.session_state.pimsleur_retry_count}",
        )

        # Handle component return value
        if result is not None:
            result_type = result.get("type", "")

            if result_type == "segment_complete":
                _advance_segment()

            elif result_type == "practice_audio":
                st.session_state.pimsleur_practice_audio = result.get("audio_b64", "")
                st.session_state.pimsleur_practice_expected = segment.get("whisper_expected", "")
                st.session_state.pimsleur_state = "FEEDBACK"
                st.rerun()

            elif result_type == "error":
                st.error(result.get("message", "An error occurred"))
                # Show fallback buttons on error
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Retry", key=f"err_retry_{seg_idx}"):
                        st.session_state.pimsleur_retry_count += 1
                        st.rerun()
                with col2:
                    if st.button("Skip", key=f"err_skip_{seg_idx}"):
                        _advance_segment()
    else:
        st.error("Segment player component not available.")

    # Manual override buttons (small, at bottom)
    st.markdown("")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Replay", key=f"replay_{seg_idx}"):
            st.session_state.pimsleur_retry_count += 1
            st.rerun()
    with col3:
        if st.button("Skip", key=f"skip_{seg_idx}"):
            _advance_segment()


def _advance_segment():
    """Move to the next segment or COMPLETE."""
    segments = st.session_state.pimsleur_segments
    seg_idx = st.session_state.pimsleur_segment
    total_segments = len(segments)

    next_seg = seg_idx + 1
    st.session_state.pimsleur_retry_count = 0
    if next_seg < total_segments:
        st.session_state.pimsleur_segment = next_seg
        st.session_state.pimsleur_state = "SEGMENT"
    else:
        st.session_state.pimsleur_state = "COMPLETE"
    st.rerun()


# ============================================================================
# FEEDBACK MODE — Whisper analysis + auto-advance or retry
# ============================================================================

def _render_feedback(voice: str):
    """Show Whisper pronunciation analysis results."""

    segments = st.session_state.pimsleur_segments
    seg_idx = st.session_state.pimsleur_segment
    lesson_id = st.session_state.get("pimsleur_lesson_id", "")
    total_segments = len(segments)

    num = int(lesson_id.split("_")[1]) if lesson_id else 0
    lesson = PIMSLEUR_LESSONS.get(lesson_id)

    st.markdown(f"### Lesson {num}: {lesson.title if lesson else ''}")
    st.progress(
        (seg_idx + 0.5) / total_segments,
        text=f"Practice ({seg_idx + 1} of {total_segments})"
    )

    st.markdown("---")

    audio_b64 = st.session_state.get("pimsleur_practice_audio")
    expected = st.session_state.get("pimsleur_practice_expected", "")
    analysis_result = None
    accuracy = 0.0

    # Partial-word drills have no whisper_expected — auto-advance immediately
    if not expected:
        st.success("Good! Moving on...")
        st.session_state.pimsleur_practice_audio = None
        time.sleep(1)
        _advance_segment()
        return

    if audio_b64 and ENABLE_SPEECH_PRACTICE:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
            with st.spinner("Analyzing your pronunciation..."):
                analysis_result = analyze_pronunciation_b64(audio_b64, expected, api_key)
            accuracy = analysis_result.accuracy
            render_speech_feedback(analysis_result)
        except SpeechAnalysisError as e:
            st.warning(str(e))
        except Exception as e:
            st.warning(f"Could not analyze: {e}")
    else:
        st.info("Recording captured.")

    st.markdown("")

    # Decide: auto-advance (good score) or retry (poor score)
    is_good = accuracy >= SPEECH_ACCURACY_THRESHOLD

    if is_good:
        # Good score: auto-advance after countdown
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                "Continue",
                type="primary",
                use_container_width=True,
                key=f"feedback_continue_{seg_idx}",
            ):
                st.session_state.pimsleur_practice_audio = None
                _advance_segment()

        if AUTO_ADVANCE_SECONDS > 0:
            placeholder = st.empty()
            for remaining in range(AUTO_ADVANCE_SECONDS, 0, -1):
                placeholder.markdown(
                    f'<div style="text-align:center;color:#999;font-size:0.85em;">'
                    f'Auto-continuing in {remaining}s...</div>',
                    unsafe_allow_html=True,
                )
                time.sleep(1)
            placeholder.empty()
            st.session_state.pimsleur_practice_audio = None
            _advance_segment()
    else:
        # Poor score: show Retry + Continue buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button(
                "Retry",
                type="primary",
                use_container_width=True,
                key=f"feedback_retry_{seg_idx}",
            ):
                # Re-enter SEGMENT for the same segment (retry recording only)
                st.session_state.pimsleur_practice_audio = None
                st.session_state.pimsleur_retry_count += 1
                st.session_state.pimsleur_skip_audio = True
                st.session_state.pimsleur_state = "SEGMENT"
                st.rerun()
        with col3:
            if st.button(
                "Continue",
                use_container_width=True,
                key=f"feedback_skip_{seg_idx}",
            ):
                st.session_state.pimsleur_practice_audio = None
                _advance_segment()


# ============================================================================
# COMPLETE MODE — Lesson finished
# ============================================================================

def _render_complete(voice: str):
    """Show lesson completion screen."""

    lesson_id = st.session_state.get("pimsleur_lesson_id", "")
    lesson = PIMSLEUR_LESSONS.get(lesson_id)
    num = int(lesson_id.split("_")[1]) if lesson_id else 0

    st.progress(1.0, text="Lesson Complete!")

    st.markdown(
        f"""<div style="
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
            border-radius: 16px;
            margin: 20px 0;
        ">
            <h1 style="color: #2E7D32; margin-bottom: 8px;">Lesson Complete!</h1>
            <h3 style="color: #388E3C;">Lesson {num}: {lesson.title if lesson else ''}</h3>
        </div>""",
        unsafe_allow_html=True,
    )

    # Vocabulary review
    if lesson and lesson.new_vocabulary:
        st.markdown("### Words You Learned")
        cols = st.columns(min(len(lesson.new_vocabulary), 3))
        for i, vocab in enumerate(lesson.new_vocabulary):
            with cols[i % len(cols)]:
                st.success(f"**{vocab}**")

    st.markdown("")

    # Action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Replay Lesson", use_container_width=True):
            st.session_state.pimsleur_state = "IDLE"
            st.rerun()

    with col2:
        next_num = num + 1
        next_id = f"pimsleur_{next_num:02d}"
        if next_id in PIMSLEUR_LESSONS:
            next_lesson = PIMSLEUR_LESSONS[next_id]
            if st.button(
                f"Next: {next_lesson.title}",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.current_conversation = next_id
                st.session_state.pimsleur_state = "IDLE"
                st.rerun()
        else:
            st.info("You've completed all lessons!")

    with col3:
        if st.button("Back to Menu", use_container_width=True):
            st.session_state.pimsleur_state = "IDLE"
            st.rerun()


# ============================================================================
# SIDEBAR CONTROLS (called from app.py)
# ============================================================================

def render_pimsleur_sidebar():
    """
    Render sidebar controls when a lesson is actively playing.
    Call this from app.py's sidebar section.
    """
    state = st.session_state.get("pimsleur_state", "IDLE")
    if state not in ("SEGMENT", "FEEDBACK", "COMPLETE"):
        return

    st.markdown("---")
    st.markdown("**Lesson Player**")

    lesson_id = st.session_state.get("pimsleur_lesson_id", "")
    if lesson_id and lesson_id in PIMSLEUR_LESSONS:
        lesson = PIMSLEUR_LESSONS[lesson_id]
        num = int(lesson_id.split("_")[1])
        st.caption(f"Lesson {num}: {lesson.title}")

    segments = st.session_state.get("pimsleur_segments", [])
    seg_idx = st.session_state.get("pimsleur_segment", 0)
    total = len(segments) if segments else 1

    st.progress(seg_idx / max(total, 1))

    if state == "FEEDBACK":
        if st.button(
            "Resume",
            type="primary",
            use_container_width=True,
            key="sidebar_resume",
        ):
            st.session_state.pimsleur_practice_audio = None
            next_seg = seg_idx + 1
            if next_seg < total:
                st.session_state.pimsleur_segment = next_seg
                st.session_state.pimsleur_state = "SEGMENT"
            else:
                st.session_state.pimsleur_state = "COMPLETE"
            st.rerun()

    if st.button("Stop Lesson", key="sidebar_stop"):
        st.session_state.pimsleur_state = "IDLE"
        st.session_state.pimsleur_segment = 0
        st.session_state.pimsleur_segments = []
        st.session_state.pimsleur_practice_audio = None
        st.rerun()
