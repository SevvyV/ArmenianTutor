import streamlit as st
from google import genai
from google.genai import types
import wave
import io

# 1. Page Configuration - Updated for Version 1.0 Branding
st.set_page_config(
    page_title="Elite Armenian AI Tutor v1.0", 
    page_icon="🇦🇲", 
    layout="centered"
)

# Persistence for Version 1.0 sessions
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Main Title Branding
st.title("🇦🇲 Elite Armenian AI Tutor v1.0")
st.caption("Official Release • Hybrid Pedagogical Engine • 2026")

# 2. Key Verification
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Missing GOOGLE_API_KEY in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. Elite Instruction Protocol
ELITE_INSTRUCTIONS = """
IDENTITY: Elite Western Armenian Language Tutor.
OPERATING MODE: Spoken-first, natural pacing.
PHILOSOPHY: Speech precedes grammar. Focus on natural flow and confidence.
OUTPUT FORMAT:
  1. Armenian Script (Հայերէն)
  2. Phonetic English
  3. English Translation
  4. Brief Cultural or Linguistic Note
"""

# 4. Helper Function: Raw PCM to Playable WAV Header
def create_wav_file(pcm_data):
    # Gemini 2.5 TTS Specs: 24kHz, 16-bit Mono
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) 
        wf.setframerate(24000)
        wf.writeframes(pcm_data)
    return buf.getvalue()

# 5. Spoken Interaction UI
audio_data = st.audio_input("Tap the microphone to speak with your tutor")

if audio_data:
    with st.status("Tutor is listening...", expanded=False) as status:
        try:
            # Package the user's audio
            audio_part = types.Part.from_bytes(data=audio_data.read(), mime_type="audio/wav")
            
            # STEP 1: ANALYSIS (Gemini 3 Flash Listening)
            analysis_response = client.models.generate_content(
                model="gemini-3-flash-preview", 
                config={'system_instruction': ELITE_INSTRUCTIONS},
                contents=[audio_part]
            )
            
            if analysis_response.text:
                status.update(label="Response generated. Preparing voice...", state="complete")
                st.session_state.chat_history.append({"role": "assistant", "content": analysis_response.text})
                
                # Display Text Feedback
                st.success("Tutor's Response:")
                st.markdown(analysis_response.text)
                
                # STEP 2: VOICE GENERATION (Gemini 2.5 TTS Speaking)
                # Cleaning: Take only the Armenian script for the speaker
                clean_armenian = analysis_response.text.split("\n")[0].strip()
                
                with st.spinner("Tutor is speaking..."):
                    tts_response = client.models.generate_content(
                        model="gemini-2.5-flash-preview-tts",
                        contents=f"Say this clearly in Western Armenian: {clean_armenian}",
                        config=types.GenerateContentConfig(response_modalities=["AUDIO"])
                    )
                    
                    # Search and Wrap Logic (v1.0 Stability)
                    try:
                        audio_found = False
                        for part in tts_response.candidates[0].content.parts:
                            if part.inline_data and part.inline_data.data:
                                # Reconstruct the WAV header
                                wav_bytes = create_wav_file(part.inline_data.data)
                                st.audio(wav_bytes, format="audio/wav")
                                audio_found = True
                                break
                        
                        if not audio_found:
                            st.warning("Audio was processed but no bytes were returned. Try again.")
                    except Exception:
                        st.info("The voice engine is calibrating. Please try your sentence once more.")
            
        except Exception as e:
            st.error(f"Technical Error: {e}")

# Sidebar Lesson Log
with st.sidebar:
    st.header("v1.0 Lesson Log")
    if st.button("New Session"):
        st.session_state.chat_history = []
        st.rerun()
    for msg in st.session_state.chat_history[-2:]:
        st.info(msg["content"][:100] + "...")

st.divider()
st.caption("Release 1.0.0 • Hybrid Engine (Analysis + TTS)")
