import streamlit as st
import requests
import base64
import json

st.set_page_config(page_title="HyeTutor Surgical 14.0", page_icon="🇦🇲")
st.title("🇦🇲 Surgical Audio Builder 14.0 (Raw REST)")
st.info("Architecture: Direct HTTP/1.1 over TLS | Endpoint: v1beta")

# 1. Configuration
# We use the REST endpoint directly to bypass SDK version conflicts
API_KEY = st.secrets["GOOGLE_API_KEY"]
MODEL_NAME = "gemini-2.0-flash-exp" # The reliable experimental model for Audio
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = None
if "active_filename" not in st.session_state:
    st.session_state.active_filename = ""

TARGETS = {
    "numbers_11_20": "Տասնըմէկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան",
    "tens_to_100": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր",
    "months_of_the_year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

selection = st.selectbox("Select Target Category", list(TARGETS.keys()))
slow_mode = st.toggle("Slow-Motion Mode", value=True)

if st.button("🚀 Execute Raw Request"):
    st.session_state.audio_buffer = None
    
    with st.status("Transmitting Raw JSON Payload...") as status:
        # Constructing the raw payload manually to ensure exact compliance
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Speak the following Western Armenian words {'slowly and clearly' if slow_mode else 'naturally'}: {TARGETS[selection]}"
                }]
            }],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {
                            "voiceName": "Puck"
                        }
                    }
                }
            }
        }
        
        try:
            # Direct POST request
            response = requests.post(
                URL, 
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=30
            )
            
            # Error Handling based on HTTP Status Codes
            if response.status_code != 200:
                st.error(f"Server Error ({response.status_code}): {response.text}")
                status.update(label="❌ Transmission Failed", state="error")
            else:
                data = response.json()
                
                # Manual parsing of the JSON structure
                try:
                    candidates = data.get("candidates", [])
                    if not candidates:
                        st.error("Protocol Error: No candidates returned.")
                    else:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        audio_data = None
                        
                        # Search for the inline_data blob
                        for part in parts:
                            if "inlineData" in part:
                                audio_data = part["inlineData"]["data"]
                                break
                        
                        if audio_data:
                            # Decode Base64 to Binary
                            binary_audio = base64.b64decode(audio_data)
                            st.session_state.audio_buffer = binary_audio
                            st.session_state.active_filename = f"{selection}.wav"
                            status.update(label="✅ Payload Received & Decoded", state="complete")
                        else:
                            st.error("Logic Error: Model returned text only. Quota or model capability mismatch.")
                            st.json(data) # Dump the JSON for inspection
                            
                except Exception as parse_error:
                    st.error(f"Parsing Failure: {parse_error}")
                    st.write(data)

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
