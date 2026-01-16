import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(page_title="Elite Hye-Tutor", page_icon="🇦🇲", layout="centered")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🇦🇲 Elite Western Armenian Tutor")
st.caption("Version 11.0 • Stable Audio Extraction (2026)")

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
            # Package the user's voice
            audio_part = types.Part.from_bytes(data=audio_data.read(), mime_type="audio/wav")
            
            # STEP 1: ANALYSIS (Using the multimodal listening model)
            analysis_response = client.models.generate_content(
                model="gemini-2.5-flash", 
                config={'system_instruction': ELITE_INSTRUCTIONS},
                contents=[audio_part]
            )
            
            if analysis_response.text:
                status.update(label="Response generated. Crafting voice...", state="complete")
                st.session_state.chat_history.append({"role": "assistant", "content": analysis_response.text})
                
                # Display the Text
                st.success("Tutor's Response:")
                st.markdown(analysis_response.text)
                
                # STEP 2: VOICE GENERATION (Updated for 2026 SDK)
                # Extract only the Armenian sentence (the first line) for speech
                armenian_text = analysis_response.text.split("\n")[0]
                
                with st.spinner("Generating native audio..."):
                    # Use the specialized stable TTS model
                    tts_response = client.models.generate_content(
                        model="gemini-2.5-flash-tts",
                        contents=f"Say this clearly in Western Armenian: {armenian_text}",
                        config=types.GenerateContentConfig(
                            response_modalities=["AUDIO"]
                        )
                    )
                    
                    # 2026 Data Path: candidates -> content -> parts -> inline_data
                    try:
                        # Extract the raw bytes directly from the nested parts
                        audio_part = tts_response.candidates[0].content.parts[0]
                        if hasattr(audio_part, 'inline_data'):
                            audio_bytes = audio_part.inline_data.data
                            # Display the audio player with the correct format
                            st.audio(audio_bytes, format="audio/wav")
                        else:
                            st.warning("Audio data generated but not found in the response parts.")
                    except (AttributeError, IndexError):
                        st.warning("The voice engine is still initializing. Try one more short sentence.")
            
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
st.caption("Hybrid System: Gemini 2.5 Flash (Listen) + Gemini 2.5 TTS (Speak)")
