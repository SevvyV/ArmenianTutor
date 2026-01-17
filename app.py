import streamlit as st
from google import genai
from google.genai import types
import wave
import io

st.set_page_config(page_title="HyeTutor Surgical Builder 8.4", page_icon="🇦🇲")
st.title("🇦🇲 Surgical Audio Builder 8.4")

# 1. API Setup
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. Initialize Session State for the audio file
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

# --- GENERATION LOGIC ---
if st.button(f"🚀 Generate {selection}"):
    with st.spinner(f"Requesting {selection} from Google..."):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=f"Say this {'slowly' if slow_mode else 'clearly'} in Western Armenian: {TARGETS[selection]}",
                config=types.GenerateContentConfig(response_modalities=["AUDIO"])
            )
            
            if response.candidates and response.candidates[0].content:
                raw_data = response.candidates[0].content.parts[0].inline_data.data
                # Store the result in Session State so it persists
                st.session_state.current_audio = create_wav(raw_data)
                st.session_state.current_filename = f"{selection}_{'slow' if slow_mode else 'fast'}.wav"
                st.success("Generation Complete! Use the player and button below.")
            else:
                st.error("AI returned empty data.")
        except Exception as e:
            st.error(f"Build Failed: {e}")

# --- PERSISTENT UI ---
# This part stays on the screen as long as current_audio isn't empty
if st.session_state.current_audio:
    st.divider()
    st.write(f"### Ready: {st.session_state.current_filename}")
    st.audio(st.session_state.current_audio)
    
    st.download_button(
        label="💾 Save to Hard Drive",
        data=st.session_state.current_audio,
        file_name=st.session_state.current_filename,
        mime="audio/wav",
        key="download_btn" # Unique key ensures it doesn't vanish
    )
