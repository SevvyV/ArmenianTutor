"""
Interactive Pimsleur Lesson Player for Armenian Tutor.

Transforms conversations from static reference into a hands-free,
sequential audio lesson that flows like real Pimsleur:

1. User taps "Start Lesson"
2. Instructor narrates (English TTS) + Armenian audio plays automatically
3. At practice points, lesson pauses for pronunciation recording
4. User taps "Continue" (or auto-continues after countdown)
5. Lesson resumes until next practice point or completion

Architecture:
- Lessons are split into "segments" at pause boundaries
- Each segment's audio plays via a JavaScript audio queue (st.components.v1.html)
- State machine: IDLE -> PLAYING -> PRACTICE -> PLAYING -> ... -> COMPLETE
"""

import json
import streamlit as st
import streamlit.components.v1 as components

from pimsleur_data import PIMSLEUR_LESSONS, PIMSLEUR_UNITS
from audio_manager import AudioManager
from config import (
    ENABLE_SPEECH_PRACTICE,
    AUTO_CONTINUE_SECONDS,
    AUDIO_GAP_MS,
)

if ENABLE_SPEECH_PRACTICE:
    from speech_analysis import render_mic_button, render_mic_inline


# ============================================================================
# SEGMENT DATA STRUCTURE (plain dicts for session state compatibility)
# ============================================================================

def build_segments(lesson, voice: str) -> list:
    """
    Split a lesson into playable segments at pause boundaries.

    Each segment is a plain dict (not a dataclass) so it survives
    Streamlit session state serialization across reruns.

    Each segment contains:
        index: int
        lines: list of dicts with speaker/text/phonetic/english/audio_key
        audio_urls: ordered list of audio URLs to play
        pause_text: str - the pause line's text (e.g., "Practice (3s)")
        has_pause: bool - whether this segment ends with a pause
        practice_text: str - Armenian text to practice
        practice_phonetic: str - phonetic guide
        practice_english: str - English translation

    Args:
        lesson: ConversationLesson instance
        voice: "male" or "female" for Armenian audio

    Returns:
        List of segment dicts
    """
    segments = []
    current_lines = []
    current_urls = []
    last_armenian_text = ""
    last_armenian_phonetic = ""
    last_armenian_english = ""

    for line in lesson.lines:
        if line.speaker == "pause":
            # Finalize current segment at this pause
            segments.append({
                "index": len(segments),
                "lines": [_line_to_dict(l) for l in current_lines],
                "audio_urls": list(current_urls),
                "has_pause": True,
                "pause_text": line.text,
                "practice_text": last_armenian_text,
                "practice_phonetic": last_armenian_phonetic,
                "practice_english": last_armenian_english,
            })
            current_lines = []
            current_urls = []
        else:
            current_lines.append(line)
            # Build audio URL based on speaker type
            if line.speaker == "instructor" and line.audio_key:
                current_urls.append(
                    AudioManager.get_instructor_url(line.audio_key, lesson.id)
                )
            elif line.speaker in ("male", "female") and line.audio_key:
                current_urls.append(
                    AudioManager.get_conversation_url(
                        line.audio_key, lesson.id, voice
                    )
                )
                last_armenian_text = line.text
                last_armenian_phonetic = line.phonetic
                last_armenian_english = line.english
            # sfx lines: no audio URL, just visual

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
# JAVASCRIPT AUDIO QUEUE
# ============================================================================

