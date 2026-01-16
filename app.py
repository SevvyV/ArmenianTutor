import streamlit as st
from google import genai
from google.genai import types
import wave
import io

# 1. Page Configuration
st.set_page_config(page_title="HyeTutor2.0beta", page_icon="🇦🇲", layout="wide")

st.title("🇦🇲 HyeTutor2.0beta")
st.caption("Version 3.4 • Cleaned Navigation Logic")

# --- FOUNDATIONS DATA ---
FOUNDATIONS = {
    "📅 Days of the Week": "Երկուշաբթի (Yerkushapti), Երեքշաբթի (Yerekshapti), Չորեքշաբթի (Chorekshapti), Հինգշաբթի (Hingshapti), Ուրբաթ (Urpatt), Շաբաթ (Shapat), Կիրակի (Giragi)",
    "🔢 Numbers (1-10)": "Մէկ (Meg), Երկու (Yergu), Երեք (Yerek), Չորս (Chors), Հինգ (Hink), Վեց (Vets), Եօթը (Yote), Ութը (Oote), Ինը (Ine), Տասը (Dase)",
    "🗓️ Months of the Year": "Յունուար (Hoonvar), Փետրուար (Pedervar), Մարտ (Mard), Ապրիլ (Abreel), Մայիս (Mayis), Յունիս (Hooneess), Յուլիս (Hooleess), Օգոստոս (Okosdos), Սեպտեմբեր (Sebdemper), Հոկտեմբեր (Hogdemper), Նոյեմբեր (Noyemper), Դեկտեմբեր (Tegdemper)"
}

# --- TOP 50 VERB LIST ---
TOP_50_VERBS = [
    "be", "have", "do", "say", "go", "can", "get", "would", "make", "know",
    "will", "think", "take", "see", "come", "could", "want", "look", "use",
    "find", "give", "tell", "work", "may", "should", "call", "try", "ask",
    "need", "feel", "become", "leave", "put", "mean", "keep", "let", "begin",
    "seem", "help", "talk", "turn", "start", "might", "show", "hear", "play",
    "run", "move", "like", "live"
]

# 2. Key Verification & Audio Utils
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

# 3. Dynamic Conjugator Logic
@st.cache_data
def get_conjugation(verb_name, tense_name):
    prompt = f"Conjugate the Western Armenian verb for '{verb_name}' in {tense_name} tense with all 6 pronouns (Ես, Դուն, Ան, Մենք, Դուք, Անոնք). Return as a comma-separated list."
    response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
    return response.text.strip().split(",")

# 4. Sidebar: Master Navigation with Improved Logic
with st.sidebar:
    st.header("🎓 Learning Plan")
    main_mode = st.selectbox("Select Learning Category:", ["Foundations", "Top 50 Verbs", "Custom Search"])
    
    st.divider()
    
    # Logic: Only show secondary options relevant to the current mode
    if main_mode == "Foundations":
        sub_selection = st.selectbox("Choose Foundation:", list(FOUNDATIONS.keys()))
        selected_content = FOUNDATIONS[sub_selection]
        mode_label = sub_selection
        tense = None # Not used in foundations
        
    elif main_mode == "Top 50 Verbs":
        sub_selection = st.selectbox("Select Verb:", TOP_50_VERBS)
        tense = st.selectbox("Tense:", ["Past", "Present", "Future"])
        mode_label = f"{sub_selection} ({tense})"
        
    elif main_mode == "Custom Search":
        sub_selection = st.text_input("Type any English verb:", "to sing")
        tense = st.selectbox("Tense:", ["Past", "Present", "Future"])
        mode_label = f"{sub_selection} ({tense})"

# 5. Main Content Logic
if main_mode == "Foundations":
    st.header(mode_label)
    # Highlight the Western Armenian script
    st.info("Listen and repeat the full sequence.")
    st.write(f"### {selected_content}")
    
    if st.button(f"🔊 Listen to Native Pronunciation"):
        # We strip the English phonetics (in brackets) for the voice engine
        armenian_only = selected_content.split("(")[0].strip() if "(" in selected_content else selected_content
        speak_text(selected_content)

else:
    # Verb Modes
    if sub_selection:
        with st.spinner(f"Generating lesson for {sub_selection}..."):
            conjugation_list = get_conjugation(sub_selection, tense)
        st.header(f"Verb Practice: {sub_selection}")
        st.subheader(f"Focus: {tense} Tense with Pronouns")
        
        # Display verbs in a clean grid
        cols = st.columns(3)
        for i, item in enumerate(conjugation_list):
            cols[i % 3].write(f"🔹 **{item.strip()}**")
            
        if st.button("🔊 Listen and Model"):
            speak_text(", ".join(conjugation_list))

st.divider()

# 6. Global Practice Interaction
audio_data = st.audio_input("Practice your pronunciation")

if audio_data:
    instruct = f"IDENTITY: Elite Western Armenian Tutor. Task: Analyze the user's pronunciation of {mode_label}."
    with st.status("Analyzing..."):
        try:
            audio_part = types.Part.from_bytes(data=audio_data.read(), mime_type="audio/wav")
            analysis = client.models.generate_content(
                model="gemini-3-flash-preview", 
                config={'system_instruction': instruct},
                contents=[audio_part]
            )
            st.success("Tutor's Evaluation:")
            st.markdown(analysis.text)
            # Auto-speak the first line of feedback
            speak_text(analysis.text.split("\n")[0])
        except Exception as e:
            st.error(f"Recording Error: {e}")
