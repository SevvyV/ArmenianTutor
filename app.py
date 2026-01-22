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

# --- 1. CONFIGURATION & CHILD-FRIENDLY STYLING ---
st.set_page_config(page_title="HyeTutor Dev", page_icon="🇦🇲", layout="wide")

st.markdown("""
    <style>
    /* 1. THE PICTURE CARD CONTAINER */
    .picture-card {
        background-color: #ffffff;
        border: 2px solid #f0f2f6;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        margin-bottom: 10px;
        height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    /* 2. MAKE EMOJIS MASSIVE */
    .card-emoji {
        font-size: 80px; /* Huge emoji for kids */
        margin-bottom: 10px;
        display: block;
    }

    /* 3. TYPOGRAPHY */
    .card-eng { font-size: 20px; color: #555; font-weight: 500; display: block; }
    .card-arm { font-size: 28px; color: #0056b3; font-weight: bold; display: block; }
    .card-phon { font-size: 16px; color: #888; font-style: italic; display: block; }

    /* 4. THE HIDDEN BUTTON TRICK */
    /* This sits on top of the card so the whole thing is clickable */
    div.stButton > button {
        position: relative;
        top: -260px; /* Moves button over the card */
        height: 250px !important;
        width: 100% !important;
        background-color: transparent !important;
        border: none !important;
        color: transparent !important;
        z-index: 10;
    }
    
    /* Hover effect for the visual card when the invisible button is hovered */
    div.stButton:hover + .picture-card, .picture-card:hover {
        border-color: #007bff;
        transform: scale(1.02);
        box-shadow: 0 8px 20px rgba(0,123,255,0.15);
    }

    /* 5. VERB CENTER FIXES */
    .phonetic-label { font-size: 14px; color: #999; font-style: italic; margin-left: 8px; }
    div.block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---

def play_audio(filename):
    base_url = "https://raw.githubusercontent.com/SevvyV/ArmenianTutor/main/audio_library"
    url = f"{base_url}/{filename}.mp3"
    st.markdown(f'<audio src="{url}" autoplay></audio>', unsafe_allow_html=True)

def render_picture_grid(data, category_prefix):
    """
    KIDS MODE: Large emojis and high-visibility cards.
    """
    cols_per_row = 3
    for i in range(0, len(data), cols_per_row):
        cols = st.columns(cols_per_row)
        batch = data[i:i+cols_per_row]
        for j, (eng_with_emoji, arm, phon) in enumerate(batch):
            with cols[j]:
                # Split emoji and text (e.g., "🍎 Apple" -> "🍎", "Apple")
                parts = eng_with_emoji.split(' ', 1)
                emoji = parts[0] if len(parts) > 1 else "❓"
                eng_text = parts[1] if len(parts) > 1 else eng_with_emoji
                
                # File naming logic
                safe_eng = eng_text.lower().replace("/", "_").replace(" ", "_")
                filename = f"{category_prefix}_{safe_eng}"
                
                # 1. Visual Card (HTML)
                st.markdown(f"""
                <div class="picture-card">
                    <span class="card-emoji">{emoji}</span>
                    <span class="card-eng">{eng_text}</span>
                    <span class="card-arm">{arm}</span>
                    <span class="card-phon">({phon})</span>
                </div>
                """, unsafe_allow_html=True)
                
                # 2. Invisible Button (Functional)
                if st.button("Play", key=filename):
                    play_audio(filename)

# Mapping for Verb Center Phonetics
pronoun_phonetics = {
    "Ես": "Yes", "Դուն": "Toun", "Ան": "An", 
    "Մենք": "Menq", "Դուք": "Touq", "Անոնք": "Anonq"
}

# --- 3. NAVIGATION & LOGIC ---
with st.sidebar:
    st.title("🇦🇲 HyeTutor Dev")
    st.caption("v4.0 Picture Card Build")
    st.divider()
    nav_category = st.radio("Select Area:", ["📚 Curriculum", "🛠️ Practice Tools"])
    
    if nav_category == "📚 Curriculum":
        module = st.radio("Lessons:", ["Lesson 2: Family", "Lesson 3: Kitchen", "Lesson 4: Food", "Lesson 5: Furniture", "Lesson 6: Animals", "Lesson 7: Objects"])
    else:
        module = st.radio("Tools:", ["Verb Center"])

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
    render_picture_grid(data, prefix)

elif module == "Verb Center":
    st.header("🏃 Verb Conjugation Center")
    verb_choice = st.selectbox("Select a Verb:", verb_list)
    
    # ... (Keep existing Verb Center logic, ensuring pronoun_phonetics are used)
    # Note: Ensure the display loop uses the c1, c2 columns we established earlier.
