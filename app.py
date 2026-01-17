import streamlit as st
from google import genai
from google.genai import types
import wave
import io

st.set_page_config(page_title="HyeTutor Backdoor Builder 8.8", page_icon="🇦🇲")
st.title("🇦🇲 Audio Builder 8.8 (Standard Model)")
st.info("Switching to the High-Limit Standard Model to bypass the 'Preview' block.")

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = None
if "active_filename" not in st.session_state:
    st.session_state.active_filename = ""

TARGETS = {
    "numbers_11_20": "Տասնըմէկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան",
    "tens_to_100": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր",
    "months_of_the_year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

selection = st.selectbox("1. Select Category", list(TARGETS.keys()))

if st.button("🚀 Emergency Build"):
    st.session_state.audio_buffer = None
    
    with st.status("Attempting Standard Model Build...") as status:
        try:
            # SWITCHING MODEL: Using the standard stable flash instead of preview-tts
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=f"Please provide an audio recording of these words in Western Armenian: {TARGETS[selection]}",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"]
                )
            )
            
            if response.candidates and response.candidates[0].content:
                audio_part = next((p for p in response.candidates[0].content.parts if p.inline_data), None)
                
                if audio_part:
                    buf = io.BytesIO()
                    with wave.open(buf, 'wb') as wf:
                        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
                        wf.writeframes(audio_part.inline_data.data)
                    
                    st.session_state.audio_buffer = buf.getvalue()
                    st.session_state.active_filename = f"{selection}.wav"
                    status.update(label="✅ Success!", state="complete")
                else:
                    status.update(label="❌ This model didn't return audio. It might be text-only today.", state="error")
            else:
                st.error("Still getting 'No Response'. This confirms a 24-hour account lockout.")
                
        except Exception as e:
            st.error(f"Critical Error: {e}")

if st.session_state.audio_buffer:
    st.audio(st.session_state.audio_buffer)
    st.download_button("💾 DOWNLOAD FILE", st.session_state.audio_buffer, st.session_state.active_filename)
