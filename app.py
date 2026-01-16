import streamlit as st
from google import genai
from google.genai import types
import wave
import io
import os
import zipfile
import time

st.set_page_config(page_title="HyeTutor2.0beta", page_icon="🇦🇲", layout="wide")
st.title("🇦🇲 HyeTutor2.0beta")
st.caption("Version 6.5 • Gentle Builder • Safety & Quota Fix")

# --- AUDIO LIBRARY SETUP ---
AUDIO_DIR = "audio_library"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

FOUNDATIONS = {
    "days_of_the_week": {"label": "📅 Days of the Week", "text": "Երկուշաբթի, Երեքշաբթի, Չորեքշաբթի, Հինգշաբթի, Ուրբաթ, Շաբաթ, Կիրակի"},
    "numbers_1_10": {"label": "🔢 Numbers (1-10)", "text": "Մէկ, Երկու, Երեք, Չորս, Հինգ, Վեց, Եօթը, Ութը, Ինը, Տասը"},
    "numbers_11_20": {"label": "🔢 Numbers (11-20)", "text": "Տասնմեկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան"},
    "tens_to_100": {"label": "🔟 Counting by 10s", "text": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր"},
    "hundreds_to_1000": {"label": "💯 Counting by 100s", "text": "Հարիւր, Երկու հարիւր, Երեք հարիւր, Չորս հարիւր, Հինգ հարիւր, Վեց հարիւր, Եօթը հարիւր, Ութը հարիւր, Ինը հարիւր, Հազար"},
    "months_of_the_year": {"label": "🗓️ Months", "text": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"}
}

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

def get_audio(text_to_speak, slug, slow_mode=False):
    filename = f"{slug}_{'slow' if slow_mode else 'fast'}.wav"
    file_path = os.path.join(AUDIO_DIR, filename)

    if os.path.isfile(file_path):
        with open(file_path, "rb") as f: return f.read()

    speed_instr = "slowly" if slow_mode else "clearly"
    words = text_to_speak.split(", ")
    chunks = [", ".join(words[i:i+3]) for i in range(0, len(words), 3)]
    
    combined_pcm = b""
    for chunk in chunks:
        # Added delay to respect API Rate Limits
        time.sleep(3) 
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=f"Say this {speed_instr} in Western Armenian: {chunk}",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    # Disable safety filters for dictionary words to prevent 400 Errors
                    safety_settings=[{"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"}]
                )
            )
            if response.candidates and response.candidates[0].content:
                combined_pcm += response.candidates[0].content.parts[0].inline_data.data
        except Exception as e:
            st.warning(f"Skipping a chunk due to API limit: {e}")
            continue
    
    if combined_pcm:
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
            wf.writeframes(combined_pcm)
        wav_data = buf.getvalue()
        with open(file_path, "wb") as f: f.write(wav_data)
        return wav_data
    return None

with st.sidebar:
    st.header("⚙️ Library Tools")
    if st.button("🚀 Build All Missing Files"):
        with st.status("Building library (this will take 2-3 minutes)..."):
            for slug, data in FOUNDATIONS.items():
                st.write(f"Checking {data['label']}...")
                get_audio(data['text'], slug, False)
                get_audio(data['text'], slug, True)
        st.success("Build Process Finished!")
        st.rerun()

    existing_files = os.listdir(AUDIO_DIR) if os.path.exists(AUDIO_DIR) else []
    if existing_files:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a") as zf:
            for f in existing_files:
                with open(os.path.join(AUDIO_DIR, f), "rb") as audio_f:
                    zf.writestr(f, audio_f.read())
        st.download_button(f"📥 Download ZIP ({len(existing_files)} files)", zip_buffer.getvalue(), "armenian_library.zip")
