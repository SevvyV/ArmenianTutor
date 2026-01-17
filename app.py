import streamlit as st
from google import genai
from google.genai import types
import wave
import io
import time

st.set_page_config(page_title="HyeTutor Surgical Builder 8.1", page_icon="🇦🇲")
st.title("🇦🇲 Surgical Audio Builder 8.1")

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
    with st.status(f"Generating {selection}...") as status:
        text = TARGETS[selection]
        success = False
        
        # Automatic Retry Loop (2 Attempts)
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-preview-tts",
                    contents=f"Say this {'slowly' if slow_mode else 'clearly'} in Western Armenian: {text}",
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        # FIX: Disable safety blocks for vocabulary lists
                        safety_settings=[{"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}],
                        # FIX: Give the server more time
                        candidate_count=1
                    )
                )
                
                if response.candidates and response.candidates[0].content:
                    audio_data = response.candidates[0].content.parts[0].inline_data.data
                    if len(audio_data) > 44: # Check if it's more than just a header
                        wav_file = create_wav(audio_data)
                        st.audio(wav_file)
                        st.download_button("📥 Save to Hard Drive", wav_file, file_name=f"{selection}.wav")
                        status.update(label="Build Successful!", state="complete")
                        success = True
                        break
                
                status.write(f"Attempt {attempt+1} returned empty. Retrying in 5 seconds...")
