import streamlit as st
from google import genai

# 1. Setup
st.set_page_config(page_title="Hye-Tutor", page_icon="🇦🇲")
st.title("🇦🇲 Western Armenian Tutor")

# 2. Key Check
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Key not found in Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. The Interaction
audio_data = st.audio_input("Tap the mic, speak, and WAIT for the checkmark")

if audio_data:
    st.info("Processing audio... please wait.")
    try:
        # We use Gemini 2.0 Flash for audio-to-text-to-audio speed
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            config={'system_instruction': "You are a Western Armenian tutor. Respond in Armenian script, phonetics, and English."},
            contents=[
                {"mime_type": "audio/wav", "data": audio_data.read()}
            ]
        )
        
        if response.text:
            st.success("Tutor's Response:")
            st.markdown(response.text)
        else:
            st.warning("The AI heard you, but didn't generate a text response. Try speaking clearer.")

    except Exception as e:
        st.error(f"Technical Error: {e}")
        st.info("Common fix: Ensure your requirements.txt has 'google-genai==0.3.0'")

st.divider()
st.caption("Michigan ↔ California Deployment")
