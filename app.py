import streamlit as st
from google import genai

# 1. Page Configuration & Mobile Styling
st.set_page_config(page_title="Hye-Tutor", page_icon="🇦🇲", layout="centered")

st.markdown("""
    <style>
    .stAudioInput { border: 2px solid #d94d3a; border-radius: 15px; }
    h1 { color: #d94d3a; text-align: center; }
    .stAlert { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🇦🇲 Western Armenian Tutor")

# 2. Key Verification (Cloud Version)
# This looks in the Streamlit Cloud 'Advanced Settings > Secrets'
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ GOOGLE_API_KEY not found in Streamlit Secrets.")
    st.info("On the Streamlit Cloud dashboard, go to Settings > Secrets and add: GOOGLE_API_KEY = 'your-key-here'")
    st.stop()

# 3. Initialize the Gemini Client
client = genai.Client(api_key=api_key)

# 4. App Content
st.write("Michigan ↔ California Practice Session")
topic = st.selectbox("What would you like to practice?", ["General Conversation", "Family", "Food", "School"])

SYSTEM_PROMPT = f"""
You are a patient Western Armenian tutor. The topic is {topic}.
- Dialect: Strictly Western Armenian.
- Format: 
  1. Armenian Script (Հայերէն)
  2. Phonetic English 
  3. English Translation
- Evaluation: Listen to the audio. Correct any Eastern Armenian variants to Western Armenian.
"""

# 5. Audio Interaction
st.write("Tap the microphone and say something in Armenian!")
audio_data = st.audio_input("Record your voice")

if audio_data:
    with st.status("Hye-Tutor is listening...", expanded=False):
        try:
            # Using Gemini 2.0 Flash for speed across the country
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                config={'system_instruction': SYSTEM_PROMPT},
                contents=[
                    "Analyze my Armenian and respond:",
                    {"mime_type": "audio/wav", "data": audio_data.read()}
                ]
            )
            
            st.success("Tutor's Feedback:")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption("Secure AI Connection • Designed for Sevag's Son")