def _build_audio_queue_html(audio_urls: list, segment_index: int) -> str:
    """
    Build an HTML/JS audio queue player that plays URLs sequentially.

    Features:
    - Chains audio playback via Audio.onended
    - Preloads upcoming files for smooth transitions
    - Configurable gap between clips (AUDIO_GAP_MS)
    - Wake Lock API to prevent screen sleep
    - Fallback "Tap to Play" if autoplay is blocked
    - Visual progress indicator
    """
    urls_json = json.dumps(audio_urls)
    gap_ms = AUDIO_GAP_MS

    return f"""
    <div id="audio-player-{segment_index}" style="
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: white;
        min-height: 80px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    ">
        <div id="progress-bar-bg" style="
            width: 100%;
            height: 6px;
            background: rgba(255,255,255,0.15);
            border-radius: 3px;
            margin-bottom: 16px;
            overflow: hidden;
        ">
            <div id="progress-bar" style="
                width: 0%;
                height: 100%;
                background: linear-gradient(90deg, #F2A900, #D90012);
                border-radius: 3px;
                transition: width 0.3s ease;
            "></div>
        </div>

        <div id="status" style="
            font-size: 1.1em;
            font-weight: 500;
            margin-bottom: 8px;
        ">Preparing audio...</div>

        <div id="counter" style="
            font-size: 0.85em;
            color: rgba(255,255,255,0.6);
        "></div>

        <button id="play-btn" onclick="startPlayback()" style="
            display: none;
            margin-top: 12px;
            padding: 16px 48px;
            font-size: 1.3em;
            font-weight: 600;
            background: linear-gradient(135deg, #F2A900, #D90012);
            color: white;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(242, 169, 0, 0.4);
        ">Tap to Play</button>
    </div>

    <script>
    (function() {{
        const urls = {urls_json};
        const gap = {gap_ms};
        let currentIndex = 0;
        let wakeLock = null;

        // Request wake lock to keep screen on during lesson
        async function requestWakeLock() {{
            try {{
                if ('wakeLock' in navigator) {{
                    wakeLock = await navigator.wakeLock.request('screen');
                }}
            }} catch(e) {{}}
        }}

        // Preload upcoming audio files
        function preload(startIdx, count) {{
            for (let j = startIdx; j < Math.min(startIdx + count, urls.length); j++) {{
                let a = new Audio(urls[j]);
                a.preload = 'auto';
            }}
        }}

        function updateProgress() {{
            const pct = urls.length > 0 ? (currentIndex / urls.length) * 100 : 100;
            const bar = document.getElementById('progress-bar');
            if (bar) bar.style.width = pct + '%';

            const counter = document.getElementById('counter');
            if (counter && urls.length > 0) {{
                counter.textContent = currentIndex + ' of ' + urls.length + ' clips';
            }}
        }}

        function playNext() {{
            if (currentIndex >= urls.length) {{
                // All audio finished
                const bar = document.getElementById('progress-bar');
                if (bar) bar.style.width = '100%';
                document.getElementById('status').innerHTML =
                    '<span style="color: #4CAF50;">&#10003;</span> Segment complete';
                document.getElementById('counter').textContent = 'Tap Continue below when ready';
                // Release wake lock
                if (wakeLock) {{ try {{ wakeLock.release(); }} catch(e) {{}} }}
                return;
            }}

            updateProgress();
            document.getElementById('status').textContent =
                'Playing ' + (currentIndex + 1) + ' of ' + urls.length + '...';

            // Preload next 2 files
            preload(currentIndex + 1, 2);

            const audio = new Audio(urls[currentIndex]);
            audio.addEventListener('ended', function() {{
                currentIndex++;
                // Add natural gap between clips
                if (gap > 0 && currentIndex < urls.length) {{
                    setTimeout(playNext, gap);
                }} else {{
                    playNext();
                }}
            }});
            audio.addEventListener('error', function() {{
                currentIndex++;
                playNext();
            }});
            audio.play().catch(function() {{
                // Autoplay blocked - show tap button
                document.getElementById('play-btn').style.display = 'inline-block';
                document.getElementById('status').textContent = 'Tap the button to start';
                document.getElementById('counter').textContent = '';
                // Store audio ref for manual play
                window._pendingAudio = audio;
            }});
        }}

        window.startPlayback = function() {{
            document.getElementById('play-btn').style.display = 'none';
            if (window._pendingAudio) {{
                window._pendingAudio.play();
                window._pendingAudio = null;
            }} else {{
                playNext();
            }}
        }};

        // Start
        if (urls.length === 0) {{
            document.getElementById('status').innerHTML =
                '<span style="color: #4CAF50;">&#10003;</span> No audio in this segment';
            document.getElementById('counter').textContent = 'Tap Continue below';
        }} else {{
            requestWakeLock();
            preload(0, 3);
            playNext();
        }}
    }})();
    </script>
    """


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
        icon = "M" if speaker == "male" else "F"
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
    - PLAYING: Audio queue + transcript
    - PRACTICE: Mic recorder + feedback + Continue
    - COMPLETE: Congratulations + next lesson

    Args:
        voice: "male" or "female" for Armenian audio
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

    state = st.session_state.pimsleur_state

    if state == "IDLE":
        _render_idle(voice)
    elif state == "PLAYING":
        _render_playing(voice)
    elif state == "PRACTICE":
        _render_practice(voice)
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

    # START BUTTON
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "Start Lesson",
            type="primary",
            use_container_width=True,
            key="start_lesson_btn",
        ):
            st.session_state.pimsleur_state = "PLAYING"
            st.session_state.pimsleur_segment = 0
            st.session_state.pimsleur_segments = segments
            st.session_state.pimsleur_lesson_id = lesson_id
            st.rerun()


