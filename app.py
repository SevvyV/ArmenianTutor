import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(page_title="Elite Hye-Tutor", page_icon="🇦🇲", layout="centered")

# Memory to track his progress and recycle words
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🇦🇲 Elite Western Armenian Tutor")
st.caption("Status: Paid Tier / 2026 Stable Engine")

# 2. Key Verification
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Missing API Key in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. Elite Pedagogical Instructions
ELITE_PROMPT = """
ROLE: Elite Western Armenian Tutor.
PHILOSOPHY: Speech precedes grammar. Focus on natural flow.
DIALECT: Western Armenian (e.g., 'Inchoos es').
OUTPUT: Armenian Script, Phonetics, English Translation.
"""

# 4. Interaction
audio_data = st.audio_input("Speak to your tutor")

if audio_data:
    with st.spinner("Analyzing..."):
        try:
            audio_part = types.Part.from_bytes(data=audio_data.read(), mime_type="audio/wav")

            # Using Gemini 3 Flash for elite-level speed
            response = client.models.generate_content(
                model="gemini-3-flash", 
                config={'system_instruction': ELITE_PROMPT},
                contents=[str(st.session_state.messages[-4:]), audio_part]
            )
            
            if response.text:
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.success("Tutor's Response:")
                st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Technical Error: {e}")

# Sidebar History
with st.sidebar:
    st.header("Session History")
    if st.button("Reset Session"):
        st.session_state.messages = []
        st.rerun()
    for m in st.session_state.messages:
        st.info(m["content"][:80] + "...")

st.divider()
st.caption("Pedagogical Engine Active • Designed for Michigan-California Connection")
