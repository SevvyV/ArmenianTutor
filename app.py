import streamlit as st
from google import genai
from google.genai import types
import wave
import io

st.set_page_config(page_title="HyeTutor Surgical 12.1", page_icon="🇦🇲")
st.title("🇦🇲 Surgical Audio Builder 12.1")
st.info("Architecture: Stable V1 API | Model: Gemini 2.5 Flash")

# 1. API Setup - Corrected for Stable V1 without AttributeError
# Passing http_options as a dictionary is the SDK-recommended stable path
client = genai.Client(
    api_key=st.secrets["GOOGLE_API_KEY"],
    http_options={'api_version': 'v1'} 
)

if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = None

TARGETS = {
    "numbers_11_20": "Տասնըմէկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան",
    "tens_to_100": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր",
    "months_of_the_year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

selection = st.selectbox("Select Category", list(TARGETS.keys()))

if st.button("🚀 Generate Audio"):
    st.session_state.audio_buffer = None
    with st.status("Building via Stable V1...") as status:
        try:
            # Using the stable 2.5-flash which is GA for audio modalities
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=f"Say these Western Armenian words clearly: {TARGETS[selection]}",
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
                    status.update(label="✅ Success!", state="complete")
                else:
                    st.error("Engine failure: No audio data in stable response.")
            else:
                st.error("No response from model. Project may be restricted.")
                
        except Exception as e:
            st.error(f"V1 Execution Error: {e}")

if st.session_state.audio_buffer:
    st.divider()
    st.audio(st.session_state.audio_buffer)
    st.download_button("💾 DOWNLOAD WAV", st.session_state.audio_buffer, f"{selection}.wav")
