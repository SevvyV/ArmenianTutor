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
st.caption("Version 6.7 • Brute Force Mode • Safety Fix Applied")

# --- AUDIO LIBRARY SETUP ---
AUDIO_DIR = "audio_library"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# --- THE DATASET ---
FOUNDATIONS = {
    "days_of_the_week": "Երկուշաբթի, Երեքշաբթի, Չորեքշաբթի, Հինգշաբթի, Ուրբաթ, Շաբաթ, Կիրակի",
    "numbers_1_10": "Մէկ, Երկու, Երեք, Չորս, Հինգ, Վեց, Եօթը, Ութը, Ինը, Տասը",
    "numbers_11_20": "Տասնըմէկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան",
    "tens_to_100": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր",
    "hundreds_to_1000": "Հարիւր, Երկու հարիւր, Երեք հարիւր, Չորս հարիւր, Հինգ հարիւր, Վեց հարիւր, Եօթը հարիւր, Ութը հարիւր, Ինը հարիւր, Հազար",
    "months_of_the_year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

def build_single_file(text, slug, slow):
    speed_tag = "slow" if slow else "fast"
    filename = f"{slug}_{speed_tag}.wav"
    file_path = os.path.join(AUDIO_DIR, filename)
    
    try:
        # Use the formal category names to satisfy the Pydantic validator
        safety_settings = [
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE")
        ]
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=f"Say this {'slowly' if slow else 'clearly'} in Western Armenian: {text}",
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                safety_settings=safety_settings
            )
        )
        
        if response.candidates and response.candidates[0].content:
            audio_bytes = response.candidates[0].content.parts[0].inline_data.data
            buf = io.BytesIO()
            with wave.open(buf, 'wb') as wf:
                wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
                wf.writeframes(audio_bytes)
            
            with open(file_path, "wb") as f:
                f.write(buf.getvalue())
            return True
    except Exception as e:
        st.error(f"Error building {filename}: {e}")
    return False

# --- THE CONTROL PANEL ---
st.header("🛠️ Brute Force Construction Site")
st.write("Click each button one at a time. The page will refresh and show a green check when done.")

# Create a grid of buttons
for slug, text in FOUNDATIONS.items():
    st.subheader(slug.replace("_", " ").title())
    c1, c2 = st.columns(2)
    
    # FAST BUTTON
    f_name = f"{slug}_fast.wav"
    with c1:
        if os.path.exists(os.path.join(AUDIO_DIR, f_name)):
            st.success(f"✅ Fast Ready")
        elif st.button(f"Build Fast: {slug}"):
            if build_single_file(text, slug, False):
                st.rerun()
                
    # SLOW BUTTON
    s_name = f"{slug}_slow.wav"
    with c2:
        if os.path.exists(os.path.join(AUDIO_DIR, s_name)):
            st.success(f"✅ Slow Ready")
        elif st.button(f"Build Slow: {slug}"):
            if build_single_file(text, slug, True):
                st.rerun()
    st.divider()

# --- EXPORT ---
with st.sidebar:
    st.header("📦 Library Export")
    existing = [f for f in os.listdir(AUDIO_DIR) if f.endswith(".wav")]
    st.write(f"Files Generated: **{len(existing)} / 12**")
    
    if existing:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "a") as zf:
            for f in existing:
                with open(os.path.join(AUDIO_DIR, f), "rb") as audio_f:
                    zf.writestr(f, audio_f.read())
        st.download_button("📥 Download ZIP", zip_buf.getvalue(), "armenian_library.zip", use_container_width=True)

    if st.button("🔴 Reset/Empty Folder"):
        for f in os.listdir(AUDIO_DIR):
            os.remove(os.path.join(AUDIO_DIR, f))
        st.rerun()
