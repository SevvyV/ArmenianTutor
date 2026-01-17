import streamlit as st
from google import genai
from google.genai import types
import wave
import io
import time

st.set_page_config(page_title="HyeTutor Surgical Builder 8.5", page_icon="🇦🇲")
st.title("🇦🇲 Surgical Audio Builder 8.5")

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

if "current_audio" not in st.session_state:
    st.session_state.current_audio = None
if "current_filename" not in st.session_state:
    st.session_state.current_filename = ""

TARGETS = {
    "numbers_11_20": "Տասնըմէկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան",
    "tens_to_100": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր",
    "hundreds_to_1000": "Հարիւր, Երկու հարիւր, Երեք հարիւր, Չորս հարիւր, Հինգ հարիւր, Վեց հարիւր, Եօթը հարիւր, Ութը հարիւր, Ինը հարիւր, Հազար",
    "months_of_the_year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

selection = st.selectbox("Select Target:", list(TARGETS.keys()))
slow_mode = st.toggle("Slow-Motion Version", value=True)

def create_wav(pcm_data):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
        wf.writeframes(pcm_data)
    return buf.getvalue()

if st.button(f"🚀 Generate {selection}"):
    with st.status(f"Requesting {selection}...") as status:
        # STEP 1: Clear previous state
        st.session_state.current_audio = None
        
        # STEP 2: The "Model Cycle" - Try Preview first, then Stable
        models_to_try = ["gemini-2.5-flash-preview-tts", "gemini-2.5-flash"]
        
        for model_choice in models_to_try:
            try:
                status.write(f"Testing model: {model_choice}...")
                response = client.models.generate_content(
                    model=model_choice,
                    contents=f"Please speak these words {'slowly' if slow_mode else 'clearly'} in Western Armenian: {TARGETS[selection]}",
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        safety_settings=[{"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}]
                    )
                )
                
                if response.candidates and response.candidates[0].content:
                    parts = response.candidates[0].content.parts
                    # Look for the first part that actually contains audio data
                    audio_part = next((p for p in parts if p.inline_data), None)
                    
                    if audio_part and len(audio_part.inline_data.data) > 200:
                        st.session_state.current_audio = create_wav(audio_part.inline_data.data)
                        st.session_state.current_filename = f"{selection}_{'slow' if slow_mode else 'fast'}.wav"
                        status.update(label="✅ Success!", state="complete")
                        break
                
                status.write(f"⚠️ {model_choice} returned empty audio. Trying next model...")
                time.sleep(2)
            except Exception as e:
                status.write(f"❌ {model_choice} failed: {e}")

# --- PERSISTENT UI ---
if st.session_state.current_audio:
    st.divider()
    st.audio(st.session_state.current_audio)
    st.download_button(
        label="💾 SAVE TO COMPUTER",
        data=st.session_state.current_audio,
        file_name=st.session_state.current_filename,
        mime="audio/wav"
    )
    st.success(f"File ready for your hard drive: {st.session_state.current_filename}")
elif not st.session_state.current_audio:
    st.warning("No file generated yet. Select a category and click 'Generate'.")
