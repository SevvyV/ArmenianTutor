import streamlit as st
from google import genai
from google.genai import types
import wave
import io

st.set_page_config(page_title="HyeTutor Surgical 10.0", page_icon="🇦🇲")
st.title("🇦🇲 Surgical Audio Builder 10.0")

# 1. API Setup
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

selection = st.selectbox("1. Category", list(TARGETS.keys()))

if st.button("🚀 Build Audio"):
    st.session_state.audio_buffer = None
    with st.status("Initializing High-Fidelity Voice Engine...") as status:
        try:
            # We use the GA (Generally Available) stable model 
            # and specify the modality in the config.
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=f"Read this Western Armenian text slowly and clearly: {TARGETS[selection]}",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    # Adding speech_config forces the engine to wake up the TTS module
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Puck" # Stable, high-quality voice
                            )
                        )
                    )
                )
            )
            
            # Diagnostic: Print the finish reason if it fails
            if response.candidates and response.candidates[0].finish_reason != "STOP":
                st.error(f"Generation Interrupted: {response.candidates[0].finish_reason}")
            
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
                st.error("Empty audio stream. The engine is active but the buffer is 0 bytes.")
                
        except Exception as e:
            st.error(f"Architectural Failure: {e}")

if st.session_state.audio_buffer:
    st.divider()
    st.audio(st.session_state.audio_buffer)
    st.download_button("💾 DOWNLOAD WAV", st.session_state.audio_buffer, st.session_state.active_filename)
