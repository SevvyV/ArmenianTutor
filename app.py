import streamlit as st
from google import genai
from google.genai import types
import wave
import io
import os
import re

# 1. Page Configuration
st.set_page_config(page_title="HyeTutor2.0beta", page_icon="🇦🇲", layout="wide")

st.title("🇦🇲 HyeTutor2.0beta")
st.caption("Version 5.0 • Hybrid Audio Library • Tier 1 Speed Optimization")

# --- AUDIO LIBRARY SETUP ---
# This folder must exist in your GitHub repo for permanent storage.
# If it doesn't exist locally, the app creates it for the current session.
AUDIO_DIR = "audio_library"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# --- PERMANENT DATA ---
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

# 3. HYBRID LIBRARY ENGINE
def create_wav_file(pcm_data):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) 
        wf.setframerate(24000)
        wf.writeframes(pcm_data)
    return buf.getvalue()

@st.cache_data(show_spinner=False)
def get_audio(text_to_speak, slow_mode=False):
    """Checks local library first, then generates via Flash-Lite if missing."""
    # Create a simple filename from the text
    clean_name = "".join(filter(str.isalnum, text_to_speak))[:40]
    speed_tag = "_slow" if slow_mode else "_fast"
    file_path = os.path.join(AUDIO_DIR, f"{clean_name}{speed_tag}.wav")

    # 1. Check Library (Instant)
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return f.read()

    # 2. Generate if missing (Flash-Lite for Tier 1 Speed)
    speed_instr = "slowly" if slow_mode else "clearly"
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite-preview-tts",
            contents=f"Say this {speed_instr} in Western Armenian: {text_to_speak}",
            config=types.GenerateContentConfig(response_modalities=["AUDIO"])
        )
        audio_bytes = response.candidates[0].content.parts[0].inline_data.data
        wav_data = create_wav_file(audio_bytes)
        
        # Save for current session use
        with open(file_path, "wb") as f:
            f.write(wav_data)
            
        return wav_data
    except Exception:
        return None

# 4. Sidebar: Master Navigation
with st.sidebar:
    st.header("🎓 Learning Plan")
    main_mode = st.selectbox("Category:", ["Foundations", "Top 50 Verbs", "Verb Drill Master", "Phrase Translator"])
    st.divider()
    slow_audio = st.toggle("🐢 Slow-Motion Audio", value=False)
    
    if main_mode == "Foundations":
        sub_selection = st.selectbox("Choose Foundation:", list(FOUNDATIONS.keys()))
        selected_content = FOUNDATIONS[sub_selection]
    elif main_mode == "Top 50 Verbs":
        sub_selection = st.selectbox("Select Verb:", TOP_50_VERBS)
        tense = st.selectbox("Tense:", ["Past", "Present", "Future"])
    elif main_mode == "Verb Drill Master":
        sub_selection = st.text_input("Type any English verb:", "to sing")
        tense = st.selectbox("Tense:", ["Past", "Present", "Future"])
    elif main_mode == "Phrase Translator":
        sub_selection = st.text_input("Type English phrase:", "How are you?")

    st.divider()
    if st.button("🔄 Reset Session", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 5. Specialized Logic
@st.cache_data
def get_verbs_only(verb_name, tense_name):
    prompt = f"Provide ONLY the 6 conjugated Western Armenian forms for '{verb_name}' in {tense_name} tense. NO PRONOUNS. Comma-separated."
    response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
    raw_verbs = response.text.strip().split(",")
    return [v.strip() for v in raw_verbs if v.strip()]

@st.cache_data
def get_translation(phrase):
    prompt = f"Translate to natural Western Armenian: '{phrase}'. Return ONLY Armenian."
    response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
    return response.text.strip()

# 6. Main Lesson Area
if main_mode == "Foundations":
    st.header(sub_selection)
    st.write(f"### {selected_content}")
    if st.button("🔊 Listen"):
        audio = get_audio(selected_content, slow_mode=slow_audio)
        if audio: st.audio(audio, format="audio/wav", autoplay=True)

elif main_mode == "Phrase Translator":
    st.header("Phrase Translator")
    if sub_selection:
        with st.spinner("Translating..."):
            translated_text = get_translation(sub_selection)
        st.write(f"**English:** {sub_selection}")
        st.write(f"### **Armenian:** {translated_text}")
        if st.button("🔊 Speak Translation"):
            audio = get_audio(translated_text, slow_mode=slow_audio)
            if audio: st.audio(audio, format="audio/wav", autoplay=True)

else: # Verb Modes
    if sub_selection:
        with st.spinner("Conjugating..."):
            verbs = get_verbs_only(sub_selection, tense)
            display_list = [f"{PRONOUNS[i]} {verbs[i]}" for i in range(min(len(PRONOUNS), len(verbs)))]
        
        st.header(f"Verb: {sub_selection}")
        cols = st.columns(3)
        for i, item in enumerate(display_list):
            cols[i % 3].write(f"🔹 **{item}**")
            
        if st.button("🔊 Listen"):
            audio_text = ", ".join(display_list)
            audio = get_audio(audio_text, slow_mode=slow_audio)
            if audio: st.audio(audio, format="audio/wav", autoplay=True)

st.divider()

# 7. Feedback Loop
audio_data = st.audio_input("Practice and get feedback")
if audio_data:
    with st.status("Analyzing..."):
        audio_part = types.Part.from_bytes(data=audio_data.read(), mime_type="audio/wav")
        analysis = client.models.generate_content(
            model="gemini-3-flash-preview", 
            config={'system_instruction': "Analyze Western Armenian pronunciation."},
            contents=[audio_part]
        )
        st.success("Tutor's Evaluation:")
        st.markdown(analysis.text)
        fb_text = analysis.text.split("\n")[0]
        fb_audio = get_audio(fb_text)
        if fb_audio: st.audio(fb_audio, format="audio/wav", autoplay=True)
