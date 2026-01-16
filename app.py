import streamlit as st
from google import genai
from google.genai import types
import wave
import io
import os
import zipfile

# 1. Page Configuration
st.set_page_config(page_title="HyeTutor2.0beta", page_icon="🇦🇲", layout="wide")

st.title("🇦🇲 HyeTutor2.0beta")
st.caption("Version 5.7 • Audio API Fix • Tier 1 Stable")

# --- AUDIO LIBRARY SETUP ---
AUDIO_DIR = "audio_library"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# --- PERMANENT DATA ---
PRONOUNS = ["Ես", "Դուն", "Ան", "Մենք", "Դուք", "Անոնք"]
FOUNDATIONS = {
    "days_of_the_week": {
        "label": "📅 Days of the Week",
        "text": "Երկուշաբթի, Երեքշաբթի, Չորեքշաբթի, Հինգշաբթի, Ուրբաթ, Շաբաթ, Կիրակի"
    },
    "numbers_1_10": {
        "label": "🔢 Numbers (1-10)",
        "text": "Մէկ, Երկու, Երեք, Չորս, Հինգ, Վեց, Եօթը, Ութը, Ինը, Տասը"
    },
    "months_of_the_year": {
        "label": "🗓️ Months of the Year",
        "text": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
    }
}

# 2. Key Verification
api_key = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=api_key)

# 3. ROBUST AUDIO ENGINE (The Fix)
def create_wav_file(pcm_data):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) 
        wf.setframerate(24000)
        wf.writeframes(pcm_data)
    return buf.getvalue()

def get_audio(text_to_speak, filename_slug, slow_mode=False):
    speed_tag = "_slow" if slow_mode else "_fast"
    file_path = os.path.join(AUDIO_DIR, f"{filename_slug}{speed_tag}.wav")

    # 1. Check if we already have it
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return f.read()

    # 2. Try specialized TTS models (The 400 Error Fix)
    # We use -tts specific models which are allowlisted for audio output
    models_to_try = ["gemini-2.5-flash-preview-tts", "gemini-2.5-flash-tts", "gemini-2.5-flash"]
    speed_instr = "slowly" if slow_mode else "clearly"
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=f"Say this {speed_instr} in Western Armenian: {text_to_speak}",
                config=types.GenerateContentConfig(response_modalities=["AUDIO"])
            )
            # If successful, extract and save
            audio_bytes = response.candidates[0].content.parts[0].inline_data.data
            wav_data = create_wav_file(audio_bytes)
            with open(file_path, "wb") as f:
                f.write(wav_data)
            return wav_data
        except Exception as e:
            continue # Try next model if this one fails
            
    st.error("All audio models failed. Please check your Google Cloud Billing Tier.")
    return None

# 4. Sidebar: Library Builder (Same logic, better engine)
with st.sidebar:
    st.header("⚙️ Library Sync")
    if st.button("🚀 1. Build All Foundation Files"):
        with st.status("Generating Armenian Audio..."):
            for slug, data in FOUNDATIONS.items():
                get_audio(data['text'], slug, slow_mode=False)
                get_audio(data['text'], slug, slow_mode=True)
            st.success("All Foundation files generated!")

    st.divider()
    
    # ZIP Logic
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        file_count = 0
        if os.path.exists(AUDIO_DIR):
            for f_name in os.listdir(AUDIO_DIR):
                if f_name.endswith(".wav"):
                    with open(os.path.join(AUDIO_DIR, f_name), "rb") as f:
                        zip_file.writestr(f_name, f.read())
                        file_count += 1
    
    if file_count > 0:
        st.download_button(
            label=f"📥 2. Download {file_count} Files as ZIP",
            data=zip_buffer.getvalue(),
            file_name="armenian_foundations.zip",
            mime="application/zip",
            use_container_width=True
        )

# 5. Main Lesson Area
main_mode = st.selectbox("Category:", ["Foundations", "Phrase Translator"])
slow_audio = st.toggle("🐢 Slow-Motion Audio", value=False)

if main_mode == "Foundations":
    sub_sel = st.selectbox("Selection:", list(FOUNDATIONS.keys()), format_func=lambda x: FOUNDATIONS[x]['label'])
    content = FOUNDATIONS[sub_sel]
    st.write(f"### {content['text']}")
    if st.button("🔊 Listen"):
        audio = get_audio(content['text'], sub_sel, slow_mode=slow_audio)
        if audio: st.audio(audio, format="audio/wav", autoplay=True)
