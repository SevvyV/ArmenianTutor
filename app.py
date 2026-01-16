import streamlit as st
from google import genai
from google.genai import types
import wave
import io
import re

# 1. Page Configuration
st.set_page_config(page_title="HyeTutor2.0beta", page_icon="🇦🇲", layout="wide")

st.title("🇦🇲 HyeTutor2.0beta")
st.caption("Version 4.3 • Automatic Audio Recovery • Hard-Wired Pronouns")

# --- PERMANENT DATA (NEVER DELETED) ---
PRONOUNS = ["Ես", "Դուն", "Ան", "Մենք", "Դուք", "Անոնք"]

FOUNDATIONS = {
    "📅 Days of the Week": "Երկուշաբթի, Երեքշաբթի, Չորեքշաբթի, Հինգշաբթի, Ուրբաթ, Շաբաթ, Կիրակի",
    "🔢 Numbers (1-10)": "Մէկ, Երկու, Երեք, Չորս, Հինգ, Վեց, Եօթը, Ութը, Ինը, Տասը",
    "🗓️ Months of the Year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

TOP_50_VERBS = ["be", "have", "do", "say", "go", "can", "get", "would", "make", "know", "will", "think", "take", "see", "come", "could", "want", "look", "use", "find", "give", "tell", "work", "may", "should", "call", "try", "ask", "need", "feel", "become", "leave", "put", "mean", "keep", "let", "begin", "seem", "help", "talk", "turn", "start", "might", "show", "hear", "play", "run", "move", "like", "live"]

# 2. Key Verification
api_key = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=api_key)

# 3. Audio Utility Functions
def create_wav_file(pcm_data):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) 
        wf.setframerate(24000)
        wf.writeframes(pcm_data)
    return buf.getvalue()

def get_stable_audio(text_to_speak, slow_mode=False):
    """Attempts the primary TTS model with a secondary fallback to prevent 404s."""
    speed = "slowly" if slow_mode else "clearly"
    # Try the two most common 2026 model names
    models_to_try = ["gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts"]
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=f"Say this {speed} in Western Armenian: {text_to_speak}",
                config=types.GenerateContentConfig(response_modalities=["AUDIO"])
            )
            # Binary extraction from the current SDK parts structure
            audio_bytes = response.candidates[0].content.parts[0].inline_data.data
            return create_wav_file(audio_bytes)
        except Exception:
            continue # Try the next model in the list
            
    st.error("Audio service is currently rotating models. Please try again in 1 minute.")
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

# 5. Hybrid Verb Engine
@st.cache_data
def get_verbs_only(verb_name, tense_name):
    prompt = f"Provide ONLY the 6 conjugated Western Armenian forms for '{verb_name}' in {tense_name} tense. NO PRONOUNS. Comma-separated."
    response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
    raw_verbs = response.text.strip().split(",")
    return [v.strip() for v in raw_verbs if v.strip()]

# 6. Main Lesson Area
if main_mode == "Foundations":
    st.header(mode_label)
    st.write(f"### {selected_content}")
    if st.button("🔊 Listen"):
        audio = get_stable_audio(selected_content, slow_mode=slow_audio)
        if audio: st.audio(audio, format="audio/wav")

else:
    if sub_selection:
        with st.spinner("Tutor is thinking..."):
            verbs = get_verbs_only(sub_selection, tense)
            # Pronoun Pairing (Manual Stitching)
            display_list = [f"{PRONOUNS[i]} {verbs[i]}" for i in range(min(len(PRONOUNS), len(verbs)))]
        
        st.header(f"Verb: {sub_selection}")
        cols = st.columns(3)
        for i, item in enumerate(display_list):
            cols[i % 3].write(f"🔹 **{item}**")
            
        if st.button("🔊 Listen"):
            audio_text = ", ".join(display_list)
            audio = get_stable_audio(audio_text, slow_mode=slow_audio)
            if audio: st.audio(audio, format="audio/wav")

st.divider()

# 7. Feedback Loop
audio_data = st.audio_input("Record your practice")
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
        # Summary Feedback audio
        fb_text = analysis.text.split("\n")[0]
        fb_audio = get_stable_audio(fb_text)
        if fb_audio: st.audio(fb_audio, format="audio/wav")
