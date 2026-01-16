import streamlit as st
from google import genai
from google.genai import types

# 1. Page Config
st.set_page_config(page_title="Hye-Tutor", page_icon="🇦🇲", layout="centered")

st.title("🇦🇲 Western Armenian Tutor")

# 2. Key Check
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Key not found in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. Audio Recording
audio_data = st.audio_input("Tap the mic, say 'Parev', and wait.")

if audio_data:
    with st.spinner("Tutor is thinking..."):
        try:
            # We must package the audio like this for the newest library
            audio_payload = types.Part.from_bytes(
                data=audio_data.read(),
                mime_type="audio/wav"
            )

            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                config={'system_instruction': "You are a Western Armenian tutor. Respond in Armenian script, phonetics, and English."},
                contents=[audio_payload]
            )
            
            st.success("Tutor's Response:")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Technical Error: {e}")

st.divider()
st.caption("Michigan ↔ California Deployment")
