import streamlit as st
from google import genai
from google.genai import types
import wave
import io
import os
import zipfile
import shutil
import time

# 1. Page Configuration
st.set_page_config(page_title="HyeTutor2.0beta", page_icon="🇦🇲", layout="wide")

st.title("🇦🇲 HyeTutor2.0beta")
st.caption("Version 6.1 • Expanded Numbers • Multi-File Builder")

# --- AUDIO LIBRARY SETUP ---
AUDIO_DIR = "audio_library"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# --- EXPANDED PERMANENT DATA ---
FOUNDATIONS = {
    "days_of_the_week": {
        "label": "📅 Days of the Week",
        "text": "Երկուշաբթի, Երեքշաբթի, Չորեքշաբթի, Հինգշաբթի, Ուրբաթ, Շաբաթ, Կիրակի"
    },
    "numbers_1_10": {
        "label": "🔢 Numbers (1-10)",
        "text": "Մէկ, Երկու, Երեք, Չորս, Հինգ, Վեց, Եօթը, Ութը, Ինը, Տասը"
    },
    "numbers_11_20": {
        "label": "🔢 Numbers (11-20)",
        "text": "Տասնըմէկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան"
    },
    "tens_to_100": {
        "label": "🔟 Counting by 10s (to 100)",
        "text": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր"
    },
    "hundreds_to_1000": {
        "label": "💯 Counting by 100s (to 1000)",
        "text": "Հարիւր, Երկու հարիւր, Երեք հարիւր, Չորս հարիւր, Հինգ հարիւր, Վեց հարիւր, Եօթը հարիւր, Ութը հարիւր, Ինը հարիւր, Հազար"
    },
    "months_of_the_year": {
        "label": "🗓️ Months of the Year",
        "text": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
    }
}

# 2. Key Verification
api_key = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=api_key)

# 3. ROBUST AUDIO ENGINE
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

    speed_instr = "slowly" if slow_mode else "clearly"
    
    # Chunking logic for longer strings (like Months or 100s)
    words = text_to_speak.split(", ")
    chunks = [", ".join(words[i:i+5]) for i in range(0, len(words), 5)]
    
    combined_pcm = b""
    for chunk in chunks:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-preview-tts",
                    contents=f"Say this {speed_instr} in Western Armenian: {chunk}",
                    config=types.GenerateContentConfig(response_modalities=["AUDIO"])
                )
                if response.candidates and response.candidates[0].content:
                    combined_pcm += response.candidates[0].content.parts[0].inline_data.data
                    break
                time.sleep(1)
            except:
                time.sleep(1)
    
    if combined_pcm:
        wav_data = create_wav_file(combined_pcm)
        with open(file_path, "wb") as f: f.write(wav_data)
        return wav_data
    return None

# 4. Sidebar: Multi-File Builder
with st.sidebar:
    st.header("⚙️ Library Tools")
    
    if st.button("🔴 Reset & Clear"):
        if os.path.exists(AUDIO_DIR): shutil.rmtree(AUDIO_DIR)
        os.makedirs(AUDIO_DIR)
        st.success("Clean Slate!")

    if st.button("🚀 Build All 10 Files"):
        with st.status("Generating Numbers and Foundations..."):
            for slug, data in FOUNDATIONS.items():
                get_audio(data['text'], slug, slow_mode=False)
                get_audio(data['text'], slug, slow_mode=True)
        st.success("All 10 audio files (Fast & Slow) are ready!")

    st.divider()
    
    # Zip Downloader for 10 pairs (20 total files)
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
            label=f"📥 Download Full Library ({file_count} files)",
            data=zip_buffer.getvalue(),
            file_name="armenian_foundations_full.zip",
            mime="application/zip",
            use_container_width=True
        )

# 5. Lessons
main_mode = st.selectbox("Category:", ["Foundations", "Phrase Translator"])
slow_audio = st.toggle("🐢 Slow-Motion Audio", value=False)

if main_mode == "Foundations":
    sub_sel = st.selectbox("Selection:", list(FOUNDATIONS.keys()), format_func=lambda x: FOUNDATIONS[x]['label'])
    content = FOUNDATIONS[sub_sel]
    st.write(f"### {content['text']}")
    if st.button("🔊 Listen"):
        audio = get_audio(content['text'], sub_sel, slow_mode=slow_audio)
        if audio: st.audio(audio, format="audio/wav", autoplay=True)
