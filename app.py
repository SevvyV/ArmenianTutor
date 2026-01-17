import streamlit as st
from google import genai
from google.genai import types
import wave
import io
import time

# 1. Page Config
st.set_page_config(page_title="Surgical Builder 8.7", page_icon="🇦🇲")
st.title("🇦🇲 Surgical Audio Builder 8.7")
st.markdown("Build one file at a time, verify it, and save it to your computer.")

# 2. API Setup
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. Initialize Persistent Storage
# This ensures that once a file is built, it stays on screen.
if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = None
if "active_filename" not in st.session_state:
    st.session_state.active_filename = ""

# 4. Data
TARGETS = {
    "numbers_11_20": "Տասնըմէկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան",
    "tens_to_100": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր",
    "hundreds_to_1000": "Հարիւր, Երկու հարիւր, Երեք հարիւր, Չորս հարիւր, Հինգ հարիւր, Վեց հարիւր, Եօթը հարիւր, Ութը հարիւր, Ինը հարիւր, Հազար",
    "months_of_the_year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

# 5. UI Layout
selection = st.selectbox("1. Choose Category", list(TARGETS.keys()))
slow_mode = st.toggle("2. Slow-Motion Mode", value=True)

# 6. The Build Action
if st.button("🚀 3. Generate Audio"):
    # Clear old results first
    st.session_state.audio_buffer = None
    
    with st.status("Building...") as status:
        try:
            # We use a very direct prompt to minimize AI 'confusion'
            # 'Listen and repeat' style prompts often bypass safety blocks better
            prompt = f"Speak these Western Armenian words {'slowly' if slow_mode else 'clearly'}: {TARGETS[selection]}"
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    safety_settings=[{"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}]
                )
            )
            
            # Extract Audio Part
            if response.candidates and response.candidates[0].content:
                parts = response.candidates[0].content.parts
                audio_part = next((p for p in parts if p.inline_data), None)
                
                if audio_part and len(audio_part.inline_data.data) > 100:
                    # Convert raw PCM to WAV
                    buf = io.BytesIO()
                    with wave.open(buf, 'wb') as wf:
                        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
                        wf.writeframes(audio_part.inline_data.data)
                    
                    # Store in session state
                    st.session_state.audio_buffer = buf.getvalue()
                    st.session_state.active_filename = f"{selection}_{'slow' if slow_mode else 'fast'}.wav"
                    status.update(label="✅ Success!", state="complete")
                else:
                    status.update(label="❌ Google returned empty audio. Try again.", state="error")
            else:
                status.update(label="❌ No response from AI.", state="error")
                
        except Exception as e:
            status.update(label=f"❌ Error: {str(e)}", state="error")

# 7. Persistent Output Section
# This stays visible even after the button click logic finishes.
if st.session_state.audio_buffer:
    st.divider()
    st.subheader(f"Results: {st.session_state.active_filename}")
    st.audio(st.session_state.audio_buffer)
    
    st.download_button(
        label="💾 SAVE TO COMPUTER",
        data=st.session_state.audio_buffer,
        file_name=st.session_state.active_filename,
        mime="audio/wav",
        use_container_width=True
    )
    st.success("Download ready. Click the button above to save to your Downloads folder.")
