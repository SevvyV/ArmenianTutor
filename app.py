import streamlit as st
import time

# 👇 IMPORT DATA
from data import (
    family_data, kitchen_data, food_data, furniture_data, animals_data, objects_data,
    verb_data, verb_list
)

# --- 1. CONFIGURATION & BIG SQUARE STYLING ---
st.set_page_config(page_title="HyeTutor Dev", page_icon="🇦🇲", layout="wide")

st.markdown("""
    <style>
    /* 1. MAKE BUTTONS LARGE SQUARES */
    div.stButton > button {
        width: 100% !important;
        height: 300px !important;     /* Large Square Shape */
        background-color: #ffffff !important;
        border: 2px solid #f0f2f6 !important;
        border-radius: 25px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
        white-space: pre-wrap !important; 
        transition: all 0.3s ease !important;
        padding: 20px !important;
    }
    
    div.stButton > button:hover {
        border-color: #007bff !important;
        transform: translateY(-5px) !important;
        box-shadow: 0 8px 25px rgba(0,123,255,0.2) !important;
    }

    /* 2. TEXT SIZING INSIDE THE BUTTON */
    /* We handle this via the label string, but we can set global font here */
    div.stButton > button p {
        font-family: 'Inter', sans-serif;
    }

    /* 3. VERB CENTER UI */
    .phonetic-label { font-size: 14px; color: #999; font-style: italic; margin-left: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---

def play_audio(filename):
    """ iPad-Safe Audio Trigger """
    base_url = "https://raw.githubusercontent.com/SevvyV/ArmenianTutor/main/audio_library"
    url = f"{base_url}/{filename}.mp3"
    # Using the standard st.audio with autoplay for the best iPad compatibility
    st.audio(url, format="audio/mp3", autoplay=True)

def render_big_square_grid(data, category_prefix):
    """ 3-Column Square Grid with Massive Emojis """
    cols_per_row = 3
    for i in range(0, len(data), cols_per_row):
        cols = st.columns(cols_per_row)
        batch = data[i:i+cols_per_row]
        for j, (eng_with_emoji, arm, phon) in enumerate(batch):
            with cols[j]:
                # Split emoji and text
                parts = eng_with_emoji.split(' ', 1)
                emoji = parts[0] if len(parts) > 1 else "❓"
                eng_text = parts[1] if len(parts) > 1 else eng_with_emoji
                
                # Create a Massive Label
                # We use many newlines to separate the giant emoji from the text
                card_label = f"{emoji}\n\n\n{eng_text}\n{arm}\n({phon})"
                
                safe_eng = eng_text.lower().replace("/", "_").replace(" ", "_")
                filename = f"{category_prefix}_{safe_eng}"
                
                if st.button(card_label, key=filename):
                    play_audio(filename)

# Pronoun Phonetics for Verb Center
pronoun_phonetics = {
    "Ես": "Yes", "Դուն": "Toun", "Ան": "An", 
    "Մենք": "Menq", "Դուք": "Touq", "Անոնք": "Anonq"
}

# --- 3. NAVIGATION ---
with st.sidebar:
    st.title("🇦🇲 HyeTutor Dev")
    st.caption("v4.2 Big Square Build")
    st.divider()
    nav_category = st.radio("Select Area:", ["📚 Curriculum", "🛠️ Practice Tools"])
    
    if nav_category == "📚 Curriculum":
        module = st.radio("Lessons:", ["Lesson 2: Family", "Lesson 3: Kitchen", "Lesson 4: Food", "Lesson 6: Animals"])
    else:
        module = st.radio("Tools:", ["Verb Center"])

# --- 4. PAGE LOGIC ---

if "Lesson" in module:
    lesson_map = {
        "Lesson 2: Family": (family_data, "family"),
        "Lesson 3: Kitchen": (kitchen_data, "kitchen"),
        "Lesson 4: Food": (food_data, "food"),
        "Lesson 6: Animals": (animals_data, "animals")
    }
    data, prefix = lesson_map[module]
    st.header(f"📖 {module}")
    render_big_square_grid(data, prefix)

elif module == "Verb Center":
    st.header("🏃 Verb Conjugation Center")
    verb_choice = st.selectbox("Select a Verb:", verb_list)
    
    # Auto-Play Logic
    if 'last_verb' not in st.session_state: st.session_state.last_verb = verb_choice
    if 'current_tense' not in st.session_state: st.session_state.current_tense = 'present'

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
    filename = f"verb_{clean_name}_{active_tense}"

    if st.session_state.last_verb != verb_choice:
        st.session_state.last_verb = verb_choice
        time.sleep(1.0) # 1 second pause for auto-play
        play_audio(filename)

    st.subheader(f"{english_label} — {active_tense.capitalize()}")
    
    if clean_name in verb_data:
        display_list = verb_data[clean_name][active_tense]
        pronouns_arm = ["Ես", "Դուն", "Ան", "Մենք", "Դուք", "Անոնք"]
        
        for i in range(6):
            p_arm = pronouns_arm[i]
            p_phon = pronoun_phonetics[p_arm]
            conj_arm = display_list[i]
            
            c1, c2 = st.columns([1, 3])
            # Added Phonetics next to pronouns
            c1.markdown(f"**{p_arm}** <span class='phonetic-label'>({p_phon})</span>", unsafe_allow_html=True)
            c2.markdown(f"**{conj_arm}**")
            st.markdown("<hr style='margin:0; border-top:1px solid #eee;'>", unsafe_allow_html=True)
