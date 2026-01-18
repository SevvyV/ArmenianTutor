import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from deep_translator import GoogleTranslator
import requests

# 👇 IMPORT YOUR DATA (Ensure data.py is updated first!)
from data import (
    days_data, months_data, nums_1_10_data, nums_11_20_data, tens_data, 
    family_data, verb_data, verb_list,
    # New Lists
    kitchen_data, food_data, furniture_data, animals_data, objects_data
)

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(page_title="HyeTutor Dev", page_icon="🇦🇲", layout="wide")

st.markdown("""
    <style>
    div.stButton > button {
        width: 100%; border-radius: 5px; height: 3em; background-color: #ffffff; border: 1px solid #d1d3d8;
    }
    div.stButton > button:hover { border: 1px solid #007bff; color: #007bff; }
    .big-font { font-size: 32px !important; line-height: 1.6; color: #007bff; font-weight: bold; }
    .label-font { font-size: 18px; color: #666; }
    .translation-font { font-size: 24px; color: #28a745; font-style: italic; }
    .row-text { font-size: 20px; padding-top: 10px; }
    .big-table { font-size: 24px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---

def play_audio(filename):
    """
    Checks if the file exists on GitHub (Dev Branch) before rendering.
    """
    base_url = "https://raw.githubusercontent.com/SevvyV/ArmenianTutor/dev/audio_library"
    url = f"{base_url}/{filename}.mp3"
    
    try:
        # Check if file exists (status code 200 = OK)
        response = requests.head(url)
        if response.status_code == 200:
            st.audio(url, format="audio/mp3")
        else:
            st.caption(f"🎧 Missing: `{filename}`")
    except:
        st.warning("⚠️ Connection Error")

def vocab_player(data, category_prefix):
    """
    Active Drill Layout:
    Renders each word as a row with an individual play button.
    """
    with st.expander("📖 Open Audio Drill", expanded=True):
        # Header Row
        h1, h2, h3, h4 = st.columns([2, 2, 2, 1])
        h1.markdown("**English**")
        h2.markdown("**Armenian**")
        h3.markdown("**Phonetic**")
        h4.markdown("**Audio**")
        st.divider()

        # Data Rows
        for eng, arm, phon in data:
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
            
            c1.markdown(f"<div class='row-text'>{eng}</div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='row-text' style='color:#007bff;'>{arm}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='row-text' style='font-style:italic;'>{phon}</div>", unsafe_allow_html=True)
            
            with c4:
                # Construct filename: category_englishword
                # e.g. "Spoon" -> "kitchen_spoon"
                safe_eng = eng.lower().replace("/", "_").replace(" ", "_")
                filename = f"{category_prefix}_{safe_eng}"
                play_audio(filename)
            
            st.divider()

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
    # Keep this for the older lessons (Days/Months) that don't have individual files yet
    with st.expander("📖 View Vocabulary"):
        md_table = "| English | Armenian | Phonetic |\n| :--- | :--- | :--- |\n"
        for eng, arm, phon in data:
            md_table += f"| {eng} | **{arm}** | *{phon}* |\n"
        st.markdown(md_table)

# --- 3. NAVIGATION (Tiered) ---
with st.sidebar:
    st.title("🇦🇲 HyeTutor")
    st.caption("v3.2 Active Drills")
    st.divider()
    
    # TIER 1: Main Category
    nav_category = st.radio("Select Area:", ["📚 Curriculum", "🛠️ Practice Tools", "🧪 AI Lab"])
    
    # TIER 2: Sub-Modules based on Category
    module = None
    
    if nav_category == "📚 Curriculum":
        module = st.radio("Lessons:", [
            "Lesson 1: Greetings", 
            "Lesson 2: Family", 
            "Lesson 3: Kitchen",
            "Lesson 4: Food",
            "Lesson 5: Furniture",
            "Lesson 6: Animals",
            "Lesson 7: Objects"
        ])
        
    elif nav_category == "🛠️ Practice Tools":
        module = st.radio("Tools:", ["Audio Gym", "Verb Center"])
        
    elif nav_category == "🧪 AI Lab":
        module = "AI Playground" # Direct assignment

# --- 4. PAGE LOGIC ---

# ----------------------
# 📚 CURRICULUM SECTION
# ----------------------
if module == "Lesson 1: Greetings":
    st.header("👋 Lesson 1: Basic Greetings")
    st.divider()
    # Lesson 1 uses the old single-file format
    play_audio("lesson_01_greetings")
    st.subheader("📝 Vocabulary")
    st.markdown("""| English | Armenian (Western) | Phonetic |
| :--- | :--- | :--- |
| Hello | **Բարեւ** | *Parev* |
| How are you? | **Ինչպէ՞ս ես** | *Inchbes es?* |
| I am well | **Լաւ եմ** | *Lav em* |
| Thank you | **Շնորհակալ եմ** | *Shnorhagal em* |
| Goodbye | **Ցտեսութիւն** | *Tsedesutyun* |""")

elif module == "Lesson 2: Family":
    st.header("👪 Lesson 2: Family Members")
    vocab_player(family_data, "family")

elif module == "Lesson 3: Kitchen":
    st.header("🍴 Lesson 3: Kitchen")
    vocab_player(kitchen_data, "kitchen")

elif module == "Lesson 4: Food":
    st.header("🍎 Lesson 4: Food")
    vocab_player(food_data, "food")

elif module == "Lesson 5: Furniture":
    st.header("🪑 Lesson 5: Furniture")
    vocab_player(furniture_data, "furniture")

elif module == "Lesson 6: Animals":
    st.header("🐶 Lesson 6: Animals")
    vocab_player(animals_data, "animals")

elif module == "Lesson 7: Objects":
    st.header("📱 Lesson 7: Objects")
    vocab_player(objects_data, "objects")

# ----------------------
# 🛠️ PRACTICE TOOLS
# ----------------------
elif module == "Audio Gym":
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

elif module == "Verb Center":
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
    
    # Robust cleanup
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

# ----------------------
# 🧪 AI LAB
# ----------------------
elif module == "AI Playground":
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
