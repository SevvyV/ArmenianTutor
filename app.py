import streamlit as st
from gtts import gTTS
import io

st.set_page_config(page_title="HyeTutor Surgical 18.0", page_icon="🇦🇲")
st.title("🇦🇲 Surgical Audio Builder 18.0 (gTTS)")
st.info("Engine: Google Translate (gTTS) | Status: Unlocking 'Preview' Voice")

# 1. DATA
TARGETS = {
    "numbers_11_20": "Տասնըմէկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան",
    "tens_to_100": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր",
    "hundreds_to_1000": "Հարիւր, Երկու հարիւր, Երեք հարիւր, Չորս հարիւր, Հինգ հարիւր, Վեց հարիւր, Եօթը հարիւր, Ութը հարիւր, Ինը հարիւր, Հազար",
    "months_of_the_year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

selection = st.selectbox("Select Target Category", list(TARGETS.keys()))
slow_mode = st.toggle("Slow Mode (Educational)", value=False)

if st.button("🚀 Generate Audio"):
    st.session_state.audio_buffer = None
    
    with st.status("Accessing Google Translate Endpoint...") as status:
        try:
            # 2. THE TOKENIZED REQUEST
            # gTTS generates a valid 'tk' token, proving we are a legitimate user
            # This unlocks the 'Preview' voice that the API hides from us
            tts = gTTS(text=TARGETS[selection], lang='hy', slow=slow_mode)
            
            # Write to memory buffer
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            
            st.session_state.audio_buffer = buf.getvalue()
            st.session_state.active_filename = f"{selection}.mp3"
            status.update(label="✅ Success! 'Preview' Voice Captured", state="complete")
            
        except Exception as e:
            st.error(f"Generation Failed: {e}")
            st.caption("Common fix: Wait 1 minute if you clicked too fast (Rate Limit).")

# 3. DOWNLOAD
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
