import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(page_title="Elite Hye-Tutor", page_icon="🇦🇲", layout="centered")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🇦🇲 Elite Western Armenian Tutor")
st.caption("Version 13.0 • Verified Spoken Audio")

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
  Armenian Script (First line only)
  Phonetic English
  English Translation
"""

# 4. Interaction UI
audio_data = st.audio_input("Tap the mic to speak with your tutor")

if audio_data:
    with st.status("Elite Tutor is analyzing...", expanded=False) as status:
        try:
            # Package the user's voice for Gemini 3 Flash (Listener)
            audio_part = types.Part.from_bytes(data=audio_data.read(), mime_type="audio/wav")
            
            # STEP 1: ANALYSIS
            analysis_response = client.models.generate_content(
                model="gemini-3-flash-preview", 
                config={'system_instruction': ELITE_INSTRUCTIONS},
                contents=[audio_part]
            )
            
            if analysis_response.text:
                status.update(label="Response generated. Preparing tutor's voice...", state="complete")
                st.session_state.chat_history.append({"role": "assistant", "content": analysis_response.text})
                
                # Display the Text
                st.success("Tutor's Response:")
                st.markdown(analysis_response.text)
                
                # STEP 2: VOICE GENERATION (Using the specialized 2.5 TTS)
                # We strictly take only the Armenian script line for the voice engine
                clean_armenian = analysis_response.text.split("\n")[0].strip()
                
                with st.spinner("Tutor is speaking..."):
                    tts_response = client.models.generate_content(
                        model="gemini-2.5-flash-preview-tts",
                        contents=f"Say this clearly in Western Armenian: {clean_armenian}",
                        config=types.GenerateContentConfig(
                            response_modalities=["AUDIO"]
                        )
                    )
                    
                    # 2026 Logic: Navigating the nested content for audio bytes
                    try:
                        # Extracting audio from the 'inline_data' part of the response
                        raw_parts = tts_response.candidates[0].content.parts
                        audio_found = False
                        for part in raw_parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                st.audio(part.inline_data.data, format="audio/wav")
                                audio_found = True
                                break
                        
                        if not audio_found:
                            st.warning("Voice data was silent. Please try another sentence.")
                    except (AttributeError, IndexError):
                        st.info("Tutor is clearing their throat. Please try your sentence again.")
            
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
st.caption("Hybrid System: Gemini 3 Flash + Gemini 2.5 TTS (V13.0)")
