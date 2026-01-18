import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from deep_translator import GoogleTranslator

# 👇 IMPORT YOUR DATA HERE (From the new data.py file)
from data import (
    days_data, months_data, nums_1_10_data, nums_11_20_data, tens_data, 
    family_data, verb_data, verb_list
)

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(page_title="HyeTutor", page_icon="🇦🇲", layout="wide")

st.markdown("""
    <style>
    div.stButton > button {
        width: 100%; border-radius: 5px; height: 3em; background-color: #ffffff; border: 1px solid #d1d3d8;
    }
    div.stButton > button:hover { border: 1px solid #007bff; color: #007bff; }
    .big-font { font-size: 32px !important; line-height: 1.6; color: #007bff; font-weight: bold; }
    .label-font { font-size: 18px; color: #666; }
    .translation-font { font-size: 24px; color: #28a745; font-style: italic; }
    .big-table { font-size: 24px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---
def play_audio(filename):
    # ⚠️ POINTING TO DEV BRANCH
    base_url = "https://raw.githubusercontent.com/SevvyV/ArmenianTutor/dev/audio_library"
    # Simplified logic: Everything is in the root folder now
    url = f"{base_url}/{filename}.mp3"
    st.audio(url, format="audio/mp3")

def get_live_speech(text, voice_name):
    try:
        if "SPEECH_KEY" not in st.secrets: return "MISSING_KEYS"
        key = st.secrets["SPEECH_KEY"]
        region = st.secrets["SPEECH_REGION"]
        speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
        
        voice_map = {"Anahit (Female)": "hy-AM-AnahitNeural", "Hayk (Male)": "hy-AM-HaykNeural"}
        speech_config.speech_synthesis_voice_name = voice_map.get(voice_name, "hy-AM-AnahitNeural")
        
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        ssml = f"<speak version='1.0' xml:lang='hy-AM'><voice name='{voice_map[voice_name]}'>{text}</voice></speak>"
        result = synthesizer.speak_ssml_async(ssml).get()
        return result.audio_data if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted else f"ERROR: {result.reason}"
    except Exception as e:
        return f"CRASH: {str(e)}"

def vocab_expander(data):
    with st.expander("📖 View Vocabulary"):
        md_table = "| English | Armenian | Phonetic |\n| :--- | :--- | :--- |\n"
        for eng, arm, phon in data:
            md_table += f"| {eng} | **{arm}** | *{phon}* |\n"
        st.markdown(md_table)

# --- 3. NAVIGATION ---
with st.sidebar:
    st.title("🇦🇲 HyeTutor")
    mode = st.radio("Navigate:", ["Audio Gym", "Lesson 1: Greetings", "Lesson 2: Family", "Verb Center", "AI Playground"])
    st.divider()
    st.caption("Version 3.0 (Modular Build - Dev)")

# --- 4. PAGE LOGIC ---

if mode == "Audio Gym":
    st.header("🏋️ Audio Gym")
    st.markdown("Repetition drills for numbers, dates, and time.")
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📅 Calendar")
        st.write("**Days of the Week**"); play_audio("drill_days_of_week"); vocab_expander(days_data)
        st.write("**Months of the Year**"); play_audio("drill_months_of_year"); vocab_expander(months_data)
    with col2:
        st.subheader("🔢 Numbers")
        st.write("**1 - 10**"); play_audio("drill_numbers_1_10"); vocab_expander(nums_1_10_data)
        st.write("**11 - 20**"); play_audio("drill_numbers_11_20"); vocab_expander(nums_11_20_data)
        st.write("**10 - 100**"); play_audio("drill_tens_10_100"); vocab_expander(tens_data)

elif mode == "Lesson 1: Greetings":
    st.header("👋 Lesson 1: Basic Greetings")
    st.divider()
    play_audio("lesson_01_greetings")
    st.subheader("📝 Vocabulary")
    st.markdown("""| English | Armenian (Western) | Phonetic |
| :--- | :--- | :--- |
| Hello | **Բարեւ** | *Parev* |
| How are you? | **Ինչպէ՞ս ես** | *Inchbes es?* |
| I am well | **Լաւ եմ** | *Lav em* |
| Thank you | **Շնորհակալ եմ** | *Shnorhagal em* |
| Goodbye | **Ցտեսութիւն** | *Tsedesutyun* |""")

elif mode == "Lesson 2: Family":
    st.header("👪 Lesson 2: Family Members")
    st.divider()
    play_audio("lesson_02_family") 
    vocab_expander(family_data)

elif mode == "Verb Center":
    st.header("🏃 Verb Conjugation Center")
    if 'current_tense' not in st.session_state: st.session_state.current_tense = 'present'
    verb_choice = st.selectbox("1. Select a Verb:", verb_list)
    tcol1, tcol2, tcol3 = st.columns(3)
    with tcol1: 
        if st.button("📍 Present"): st.session_state.current_tense = 'present'
    with tcol2:
        if st.button("🕰️ Past"): st.session_state.current_tense = 'past'
    with tcol3:
        if st.button("🚀 Future"): st.session_state.current_tense = 'future'
    
    active_tense = st.session_state.current_tense
    
    # ROBUST CLEANUP: Handles "—" (Em Dash) and "-" (Hyphen)
    english_label = verb_choice.split('—')[0].split('-')[0].strip()
    clean_name = english_label.lower().replace(" ", "_")
    
    st.subheader(f"{english_label} — {active_tense.capitalize()}")
    play_audio(f"verb_{clean_name}_{active_tense}")
    
    st.markdown('<div class="big-table">', unsafe_allow_html=True)
    
    if clean_name in verb_data:
        display_list = verb_data[clean_name][active_tense]
        pronouns_eng = ["I", "You", "He/She", "We", "You pl.", "They"]
        pronouns_arm = ["Ես", "Դուն", "Ան", "Մենք", "Դուք", "Անոնք"]
        
        table_html = "| English | Pronoun | Conjugation |\n| :--- | :--- | :--- |\n"
        for i in range(6):
            table_html += f"| {pronouns_eng[i]} | **{pronouns_arm[i]}** | {display_list[i]} |\n"
        st.markdown(table_html)
    else:
        st.info(f"Conjugation text coming soon for: {clean_name}")
    st.markdown('</div>', unsafe_allow_html=True)

elif mode == "AI Playground":
    st.header("🧪 AI Playground")
    st.write("Translate and speak phrases in Western Armenian.")
    
    col1, col2 = st.columns(2)
    with col1:
        input_mode = st.radio("Translation Mode:", ["English ➡️ Armenian", "Armenian ➡️ English"])
    with col2:
        voice_choice = st.radio("Select Voice:", ["Anahit (Female)", "Hayk (Male)"])
    
    user_input = st.text_area("Type your phrase here:", placeholder="Type here...")
    
    if st.button("🔊 Translate & Speak"):
        if user_input:
            with st.spinner(f"{voice_choice.split(' ')[0]} is thinking..."):
                if "English ➡️ Armenian" in input_mode:
                    armenian_text = GoogleTranslator(source='en', target='hy').translate(user_input)
                    st.markdown(f'<p class="label-font">Armenian Spelling:</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="big-font">{armenian_text}</p>', unsafe_allow_html=True)
                else:
                    english_text = GoogleTranslator(source='hy', target='en').translate(user_input)
                    armenian_text = user_input
                    st.markdown(f'<p class="label-font">English Meaning:</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="translation-font">{english_text}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="label-font">Armenian Input:</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="big-font">{armenian_text}</p>', unsafe_allow_html=True)
                
                audio_response = get_live_speech(armenian_text, voice_choice)
                if isinstance(audio_response, bytes):
                    st.audio(audio_response, format="audio/mp3")
                else:
                    st.error(f"Speech Error: {audio_response}")
        else:
            st.warning("Please enter text first.")
