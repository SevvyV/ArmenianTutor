import streamlit as st
from google import genai
from google.genai import types
import wave
import io
import re

# 1. Page Configuration
st.set_page_config(page_title="HyeTutor2.0beta", page_icon="🇦🇲", layout="wide")

st.title("🇦🇲 HyeTutor2.0beta")
st.caption("Version 4.0 • Hard-Wired Pronouns • Stable Audio Stream")

# --- PERMANENT PRONOUNS ---
PRONOUNS = ["Ես", "Դուն", "Ան", "Մենք", "Դուք", "Անոնք"]

# --- DATA: FOUNDATIONS & TOP 50 ---
FOUNDATIONS = {
    "📅 Days of the Week": "Երկուշաբթի, Երեքշաբթի, Չորեքշաբթի, Հինգշաբթի, Ուրբաթ, Շաբաթ, Կիրակի",
    "🔢 Numbers (1-10)": "Մէկ, Երկու, Երեք, Չորս, Հինգ, Վեց, Եօթը, Ութը, Ինը, Տասը",
    "🗓️ Months of the Year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

TOP_50_VERBS = ["be", "have", "do", "say", "go", "can", "get", "would", "make", "know", "will", "think", "take", "see", "come", "could", "want", "look", "use", "find", "give", "tell", "work", "may", "should", "call", "try", "ask", "need", "feel", "become", "leave", "put", "mean", "keep", "let", "begin", "seem", "help", "talk", "turn", "start", "might", "show", "hear", "play", "run", "move", "like", "live"]

# 2. Key Verification
api_key = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=api_key)

# 3. Robust Audio Utility
def create_wav_file(pcm_data):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) 
        wf.setframerate(24000)
        wf.writeframes(pcm_data)
    return buf.getvalue()

def get_audio_stream(text_to_speak, slow_mode=False):
    """Directly fetches audio bytes for the speaker."""
    speed = "slowly" if slow_mode else "naturally"
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite-preview-tts",
            contents=f"Say this {speed} in Western Armenian: {text_to_speak}",
            config=types.GenerateContentConfig(response_modalities=["AUDIO"])
        )
        # Extract binary data safely
        audio_part = response.candidates[0].content.parts[0]
        if hasattr(audio_part, 'inline_data'):
            return create_wav_file(audio_part.inline_data.data)
    except:
        return None
    return None

# 4. Sidebar: Master Navigation
with st.sidebar:
    st.header("🎓 Learning Plan")
    main_mode = st.selectbox("Select Learning Category:", ["Foundations", "Top 50 Verbs", "Custom Search"])
    st.divider()
    slow_audio = st.toggle("🐢 Slow-Motion Audio", value=False)
    
    if main_mode == "Foundations":
        sub_selection = st.selectbox("Choose Foundation:", list(FOUNDATIONS.keys()))
        selected_content = FOUNDATIONS[sub_selection]
        mode_label = sub_selection
    elif main_mode == "Top 50 Verbs":
        sub_selection = st.selectbox("Select Verb:", TOP_50_VERBS)
        tense = st.selectbox("Tense:", ["Past", "Present", "Future"])
        mode_label = f"{sub_selection} ({tense})"
    else:
        sub_selection = st.text_input("Type any English verb:", "to sing")
        tense = st.selectbox("Tense:", ["Past", "Present", "Future"])
        mode_label = f"{sub_selection} ({tense})"

    st.divider()
    if st.button("🔄 Reset Session", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 5. Hybrid Verb Logic (Pronouns Hard-Wired)
@st.cache_data
def get_verb_only(verb_name, tense_name):
    """Asks the AI for ONLY the 6 conjugated verbs without pronouns."""
    prompt = f"Provide the 6 Western Armenian conjugated forms for the verb '{verb_name}' in {tense_name} tense. Return ONLY a comma-separated list of the verbs. No pronouns, no English."
    response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
    verbs = response.text.strip().split(",")
    return [v.strip() for v in verbs if v.strip()]

# 6. Main Lesson Area
if main_mode == "Foundations":
    st.header(mode_label)
    st.write(f"### {selected_content}")
    if st.button(f"🔊 Listen"):
        audio_bytes = get_audio_stream(selected_content, slow_mode=slow_audio)
        if audio_bytes: st.audio(audio_bytes, format="audio/wav")

else:
    if sub_selection:
        with st.spinner("Tutor is thinking..."):
            verbs_only = get_verb_only(sub_selection, tense)
            # HARD-WIRING STEP: Pair hard-coded pronouns with AI-generated verbs
            full_conjugation = [f"{p} {v}" for p, v in zip(PRONOUNS, verbs_only)]
        
        st.header(f"Verb: {sub_selection}")
        cols = st.columns(3)
        for i, item in enumerate(full_conjugation):
            cols[i % 3].write(f"🔹 **{item}**")
            
        if st.button("🔊 Listen"):
            audio_bytes = get_audio_stream(", ".join(full_conjugation), slow_mode=slow_audio)
            if audio_bytes: st.audio(audio_bytes, format="audio/wav")

st.divider()

# 7. Practice Interaction
audio_data = st.audio_input("Practice and get feedback")
if audio_data:
    with st.status("Analyzing..."):
        audio_part = types.Part.from_bytes(data=audio_data.read(), mime_type="audio/wav")
        analysis = client.models.generate_content(
            model="gemini-3-flash-preview", 
            config={'system_instruction': f"Analyze pronunciation of {mode_label}."},
            contents=[audio_part]
        )
        st.success("Tutor's Evaluation:")
        st.markdown(analysis.text)
        # Speak feedback
        clean_fb = re.sub(r'[*#]', '', analysis.text.split("\n")[0])
        fb_audio = get_audio_stream(clean_fb)
        if fb_audio: st.audio(fb_audio, format="audio/wav")
