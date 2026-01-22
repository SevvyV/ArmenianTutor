import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from deep_translator import GoogleTranslator
import requests
import time

# 👇 IMPORT DATA
from data import (
    days_data, months_data, nums_1_10_data, nums_11_20_data, tens_data, 
    family_data, verb_data, verb_list,
    kitchen_data, food_data, furniture_data, animals_data, objects_data
)

# --- 1. CONFIGURATION & IPAD OPTIMIZED STYLING ---
st.set_page_config(page_title="HyeTutor Dev", page_icon="🇦🇲", layout="wide")

st.markdown("""
    <style>
    /* 1. MAKE BUTTONS LOOK LIKE CARDS */
    div.stButton > button {
        width: 100% !important;
        height: 150px !important;     /* Large tap target */
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 15px !important;
        white-space: pre-wrap !important; /* Allows newlines in button text */
        font-size: 20px !important;
        color: #0056b3 !important;
        font-weight: bold !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        transition: all 0.2s ease;
    }
    
    div.stButton > button:hover {
        border-color: #007bff !important;
        box-shadow: 0 6px 12px rgba(0,123,255,0.15) !important;
        transform: translateY(-3px);
    }

    /* 2. VERB TABLE PHONETICS */
    .phonetic-label { font-size: 14px; color: #999; font-style: italic; margin-left: 8px; }

    /* 3. LAYOUT CLEANUP */
    div.block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---

def play_audio(filename):
    base_url = "https://raw.githubusercontent.com/SevvyV/ArmenianTutor/main/audio_library"
    url = f"{base_url}/{filename}.mp3"
    st.markdown(f'<audio src="{url}" autoplay></audio>', unsafe_allow_html=True)

def render_grid_player(data, category_prefix):
    """
    IPAD MODE: Every card is a giant button with multi-line text.
    """
    cols_per_row = 3
    for i in range(0, len(data), cols_per_row):
        cols = st.columns(cols_per_row)
        batch = data[i:i+cols_per_row]
        for j, (eng, arm, phon) in enumerate(batch):
            with cols[j]:
                # Prepare filename
                clean_eng = eng.split(' ')[-1] if ' ' in eng else eng
                safe_eng = clean_eng.lower().replace("/", "_").replace(" ", "_")
                filename = f"{category_prefix}_{safe_eng}"
                
                # Combine text into a single string with newlines
                # Streamlit buttons will respect \n because of 'white-space: pre-wrap' in CSS
                label = f"{eng}\n{arm}\n({phon})"
                
                if st.button(label, key=filename, help=f"Click to hear {eng}"):
                    play_audio(filename)

# Mapping for Verb Center Phonetics
pronoun_phonetics = {
    "Ես": "Yes", "Դուն": "Toun", "Ան": "An", 
    "Մենք": "Menq", "Դուք": "Touq", "Անոնք": "Anonq"
}

# --- 3. NAVIGATION ---
with st.sidebar:
    st.title("🇦🇲 HyeTutor Dev")
    st.caption("v3.9 iPad Demo Build")
    st.divider()
    nav_category = st.radio("Select Area:", ["📚 Curriculum", "🛠️ Practice Tools", "🧪 AI Lab"])
    
    module = None
    if nav_category == "📚 Curriculum":
        module = st.radio("Lessons:", ["Lesson 1: Greetings", "Lesson 2: Family", "Lesson 3: Kitchen", "Lesson 4: Food", "Lesson 5: Furniture", "Lesson 6: Animals", "Lesson 7: Objects"])
    elif nav_category == "🛠️ Practice Tools":
        module = st.radio("Tools:", ["Audio Gym", "Verb Center"])
    elif nav_category == "🧪 AI Lab":
        module = "AI Playground"

# --- 4. PAGE LOGIC ---

if module == "Lesson 1: Greetings":
    st.header("👋 Lesson 1: Basic Greetings")
    greetings_data = [("Hello", "Բարեւ", "Parev"), ("How are you?", "Ինչպէ՞ս ես", "Inchbes es?"), ("Thank you", "Շնորհակալ եմ", "Shnorhagal em")]
    render_grid_player(greetings_data, "lesson_01")

elif module in ["Lesson 2: Family", "Lesson 3: Kitchen", "Lesson 4: Food", "Lesson 5: Furniture", "Lesson 6: Animals", "Lesson 7: Objects"]:
    lesson_map = {
        "Lesson 2: Family": (family_data, "family"),
        "Lesson 3: Kitchen": (kitchen_data, "kitchen"),
        "Lesson 4: Food": (food_data, "food"),
        "Lesson 5: Furniture": (furniture_data, "furniture"),
        "Lesson 6: Animals": (animals_data, "animals"),
        "Lesson 7: Objects": (objects_data, "objects")
    }
    data, prefix = lesson_map[module]
    st.header(f"📖 {module}")
    render_grid_player(data, prefix)

elif module == "Verb Center":
    st.header("🏃 Verb Conjugation Center")
    
    verb_choice = st.selectbox("Select a Verb:", verb_list, key="verb_selector")
    
    # Auto-Play Logic on Selection
    if 'last_verb' not in st.session_state: st.session_state.last_verb = verb_choice
    
    tcol1, tcol2, tcol3 = st.columns(3)
    if 'current_tense' not in st.session_state: st.session_state.current_tense = 'present'
    with tcol1: 
        if st.button("📍 Present"): st.session_state.current_tense = 'present'
    with tcol2:
        if st.button("🕰️ Past"): st.session_state.current_tense = 'past'
    with tcol3:
        if st.button("🚀 Future"): st.session_state.current_tense = 'future'

    active_tense = st.session_state.current_tense
    english_label = verb_choice.split('—')[0].split('-')[0].strip()
    clean_name = english_label.lower().replace(" ", "_")
    filename = f"verb_{clean_name}_{active_tense}"

    if st.session_state.last_verb != verb_choice:
        st.session_state.last_verb = verb_choice
        time.sleep(0.8) 
        play_audio(filename)

    st.subheader(f"{english_label} — {active_tense.capitalize()}")
    if st.button(f"🔊 Replay Conjugation"):
        play_audio(filename)
    
    if clean_name in verb_data:
        display_list = verb_data[clean_name][active_tense]
        pronouns_arm = ["Ես", "Դուն", "Ան", "Մենք", "Դուք", "Անոնք"]
        
        for i in range(6):
            p_arm = pronouns_arm[i]
            p_phon = pronoun_phonetics[p_arm]
            conj_arm = display_list[i]
            
            c1, c2 = st.columns([1, 3])
            c1.markdown(f"**{p_arm}** <span class='phonetic-label'>({p_phon})</span>", unsafe_allow_html=True)
            c2.markdown(f"**{conj_arm}**")
            st.markdown("<hr style='margin:0; border-top:1px solid #eee;'>", unsafe_allow_html=True)

# (Rest of Tools and Lab logic follows...)
