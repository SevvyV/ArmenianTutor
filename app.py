import streamlit as st
import time

# 👇 IMPORT DATA (Assumes data.py exists in the same directory)
from data import (
    family_data, kitchen_data, food_data, furniture_data, animals_data, objects_data,
    verb_data, verb_list
)

# --- 1. CONFIGURATION & WIDE UI STYLING ---
st.set_page_config(page_title="HyeTutor Dev", page_icon="🇦🇲", layout="wide")

st.markdown("""
    <style>
    /* 1. THE BIG EMOJI BOX */
    .big-card-container {
        background-color: #ffffff;
        border: 2px solid #f0f2f6;
        border-radius: 25px 25px 0 0; 
        height: 350px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 0px; 
    }

    .huge-emoji {
        font-size: 150px; 
        line-height: 1.2;
    }

    .card-text-eng { font-size: 24px; color: #555; font-weight: 600; }
    .card-text-arm { font-size: 32px; color: #0056b3; font-weight: bold; }
    .card-text-phon { font-size: 18px; color: #888; font-style: italic; }

    /* 2. THE STRETCHED LISTEN BUTTON (STRECHED TO 100% WIDTH) */
    [data-testid="stVerticalBlock"] > div:has(div.stButton) {
        width: 100% !important;
    }

    div.stButton > button {
        width: 100% !important;      
        height: 90px !important;      
        background-color: #e3f2fd !important; 
        color: #007bff !important;
        border: 2px solid #f0f2f6 !important;
        border-top: none !important;  
        border-radius: 0 0 25px 25px !important; 
        font-weight: bold !important;
        font-size: 24px !important;   
        margin-top: -2px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    div.stButton > button:hover {
        background-color: #007bff !important;
        color: white !important;
    }

    /* 3. LAYOUT SPACING & TYPOGRAPHY */
    div[data-testid="column"] { padding: 10px 15px !important; }
    .element-container { margin-bottom: 0px !important; }
    .phonetic-label { font-size: 14px; color: #999; font-style: italic; margin-left: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---

def play_audio(filename):
    """ Hidden audio trigger optimized for iPad Safari compatibility """
    # Using the 'main' branch as established
    base_url = "https://raw.githubusercontent.com/SevvyV/ArmenianTutor/main/audio_library"
    url = f"{base_url}/{filename}.mp3"
    st.markdown(f'<audio src="{url}" autoplay></audio>', unsafe_allow_html=True)

def render_maximized_grid(data, category_prefix):
    """ 3-Column Grid with full-width buttons and large emojis """
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
                
                # Visual Flashcard
                st.markdown(f"""
                    <div class="big-card-container">
                        <div class="huge-emoji">{emoji}</div>
                        <div class="card-text-eng">{eng_text}</div>
                        <div class="card-text-arm">{arm}</div>
                        <div class="card-text-phon">({phon})</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Action Button
                if st.button(f"🔊 Press to Play", key=filename):
                    play_audio(filename)

# Mapping for Verb Center Pronoun Phonetics
pronoun_phonetics = {
    "Ես": "Yes", "Դուն": "Toun", "Ան": "An", 
    "Մենք": "Menq", "Դուք": "Touq", "Անոնք": "Anonq"
}

# --- 3. NAVIGATION ---
with st.sidebar:
    st.title("🇦🇲 HyeTutor Dev")
    st.caption("v4.13 Complete Build")
    st.divider()
    nav_category = st.radio("Select Area:", ["📚 Curriculum", "🛠️ Practice Tools"])
    
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
    else:
        module = st.radio("Tools:", ["Verb Center"])

# --- 4. PAGE LOGIC ---

if module == "Lesson 1: Greetings":
    st.header("👋 Lesson 1: Basic Greetings")
    greetings_data = [
        ("👋 Hello", "Բարեւ", "Parev"),
        ("❓ How are you?", "Ինչպէ՞ս ես", "Inchbes es?"),
        ("😊 I am well", "Լաւ եմ", "Lav em"),
        ("🙏 Thank you", "Շնորհակալ եմ", "Shnorhagal em"),
        ("👋 Goodbye", "Ցտեսութիւն", "Tsedesutyun")
    ]
    render_maximized_grid(greetings_data, "lesson_01")

elif "Lesson" in module:
    lesson_map = {
        "Lesson 2: Family": (family_data, "family"),
        "Lesson 3: Kitchen": (kitchen_data, "kitchen"),
        "Lesson 4: Food": (food_data, "food"),
        "Lesson 5: Furniture": (furniture_data, "furniture"),
        "Lesson 6: Animals": (animals_data, "animals"),
        "Lesson 7: Objects": (objects_data, "objects")
    }
    raw_data, prefix = lesson_map[module]
    
    # Apply Visual Corrections for better child engagement
    corrected_data = []
    for eng, arm, phon in raw_data:
        # Family Correction
        if "Son" in eng: eng = "👦 Son"
        
        # Furniture Fixes
        if "Table" in eng: eng = "🪵 Table"
        if "Sofa" in eng: eng = "🛋️ Sofa"
        if "Window" in eng: eng = "🪟 Window"
        if "Mirror" in eng: eng = "🪞 Mirror"
        if "Carpet" in eng: eng = "🧶 Carpet"
        if "Lamp" in eng: eng = "🏮 Lamp"
        if "Stairs" in eng: eng = "🪜 Stairs"
        if "Closet" in eng: eng = "🚪 Closet"
        
        # Kitchen Fixes
        if "Pot" in eng: eng = "🥘 Pot"
        if "Pitcher" in eng: eng = "🏺 Pitcher"
        if "Napkin" in eng: eng = "🧺 Napkin"
        
        corrected_data.append((eng, arm, phon))

    st.header(f"📖 {module}")
    render_maximized_grid(corrected_data, prefix)

elif module == "Verb Center":
    st.header("🏃 Verb Conjugation Center")
    verb_choice = st.selectbox("Select a Verb:", verb_list)
    
    # Auto-play logic on selection change
    if 'last_verb' not in st.session_state: st.session_state.last_verb = verb_choice
    if 'current_tense' not in st.session_state: st.session_state.current_tense = 'present'

    tcol1, tcol2, tcol3 = st.columns(3)
    with tcol1: 
        if st.button("📍 Present", key="verb_pres"): st.session_state.current_tense = 'present'
    with tcol2:
        if st.button("🕰️ Past", key="verb_past"): st.session_state.current_tense = 'past'
    with tcol3:
        if st.button("🚀 Future", key="verb_fut"): st.session_state.current_tense = 'future'

    active_tense = st.session_state.current_tense
    english_label = verb_choice.split('—')[0].split('-')[0].strip()
    clean_name = english_label.lower().replace(" ", "_")
    filename = f"verb_{clean_name}_{active_tense}"

    if st.session_state.last_verb != verb_choice:
        st.session_state.last_verb = verb_choice
        time.sleep(1.0) # 1-second auto-play delay
        play_audio(filename)

    st.subheader(f"{english_label} — {active_tense.capitalize()}")
    
    if clean_name in verb_data:
        display_list = verb_data[clean_name][active_tense]
        pronouns_arm = ["Ես", "Դուն", "Ան", "Մենք", "Դուք", "Անոնք"]
        
        for i in range(6):
            p_arm = pronouns_arm[i]
            p_phon = pronoun_phonetics.get(p_arm, "")
            conj_arm = display_list[i]
            
            c1, c2 = st.columns([1, 3])
            c1.markdown(f"**{p_arm}** <span class='phonetic-label'>({p_phon})</span>", unsafe_allow_html=True)
            c2.markdown(f"**{conj_arm}**")
            st.markdown("<hr style='margin:0; border-top:1px solid #eee;'>", unsafe_allow_html=True)