# ============================================================================
# PLAYING MODE — Audio queue + transcript
# ============================================================================

def _render_playing(voice: str):
    """Play current segment's audio and show transcript."""

    segments = st.session_state.pimsleur_segments
    seg_idx = st.session_state.pimsleur_segment
    lesson_id = st.session_state.get("pimsleur_lesson_id", "")

    if not segments or seg_idx >= len(segments):
        st.session_state.pimsleur_state = "COMPLETE"
        st.rerun()
        return

    segment = segments[seg_idx]
    lesson = PIMSLEUR_LESSONS.get(lesson_id)
    num = int(lesson_id.split("_")[1]) if lesson_id else 0
    total_segments = len(segments)

    # Header with progress
    st.markdown(
        f"### Lesson {num}: {lesson.title if lesson else ''}"
    )
    st.progress(
        (seg_idx) / total_segments,
        text=f"Segment {seg_idx + 1} of {total_segments}"
    )

    # Show transcript of current segment
    st.markdown("---")
    for line in segment["lines"]:
        _render_line_transcript(line)

    # Audio queue player
    st.markdown("")
    if segment["audio_urls"]:
        components.html(
            _build_audio_queue_html(segment["audio_urls"], seg_idx),
            height=130,
        )
    else:
        st.info("No audio in this segment.")

    st.markdown("")

    # Continue button — advances to practice or next segment
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if segment["has_pause"]:
            btn_label = "Continue to Practice"
        elif seg_idx + 1 < total_segments:
            btn_label = "Continue"
        else:
            btn_label = "Finish Lesson"

        if st.button(
            btn_label,
            type="primary",
            use_container_width=True,
            key=f"continue_playing_{seg_idx}",
        ):
            if segment["has_pause"]:
                st.session_state.pimsleur_state = "PRACTICE"
            elif seg_idx + 1 < total_segments:
                st.session_state.pimsleur_segment = seg_idx + 1
                # stays PLAYING
            else:
                st.session_state.pimsleur_state = "COMPLETE"
            st.rerun()

    # Replay segment button (small)
    with col1:
        if st.button("Replay", key=f"replay_{seg_idx}"):
            st.rerun()  # Re-renders same segment, restarts audio


# ============================================================================
# PRACTICE MODE — Mic recording + feedback
# ============================================================================

