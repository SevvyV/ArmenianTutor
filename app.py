import streamlit as st
from google import genai
from google.genai import types
import wave
import io
import os

# 1. Page Configuration
st.set_page_config(page_title="HyeTutor2.0beta", page_icon="🇦🇲", layout="wide")

st.title("🇦🇲 HyeTutor2.0beta")
st.caption("Version 5.5 • English Filename Slugs • Tier 1 Speed")

# --- AUDIO LIBRARY SETUP ---
AUDIO_DIR = "audio_library"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# --- PERMANENT DATA ---
PRONOUNS = ["Ես", "Դուն", "Ան", "Մենք", "Դուք", "Անոնք"]

# Mapping Armenian text to English filenames for stability
FOUNDATIONS = {
    "days_of_the_week": {
        "label": "📅 Days of the Week",
        "text": "Երկուշաբթի, Երեքշաբթի, Չորեքշաբթի, Հինգշաբթի, Ուրբաթ, Շաբաթ, Կիրակի"
    },
    "numbers_1_10": {
        "label": "🔢 Numbers (1-10)",
        "text": "Մէկ, Երկու, Երեք, Չորս, Հինգ, Վեց, Եօթը, Ութը, Ինը, Տասը"
    },
    "months_of_the_year": {
        "label": "🗓️ Months of the Year",
        "text": "Յունուար, Փետրուար, Մարտ, Ապրիլ, Մայիս, Յունիս, Յուլիս, Օգոստոս, Սեպտեմբեր, Հոկտեմբեր, Նոյեմբեր, Դեկտեմբեր"
    }
}

TOP_50_VERBS = ["be", "have", "do", "say", "go", "can", "get", "would", "make", "know", "will", "think", "take", "see", "come", "could", "want", "look", "use", "find", "give", "tell", "work", "may", "should", "call", "try", "ask", "need", "feel", "become", "leave", "put", "mean", "keep", "let", "begin", "seem", "help", "talk", "turn", "start", "might", "show", "hear", "play", "run", "move", "like", "live"]

# 2. Key Verification
api_key = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=api_key)

# 3. AUDIO ENGINE
def create_wav_file(pcm_data):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) 
        wf.setframerate(24000)
        wf.writeframes(pcm_data)
    return buf.getvalue()

def get_audio(text_to_speak, filename_slug, slow_mode=False):
    """Uses filename_slug for stable file naming on GitHub/Windows."""
    speed_tag = "_slow" if slow_mode else "_fast"
    file_path = os.path.join(AUDIO_DIR, f"{filename_slug}{speed_tag}.wav")

    # 1. Instant Play from Library if it exists
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return f.read()

    # 2. Generate and Save to Library using Flash-Lite
    speed_instr = "slowly" if slow_mode else "clearly"
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=f"Say this {speed_instr} in Western Armenian: {text_to_speak}",
            config=types.GenerateContentConfig(response_modalities=["AUDIO"])
        )
        audio_bytes = response.candidates[0].content.parts[0].inline_data.data
        wav_data = create_wav_file(audio_bytes)
        
        with open(file_path, "wb") as f:
            f.write(wav_data)
            
        return wav_data
    except Exception as e:
        st.error(f"Audio Error: {e}")
        return None

# 4. Sidebar: Admin & Navigation
with st.sidebar:
    st.header("⚙️ Admin Controls")
    
    if st.button("🛠️ Build Stable Library"):
        with st.status("Generating Stable Audio Files..."):
            for slug, data in FOUNDATIONS.items():
                get_audio(data['text'], slug, slow_mode=False)
                get_audio(data['text'], slug, slow_mode=True)
        st.success("Stable Library Built!")

    st.divider()
    st.write("📥 Download for GitHub:")
    # Display download buttons only for files that exist
    if os.path.exists(AUDIO_DIR):
        files = [f for f in os.listdir(AUDIO_DIR) if f.endswith(".wav")]
        if not files:
            st.info("No files generated yet. Click 'Build' above.")
        for f_name in files:
            with open(os.path.join(AUDIO_DIR, f_name), "rb") as f:
                st.download_button(label=f"Save {f_name}", data=f, file_name=f_name, use_container_width=True)

    st.divider()
    st.header("🎓 Lessons")
    main_mode = st.selectbox("Category:", ["Foundations", "Top 50 Verbs", "Verb Drill Master", "Phrase Translator"])
    slow_audio = st.toggle("🐢 Slow-Motion Audio", value=False)

# 5. Main Lesson Area
if main_mode == "Foundations":
    sub_sel = st.selectbox("Selection:", list(FOUNDATIONS.keys()), format_func=lambda x: FOUNDATIONS[x]['label'])
    content = FOUNDATIONS[sub_sel]
    st.header(content['label'])
    st.write(f"### {content['text']}")
    if st.button("🔊 Listen"):
        audio = get_audio(content['text'], sub_sel, slow_mode=slow_audio)
        if audio: st.audio(audio, format="audio/wav", autoplay=True)

elif main_mode == "Phrase Translator":
    st.header("Phrase Translator")
    phrase = st.text_input("Type English phrase:", "How are you?")
    if phrase:
        prompt = f"Translate to natural Western Armenian: '{phrase}'. Return ONLY Armenian."
        response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
        translated_text = response.text.strip()
        st.write(f"### **Armenian:** {translated_text}")
        if st.button("🔊 Speak"):
            # Phrases still use a simple slug since they aren't pre-built
            phrase_slug = "".join(filter(str.isalnum, phrase))[:20]
            audio = get_audio(translated_text, f"phrase_{phrase_slug}", slow_mode=slow_audio)
            if audio: st.audio(audio, format="audio/wav", autoplay=True)

else: # Verb Modes
    st.header(main_mode)
    verb_input = st.selectbox("Select Verb:", TOP_50_VERBS) if main_mode == "Top 50 Verbs" else st.text_input("Type Verb:", "to dance")
    tense = st.selectbox("Tense:", ["Past", "Present", "Future"])
    
    if verb_input:
        prompt = f"Provide ONLY the 6 conjugated Western Armenian forms for '{verb_input}' in {tense} tense. NO PRONOUNS. Comma-separated."
        response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
        verbs = [v.strip() for v in response.text.strip().split(",") if v.strip()]
        display_list = [f"{PRONOUNS[i]} {verbs[i]}" for i in range(min(len(PRONOUNS), len(verbs)))]
        
        cols = st.columns(3)
        for i, item in enumerate(display_list):
            cols[i % 3].write(f"🔹 **{item}**")
            
        if st.button("🔊 Listen"):
            verb_slug = f"verb_{verb_input.replace(' ', '_')}_{tense.lower()}"
            audio = get_audio(", ".join(display_list), verb_slug, slow_mode=slow_audio)
            if audio: st.audio(audio, format="audio/wav", autoplay=True)
