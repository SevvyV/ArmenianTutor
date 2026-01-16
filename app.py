import streamlit as st
from google import genai
from google.genai import types
import wave
import io
import os

# 1. Page Configuration
st.set_page_config(page_title="HyeTutor2.0beta", page_icon="🇦🇲", layout="wide")

st.title("🇦🇲 HyeTutor2.0beta")
st.caption("Version 5.4 • Direct Download Mode")

# --- AUDIO LIBRARY SETUP ---
AUDIO_DIR = "audio_library"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# --- PERMANENT DATA ---
PRONOUNS = ["Ես", "Դուն", "Ան", "Մենք", "Դուք", "Անոնք"]
FOUNDATIONS = {
    "Days": "Երկուշաբթի, Երեքշաբթի, Չորեքշաբթի, Հինգշաբթի, Ուրբաթ, Շաբաթ, Կիրակի",
    "Numbers": "Մէկ, Երկու, Երեք, Չորս, Հինգ, Վեց, Եօթը, Ութը, Ինը, Տասը",
    "Months": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

# 2. Key Verification
api_key = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=api_key)

# 3. AUDIO ENGINE
def create_wav_file(pcm_data):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) 
        wf.setframerate(24000)
        wf.writeframes(pcm_data)
    return buf.getvalue()

def get_audio(text_to_speak, slow_mode=False):
    clean_name = "".join(filter(str.isalnum, text_to_speak))[:40]
    speed_tag = "_slow" if slow_mode else "_fast"
    file_path = os.path.join(AUDIO_DIR, f"{clean_name}{speed_tag}.wav")

    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return f.read()

    try:
        speed_instr = "slowly" if slow_mode else "clearly"
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=f"Say this {speed_instr} in Western Armenian: {text_to_speak}",
            config=types.GenerateContentConfig(response_modalities=["AUDIO"])
        )
        audio_bytes = response.candidates[0].content.parts[0].inline_data.data
        wav_data = create_wav_file(audio_bytes)
        with open(file_path, "wb") as f: f.write(wav_data)
        return wav_data
    except:
        return None

# 4. Sidebar: Library Builder
with st.sidebar:
    st.header("🛠️ Admin Tools")
    if st.button("Generate Audio Files"):
        with st.status("Creating files..."):
            for name, text in FOUNDATIONS.items():
                get_audio(text, False)
                get_audio(text, True)
        st.success("Files ready!")

    st.divider()
    st.write("📥 Download Created Files:")
    for file_name in os.listdir(AUDIO_DIR):
        if file_name.endswith(".wav"):
            with open(os.path.join(AUDIO_DIR, file_name), "rb") as f:
                st.download_button(label=f"Download {file_name}", data=f, file_name=file_name)

# 5. Main Lesson Area (Simplified for testing)
main_mode = st.selectbox("Category:", ["Foundations", "Phrase Translator"])
if main_mode == "Foundations":
    sel = st.selectbox("Selection:", list(FOUNDATIONS.keys()))
    if st.button("🔊 Listen"):
        audio = get_audio(FOUNDATIONS[sel])
        if audio: st.audio(audio, format="audio/wav", autoplay=True)
