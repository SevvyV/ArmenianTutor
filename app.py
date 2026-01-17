import streamlit as st
import asyncio
import edge_tts
import io

st.set_page_config(page_title="HyeTutor Dev 16.1", page_icon="🇦🇲")
st.title("🇦🇲 Surgical Audio Builder 16.1 (Dev Mode)")
st.info("Engine: Microsoft Edge Neural | Status: Dev Branch")

# 1. DATA
TARGETS = {
    "numbers_11_20": "Տասնըմէկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան",
    "tens_to_100": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր",
    "hundreds_to_1000": "Հարիւր, Երկու հարիւր, Երեք հարիւր, Չորս հարիւր, Հինգ հարիւր, Վեց հարիւր, Եօթը հարիւր, Ութը հարիւր, Ինը հարիւր, Հազար",
    "months_of_the_year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

selection = st.selectbox("Select Target Category", list(TARGETS.keys()))
gender = st.radio("Voice Gender", ["Female (Anahit)", "Male (Hayk)"], index=0)

# Map selection to the correct Microsoft Neural Voice ID
voice_id = "hy-AM-AnahitNeural" if "Female" in gender else "hy-AM-HaykNeural"

# Speed adjustment
rate_str = st.select_slider("Speaking Rate", options=["-10%", "-5%", "+0%", "+5%"], value="-5%")

# 2. ASYNC GENERATION FUNCTION
async def generate_audio(text, voice, rate):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    out_buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            out_buffer.write(chunk["data"])
    return out_buffer.getvalue()

# 3. UI LOGIC
if st.button("🚀 Generate Neural Audio"):
    st.session_state.audio_buffer = None
    
    with st.status("Connecting to Microsoft Neural Cloud...") as status:
        try:
            # We must run the async function inside Streamlit's sync environment
            audio_data = asyncio.run(generate_audio(TARGETS[selection], voice_id, rate_str))
            
            st.session_state.audio_buffer = audio_data
            st.session_state.active_filename = f"{selection}_{'female' if 'Female' in gender else 'male'}.mp3"
            status.update(label="✅ Success! Neural Audio Generated", state="complete")
            
        except Exception as e:
            st.error(f"Generation Error: {e}")

# 4. DOWNLOAD
if "audio_buffer" in st.session_state and st.session_state.audio_buffer:
    st.divider()
    st.write(f"### Ready: {st.session_state.active_filename}")
    st.audio(st.session_state.audio_buffer, format="audio/mp3")
    st.download_button(
        label="💾 SAVE MP3 FILE",
        data=st.session_state.audio_buffer,
        file_name=st.session_state.active_filename,
        mime="audio/mpeg"
    )
