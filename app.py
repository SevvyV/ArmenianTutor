import streamlit as st
from google import genai
from google.genai import types
import wave
import io

# 1. Page Configuration
st.set_page_config(page_title="HyeTutor2.0beta", page_icon="🇦🇲", layout="wide")

# --- EXPANDED DATA STRUCTURES ---
PRONOUNS = ["Ես (I)", "Դուն (You)", "Ան (He/She/It)", "Մենք (We)", "Դուք (You pl.)", "Անոնք (They)"]

# Pre-loaded Verb Bank
VERB_BANK = {
    "Վազել (To Run)": {
        "Past": ["Ես վազեցի", "Դուն վազեցիր", "Ան վազեց", "Մենք վազեցինք", "Դուք վազեցիք", "Անոնք վազեցին"],
        "Present": ["Ես կը վազեմ", "Դուն կը վազես", "Ան կը վազէ", "Մենք կը վազենք", "Դուք կը վազէք", "Անոնք կը վազեն"],
        "Future": ["Ես պիտի վազեմ", "Դուն պիտի վազես", "Ան պիտի վազէ", "Մենք պիտի վազենք", "Դուք պիտի վազէք", "Անոնք պիտի վազեն"]
    },
    "Ուտել (To Eat)": {
        "Past": ["Ես կերայ", "Դուն կերար", "Ան կերաւ", "Մենք կերանք", "Դուք կերաք", "Անոնք կերան"],
        "Present": ["Ես կ'ուտեմ", "Դուն կ'ուտես", "Ան կ'ուտէ", "Մենք կ'ուտենք", "Դուք կ'ուտէք", "Անոնք կ'ուտեն"],
        "Future": ["Ես պիտի ուտեմ", "Դուն պիտի ուտես", "Ան պիտի ուտէ", "Մենք պիտի ուտենք", "Դուք պիտի ուտէք", "Անոնք պիտի ուտեն"]
    },
    "Խմել (To Drink)": {
        "Past": ["Ես խմեցի", "Դուն խմեցիր", "Ան խմեց", "Մենք խմեցինք", "Դուք խմեցիք", "Անոնք խմեցին"],
        "Present": ["Ես կը խմեմ", "Դուն կը խմես", "Ան կը խմէ", "Մենք կը խմենք", "Դուք կը խմէք", "Անոնք կը խմեն"],
        "Future": ["Ես պիտի խմեմ", "Դուն պիտի խմես", "Ան պիտի խմէ", "Մենք պիտի խմենք", "Դուք պիտի խմէք", "Անոնք պիտի խմեն"]
    }
}

# 2. Sidebar Navigation
with st.sidebar:
    st.title("🎓 HyeTutor2.0beta")
    st.subheader("Interactive Lessons")
    lesson_mode = st.radio("Choose Mode:", ["Verb Bank", "Custom Verb Search", "Foundations"])
    
    if lesson_mode == "Verb Bank":
        verb_choice = st.selectbox("Select a Verb:", list(VERB_BANK.keys()))
        tense_choice = st.radio("Select Tense:", ["Past", "Present", "Future"])
    
    elif lesson_mode == "Custom Verb Search":
        custom_verb = st.text_input("Enter an English Verb (e.g. 'to sleep')")
        tense_choice = st.radio("Select Tense:", ["Past", "Present", "Future"])

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

# 4. Custom Verb Generator Logic
def get_custom_conjugation(verb, tense):
    prompt = f"Translate the verb '{verb}' to Western Armenian infinitive and conjugate it for the {tense} tense with all 6 personal pronouns. Return ONLY the list of 6 phrases separated by commas."
    response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
    return response.text.split(",")

# 5. Main Content Area
st.title("🇦🇲 Elite Western Armenian Learning Lab")

current_drill = []

if lesson_mode == "Verb Bank":
    current_drill = VERB_BANK[verb_choice][tense_choice]
    st.header(f"Mastering: {verb_choice}")
    
elif lesson_mode == "Custom Verb Search" and custom_verb:
    with st.spinner("Tutor is generating custom conjugation..."):
        current_drill = get_custom_conjugation(custom_verb, tense_choice)
    st.header(f"Mastering: {custom_verb}")

# Display Drill
if current_drill:
    st.subheader(f"Pronoun + Verb ({tense_choice})")
    display_str = " • ".join(current_drill)
    st.write(f"### {display_str}")
    
    if st.button("🔊 Listen to native pronunciation"):
        speak_text(", ".join(current_drill))

st.divider()

# 6. Microphone Interaction
audio_data = st.audio_input("Tap to repeat the full conjugation")

if audio_data:
    ELITE_INSTRUCTIONS = f"IDENTITY: Elite Western Armenian Tutor. USER TASK: Repeat the conjugation {current_drill}. Listen for pronoun agreement and correct verb ending."
    
    with st.status("Analyzing your accent..."):
        try:
            audio_part = types.Part.from_bytes(data=audio_data.read(), mime_type="audio/wav")
            analysis = client.models.generate_content(
                model="gemini-3-flash-preview", 
                config={'system_instruction': ELITE_INSTRUCTIONS},
                contents=[audio_part]
            )
            st.success("Tutor's Feedback:")
            st.markdown(analysis.text)
            speak_text(analysis.text.split("\n")[0])
        except Exception as e:
            st.error(f"Error: {e}")
