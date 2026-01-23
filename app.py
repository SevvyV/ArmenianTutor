import streamlit as st
import time

# 👇 IMPORT DATA
from data import (
    family_data, kitchen_data, food_data, furniture_data, animals_data, objects_data,
    verb_data, verb_list
)

# --- 1. CONFIGURATION & WIDE UI STYLING ---
st.set_page_config(page_title="HyeTutor Dev", page_icon="🇦🇲", layout="wide")

st.markdown("""
    <style>
    .big-card-container {
        background-color: #ffffff;
        border: 2px solid #f0f2f6;
        border-radius: 25px 25px 0 0; 
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
        object-fit: contain; /* Keeps your PNGs perfectly shaped */
        padding: 15px;
    }

    .huge-emoji { font-size: 150px; line-height: 1.2; }
    .card-text-eng { font-size: 24px; color: #555; font-weight: 600; margin-top: 5px; }
    .card-text-arm { font-size: 32px; color: #0056b3; font-weight: bold; }
    .card-text-phon { font-size: 18px; color: #888; font-style: italic; }

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
    }
    div.stButton > button:hover { background-color: #007bff !important; color: white !important; }
    div[data-testid="column"] { padding: 10px 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---

def play_audio(filename):
    base_url = "https://raw.githubusercontent.com/SevvyV/ArmenianTutor/main/audio_library"
    url = f"{base_url}/{filename}.mp3"
    st.markdown(f'<audio src="{url}" autoplay></audio>', unsafe_allow_html=True)

def render_maximized_grid(data, category_prefix):
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

                # Clean text for filename
                eng_text = eng_label.split(' ')[-1] if ' ' in eng_label else eng_label
                safe_eng = eng_text.lower().replace("/", "_").replace(" ", "_")
                filename = f"{category_prefix}_{safe_eng}"
                
                visual_html = ""
                if image_file:
                    visual_html = f'<img src="{base_img_url}/{image_file}" class="card-image">'
                else:
                    emoji = eng_label.split(' ')[0] if ' ' in eng_label else "❓"
                    visual_html = f'<div class="huge-emoji">{emoji}</div>'

                st.markdown(f"""
                    <div class="big-card-container">
                        {visual_html}
                        <div class="card-text-eng">{eng_text}</div>
                        <div class="card-text-arm">{arm}</div>
                        <div class="card-text-phon">({phon})</div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🔊 Press to Play", key=f"btn_{filename}"):
                    play_audio(filename)

# --- 3. NAVIGATION ---
with st.sidebar:
    st.title("🇦🇲 HyeTutor Dev")
    st.caption("v5.1 Branch Sync Build")
    st.divider()
    module = st.radio("Lessons:", [
        "Lesson 1: Greetings", "Lesson 2: Family", "Lesson 3: Kitchen", 
        "Lesson 4: Food", "Lesson 5: Furniture", "Lesson 6: Animals", "Lesson 7: Objects"
    ])

# --- 4. PAGE LOGIC ---
if module == "Lesson 5: Furniture":
    st.header("🪑 Lesson 5: Furniture")
    render_maximized_grid(furniture_data, "furniture")
elif "Lesson" in module:
    # Use a dictionary to map sidebar selection to data
    lesson_map = {
        "Lesson 1: Greetings": ([], "lesson_01"), # Add Lesson 1 data here if needed
        "Lesson 2: Family": (family_data, "family"),
        "Lesson 3: Kitchen": (kitchen_data, "kitchen"),
        "Lesson 4: Food": (food_data, "food"),
        "Lesson 6: Animals": (animals_data, "animals"),
        "Lesson 7: Objects": (objects_data, "objects")
    }
    raw_data, prefix = lesson_map[module]
    st.header(f"📖 {module}")
    render_maximized_grid(raw_data, prefix)
