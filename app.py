import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(page_title="Elite Hye-Tutor", page_icon="🇦🇲", layout="centered")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🇦🇲 Elite Western Armenian Tutor")
st.caption("2026 Stable Engine • Status: Paid Tier Enabled")

# 2. Key Verification
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Missing GOOGLE_API_KEY in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. Instruction Protocol (Your Advanced ChatGPT Prompt)
ELITE_INSTRUCTIONS = """
IDENTITY: Elite Western Armenian Language Tutor.
OPERATING MODE: Spoken-first, natural pacing.
PRONUNCIATION: Focus on consonant aspiration and rolled 'ռ'.
OUTPUT: Armenian Script, Phonetic English, English Translation.
"""

# 4. Interaction UI
audio_data = st.audio_input("Speak to your tutor")

if audio_data:
    with st.status("Elite Tutor is analyzing...", expanded=False) as status:
        try:
            # Package the audio
            audio_part = types.Part.from_bytes(data=audio_data.read(), mime_type="audio/wav")
            
            # Use the exact 2026 model name: gemini-3-flash-preview
            # This model is a "thinking" model optimized for speed
            response = client.models.generate_content(
                model="gemini-3-flash-preview", 
                config={'system_instruction': ELITE_INSTRUCTIONS},
                contents=[audio_part]
            )
            
            if response.text:
                status.update(label="Tutor is ready!", state="complete")
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                st.success("Tutor's Response:")
                st.markdown(response.text)
            else:
                status.update(label="No audio detected", state="complete")
            
        except Exception as e:
            st.error(f"Technical Error: {e}")
            if "404" in str(e):
                st.info("Ensure the model name is 'gemini-3-flash-preview' in your code.")

# Sidebar for Lesson Review
with st.sidebar:
    st.header("Lesson Progress")
    if st.button("Clear Session"):
        st.session_state.chat_history = []
        st.rerun()
    for msg in st.session_state.chat_history[-5:]:
        st.info(msg["content"][:100] + "...")

st.divider()
st.caption("Model: Gemini 3 Flash Preview • Updated January 15, 2026")