def _render_practice(voice: str):
    """Show practice UI at a pause point."""

    segments = st.session_state.pimsleur_segments
    seg_idx = st.session_state.pimsleur_segment
    lesson_id = st.session_state.get("pimsleur_lesson_id", "")
    total_segments = len(segments)

    if not segments or seg_idx >= len(segments):
        st.session_state.pimsleur_state = "COMPLETE"
        st.rerun()
        return

    segment = segments[seg_idx]
    lesson = PIMSLEUR_LESSONS.get(lesson_id)
    num = int(lesson_id.split("_")[1]) if lesson_id else 0

    # Header
    st.markdown(f"### Lesson {num}: {lesson.title if lesson else ''}")
    st.progress(
        (seg_idx + 0.5) / total_segments,
        text=f"Practice ({seg_idx + 1} of {total_segments})"
    )

    st.markdown("---")

    # Practice prompt
    pause_text = segment.get("pause_text", "Practice") if isinstance(segment, dict) else "Practice"
    st.markdown(
        f"""<div style="
            background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
            border-left: 5px solid #F57C00;
            padding: 24px;
            margin: 16px 0;
            border-radius: 0 12px 12px 0;
            text-align: center;
        ">
            <h2 style="margin: 0 0 8px 0; color: #E65100;">Your Turn!</h2>
            <p style="margin: 0; color: #555; font-size: 1.1em;">
                {pause_text}
            </p>
        </div>""",
        unsafe_allow_html=True,
    )

    # Find the Armenian phrase to practice
    p_text = segment.get("practice_text", "") or ""
    p_phonetic = segment.get("practice_phonetic", "") or ""
    p_english = segment.get("practice_english", "") or ""

    # Fallback: scan this segment's lines for the last Armenian line
    if not p_text:
        for line in reversed(segment.get("lines", [])):
            speaker = line.get("speaker", "") if isinstance(line, dict) else ""
            text = line.get("text", "") if isinstance(line, dict) else ""
            if speaker in ("male", "female") and text:
                p_text = text
                p_phonetic = line.get("phonetic", "")
                p_english = line.get("english", "")
                break

    # Show the Armenian phrase to practice
    if p_text:
        st.markdown(
            f"""<div style="text-align: center; padding: 16px 0;">
                <div style="font-size: 2.2em; font-weight: bold; margin-bottom: 8px;">
                    {p_text}
                </div>
                <div style="font-size: 1.2em; color: #888; font-style: italic;">
                    {p_phonetic}
                </div>
                <div style="font-size: 1em; color: #666; margin-top: 4px;">
                    {p_english}
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    # Mic recorder with Whisper feedback (inline, always visible)
    if ENABLE_SPEECH_PRACTICE and p_text:
        render_mic_inline(
            p_text,
            f"mic_pimsleur_{lesson_id}_seg_{seg_idx}"
        )

    st.markdown("")

    # Auto-continue countdown (if enabled)
    auto_continue_html = ""
    if AUTO_CONTINUE_SECONDS > 0:
        auto_continue_html = f"""
        <div style="text-align: center; margin-top: 8px;">
            <span style="color: #999; font-size: 0.85em;">
                Auto-continuing in <span id="countdown">{AUTO_CONTINUE_SECONDS}</span>s...
                (tap Continue to skip)
            </span>
        </div>
        <script>
        (function() {{
            let secs = {AUTO_CONTINUE_SECONDS};
            const el = document.getElementById('countdown');
            const timer = setInterval(() => {{
                secs--;
                if (el) el.textContent = secs;
                if (secs <= 0) {{
                    clearInterval(timer);
                    // Note: Cannot auto-click Streamlit button from iframe,
                    // but the visual countdown prompts the user
                    if (el) el.parentElement.innerHTML =
                        '<b style="color: #F57C00;">Ready to continue!</b>';
                }}
            }}, 1000);
        }})();
        </script>
        """

    # CONTINUE button (prominent)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "Continue",
            type="primary",
            use_container_width=True,
            key=f"continue_practice_{seg_idx}",
        ):
            # Advance to next segment
            next_seg = seg_idx + 1
            if next_seg < total_segments:
                st.session_state.pimsleur_segment = next_seg
                st.session_state.pimsleur_state = "PLAYING"
            else:
                st.session_state.pimsleur_state = "COMPLETE"
            st.rerun()

    # Skip practice (small link)
    with col3:
        if st.button("Skip", key=f"skip_practice_{seg_idx}"):
            next_seg = seg_idx + 1
            if next_seg < total_segments:
                st.session_state.pimsleur_segment = next_seg
                st.session_state.pimsleur_state = "PLAYING"
            else:
                st.session_state.pimsleur_state = "COMPLETE"
            st.rerun()

    # Auto-continue countdown display
    if auto_continue_html:
        components.html(auto_continue_html, height=40)


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
        # Next lesson button
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
    if state not in ("PLAYING", "PRACTICE", "COMPLETE"):
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

    if state == "PRACTICE":
        if st.button(
            "Resume",
            type="primary",
            use_container_width=True,
            key="sidebar_resume",
        ):
            next_seg = seg_idx + 1
            if next_seg < total:
                st.session_state.pimsleur_segment = next_seg
                st.session_state.pimsleur_state = "PLAYING"
            else:
                st.session_state.pimsleur_state = "COMPLETE"
            st.rerun()

    if st.button("Stop Lesson", key="sidebar_stop"):
        st.session_state.pimsleur_state = "IDLE"
        st.session_state.pimsleur_segment = 0
        st.session_state.pimsleur_segments = []
        st.rerun()
