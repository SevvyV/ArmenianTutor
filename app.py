import streamlit as st
from google import genai
from google.genai import types
import wave
import io

# 1. Page Configuration
st.set_page_config(page_title="HyeTutor2.0beta", page_icon="🇦🇲", layout="wide")

st.title("🇦🇲 HyeTutor2.0beta")
st.caption("Version 3.7 • Pronouns Restored • Guided Top 50 • Foundations • Slow-Mo & Reset")

# --- DATA: FOUNDATIONS & TOP 50 ---
FOUNDATIONS = {
    "📅 Days of the Week": "Երկուշաբթի, Երեքշաբթի, Չորեքշաբթի, Հինգշաբթի, Ուրբաթ, Շաբաթ, Կիրակի",
    "🔢 Numbers (1-10)": "Մէկ, Երկու, Երեք, Չորս, Հինգ, Վեց, Եօթը, Ութը, Ինը, Տասը",
    "🗓️ Months of the Year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

TOP_50_VERBS = [
    "be", "have", "do", "say", "go", "can", "get", "would", "make", "know",
    "will", "think", "take", "see", "come", "could", "want", "look", "use",
    "find", "give", "tell", "work", "may", "should", "call", "try", "ask",
    "need", "feel", "become", "leave", "put", "mean", "keep", "let", "begin",
    "seem", "help", "talk", "turn", "start", "might", "show", "hear", "play",
    "run", "move", "like", "live"
]

# 2. Key Verification
api_key = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=api_key)

# 3. Audio Utility Functions (Manual WAV Header Logic)
def create_wav_file(pcm_data):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) 
        wf.setframerate(24000)
        wf.writeframes(pcm_data)
    return buf.getvalue()

@st.cache_data(show_spinner=False)
def get_cached_audio(text_to_speak, slow_mode=False):
    speed_instruction = "slowly and clearly" if slow_mode else "at a natural pace"
    try:
        tts_response = client.models.generate_content(
            model="gemini-2.5-flash-lite-preview-tts",
            contents=f"Say this {speed_instruction} in Western Armenian: {text_to_speak}",
            config=types.GenerateContentConfig(response_modalities=["AUDIO"])
        )
        for part in tts_response.candidates[0].content.parts:
            if part.inline_data:
                return create_wav_file(part.inline_data.data)
    except:
        return None
    return None

# 4. Sidebar: Master Navigation (Logic Preserved)
with st.sidebar:
    st.header("🎓 Learning Plan")
    main_mode = st.selectbox("Select Learning Category:", ["Foundations", "Top 50 Verbs", "Custom Search"])
    
    st.divider()
    
    # Feature Preservation: Slow-Motion Toggle
    slow_audio = st.toggle("🐢 Slow-Motion Audio", value=False)
    
    if main_mode == "Foundations":
        sub_selection = st.selectbox("Choose Foundation:", list(FOUNDATIONS.keys()))
        selected_content = FOUNDATIONS[sub_selection]
        mode_label = sub_selection
    elif main_mode == "Top 50 Verbs":
        sub_selection = st.selectbox("Select Verb:", TOP_50_VERBS)
        tense = st.selectbox("Tense:", ["Past", "Present", "Future"])
        mode_label = f"{sub_selection} ({tense})"
    else:
        sub_selection = st.text_input("Type any English verb:", "to sing")
        tense = st.selectbox("Tense:", ["Past", "Present", "Future"])
        mode_label = f"{sub_selection} ({tense})"

    st.divider()
    # Feature Preservation: Reset Button
    if st.button("🔄 Reset Session", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 5. Dynamic Conjugator Logic (Strict Pronoun Enforcement)
@st.cache_data
def get_conjugation(verb_name, tense_name):
    # Prompt explicitly asks for pronouns to prevent model "shortcuts"
    prompt = f"""
    Translate '{verb_name}' into Western Armenian.
    Conjugate it for the {tense_name} tense.
    You MUST include the personal pronouns in this exact order:
    Ես, Դուն, Ան, Մենք, Դուք, Անոնք.
    Return ONLY a comma-separated list of the 6 conjugated phrases.
    Example: Ես վազեցի, Դուն վազեցիր, Ան վազեց, Մենք վազեցինք, Դուք վազեցիք, Անոնք վազեցին
    """
    response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
    return response.text.strip().split(",")

# 6. Main Lesson Area
if main_mode == "Foundations":
    st.header(mode_label)
    st.write(f"### {selected_content}")
    if st.button(f"🔊 Listen"):
        audio_bytes = get_cached_audio(selected_content, slow_mode=slow_audio)
        if audio_bytes: st.audio(audio_bytes, format="audio/wav")
else:
    if sub_selection:
        with st.spinner(f"Tutor is conjugating '{sub_selection}'..."):
            conjugation_list = get_conjugation(sub_selection, tense)
        st.header(f"Verb: {sub_selection}")
        # Feature Preservation: Pronoun Grid Layout
        cols = st.columns(3)
        for i, item in enumerate(conjugation_list):
            cols[i % 3].write(f"🔹 **{item.strip()}**")
        if st.button("🔊 Listen"):
            audio_bytes = get_cached_audio(", ".join(conjugation_list), slow_mode=slow_audio)
            if audio_bytes: st.audio(audio_bytes, format="audio/wav")

st.divider()

# 7. Global Practice Interaction
audio_data = st.audio_input("Practice and get feedback")
if audio_data:
    with st.status("Analyzing..."):
        audio_part = types.Part.from_bytes(data=audio_data.read(), mime_type="audio/wav")
        analysis = client.models.generate_content(
            model="gemini-3-flash-preview", 
            config={'system_instruction': f"Analyze pronunciation of {mode_label}. Provide feedback in English with Armenian phonetic examples."},
            contents=[audio_part]
        )
        st.success("Tutor's Evaluation:")
        st.markdown(analysis.text)
        # Speak the summary line
        speak_bytes = get_cached_audio(analysis.text.split("\n")[0])
        if speak_bytes: st.audio(speak_bytes, format="audio/wav")
