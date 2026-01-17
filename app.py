import streamlit as st
from google import genai
from google.genai import types
import wave
import io

st.set_page_config(page_title="Surgical Builder 9.0", page_icon="🇦🇲")
st.title("🇦🇲 Surgical Audio Builder 9.0")
st.info("Status: Using New Project Quota & Stable TTS Engine")

# 1. API Setup - Make sure you updated the secret in Streamlit!
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

selection = st.selectbox("1. Select Target Category", list(TARGETS.keys()))
slow_mode = st.toggle("2. Slow-Motion Mode", value=True)

if st.button("🚀 3. Generate Audio File"):
    st.session_state.audio_buffer = None # Reset
    
    with st.status("Building...") as status:
        try:
            # Using the stable 2.4-flash-tts model for Western Armenian
            response = client.models.generate_content(
                model="gemini-2.4-flash-tts", 
                contents=f"Speak these Western Armenian words {'slowly' if slow_mode else 'clearly'}: {TARGETS[selection]}",
                config=types.GenerateContentConfig(response_modalities=["AUDIO"])
            )
            
            if response.candidates and response.candidates[0].content:
                audio_part = next((p for p in response.candidates[0].content.parts if p.inline_data), None)
                
                if audio_part:
                    # Packaging as a valid WAV
                    buf = io.BytesIO()
                    with wave.open(buf, 'wb') as wf:
                        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
                        wf.writeframes(audio_part.inline_data.data)
                    
                    st.session_state.audio_buffer = buf.getvalue()
                    st.session_state.active_filename = f"{selection}_{'slow' if slow_mode else 'fast'}.wav"
                    status.update(label="✅ Audio Generated!", state="complete")
                else:
                    st.error("AI responded but provided no audio data.")
            else:
                st.error("No response. Your new API key might not be active yet (wait 60s).")
                
        except Exception as e:
            st.error(f"Error: {e}")

# PERSISTENT DOWNLOAD SECTION
if st.session_state.audio_buffer:
    st.divider()
    st.write(f"### Ready: {st.session_state.active_filename}")
    st.audio(st.session_state.audio_buffer)
    
    st.download_button(
        label="💾 SAVE FILE TO COMPUTER",
        data=st.session_state.audio_buffer,
        file_name=st.session_state.active_filename,
        mime="audio/wav",
        use_container_width=True
    )
    st.success("Click the button above to move the file to your Downloads folder.")
