import streamlit as st
from google import genai
from google.genai import types
import wave
import io

st.set_page_config(page_title="HyeTutor Surgical 11.0", page_icon="🇦🇲")
st.title("🇦🇲 Surgical Audio Builder 11.0")

# 1. API Setup
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = None

TARGETS = {
    "numbers_11_20": "Տասնըմէկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան",
    "tens_to_100": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր",
    "months_of_the_year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

selection = st.selectbox("Select Category", list(TARGETS.keys()))

if st.button("🚀 Execute Audio Generation"):
    st.session_state.audio_buffer = None
    with st.status("Accessing Native Audio Engine...") as status:
        try:
            # THIS IS THE STABLE GA MODEL FOR AUDIO OUTPUT
            response = client.models.generate_content(
                model="gemini-live-2.5-flash-native-audio", 
                contents=f"Say these words clearly in Western Armenian: {TARGETS[selection]}",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"]
                )
            )
            
            # Extracting from the native audio stream
            if response.candidates and response.candidates[0].content:
                audio_part = next((p for p in response.candidates[0].content.parts if p.inline_data), None)
                
                if audio_part:
                    # Native Audio Output is 24kHz, 16-bit PCM
                    buf = io.BytesIO()
                    with wave.open(buf, 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(24000)
                        wf.writeframes(audio_part.inline_data.data)
                    
                    st.session_state.audio_buffer = buf.getvalue()
                    status.update(label="✅ Audio Generated", state="complete")
                else:
                    st.error("No inline_data found in response parts.")
            else:
                st.error("Empty response candidates. Verify Project/Key permissions.")
                
        except Exception as e:
            st.error(f"Engine Error: {e}")

if st.session_state.audio_buffer:
    st.divider()
    st.audio(st.session_state.audio_buffer)
    st.download_button(
        "💾 DOWNLOAD WAV", 
        st.session_state.audio_buffer, 
        f"{selection}.wav",
        mime="audio/wav"
    )
