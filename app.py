import streamlit as st
from google import genai
from google.genai import types
import wave
import io
import os
import zipfile
import time

# 1. Page Configuration
st.set_page_config(page_title="HyeTutor2.0beta", page_icon="🇦🇲", layout="wide")

st.title("🇦🇲 HyeTutor2.0beta")
st.caption("Version 5.9 • Auto-Retry Logic • Stable TTS")

# --- AUDIO LIBRARY SETUP ---
AUDIO_DIR = "audio_library"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# --- PERMANENT DATA ---
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

# 3. ROBUST AUDIO ENGINE (With Retry Logic)
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

    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return f.read()

    # RETRY LOGIC: Try up to 3 times if the API returns None
    for attempt in range(3):
        try:
            speed_instr = "slowly" if slow_mode else "clearly"
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=f"Say this {speed_instr} in Western Armenian: {text_to_speak}",
                config=types.GenerateContentConfig(response_modalities=["AUDIO"])
            )
            
            # THE SAFETY CHECK: Ensure response.candidates[0].content is NOT None
            if response.candidates and response.candidates[0].content:
                audio_bytes = response.candidates[0].content.parts[0].inline_data.data
                wav_data = create_wav_file(audio_bytes)
                with open(file_path, "wb") as f:
                    f.write(wav_data)
                return wav_data
            else:
                time.sleep(1) # Wait 1 second before retrying
                continue
        except Exception:
            time.sleep(1)
            continue
            
    return None

# 4. Sidebar: Same logic as before
with st.sidebar:
    st.header("⚙️ Library Sync")
    if st.button("🚀 1. Build Foundations (with Retry)"):
        with st.status("Generating Armenian Audio..."):
            for slug, data in FOUNDATIONS.items():
                get_audio(data['text'], slug, slow_mode=False)
                get_audio(data['text'], slug, slow_mode=True)
            st.success("Foundation library build attempted!")

    st.divider()
    
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
            file_name="armenian_foundations_v59.zip",
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
