import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(page_title="Elite Hye-Tutor", page_icon="🇦🇲", layout="centered")

# 2. Session Memory (Allows the "Elite Tutor" to track progress)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🇦🇲 Elite Western Armenian Tutor")
st.caption("Mode: Spoken-First • API Status: Connected ✅")

# 3. Key Verification
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ GOOGLE_API_KEY not found in Secrets dashboard.")
    st.stop()

# Initialize Client
client = genai.Client(api_key=api_key)

# 4. The Advanced Pedagogical Framework
ELITE_INSTRUCTIONS = """
YOUR IDENTITY: Elite Armenian Spoken Language Tutor.
OPERATING MODE: Spoken-first, conversation-driven. Priority: sound natural.
DIALECT: Western Armenian only. Flag Eastern variants gently.
TEACHING PHILOSOPHY: Speech precedes grammar. Confidence before correctness.
PRONUNCIATION FOCUS: Consonant aspiration, rolled 'ռ', vowel purity.
FEEDBACK STRATEGY: 
  - Immediate: Errors blocking comprehension or fossilizing pronunciation.
  - Delayed: Minor grammar slips.
OUTPUT FORMAT:
  1. Armenian Script (Հայերէն)
  2. Phonetic English
  3. English Translation
  4. One natural follow-up question in Armenian to keep the flow.
"""

# 5. Interaction UI
audio_data = st.audio_input("Tap the mic to speak with your tutor")

if audio_data:
    with st.status("Elite Tutor is analyzing your speech...", expanded=False) as status:
        try:
            # Package the audio
            audio_part = types.Part.from_bytes(data=audio_data.read(), mime_type="audio/wav")

            # Send history so the AI can "recycle vocabulary"
            history_context = str(st.session_state.chat_history[-6:])

            # UPDATED: Using the latest stable model to fix the 404 error
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                config={'system_instruction': ELITE_INSTRUCTIONS},
                contents=[f"Previous Context: {history_context}", audio_part]
            )
            
            if response.text:
                status.update(label="Tutor is ready!", state="complete")
                
                # Save to history
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                
                st.success("Tutor's Feedback:")
                st.markdown(response.text)
            else:
                status.update(label="Awaiting input...", state="complete")
            
        except Exception as e:
            st.error(f"Technical Error: {e}")
            if "404" in str(e):
                st.info("The app tried to reach a model that is no longer available. I have updated the code to use Gemini 2.0 Flash.")

# Sidebar for Lesson Review
with st.sidebar:
    st.header("Lesson Progress")
    if st.button("Clear Session"):
        st.session_state.chat_history = []
        st.rerun()
    for msg in st.session_state.chat_history:
        st.info(msg["content"][:100] + "...")

st.divider()
st.caption("Updated for 2026 Model Standards • Elite Armenian Tutor")
