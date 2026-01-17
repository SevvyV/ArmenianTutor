import streamlit as st
import requests
import base64
import json

st.set_page_config(page_title="HyeTutor Surgical 15.1", page_icon="🇦🇲")
st.title("🇦🇲 Surgical Audio Builder 15.1 (WaveNet)")
st.info("Engine: Google Cloud WaveNet (Premium) | Protocol: REST")

# 1. Configuration
# We use your existing API Key from the Secrets
API_KEY = st.secrets["GOOGLE_API_KEY"]
TTS_ENDPOINT = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={API_KEY}"

if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = None
if "active_filename" not in st.session_state:
    st.session_state.active_filename = ""

TARGETS = {
    "numbers_11_20": "Տասնըմէկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան",
    "tens_to_100": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր",
    "hundreds_to_1000": "Հարիւր, Երկու հարիւր, Երեք հարիւր, Չորս հարիւր, Հինգ հարիւր, Վեց հարիւր, Եօթը հարիւր, Ութը հարիւր, Ինը հարիւր, Հազար",
    "months_of_the_year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

selection = st.selectbox("Select Target Category", list(TARGETS.keys()))

# Speed control mapping for TTS engine
speed_multiplier = st.radio("Speed", [0.85, 1.0], format_func=lambda x: "Teacher Mode (Slow)" if x == 0.85 else "Native Speed (Normal)", index=0)

if st.button("🚀 Synthesize WaveNet Audio"):
    st.session_state.audio_buffer = None
    
    with st.status("Requesting High-Fidelity WaveNet Stream...") as status:
        # Construct the specialized TTS payload
        payload = {
            "input": {
                "text": TARGETS[selection]
            },
            "voice": {
                "languageCode": "hy-AM",       # Armenian Locale
                "name": "hy-AM-Wavenet-A"      # <--- SWITCHED TO WAVENET (Higher Quality)
            },
            "audioConfig": {
                "audioEncoding": "LINEAR16",   # WAV format
                "speakingRate": speed_multiplier
            }
        }
        
        try:
            # Direct POST to the stable TTS endpoint
            response = requests.post(
                TTS_ENDPOINT, 
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "audioContent" in data:
                    # Decode the base64 audio content
                    binary_audio = base64.b64decode(data["audioContent"])
                    st.session_state.audio_buffer = binary_audio
                    st.session_state.active_filename = f"{selection}.wav"
                    status.update(label="✅ WaveNet Audio Synthesized", state="complete")
                else:
                    st.error("Protocol Error: API returned 200 but no 'audioContent'.")
            
            elif response.status_code == 400:
                 st.error(f"Configuration Error: {response.text}")
                 st.info("Note: If 'hy-AM-Wavenet-A' is unavailable in your region, we can revert to 'Standard-A'.")
            
            elif response.status_code == 403:
                st.error("🚨 PERMISSION DENIED: Please enable the 'Cloud Text-to-Speech API' in your Google Cloud Console.")
                st.markdown(f"[Click here to Enable API](https://console.cloud.google.com/marketplace/product/google/texttospeech.googleapis.com)")
                status.update(label="❌ API Not Enabled", state="error")
                
            else:
                st.error(f"Server Error ({response.status_code}): {response.text}")
                status.update(label="❌ Transmission Failed", state="error")

        except Exception as e:
            st.error(f"Connection Failure: {e}")

if st.session_state.audio_buffer:
    st.divider()
    st.write(f"### Ready: {st.session_state.active_filename}")
    st.audio(st.session_state.audio_buffer, format="audio/wav")
    st.download_button(
        label="💾 SAVE WAV FILE",
        data=st.session_state.audio_buffer,
        file_name=st.session_state.active_filename,
        mime="audio/wav"
    )
