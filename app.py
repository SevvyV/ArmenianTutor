import streamlit as st
from google import genai
from google.genai import types
import wave
import io

st.title("🛠️ Months-of-the-Year Fixer")

# 1. API Setup
api_key = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=api_key)

# 2. The Missing Content
TEXT = "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
FILENAME = "months_of_the_year_slow.wav"

def create_wav(pcm_data):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) 
        wf.setframerate(24000)
        wf.writeframes(pcm_data)
    return buf.getvalue()

st.write(f"Click the button to generate: **{FILENAME}**")

if st.button("Generate Audio"):
    try:
        # Using the specific TTS model that worked for the other 5
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=f"Say this slowly and clearly in Western Armenian: {TEXT}",
            config=types.GenerateContentConfig(response_modalities=["AUDIO"])
        )
        
        if response.candidates and response.candidates[0].content:
            audio_bytes = response.candidates[0].content.parts[0].inline_data.data
            wav_data = create_wav(audio_bytes)
            
            st.audio(wav_data)
            st.download_button("📥 Download Missing File", wav_data, file_name=FILENAME)
            st.success("Success! Download it now.")
        else:
            st.error("Google returned an empty file. Try clicking again.")
    except Exception as e:
        st.error(f"Error: {e}")
