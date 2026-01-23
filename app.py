import streamlit as st
import time

# 👇 IMPORT DATA
from data import (
    days_data, months_data, nums_1_10_data, nums_11_20_data, tens_data,
    family_data, kitchen_data, food_data, furniture_data, animals_data, objects_data,
    verb_data, verb_list
)

# --- 1. CONFIGURATION & WIDE UI STYLING ---
st.set_page_config(page_title="HyeTutor Dev", page_icon="🇦🇲", layout="wide")

st.markdown("""
    <style>
    /* 1. THE BIG IMAGE/EMOJI BOX */
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

    /* 🖼️ REAL IMAGE STYLING */
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

    /* 2. THE STRETCHED LISTEN BUTTON (Only for grids) */
    /* This specifically targets buttons inside vertical blocks typically used for grids */
    [data-testid="stVerticalBlock"] > div:has(div.stButton) {
        width: 100% !important;
    }

    /* We need to be careful not to affect the Verb Center Radio Buttons */
    /* The previous global rule was too aggressive. We will rely on Streamlit's default button behavior for everything except the grid cards. */
    
    /* Specific styling for the grid card buttons */
    div.stButton > button {
        /* We leave this generic for now but removed the hard height so other buttons look normal */
        width: 100% !important;
        border-radius: 10px !important;
    }
    
    /* Styling for the card buttons specifically would ideally be done via a custom component or key-based CSS, 
       but for now we will just make sure standard buttons aren't huge */

    div[data-testid="column"] { padding: 10px 15px !important; }
    .phonetic-label { font-size: 14px; color: #999; font-style: italic; margin-left: 8px; }
    .eng-pronoun { font-size: 16px; color: #444; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---

def play_audio(filename):
    """ iPad-Safe Audio Trigger """
    base_url = "https://raw.githubusercontent.com/SevvyV/ArmenianTutor/main/audio_library"
    url = f"{base_url}/{filename}.mp3"
    st.markdown(f'<audio src="{url}" autoplay></audio>', unsafe_allow_html=True)

def render_maximized_grid(data, category_prefix, default_emoji="❓"):
    """ 3-Column Grid with PNG Support + Fallback Emoji """
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

                # Visual Logic
                parts = eng_label.split(' ', 1)
                if len(parts) > 1:
                    emoji = parts[0]
                    eng_text = parts[1]
                else:
                    emoji = default_emoji
                    eng_text = eng_label

                safe_eng = eng_text.lower().replace("/", "_").replace(" ", "_")
                filename = f"{category_prefix}_{safe_eng}"
                
                visual_html = ""
                if image_file:
                    visual_html = f'<img src="{base_img_url}/{image_file}" class="card-image">'
                else:
                    visual_html = f'<div class="huge-emoji" style="text-align:center;">{emoji}</div>'

                st.markdown(f"""
                    <div class="big-card-container">
                        {visual_html}
                        <div class="card-text-eng">{eng_text}</div>
                        <div class="card-text-arm">{arm}</div>
                        <div class="card-text-phon">({phon})</div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🔊 Press to Play", key=f"btn_{filename}_{i}_{j}"):
                    play_audio(filename)

# --- 3. NAVIGATION ---
with st.sidebar:
    st.title("🇦🇲 HyeTutor Dev")
    st.caption("v5.10 Verb Center UI Fix")
    st.divider()
    nav_category = st.radio("Select Area:", ["📚 Curriculum", "🛠️ Practice Tools"])
    
    if nav_category == "📚 Curriculum":
        module = st.radio("Lessons:", [
            "Lesson 1: Greetings", "Lesson 2: Family", "Lesson 3: Kitchen", 
            "Lesson 4: Food", "Lesson 5: Furniture", "Lesson 6: Animals", "Lesson 7: Objects"
        ])
    else:
        module = st.radio("Tools:", [
            "Verb Conjugation Center", 
            "Days of the Week", 
            "Months of the Year", 
            "Numbers 1-20", 
            "Counting by 10s"
        ])

# --- 4. PAGE LOGIC ---

if module == "Verb Conjugation Center":
    st.header("🏃 Verb Conjugation Center")
    verb_choice = st.selectbox("Select a Verb:", verb_list)
    
    # 2. UI FIX: Replaced huge buttons with a clean toggle bar
    tenses = ["Present", "Past", "Future"]
    active_tense = st.radio("Select Tense:", tenses, horizontal=True).lower()
    
    english_label = verb_choice.split('—')[0].split('-')[0].strip()
    clean_name = english_label.lower().replace(" ", "_")
    
    st.subheader(f"{english_label} — {active_tense.capitalize()}")

    if clean_name in verb_data:
        display_list = verb_data[clean_name][active_tense]
        
        # 3. CONTENT FIX: Added English Pronouns Column
        pronouns_eng = ["I", "You", "He/She", "We", "You (pl)", "They"]
        pronouns_arm = ["Ես", "Դուն", "Ան", "Մենք", "Դուք", "Անոնք"]
        pronoun_phonetics = {"Ես": "Yes", "Դուն": "Toun", "Ան": "An", "Մենք": "Menq", "Դուք": "Touq", "Անոնք": "Anonq"}
        
        for i in range(6):
            p_eng = pronouns_eng[i]
            p_arm = pronouns_arm[i]
            p_phon = pronoun_phonetics[p_arm]
            
            # 3 Columns now
            c1, c2, c3 = st.columns([1, 1, 2])
            c1.markdown(f"<span class='eng-pronoun'>{p_eng}</span>", unsafe_allow_html=True)
            c2.markdown(f"**{p_arm}** <span class='phonetic-label'>({p_phon})</span>", unsafe_allow_html=True)
            c3.markdown(f"**{display_list[i]}**")
            st.markdown("<hr style='margin:0; border-top:1px solid #eee;'>", unsafe_allow_html=True)

    st.info("ℹ️ Audio coming soon for verb conjugations!")

# --- RESTORED PRACTICE TOOLS LOGIC ---
elif module == "Days of the Week":
    st.header("📅 Days of the Week")
    render_maximized_grid(days_data, "days", default_emoji="📅")

elif module == "Months of the Year":
    st.header("🗓️ Months of the Year")
    render_maximized_grid(months_data, "months", default_emoji="🗓️")

elif module == "Numbers 1-20":
    st.header("🔢 Numbers 1-20")
    full_numbers = nums_1_10_data + nums_11_20_data
    render_maximized_grid(full_numbers, "numbers", default_emoji="🔢")

elif module == "Counting by 10s":
    st.header("🔟 Counting by 10s")
    render_maximized_grid(tens_data, "numbers", default_emoji="🔟")

# --- LESSON LOGIC ---
elif module == "Lesson 1: Greetings":
    st.header("👋 Lesson 1: Basic Greetings")
    greetings_data = [
        ("👋 Hello", "Բարեւ", "Parev"), ("❓ How are you?", "Ինչպէ՞ս ես", "Inchbes es?"),
        ("😊 I am well", "Լաւ եմ", "Lav em"), ("🙏 Thank you", "Շնորհակալ եմ", "Shnorhagal em"),
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
    st.header(f"📖 {module}")
    render_maximized_grid(raw_data, prefix)
