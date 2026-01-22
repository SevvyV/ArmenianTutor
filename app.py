import streamlit as st
import time

# 👇 IMPORT DATA
from data import (
    family_data, kitchen_data, food_data, furniture_data, animals_data, objects_data,
    verb_data, verb_list
)

# --- 1. CONFIGURATION & MAXIMIZED GRID STYLING ---
st.set_page_config(page_title="HyeTutor Dev", page_icon="🇦🇲", layout="wide")

st.markdown("""
    <style>
    /* 1. THE VISUAL CARD (Underneath) */
    .big-card-container {
        position: relative;
        height: 400px; /* Increased height for larger emoji */
        margin-bottom: 20px;
    }

    .visual-card {
        background-color: #ffffff;
        border: 2px solid #f0f2f6;
        border-radius: 25px;
        height: 100%;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 6px 15px rgba(0,0,0,0.08);
        pointer-events: none; /* Let clicks pass through to the invisible button */
        z-index: 1;
        position: absolute;
    }

    /* 2. THE MASSIVE EMOJI (The setting you were adjusting) */
    .huge-emoji {
        font-size: 150px; /* Set to 150px as requested */
        line-height: 1.2; /* Using your discovered spacing value */
        margin-top: -20px;
    }

    .card-text-eng { font-size: 24px; color: #555; font-weight: 600; margin-top: 10px; }
    .card-text-arm { font-size: 32px; color: #0056b3; font-weight: bold; }
    .card-text-phon { font-size: 18px; color: #888; font-style: italic; }

    /* 3. THE INVISIBLE CLICKER (On Top) */
    div.stButton > button {
        height: 400px !important;
        width: 100% !important;
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 2;
        position: relative;
        box-shadow: none !important;
    }
    
    div.stButton > button:hover {
        background-color: rgba(0, 123, 255, 0.03) !important;
    }
    
    /* 4. LAYOUT FIXES */
    div[data-testid="column"] {
        padding: 5px 15px !important;
    }
    .phonetic-label { font-size: 14px; color: #999; font-style: italic; margin-left: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---

def play_audio(filename):
    """ iPad-Safe Audio Trigger """
    base_url = "https://raw.githubusercontent.com/SevvyV/ArmenianTutor/main/audio_library"
    url = f"{base_url}/{filename}.mp3"
    st.audio(url, format="audio/mp3", autoplay=True)

def render_maximized_grid(data, category_prefix):
    """ 3-Column Grid using Visual Cards for Maximum Emoji Size """
    cols_per_row = 3
    for i in range(0, len(data), cols_per_row):
        cols = st.columns(cols_per_row)
        batch = data[i:i+cols_per_row]
        for j, (eng_with_emoji, arm, phon) in enumerate(batch):
            with cols[j]:
                parts = eng_with_emoji.split(' ', 1)
                emoji = parts[0] if len(parts) > 1 else "❓"
                eng_text = parts[1] if len(parts) > 1 else eng_with_emoji
                
                safe_eng = eng_text.lower().replace("/", "_").replace(" ", "_")
                filename = f"{category_prefix}_{safe_eng}"
                
                # HTML Container for the Visual Card
                st.markdown(f"""
                    <div class="big-card-container">
                        <div class="visual-card">
                            <div class="huge-emoji">{emoji}</div>
                            <div class="card-text-eng">{eng_text}</div>
                            <div class="card-text-arm">{arm}</div>
                            <div class="card-text-phon">({phon})</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Invisible button positioned on top
                if st.button("Click", key=filename):
                    play_audio(filename)

# Pronoun Phonetics
pronoun_phonetics = {
    "Ես": "Yes", "Դուն": "Toun", "Ան": "An", 
    "Մենք": "Menq", "Դուք": "Touq", "Անոնք": "Anonq"
}

# --- 3. NAVIGATION ---
with st.sidebar:
    st.title("🇦🇲 HyeTutor Dev")
    st.caption("v4.7 Visual Card Build")
    st.divider()
    nav_category = st.radio("Select Area:", ["📚 Curriculum", "🛠️ Practice Tools"])
    
    if nav_category == "📚 Curriculum":
        module = st.radio("Lessons:", ["Lesson 2: Family", "Lesson 3: Kitchen", "Lesson 4: Food", "Lesson 5: Furniture", "Lesson 6: Animals", "Lesson 7: Objects"])
    else:
        module = st.radio("Tools:", ["Verb Center"])

# --- 4. PAGE LOGIC ---

if "Lesson" in module:
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
    render_maximized_grid(data, prefix)

elif module == "Verb Center":
    st.header("🏃 Verb Conjugation Center")
    verb_choice = st.selectbox("Select a Verb:", verb_list)
    
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
        time.sleep(1.0)
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
            c1.markdown(f"**{p_arm}** <span class='phonetic-label'>({p_phon})</span>", unsafe_allow_html=True)
            c2.markdown(f"**{conj_arm}**")
            st.markdown("<hr style='margin:0; border-top:1px solid #eee;'>", unsafe_allow_html=True)
