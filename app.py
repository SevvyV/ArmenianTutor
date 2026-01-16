import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(page_title="Elite Hye-Tutor", page_icon="🇦🇲", layout="centered")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🇦🇲 Elite Western Armenian Tutor")
st.caption("Version 14.0 • Deep-Path Audio Extraction")

# 2. Key Verification
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Missing GOOGLE_API_KEY in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. Instruction Protocol (Elite Tutor Framework)
ELITE_INSTRUCTIONS = """
IDENTITY: Elite Western Armenian Language Tutor.
OPERATING MODE: Spoken-first, natural pacing.
OUTPUT FORMAT:
  1. Armenian Script (Հայերէն)
  2. Phonetic English
  3. English Translation
  4. Brief Tutor Note
"""

# 4. Interaction UI
audio_data = st.audio_input("Tap the mic to speak with your tutor")

if audio_data:
    with st.status("Elite Tutor is analyzing...", expanded=False) as status:
        try:
            # Package user audio for the 'Listening' model
            audio_part = types.Part.from_bytes(data=audio_data.read(), mime_type="audio/wav")
            
            # STEP 1: ANALYSIS (Gemini 3 Flash handles the "brain" work)
            analysis_response = client.models.generate_content(
                model="gemini-3-flash-preview", 
                config={'system_instruction': ELITE_INSTRUCTIONS},
                contents=[audio_part]
            )
            
            if analysis_response.text:
                status.update(label="Response generated. Finalizing audio...", state="complete")
                st.session_state.chat_history.append({"role": "assistant", "content": analysis_response.text})
                
                # Display the Text
                st.success("Tutor's Response:")
                st.markdown(analysis_response.text)
                
                # STEP 2: VOICE GENERATION (Gemini 2.5 TTS handles the "voice" work)
                # We extract only the Armenian script for the voice engine
                armenian_text = analysis_response.text.split("\n")[0].strip()
                
                with st.spinner("Tutor is speaking..."):
                    tts_response = client.models.generate_content(
                        model="gemini-2.5-flash-preview-tts",
                        contents=f"Say this clearly in Western Armenian: {armenian_text}",
                        config=types.GenerateContentConfig(
                            response_modalities=["AUDIO"]
                        )
                    )
                    
                    # 2026 Deep-Path Extraction: 
                    # We navigate carefully through candidates -> content -> parts -> inline_data
                    try:
                        # Extract the first part of the first candidate
                        candidate = tts_response.candidates[0]
                        parts = candidate.content.parts
                        
                        audio_found = False
                        for part in parts:
                            # Use the 2026 'inline_data' path for raw pcm/wav bytes
                            if part.inline_data and part.inline_data.data:
                                # Provide the raw bytes to the Streamlit audio player
                                st.audio(part.inline_data.data, format="audio/wav")
                                audio_found = True
                                break
                        
                        if not audio_found:
                            st.warning("The tutor generated a response, but the audio data was missing.")
                    except (AttributeError, IndexError) as audio_err:
                        st.warning("The voice engine is warming up. Please try again.")
            
        except Exception as e:
            st.error(f"Technical Error: {e}")

# Sidebar for Lesson Review
with st.sidebar:
    st.header("Lesson Progress")
    if st.button("Clear Session"):
        st.session_state.chat_history = []
        st.rerun()
    for msg in st.session_state.chat_history[-2:]:
        st.info(msg["content"][:100] + "...")

st.divider()
st.caption("Hybrid System: Gemini 3 Flash (Analysis) + Gemini 2.5 TTS (Voice)")
