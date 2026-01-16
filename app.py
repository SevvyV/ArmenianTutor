import streamlit as st
from google import genai
from google.genai import types
import wave
import io

# 1. Page Configuration
st.set_page_config(page_title="Elite Hye-Tutor", page_icon="🇦🇲", layout="centered")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🇦🇲 Elite Western Armenian Tutor")
st.caption("Version 15.0 • Raw Audio Header Reconstruction")

# 2. Key Verification
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Missing GOOGLE_API_KEY in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. Instruction Protocol
ELITE_INSTRUCTIONS = """
IDENTITY: Elite Western Armenian Language Tutor.
OPERATING MODE: Spoken-first, natural pacing.
OUTPUT FORMAT:
  Armenian Script (Line 1)
  Phonetic English (Line 2)
  English Translation (Line 3)
"""

# 4. Helper Function to Wrap Raw PCM into a Playable WAV
def create_wav_file(pcm_data):
    # Gemini 2.5 TTS standard: 24kHz, 1 channel (mono), 16-bit
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) # 2 bytes = 16 bit
        wf.setframerate(24000)
        wf.writeframes(pcm_data)
    return buf.getvalue()

# 5. Interaction UI
audio_data = st.audio_input("Speak with your tutor")

if audio_data:
    with st.status("Elite Tutor is analyzing...", expanded=False) as status:
        try:
            audio_part = types.Part.from_bytes(data=audio_data.read(), mime_type="audio/wav")
            
            # STEP 1: ANALYSIS
            analysis_response = client.models.generate_content(
                model="gemini-3-flash-preview", 
                config={'system_instruction': ELITE_INSTRUCTIONS},
                contents=[audio_part]
            )
            
            if analysis_response.text:
                status.update(label="Response generated. Finalizing audio...", state="complete")
                st.session_state.chat_history.append({"role": "assistant", "content": analysis_response.text})
                
                # Display Text
                st.success("Tutor's Response:")
                st.markdown(analysis_response.text)
                
                # STEP 2: VOICE GENERATION
                armenian_text = analysis_response.text.split("\n")[0].strip()
                
                with st.spinner("Tutor is speaking..."):
                    tts_response = client.models.generate_content(
                        model="gemini-2.5-flash-preview-tts",
                        contents=f"Say this clearly in Western Armenian: {armenian_text}",
                        config=types.GenerateContentConfig(response_modalities=["AUDIO"])
                    )
                    
                    # Search and Wrap Logic
                    try:
                        audio_found = False
                        for part in tts_response.candidates[0].content.parts:
                            if part.inline_data and part.inline_data.data:
                                # Reconstruct the WAV header for raw PCM bytes
                                wav_bytes = create_wav_file(part.inline_data.data)
                                st.audio(wav_bytes, format="audio/wav")
                                audio_found = True
                                break
                        
                        if not audio_found:
                            st.warning("Voice engine returned text but no sound data.")
                    except Exception as audio_err:
                        st.info("The audio path needs a quick reset. Try speaking once more.")
            
        except Exception as e:
            st.error(f"Technical Error: {e}")

# Sidebar
with st.sidebar:
    st.header("Lesson Progress")
    if st.button("Clear Session"):
        st.session_state.chat_history = []
        st.rerun()
    for msg in st.session_state.chat_history[-2:]:
        st.info(msg["content"][:100] + "...")

st.divider()
st.caption("Hybrid Engine • V15.0 • Header Construction Active")
