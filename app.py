import streamlit as st
import requests
import io
import urllib.parse

st.set_page_config(page_title="HyeTutor Surgical 17.0", page_icon="🇦🇲")
st.title("🇦🇲 Surgical Audio Builder 17.0 (Google Translate)")
st.info("Engine: Google Translate (Web Endpoint) | Voice: Armenian (Standard)")

# 1. DATA
TARGETS = {
    "numbers_11_20": "Տասնըմէկ, Տասնըերկու, Տասնըերեք, Տասնըչորս, Տասնըհինգ, Տասնըվեց, Տասնըեօթը, Տասնըութը, Տասնըինը, Քսան",
    "tens_to_100": "Տասը, Քսան, Երեսուն, Քառասուն, Հիսուն, Վաթսուն, Եօթանասուն, Ութսուն, Իննսուն, Հարիւր",
    "hundreds_to_1000": "Հարիւր, Երկու հարիւր, Երեք հարիւր, Չորս հարիւր, Հինգ հարիւր, Վեց հարիւր, Եօթը հարիւր, Ութը հարիւր, Ինը հարիւր, Հազար",
    "months_of_the_year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

selection = st.selectbox("Select Target Category", list(TARGETS.keys()))

if st.button("🚀 Fetch Google Translate Audio"):
    st.session_state.audio_buffer = None
    
    with st.status("Requesting Audio from Google Translate...") as status:
        try:
            # 2. THE "BACKDOOR" REQUEST
            # We hit the internal API used by the Google Translate website
            text = urllib.parse.quote(TARGETS[selection])
            url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl=hy&client=tw-ob"
            
            # Use standard headers to look like a browser
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                st.session_state.audio_buffer = response.content
                st.session_state.active_filename = f"{selection}.mp3"
                status.update(label="✅ Success! Audio Captured", state="complete")
            else:
                st.error(f"Google Refused Connection ({response.status_code})")
                
        except Exception as e:
            st.error(f"Connection Error: {e}")

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
