import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from deep_translator import GoogleTranslator
import requests

# 👇 IMPORT DATA
from data import (
    days_data, months_data, nums_1_10_data, nums_11_20_data, tens_data, 
    family_data, verb_data, verb_list,
    kitchen_data, food_data, furniture_data, animals_data, objects_data
)

# --- 1. CONFIGURATION & SPREADSHEET STYLING ---
st.set_page_config(page_title="HyeTutor Dev", page_icon="🇦🇲", layout="wide")

st.markdown("""
    <style>
    /* 1. MICRO BUTTONS: Height reduced to 20px */
    div.stButton > button {
        width: 100%; 
        border-radius: 3px; 
        height: 20px;             /* TARGET HEIGHT: 20px */
        font-size: 11px;          /* Smaller font for button */
        background-color: #f8f9fa; 
        border: 1px solid #d1d5db;
        margin: 0px; 
        padding: 0px;
        line-height: 1;
        min-height: 0px !important; /* Override Streamlit minimums */
    }
    div.stButton > button:hover { 
        border-color: #007bff; 
        color: #007bff; 
        background-color: #fff; 
    }
    
    /* 2. REMOVE ALL MARGINS */
    .stButton { margin-bottom: 0px !important; height: 20px !important; }
    div[data-testid="column"] { padding: 0px !important; }
    div.block-container { padding-top: 1rem; padding-bottom: 2rem; }
    
    /* 3. ROW TEXT: Compact Font (15px) & Height (20px) */
    .row-text { 
        font-size: 15px; 
        height: 20px;             /* Match Button Height */
        display: flex;
        align-items: center;
        padding-left: 4px;
        white-space: nowrap;      
        overflow: hidden;         
        text-overflow: ellipsis; 
        line-height: 20px;
    }
    .phonetic { 
        font-size: 13px; 
        color: #777; 
        font-style: italic; 
    }
    
    /* 4. SEPARATOR: Micro line */
    .thin-hr { margin: 0px 0; border: 0; border-top: 1px solid #eee; }
    
    /* 5. HEADER ADJUSTMENT */
    .header-text {
        font-size: 14px;
        font-weight: bold;
        color: #333;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding-bottom: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---

def play_audio(filename):
    """ Standard player for drills """
    base_url = "https://raw.githubusercontent.com/SevvyV/ArmenianTutor/dev/audio_library"
    url = f"{base_url}/{filename}.mp3"
    st.audio(url, format="audio/mp3")

def vocab_player_dense(data, category_prefix):
    """
    SPREADSHEET MODE:
    - Uses Spacer Columns to center the table (20% narrower).
    - Uses 20px rows (35% shorter).
    """
    
    # COLUMN RATIO: [Spacer, Eng, Arm, Phon, Play, Spacer]
    # We use roughly 20% spacers on sides to center the 60% content.
    col_ratio = [3, 4, 4, 4, 1, 3]

    # --- HEADER ---
    _, c1, c2, c3, c4, _ = st.columns(col_ratio)
    c1.markdown("<div class='header-text'>English</div>", unsafe_allow_html=True)
    c2.markdown("<div class='header-text'>Armenian</div>", unsafe_allow_html=True)
    c3.markdown("<div class='header-text'>Phonetic</div>", unsafe_allow_html=True)
    c4.markdown("<div class='header-text' style='text-align:center'>🔊</div>", unsafe_allow_html=True)
    
    # Use a container to group the rows closely
    with st.container():
        st.markdown("<hr style='margin: 0 0 4px 0; border-top: 2px solid #ccc;'>", unsafe_allow_html=True)

        base_url = "https://raw.githubusercontent.com/SevvyV/ArmenianTutor/dev/audio_library"

        # --- DATA ROWS ---
        for eng, arm, phon in data:
            _, c1, c2, c3, c4, _ = st.columns(col_ratio)
            
            clean_eng_for_file = eng.split(' ')[-1] if ' ' in eng else eng
            safe_eng = clean_eng_for_file.lower().replace("/", "_").replace(" ", "_")
            filename = f"{category_prefix}_{safe_eng}"
            url = f"{base_url}/{filename}.mp3"
            
            c1.markdown(f"<div class='row-text'>{eng}</div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='row-text' style='color:#0056b3; font-weight:600;'>{arm}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='row-text phonetic'>{phon}</div>", unsafe_allow_html=True)
            
            with c4:
                # 20px high button
                if st.button("▶", key=filename):
                    st.markdown(f'<audio src="{url}" autoplay></audio>', unsafe_allow_html=True)
            
            # The Divider
            st.markdown("<hr class='thin-hr'>", unsafe_allow_html=True)

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
    with st.expander("📖 View Vocabulary List"):
        md_table = "| English | Armenian | Phonetic |\n| :--- | :--- | :--- |\n"
        for eng, arm, phon in data:
            md_table += f"| {eng} | **{arm}** | *{phon}* |\n"
        st.markdown(md_table)

# --- 3. NAVIGATION ---
with st.sidebar:
    st.title("🇦🇲 HyeTutor")
    st.caption("v3.6 Spreadsheet Build")
    st.divider()
    
    nav_category = st.radio("Select Area:", ["📚 Curriculum", "🛠️ Practice Tools", "🧪 AI Lab"])
    
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
        module = "AI Playground"

# --- 4. PAGE LOGIC ---

if module == "Lesson 1: Greetings":
    st.header("👋 Lesson 1: Basic Greetings")
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
    vocab_player_dense(family_data, "family")

elif module == "Lesson 3: Kitchen":
    st.header("🍴 Lesson 3: Kitchen")
    vocab_player_dense(kitchen_data, "kitchen")

elif module == "Lesson 4: Food":
    st.header("🍎 Lesson 4: Food")
    vocab_player_dense(food_data, "food")

elif module == "Lesson 5: Furniture":
    st.header("🪑 Lesson 5: Furniture")
    vocab_player_dense(furniture_data, "furniture")

elif module == "Lesson 6: Animals":
    st.header("🐶 Lesson 6: Animals")
    vocab_player_dense(animals_data, "animals")

elif module == "Lesson 7: Objects":
    st.header("📱 Lesson 7: Objects")
    vocab_player_dense(objects_data, "objects")

# --- TOOLS ---
elif module == "Audio Gym":
    st.header("🏋️ Audio Gym")
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
    english_label = verb_choice.split('—')[0].split('-')[0].strip()
    clean_name = english_label.lower().replace(" ", "_")
    
    st.subheader(f"{english_label} — {active_tense.capitalize()}")
    play_audio(f"verb_{clean_name}_{active_tense}")
    
    if clean_name in verb_data:
        display_list = verb_data[clean_name][active_tense]
        pronouns_eng = ["I", "You", "He/She", "We", "You pl.", "They"]
        pronouns_arm = ["Ես", "Դուն", "Ան", "Մենք", "Դուք", "Անոնք"]
        md_table = "| English | Pronoun | Conjugation |\n| :--- | :--- | :--- |\n"
        for i in range(6):
            md_table += f"| {pronouns_eng[i]} | **{pronouns_arm[i]}** | {display_list[i]} |\n"
        st.markdown(md_table)

# --- AI LAB ---
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
            with st.spinner("Thinking..."):
                if "English ➡️ Armenian" in input_mode:
                    armenian_text = GoogleTranslator(source='en', target='hy').translate(user_input)
                    st.markdown(f'<p class="big-font">{armenian_text}</p>', unsafe_allow_html=True)
                else:
                    english_text = GoogleTranslator(source='hy', target='en').translate(user_input)
                    armenian_text = user_input
                    st.markdown(f'<p class="translation-font">{english_text}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="big-font">{armenian_text}</p>', unsafe_allow_html=True)
                
                audio_response = get_live_speech(armenian_text, voice_choice)
                if isinstance(audio_response, bytes):
                    st.audio(audio_response, format="audio/mp3")
