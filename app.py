import streamlit as st
import os

st.set_page_config(page_title="HyeTutor2.0beta", page_icon="🇦🇲", layout="wide")
st.title("🇦🇲 HyeTutor2.0beta")
st.caption("Version 7.2 • Production Ready • GitHub Linked")

# --- PATH CONFIGURATION ---
# Streamlit Cloud looks at your GitHub folder structure
AUDIO_DIR = "audio_library"

FOUNDATIONS = {
    "days_of_the_week": "📅 Days of the Week",
    "numbers_1_10": "🔢 Numbers (1-10)",
    "months_of_the_year": "🗓️ Months of the Year",
    "tens_to_100": "🔟 Counting by 10s (to 100)"
}

st.header("📖 Foundations")
st.info("Select a category. If the audio is in our GitHub library, it will play instantly.")

# UI Layout
col1, col2 = st.columns([1, 2])

with col1:
    selection = st.radio("Category:", list(FOUNDATIONS.keys()), format_func=lambda x: FOUNDATIONS[x])
    slow_mode = st.toggle("🐢 Slow Mode")

with col2:
    speed = "slow" if slow_mode else "fast"
    filename = f"{selection}_{speed}.wav"
    file_path = os.path.join(AUDIO_DIR, filename)
    
    st.subheader(FOUNDATIONS[selection])
    
    # Check if the file exists in the GitHub folder
    if os.path.isfile(file_path):
        st.success(f"Audio Found: {filename}")
        st.audio(file_path)
    else:
        st.warning(f"Audio missing from library: {filename}")
        st.write("We will build this file once the daily API quota resets.")

st.divider()
st.caption("Note: Phrase Translator is still available in the sidebar.")
