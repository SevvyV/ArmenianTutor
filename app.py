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
st.caption("Version 7.3 • Seamless Chunked Audio • Quota Protection")

AUDIO_DIR = "audio_library"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

FOUNDATIONS = {
    "days_of_the_week": "Երկուշաբթի, Երեքշաբթի, Չորեքշաբթի, Հինգշաբթի, Ուրբաթ, Շաբաթ, Կիրակի",
    "numbers_1_10": "Մէկ, Երկու, Երեք, Չորս, Հինգ, Վեց, Եօթը, Ութը, Ինը, Տասը",
    "numbers_11_20": "Տասնըմէկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան",
    "tens_to_100": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր",
    "hundreds_to_1000": "Հարիւր, Երկու հարիւր, Երեք հարիւր, Չորս հարիւր, Հինգ հարիւր, Վեց հարիւր, Եօթը հարիւր, Ութը հարիւր, Ինը հարիւր, Հազար",
    "months_of_the_year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

def build_chunked_audio(text_list, slug, slow):
    speed_tag = "slow" if slow else "fast"
    filename = f"{slug}_{speed_tag}.wav"
    file_path = os.path.join(AUDIO_DIR, filename)
    
    # Split the text into chunks of 5 items each to prevent truncation
    words = text_list.split(", ")
    chunks = [", ".join(words[i:i+5]) for i in range(0, len(words), 5)]
    
    combined_pcm = b""
    
    for i, chunk in enumerate(chunks):
        try:
            # We use the TTS specific model for the best Western Armenian accent
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=f"Say this {'slowly' if slow else 'clearly'} in Western Armenian: {chunk}",
                config=types.GenerateContentConfig(response_modalities=["AUDIO"])
            )
            
            if response.candidates and response.candidates[0].content:
                # Add the raw audio data from this chunk to our master list
                combined_pcm += response.candidates[0].content.parts[0].inline_data.data
                # Small pause (0.5s) between chunks for natural flow
                combined_pcm += b'\x00' * 12000 
                time.sleep(2) # Prevent RPD/RPM limits
            else:
                st.error(f"Failed to generate audio for chunk {i+1}")
                return False
        except Exception as e:
            st.error(f"Error at chunk {i+1}: {e}")
            return False

    if combined_pcm:
        # Wrap the raw PCM data in a proper WAV header
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
            wf.writeframes(combined_pcm)
        
        with open(file_path, "wb") as f:
            f.write(buf.getvalue())
        return True
    return False

# --- UI CONTROL PANEL ---
st.header("⚒️ Smart Library Builder")
st.info("Long lists are now generated in 'chunks' to ensure they don't cut off.")

for slug, text in FOUNDATIONS.items():
    st.subheader(slug.replace("_", " ").title())
    c1, c2 = st.columns(2)
    
    with c1:
        f_name = f"{slug}_fast.wav"
        if os.path.isfile(os.path.join(AUDIO_DIR, f_name)):
            st.success(f"✅ Fast Ready"); st.audio(os.path.join(AUDIO_DIR, f_name))
        else:
            if st.button(f"Build {f_name}"):
                if build_chunked_audio(text, slug, False): st.rerun()
                
    with c2:
        s_name = f"{slug}_slow.wav"
        if os.path.isfile(os.path.join(AUDIO_DIR, s_name)):
            st.success(f"✅ Slow Ready"); st.audio(os.path.join(AUDIO_DIR, s_name))
        else:
            if st.button(f"Build {s_name}"):
                if build_chunked_audio(text, slug, True): st.rerun()
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
        st.download_button("📥 Download ZIP", zip_buf.getvalue(), "armenian_library.zip", use_container_width=True)
