import streamlit as st
from google import genai
from google.genai import types
import wave
import io

st.set_page_config(page_title="Surgical Builder 12.0 (Stable)", page_icon="🇦🇲")
st.title("🇦🇲 Surgical Audio Builder 12.0")
st.info("Architecture: Stable V1 API | Model: Gemini 3 Flash")

# 1. API Setup - PINNED TO STABLE V1
client = genai.Client(
    api_key=st.secrets["GOOGLE_API_KEY"],
    http_options=types.HttpOptions(api_version="v1") # Bypasses v1beta
)

if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = None

TARGETS = {
    "numbers_11_20": "Տասնըմէկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան",
    "tens_to_100": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր",
    "hundreds_to_1000": "Հարիւր, Երկու հարիւր, Երեք հարիւր, Չորս հարիւր, Հինգ հարիւր, Վեց հարիւր, Եօթը հարիւր, Ութը հարիւր, Ինը հարիւր, Հազար",
    "months_of_the_year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Ութը հարիւր, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

selection = st.selectbox("Select Target Category", list(TARGETS.keys()))

if st.button("🚀 Generate Stable Audio"):
    st.session_state.audio_buffer = None
    with st.status("Requesting Stable V1 Audio Pipe...") as status:
        try:
            # GEMINI 3 FLASH: The production-ready multimodal model
            response = client.models.generate_content(
                model="gemini-3-flash", 
                contents=f"Say these Armenian words clearly and distinctly: {TARGETS[selection]}",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"]
                )
            )
            
            # Extract and package
            if response.candidates and response.candidates[0].content:
                # Look for the audio data part
                audio_part = next((p for p in response.candidates[0].content.parts if p.inline_data), None)
                
                if audio_part:
                    # Package as 24kHz Mono WAV
                    buf = io.BytesIO()
                    with wave.open(buf, 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(24000)
                        wf.writeframes(audio_part.inline_data.data)
                    
                    st.session_state.audio_buffer = buf.getvalue()
                    status.update(label="✅ Audio Generated Successfully", state="complete")
                else:
                    st.error("Audio stream was empty. Please check your project's audio quota.")
            else:
                st.error("No response candidates found. The stable model might be throttled.")
                
        except Exception as e:
            st.error(f"Stable V1 Failure: {e}")

if st.session_state.audio_buffer:
    st.divider()
    st.audio(st.session_state.audio_buffer)
    st.download_button(
        "💾 SAVE TO DOWNLOADS", 
        st.session_state.audio_buffer, 
        f"{selection}.wav",
        mime="audio/wav",
        use_container_width=True
    )
