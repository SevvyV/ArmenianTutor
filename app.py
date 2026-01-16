import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(page_title="Hye-Tutor", page_icon="🇦🇲", layout="centered")

st.markdown("""
    <style>
    .stAudioInput { border: 2px solid #d94d3a; border-radius: 15px; }
    h1 { color: #d94d3a; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🇦🇲 Western Armenian Tutor")

# 2. Key Verification (Cloud Version)
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ GOOGLE_API_KEY not found in Streamlit Secrets.")
    st.stop()

# 3. Initialize the Gemini Client
client = genai.Client(api_key=api_key)

# 4. App Content
st.write("Michigan ↔ California Practice Session")
topic = st.selectbox("What would you like to practice?", ["General Conversation", "Family", "Food", "School"])

# Optimized prompt for the stable 1.5 model
SYSTEM_PROMPT = f"""
You are a patient Western Armenian tutor. The topic is {topic}.
- Dialect: Strictly Western Armenian (e.g. 'Inchoos es', 'Parev').
- Format: 
  1. Armenian Script (Հայերէն)
  2. Phonetic English 
  3. English Translation
- Evaluation: Listen to the student's audio and respond in Western Armenian.
"""

# 5. Audio Interaction
audio_data = st.audio_input("Tap the microphone to speak")

if audio_data:
    with st.status("Hye-Tutor is thinking...", expanded=False):
        try:
            # Packaging audio data for the stable 1.5 library
            audio_part = types.Part.from_bytes(
                data=audio_data.read(),
                mime_type="audio/wav"
            )

            # SWITCHED TO STABLE MODEL: gemini-1.5-flash
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                config={'system_instruction': SYSTEM_PROMPT},
                contents=[audio_part]
            )
            
            if response.text:
                st.success("Tutor's Response:")
                st.markdown(response.text)
            else:
                st.warning("The AI processed the audio but didn't provide text. Try again.")
            
        except Exception as e:
            # If the quota error persists, we show a helpful wait message
            if "429" in str(e):
                st.error("Google's free tier is busy. Please wait 60 seconds and try again.")
            else:
                st.error(f"Technical Error: {e}")

st.divider()
st.caption("Stable Connection • Michigan-California Active")
