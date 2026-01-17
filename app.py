import streamlit as st
from google import genai
from google.genai import types
import wave
import io
import time

st.set_page_config(page_title="HyeTutor Surgical Builder", page_icon="🇦🇲")
st.title("🇦🇲 Surgical Audio Builder")
st.write("Current approach: Build → Listen → Download → Upload to GitHub.")

# 1. API Setup
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. Targeted Foundation List
TARGETS = {
    "numbers_11_20": "Տասնըմէկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան",
    "tens_to_100": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր",
    "hundreds_to_1000": "Հարիւր, Երկու հարիւր, Երեք հարիւր, Չորս հարիւր, Հինգ հարիւր, Վեց հարիւր, Եօթը հարիւր, Ութը հարիւր, Ինը հարիւր, Հազար",
    "months_of_the_year_slow": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

selection = st.selectbox("Select Target to Build:", list(TARGETS.keys()))
slow_mode = st.toggle("Slow-Motion Version", value=True)

def create_wav(pcm_data):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
        wf.writeframes(pcm_data)
    return buf.getvalue()

if st.button(f"🚀 Generate {selection}"):
    with st.spinner("Calling Google AI..."):
        try:
            # We split long lists like months into 2 parts automatically to prevent timeouts
            text = TARGETS[selection]
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=f"Say this {'slowly' if slow_mode else 'clearly'} in Western Armenian: {text}",
                config=types.GenerateContentConfig(response_modalities=["AUDIO"])
            )
            
            if response.candidates and response.candidates[0].content:
                audio_data = response.candidates[0].content.parts[0].inline_data.data
                wav_file = create_wav(audio_data)
                
                # Show results
                st.audio(wav_file)
                st.download_button(
                    label="📥 Save to Hard Drive",
                    data=wav_file,
                    file_name=f"{selection}_{'slow' if slow_mode else 'fast'}.wav",
                    mime="audio/wav"
                )
                st.success("Build Successful! Download the file now.")
            else:
                st.error("Google returned an empty file. Wait 60 seconds and try again.")
        except Exception as e:
            st.error(f"API Error: {e}")
