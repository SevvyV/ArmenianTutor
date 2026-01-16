import streamlit as st
from google import genai
from google.genai import types
import wave
import io

# 1. Page Configuration
st.set_page_config(page_title="HyeTutor2.0beta", page_icon="🇦🇲", layout="wide")

st.title("🇦🇲 HyeTutor2.0beta")
st.caption("Version 3.2 • Guided Curriculum: Top 50 Essential Verbs")

# 2. Top 50 Verb List (The Roadmap)
TOP_50_VERBS = [
    "be", "have", "do", "say", "go", "can", "get", "would", "make", "know",
    "will", "think", "take", "see", "come", "could", "want", "look", "use",
    "find", "give", "tell", "work", "may", "should", "call", "try", "ask",
    "need", "feel", "become", "leave", "put", "mean", "keep", "let", "begin",
    "seem", "help", "talk", "turn", "start", "might", "show", "hear", "play",
    "run", "move", "like", "live"
]

# 3. Key Verification & Audio Utils
api_key = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=api_key)

def create_wav_file(pcm_data):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) 
        wf.setframerate(24000)
        wf.writeframes(pcm_data)
    return buf.getvalue()

def speak_text(text_to_speak):
    try:
        tts_response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=f"Read this clearly in Western Armenian: {text_to_speak}",
            config=types.GenerateContentConfig(response_modalities=["AUDIO"])
        )
        for part in tts_response.candidates[0].content.parts:
            if part.inline_data:
                st.audio(create_wav_file(part.inline_data.data), format="audio/wav")
    except:
        st.warning("Tutor voice engine loading...")

# 4. Sidebar: Guided Lesson Plan
with st.sidebar:
    st.header("🎓 Guided Lessons")
    lesson_mode = st.radio("Mode:", ["Top 50 List", "Search Any Verb", "Foundations"])
    
    if lesson_mode == "Top 50 List":
        selected_verb = st.selectbox("Select a Verb:", TOP_50_VERBS)
    elif lesson_mode == "Search Any Verb":
        selected_verb = st.text_input("Type a verb:", "to dance")
    else:
        selected_verb = None
        
    tense = st.selectbox("Tense:", ["Past", "Present", "Future"])
    st.divider()
    if st.button("Reset Session"):
        st.session_state.chat_history = []
        st.rerun()

# 5. Dynamic Conjugator with Pronouns
@st.cache_data
def get_conjugation(verb_name, tense_name):
    prompt = f"""
    Translate the English verb '{verb_name}' into Western Armenian.
    Then, conjugate it for the {tense_name} tense using all 6 Western Armenian pronouns:
    Ես, Դուն, Ան, Մենք, Դուք, Անոնք.
    Format your response EXACTLY as a list of 6 strings, separated by commas.
    Example: Ես վազեցի, Դուն վազեցիր, Ան վազեց, Մենք վազեցինք, Դուք վազեցիք, Անոնք վազեցին
    """
    response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
    return response.text.strip().split(",")

# 6. Main Interaction Area
if selected_verb:
    with st.spinner(f"Preparing lesson for '{selected_verb}'..."):
        conjugation_list = get_conjugation(selected_verb, tense)
    
    st.header(f"Mastering: '{selected_verb}'")
    st.subheader(f"Lesson: {tense} Tense with Pronouns")
    
    # Display verbs in a clean grid
    cols = st.columns(3)
    for i, item in enumerate(conjugation_list):
        cols[i % 3].write(f"🔹 **{item.strip()}**")
        
    if st.button("🔊 Listen and Model Pronunciation"):
        speak_text(", ".join(conjugation_list))

    st.divider()

    # 7. Practice & Analysis
    audio_data = st.audio_input("Repeat the sequence above for feedback")

    if audio_data:
        instruction = f"IDENTITY: Elite Western Armenian Tutor. Task: Analyze pronunciation for the sequence {conjugation_list}."
        with st.status("Tutor is analyzing..."):
            audio_part = types.Part.from_bytes(data=audio_data.read(), mime_type="audio/wav")
            analysis = client.models.generate_content(
                model="gemini-3-flash-preview", 
                config={'system_instruction': instruction},
                contents=[audio_part]
            )
            st.success("Tutor's Evaluation:")
            st.markdown(analysis.text)
            # Speak only the summary Armenian feedback
            speak_text(analysis.text.split("\n")[0])
