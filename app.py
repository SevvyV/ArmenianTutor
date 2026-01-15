import streamlit as st
from google import genai
import os

# 1. Page Config
st.set_page_config(page_title="Hye-Tutor", page_icon="🇦🇲", layout="centered")

st.markdown("""
    <style>
    .stAudioInput { border: 2px solid #d94d3a; border-radius: 15px; }
    .stAlert { border-radius: 15px; }
    h1 { color: #d94d3a; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🇦🇲 Western Armenian Tutor")

# 2. Environment Check
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("GOOGLE_API_KEY not found. Please check your Windows Environment Variables.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. Practice Settings
st.write("Practicing with Sevag's son. Focus: **Western Armenian Vernacular**")
topic = st.selectbox("Choose a topic:", ["General Chat", "Family", "Food", "School"])

# 4. The AI Instructions
SYSTEM_PROMPT = f"""
You are a patient Western Armenian tutor. The topic is {topic}.
- Always use Western Armenian (e.g., 'Inchoos es', 'Abris').
- Format your response as:
  1. Armenian Script (Հայերէն)
  2. Phonetic Transliteration (English letters)
  3. English Translation
- Evaluation: If the student uses Eastern Armenian (e.g. 'Barev dzez' instead of 'Parev'), gently correct them to the Western version.
"""

# 5. Audio Interaction
audio_data = st.audio_input("Tap the mic to speak to your tutor")

if audio_data:
    with st.status("Hye-Tutor is listening...", expanded=False):
        try:
            # Using Gemini 2.0 Flash for low-latency speed
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                config={'system_instruction': SYSTEM_PROMPT},
                contents=[
                    "Listen to the student and respond in Western Armenian:",
                    {"mime_type": "audio/wav", "data": audio_data.read()}
                ]
            )
            
            st.success("Tutor's Feedback:")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption(f"Connected to Local Network: http://192.168.68.54:8501")