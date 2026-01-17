import streamlit as st
from google import genai
from google.genai import types
import wave
import io

st.set_page_config(page_title="Surgical Builder 9.2", page_icon="🇦🇲")
st.title("🇦🇲 Surgical Audio Builder 9.2")
st.info("Status: Routing to Gemini 2.5 Flash Preview TTS")

# 1. API Setup
# This will pick up your NEW key from the Streamlit Secrets (Dev app)
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = None
if "active_filename" not in st.session_state:
    st.session_state.active_filename = ""

TARGETS = {
    "numbers_11_20": "Տասնըմէկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան",
    "tens_to_100": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր",
    "hundreds_to_1000": "Հարիւր, Երկու հարիւր, Երեք հարիւր, Չորս հարիւր, Հինգ հարիւր, Վեց հարիւր, Եօթը հարիւր, Ութը հարիւր, Ինը հարիւր, Հազար",
    "months_of_the_year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

selection = st.selectbox("1. Select Target Category", list(TARGETS.keys()))
slow_mode = st.toggle("2. Slow-Motion Mode", value=True)

if st.button("🚀 3. Generate Audio File"):
    st.session_state.audio_buffer = None
    
    with st.status("Requesting Audio Generation...") as status:
        try:
            # THE CORRECT ID: gemini-2.5-flash-preview-tts
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts", 
                contents=f"Speak these Western Armenian words {'slowly' if slow_mode else 'clearly'}: {TARGETS[selection]}",
                config=types.GenerateContentConfig(response_modalities=["AUDIO"])
            )
            
            if response.candidates and response.candidates[0].content:
                audio_part = next((p for p in response.candidates[0].content.parts if p.inline_data), None)
                
                if audio_part:
                    buf = io.BytesIO()
                    with wave.open(buf, 'wb') as wf:
                        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
                        wf.writeframes(audio_part.inline_data.data)
                    
                    st.session_state.audio_buffer = buf.getvalue()
                    st.session_state.active_filename = f"{selection}_{'slow' if slow_mode else 'fast'}.wav"
                    status.update(label="✅ Success!", state="complete")
                else:
                    st.error("AI returned text but no audio. Check modality support.")
            else:
                st.error("No response from model. Project or key may be inactive.")
                
        except Exception as e:
            st.error(f"Error detail: {e}")

if st.session_state.audio_buffer:
    st.divider()
    st.audio(st.session_state.audio_buffer)
    st.download_button(
        label="💾 SAVE TO COMPUTER",
        data=st.session_state.audio_buffer,
        file_name=st.session_state.active_filename,
        mime="audio/wav"
    )
