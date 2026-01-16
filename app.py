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
st.caption("Version 6.8 • Brute Force Manual Mode • Quota Recovery")

# --- AUDIO LIBRARY SETUP ---
AUDIO_DIR = "audio_library"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

FOUNDATIONS = {
    "days_of_the_week": "Երկուշաբթի, Երեքշաբթի, Չորեքշաբթի, Հինգշաբթի, Ուրբաթ, Շաբաթ, Կիրակի",
    "numbers_1_10": "Մէկ, Երկու, Երեք, Չորս, Հինգ, Վեց, Եօթը, Ութը, Ինը, Տասը",
    "numbers_11_20": "Տասնմեկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան",
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
        # SWITCHING TO STANDARD FLASH (More stable quota)
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=f"Provide audio of these words spoken {'slowly' if slow else 'clearly'} in Western Armenian: {text}",
            config=types.GenerateContentConfig(response_modalities=["AUDIO"])
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
        st.error(f"Quota Error for {filename}. Wait 60 seconds. Details: {e}")
    return False

# --- UI CONTROL PANEL ---
st.header("⚒️ Manual Construction Site")
st.warning("Google has throttled your requests. You MUST wait 30-60 seconds between clicks.")

for slug, text in FOUNDATIONS.items():
    st.subheader(slug.replace("_", " ").title())
    c1, c2 = st.columns(2)
    
    with c1:
        f_path = os.path.join(AUDIO_DIR, f"{slug}_fast.wav")
        if os.path.exists(f_path):
            st.success("✅ Fast Ready")
            st.audio(f_path)
        else:
            if st.button(f"Generate Fast: {slug}"):
                if build_single_file(text, slug, False): st.rerun()
                
    with c2:
        s_path = os.path.join(AUDIO_DIR, f"{slug}_slow.wav")
        if os.path.exists(s_path):
            st.success("✅ Slow Ready")
            st.audio(s_path)
        else:
            if st.button(f"Generate Slow: {slug}"):
                if build_single_file(text, slug, True): st.rerun()
    st.divider()

# --- EXPORT ---
with st.sidebar:
    existing = [f for f in os.listdir(AUDIO_DIR) if f.endswith(".wav")]
    st.metric("Library Progress", f"{len(existing)} / 12")
    
    if existing:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "a") as zf:
            for f in existing:
                with open(os.path.join(AUDIO_DIR, f), "rb") as audio_f:
                    zf.writestr(f, audio_f.read())
        st.download_button("📥 Download Final ZIP", zip_buf.getvalue(), "armenian_library.zip", use_container_width=True)
