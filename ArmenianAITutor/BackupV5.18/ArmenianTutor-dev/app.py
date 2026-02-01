#  Stable version 5.18 January 23rd, 2026
import streamlit as st
import time

# 👇 IMPORT DATA
from data import (
    greetings_data, days_data, months_data, nums_1_10_data, nums_11_20_data, tens_data,
    family_data, kitchen_data, food_data, furniture_data, animals_data, objects_data,
    verb_data, verb_list
)

# --- 1. CONFIGURATION & WIDE UI STYLING ---
st.set_page_config(page_title="HyeTutor Dev", page_icon="🇦🇲", layout="wide")

st.markdown("""
    <style>
    /* THE BIG IMAGE/EMOJI BOX */
    .big-card-container {
        background-color: #ffffff;
        border: 2px solid #f0f2f6;
        border-radius: 25px; 
        height: 380px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 0px; 
        overflow: hidden;
    }

    .card-image {
        width: 100%;
        height: 230px;
        object-fit: contain;
        padding: 15px;
    }

    .huge-emoji { font-size: 150px; line-height: 1.2; }
    .card-text-eng { font-size: 24px; color: #555; font-weight: 600; margin-top: 5px; }
    .card-text-arm { font-size: 32px; color: #0056b3; font-weight: bold; }
    .card-text-phon { font-size: 18px; color: #888; font-style: italic; }

    /* --- ROBUST FIX FOR LESSON BUTTONS --- */
    /* This targets the Streamlit container holding the button that comes immediately 
       after the container holding our 'lesson-btn-marker' */
    div.element-container:has(div.lesson-btn-marker) + div.element-container button {
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
    }
    div.element-container:has(div.lesson-btn-marker) + div.element-container button:hover { 
        background-color: #007bff !important; 
        color: white !important; 
    }
    
    div[data-testid="column"] { padding: 10px 15px !important; }
    .phonetic-label { font-size: 14px; color: #999; font-style: italic; margin-left: 8px; }
    .eng-pronoun { font-size: 16px; color: #444; font-weight: 600; }
    
    /* MASTER PLAY BUTTON (GREEN) */
    .master-play-btn div.stButton > button {
        width: 100% !important;
        background-color: #28a745 !important;
        color: white !important;
        font-size: 20px !important;
        font-weight: bold !important;
        padding: 15px !important;
        margin-bottom: 20px !important;
    }

    /* VERB SELECTOR STYLING (Bigger Font) */
    div[data-baseweb="select"] > div {
        font-size: 1.5rem !important; 
        min-height: 60px !important;   
        display: flex;
        align-items: center;
    }
    li[role="option"] {
        font-size: 1.2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---

def play_audio(filename):
    """ iPad-Safe Audio Trigger """
    base_url = "https://raw.githubusercontent.com/SevvyV/ArmenianTutor/main/audio_library"
    url = f"{base_url}/{filename}.mp3"
    st.markdown(f'<audio src="{url}" autoplay></audio>', unsafe_allow_html=True)

def render_maximized_grid(data, category_prefix):
    """ LESSON GRID: Visual Card + Individual Audio Button (For Lessons 2-7) """
    cols_per_row = 3
    base_img_url = "https://raw.githubusercontent.com/SevvyV/ArmenianTutor/main/image_library"
    
    for i in range(0, len(data), cols_per_row):
        cols = st.columns(cols_per_row)
        batch = data[i:i+cols_per_row]
        for j, item in enumerate(batch):
            with cols[j]:
                eng_label = item[0]
                arm = item[1]
                phon = item[2]
                image_file = item[3] if len(item) > 3 else None

                parts = eng_label.split(' ', 1)
                emoji, eng_text = (parts[0], parts[1]) if len(parts) > 1 else ("❓", eng_label)
                safe_eng = eng_text.lower().replace("/", "_").replace(" ", "_")
                filename = f"{category_prefix}_{safe_eng}"
                
                visual_html = f'<img src="{base_img_url}/{image_file}" class="card-image">' if image_file else f'<div class="huge-emoji" style="text-align:center;">{emoji}</div>'

                st.markdown(f"""
                    <div class="big-card-container" style="border-radius: 25px 25px 0 0; margin-bottom: 0;">
                        {visual_html}
                        <div class="card-text-eng">{eng_text}</div>
                        <div class="card-text-arm">{arm}</div>
                        <div class="card-text-phon">({phon})</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # --- SIBLING MARKER FOR CSS ---
                st.markdown('<div class="lesson-btn-marker"></div>', unsafe_allow_html=True)
                if st.button(f"🔊 Press to Play", key=f"btn_{filename}_{i}_{j}"):
                    play_audio(filename)

def render_practice_grid(data):
    """ PRACTICE GRID: Visual cards only (For Practice Tools & Greetings) """
    cols_per_row = 3
    
    for i in range(0, len(data), cols_per_row):
        cols = st.columns(cols_per_row)
        batch = data[i:i+cols_per_row]
        for j, item in enumerate(batch):
            with cols[j]:
                eng_label = item[0]
                arm = item[1]
                phon = item[2]

                parts = eng_label.split(' ', 1)
                emoji, eng_text = (parts[0], parts[1]) if len(parts) > 1 else ("❓", eng_label)

                st.markdown(f"""
                    <div class="big-card-container">
                        <div class="huge-emoji" style="text-align:center;">{emoji}</div>
                        <div class="card-text-eng">{eng_text}</div>
                        <div class="card-text-arm">{arm}</div>
                        <div class="card-text-phon">({phon})</div>
                    </div>
                """, unsafe_allow_html=True)

# --- 3. NAVIGATION ---
with st.sidebar:
    st.title("🇦🇲 HyeTutor Dev")
    st.divider()
    nav_category = st.radio("Select Area:", ["📚 Curriculum", "🛠️ Practice Tools"])
    
    if nav_category == "📚 Curriculum":
        module = st.radio("Lessons:", [
            "Lesson 1: Greetings", "Lesson 2: Family", "Lesson 3: Kitchen", 
            "Lesson 4: Food", "Lesson 5: Furniture", "Lesson 6: Animals", "Lesson 7: Objects"
        ])
    else:
        module = st.radio("Tools:", ["Verb Conjugation Center", "Days of the Week", "Months of the Year", "Numbers 1-20", "Counting by 10s"])

# --- 4. PAGE LOGIC ---

if module == "Verb Conjugation Center":
    st.header("🏃 Verb Conjugation Center")
    verb_choice = st.selectbox("Select a Verb:", verb_list)
    active_tense = st.radio("Select Tense:", ["Present", "Past", "Future"], horizontal=True).lower()
    
    english_label = verb_choice.split('—')[0].split('-')[0].strip()
    clean_name = english_label.lower().replace(" ", "_")
    
    st.subheader(f"{english_label} — {active_tense.capitalize()}")
    
    st.markdown('<div class="master-play-btn">', unsafe_allow_html=True)
    audio_file = f"verb_{clean_name}_{active_tense}"
    if st.button("🔊 Play Conjugation", key=f"play_verb_{clean_name}_{active_tense}"):
        play_audio(audio_file)
    st.markdown('</div>', unsafe_allow_html=True)

    if clean_name in verb_data:
        display_list = verb_data[clean_name][active_tense]
        pronouns_eng = ["I", "You", "He/She", "We", "You (pl)", "They"]
        pronouns_arm = ["Ես", "Դուն", "Ան", "Մենք", "Դուք", "Անոնք"]
        pronoun_phonetics = {"Ես": "Yes", "Դուն": "Toun", "Ան": "An", "Մենք": "Menq", "Դուք": "Touq", "Անոնք": "Anonq"}
        
        for i in range(6):
            p_eng, p_arm, p_phon = pronouns_eng[i], pronouns_arm[i], pronoun_phonetics[pronouns_arm[i]]
            
            # Tighter columns
            c1, c2, c3, _ = st.columns([1.5, 1.5, 3, 5])
            
            c1.markdown(f"<span class='eng-pronoun'>{pronouns_eng[i]}</span>", unsafe_allow_html=True)
            c2.markdown(f"**{pronouns_arm[i]}** <span class='phonetic-label'>({pronoun_phonetics[pronouns_arm[i]]})</span>", unsafe_allow_html=True)
            c3.markdown(f"**{display_list[i]}**")
            st.markdown("<hr style='margin:0; border-top:1px solid #eee;'>", unsafe_allow_html=True)

elif module == "Days of the Week":
    st.header("📅 Days of the Week")
    st.markdown('<div class="master-play-btn">', unsafe_allow_html=True)
    if st.button("🔊 Play Sequence", key="play_days"):
        play_audio("drill_days_of_week") 
    st.markdown('</div>', unsafe_allow_html=True)
    render_practice_grid(days_data)

elif module == "Months of the Year":
    st.header("🗓️ Months of the Year")
    st.markdown('<div class="master-play-btn">', unsafe_allow_html=True)
    if st.button("🔊 Play Sequence", key="play_months"):
        play_audio("drill_months_of_year")
    st.markdown('</div>', unsafe_allow_html=True)
    render_practice_grid(months_data)

elif module == "Numbers 1-20":
    st.header("🔢 Numbers 1-20")
    st.markdown('<div class="master-play-btn">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔊 Play 1-10", key="play_1_10"):
            play_audio("drill_numbers_1_10")
    with c2:
        if st.button("🔊 Play 11-20", key="play_11_20"):
            play_audio("drill_numbers_11_20")
    st.markdown('</div>', unsafe_allow_html=True)
    
    full_numbers = nums_1_10_data + nums_11_20_data
    render_practice_grid(full_numbers)

elif module == "Counting by 10s":
    st.header("🔟 Counting by 10s")
    st.markdown('<div class="master-play-btn">', unsafe_allow_html=True)
    if st.button("🔊 Play 10-100", key="play_tens"):
        play_audio("drill_tens_10_100")
    st.markdown('</div>', unsafe_allow_html=True)
    render_practice_grid(tens_data)

elif module == "Lesson 1: Greetings":
    st.header("👋 Lesson 1: Basic Greetings")
    
    st.markdown('<div class="master-play-btn">', unsafe_allow_html=True)
    if st.button("🔊 Play All Greetings", key="play_greetings_all"):
        play_audio("lesson_01_greetings")
    st.markdown('</div>', unsafe_allow_html=True)
    
    render_practice_grid(greetings_data)

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
    st.header(f"📖 {module}")
    render_maximized_grid(raw_data, prefix)

