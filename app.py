import streamlit as st
from google import genai
from google.genai import types
import wave
import io

# 1. Page Configuration
st.set_page_config(page_title="HyeTutor2.0beta", page_icon="🇦🇲", layout="wide")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- EXTENDED CURRICULUM DATA ---
TOPICS = {
    "📅 Days of the Week": "Երկուշաբթի, Երեքշաբթի, Չորեքշաբթի, Հինգշաբթի, Ուրբաթ, Շաբաթ, Կիրակի",
    "🔢 Numbers (1-10)": "Մէկ, Երկու, Երեք, Չորս, Հինգ, Վեց, Եօթը, Ութը, Ինը, Տասը",
    "🗓️ Months of the Year": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
}

# --- VERB CONJUGATION ENGINE (Top 100 Sample) ---
# Format: { Verb: { Tense: "I, You, He/She, We, You(pl), They" } }
VERBS = {
    "Վազել (To Run)": {
        "Past": "Վազեցի, Վազեցիր, Վազեց, Վազեցինք, Վազեցիք, Վազեցին",
        "Present": "Կը վազեմ, Կը վազես, Կը վազէ, Կը վազենք, Կը վազէք, Կը վազեն",
        "Future": "Պիտի վազեմ, Պիտի վազես, Պիտի վազէ, Պիտի վազենք, Պիտի վազէք, Պիտի վազեն"
    },
    "Ուտել (To Eat)": {
        "Past": "Կերայ, Կերար, Կերաւ, Կերանք, Կերաք, Կերան",
        "Present": "Կ'ուտեմ, Կ'ուտես, Կ'ուտէ, Կ'ուտենք, Կ'ուտէք, Կ'ուտեն",
        "Future": "Պիտի ուտեմ, Պիտի ուտես, Պիտի ուտէ, Պիտի ուտենք, Պիտի ուտէք, Պիտի ուտեն"
    }
}

# 2. Sidebar Navigation
with st.sidebar:
    st.title("🎓 Learning Plan")
    
    st.subheader("Foundations")
    selected_topic = st.selectbox("Topic Lessons:", ["Choose a Topic"] + list(TOPICS.keys()))
    
    st.divider()
    
    st.subheader("Verb Mastery")
    verb_choice = st.selectbox("Select a Verb:", ["Choose a Verb"] + list(VERBS.keys()))
    tense_choice = st.radio("Tense:", ["Past", "Present", "Future"])
    
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# 3. Key Verification
api_key = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=api_key)

# 4. Helper Function: Audio Packaging
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
            contents=f"Read this Western Armenian text slowly and clearly: {text_to_speak}",
            config=types.GenerateContentConfig(response_modalities=["AUDIO"])
        )
        for part in tts_response.candidates[0].content.parts:
            if part.inline_data:
                wav_bytes = create_wav_file(part.inline_data.data)
                st.audio(wav_bytes, format="audio/wav")
    except:
        st.warning("Voice engine initializing...")

# 5. Main UI Logic
st.title("🇦🇲 HyeTutor2.0beta")

# Logic for Verb Practice
if verb_choice != "Choose a Verb":
    drill_text = VERBS[verb_choice][tense_choice]
    st.header(f"Practice: {verb_choice} ({tense_choice} Tense)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### The Drill:\n{drill_text}")
        if st.button("🔊 Listen to Drill"):
            speak_text(drill_text)
    
    with col2:
        st.info("Tap the mic and repeat the full sequence: I, You, He/She, We, You(pl), They.")

elif selected_topic != "Choose a Topic":
    st.header(selected_topic)
    st.write(f"**Content:** {TOPICS[selected_topic]}")
    if st.button(f"🔊 Listen"):
        speak_text(TOPICS[selected_topic])

# 6. Interaction Protocol
audio_data = st.audio_input("Record your practice")

if audio_data:
    # Determine context for the AI
    mode_context = f"The user is practicing the verb {verb_choice} in the {tense_choice} tense." if verb_choice != "Choose a Verb" else f"The user is practicing {selected_topic}."
    
    ELITE_INSTRUCTIONS = f"""
    IDENTITY: Elite Western Armenian Tutor.
    CONTEXT: {mode_context}
    TASK: Listen to the user's pronunciation of the sequence. 
    1. Correct any specific vowel or consonant slips.
    2. Provide a 1-10 'Native Accent' score.
    3. If they missed a person (e.g. they forgot 'We ran'), point it out.
    FORMAT: Armenian Script, Phonetic, then English Feedback.
    """

    with st.status("Analyzing pronunciation..."):
        try:
            audio_part = types.Part.from_bytes(data=audio_data.read(), mime_type="audio/wav")
            analysis = client.models.generate_content(
                model="gemini-3-flash-preview", 
                config={'system_instruction': ELITE_INSTRUCTIONS},
                contents=[audio_part]
            )
            st.success("Tutor's Feedback:")
            st.markdown(analysis.text)
            
            # Auto-speak the tutor's summary
            speak_text(analysis.text.split("\n")[0])
        except Exception as e:
            st.error(f"Error: {e}")
