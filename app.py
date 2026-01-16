import streamlit as st
from google import genai
from google.genai import types
import wave
import io
import time

st.title("🏥 Surgical Fix: Months of the Year (Slow)")

# 1. API Setup
api_key = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=api_key)

# 2. The Task
MONTHS = ["Յունուար", "Փետրուար", "Մարտ", "Ապրիլ", "Մայիս", "Յունիս", "Յուլիս", "Օգոստոս", "Սեպտեմբեր", "Հոկտեմբեր", "Նոյեմբեր", "Դեկտեմբեր"]
FILENAME = "months_of_the_year_slow.wav"

def create_wav_header(pcm_data):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) 
        wf.setframerate(24000)
        wf.writeframes(pcm_data)
    return buf.getvalue()

st.info("This script will generate each month individually and stitch them together to prevent the 'Empty File' error.")

if st.button("🚀 Start Surgical Build"):
    combined_pcm = b""
    progress_bar = st.progress(0)
    
    for i, month in enumerate(MONTHS):
        st.write(f"Processing: {month}...")
        
        # Try up to 3 times per month
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-preview-tts",
                    contents=f"Say this slowly and clearly in Western Armenian: {month}",
                    config=types.GenerateContentConfig(response_modalities=["AUDIO"])
                )
                
                if response.candidates and response.candidates[0].content:
                    # Collect the raw PCM data
                    combined_pcm += response.candidates[0].content.parts[0].inline_data.data
                    # Add a tiny bit of silence (0.5s) between months
                    combined_pcm += b'\x00' * 12000 
                    break
                else:
                    time.sleep(2)
            except Exception as e:
                st.warning(f"Attempt {attempt+1} failed for {month}. Retrying...")
                time.sleep(2)
        
        progress_bar.progress((i + 1) / len(MONTHS))

    if combined_pcm:
        final_wav = create_wav_header(combined_pcm)
        st.success("All months captured and stitched!")
        st.audio(final_wav)
        st.download_button("📥 Download Missing File", final_wav, file_name=FILENAME)
    else:
        st.error("Stitching failed. Google is still refusing the connection. Please wait 5 minutes and try once more.")
