"""
UI Renderers for Armenian Tutor v20 Tools.

Contains rendering functions for:
- Verb Conjugation Tool
- Live Translator
"""

import streamlit as st
from verb_conjugation import VERBS, list_verbs_alphabetically, PRONOUNS
from audio_manager import AudioManager
from translation import translate_and_speak
from config import ENABLE_SPEECH_PRACTICE

if ENABLE_SPEECH_PRACTICE:
    from speech_analysis import render_mic_button


# ============================================================================
# VERB CONJUGATION TOOL
# ============================================================================

def render_verb_conjugation_tool(voice: str):
    """
    Render the verb conjugation tool with dropdown and audio.
    
    Args:
        voice: "male" or "female" - which voice to use for audio
    """
    st.markdown("### 🔤 Verb Conjugation Tool")
    st.markdown("Practice all 50 Western Armenian verbs with audio conjugations.")
    
    # Get alphabetically sorted verb list
    verb_list = list_verbs_alphabetically()
    verb_options = [f"{infinitive}" for _, infinitive in verb_list]
    
    # Verb selector
    selected_verb_display = st.selectbox(
        "Select a verb:",
        verb_options,
        key="verb_selector"
    )
    
    # Find the verb key
    selected_verb_key = None
    for verb_key, infinitive in verb_list:
        if infinitive == selected_verb_display:
            selected_verb_key = verb_key
            break
    
    if not selected_verb_key:
        st.error("Verb not found")
        return
    
    # Get verb data
    verb = VERBS[selected_verb_key]
    
    # Display infinitive
    st.markdown(f"**{verb.infinitive_armenian}** ({verb.infinitive_phonetic})")
    st.markdown("---")
    
    # Tense selector
    tense = st.radio(
        "Select tense:",
        ["Present", "Past", "Future"],
        horizontal=True,
        key="tense_selector"
    )
    
    tense_key = tense.lower()
    
    # Get conjugations for selected tense
    conjugations = verb.conjugations[tense_key]
    
    # Display conjugations in a nice format
    st.markdown(f"#### {tense} Tense")
    
    # Create 2 columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Display all 6 conjugations
        for i, (pronoun, conjugation) in enumerate(zip(PRONOUNS, conjugations)):
            st.markdown(f"**{pronoun}:** {conjugation}")
    
    with col2:
        # Audio button
        audio_url = AudioManager.get_verb_url(verb.verb_key, tense_key, voice)
        
        st.markdown("**Listen:**")
        st.audio(audio_url, format="audio/mp3")
        
        st.caption(f"🎙️ {voice.capitalize()} voice")
    
    # Info box
    st.info(
        "💡 **Tip:** The audio includes pronouns with 750ms pauses between each conjugation. "
        "Listen carefully to hear the proper pronunciation!"
    )


# ============================================================================
# LIVE TRANSLATOR
# ============================================================================

def render_live_translator(voice: str):
    """
    Render the live English → Armenian translator with TTS.
    
    Args:
        voice: "male" or "female" - which voice to use for TTS
    """
    st.markdown("### 🗣️ Live Translator")
    st.markdown("Type English text and hear it in Western Armenian!")
    
    # Check for Azure credentials
    if "AZURE_SPEECH_KEY" not in st.secrets:
        st.error(
            "⚠️ Azure Speech API key not configured. "
            "Please add AZURE_SPEECH_KEY to Streamlit secrets."
        )
        st.info(
            "To use this feature locally, set the environment variable:\n"
            "```\n"
            "export AZURE_SPEECH_KEY='your-key-here'\n"
            "```"
        )
        return
    
    # Text input
    english_text = st.text_area(
        "Enter English text:",
        placeholder="Type something like: Hello, how are you?",
        height=100,
        key="translator_input"
    )
    
    # Translate button
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        translate_button = st.button(
            "🔊 Translate & Speak",
            use_container_width=True,
            type="primary"
        )
    
    # Handle translation
    if translate_button and english_text.strip():
        with st.spinner("Translating..."):
            try:
                # Get Azure credentials from secrets
                api_key = st.secrets["AZURE_SPEECH_KEY"]
                region = st.secrets.get("AZURE_SPEECH_REGION", "eastus")
                
                # Translate and generate audio
                armenian_text, audio_data = translate_and_speak(
                    english_text,
                    api_key,
                    region,
                    voice
                )
                
                # Store in session state so it persists across reruns
                st.session_state.last_translation = armenian_text
                st.session_state.last_translation_audio = audio_data

                st.success("✅ Translation complete!")

            except Exception as e:
                st.error(f"Translation failed: {str(e)}")
                st.info(
                    "💡 Make sure your Azure Speech API key is valid and has quota remaining."
                )

    elif translate_button:
        st.warning("Please enter some text to translate.")

    # Display last translation (persists across reruns)
    if st.session_state.get("last_translation"):
        st.markdown("#### Armenian:")
        st.markdown(f"**{st.session_state.last_translation}**")

        if st.session_state.get("last_translation_audio"):
            st.audio(st.session_state.last_translation_audio, format="audio/mp3")
            st.caption(f"🎙️ {voice.capitalize()} voice")

        # Speech practice
        if ENABLE_SPEECH_PRACTICE:
            render_mic_button(
                st.session_state.last_translation,
                "mic_translator"
            )
    
    # Info boxes
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(
            "💡 **Common Phrases:**\n"
            "- Hello\n"
            "- Good morning\n"
            "- Thank you\n"
            "- How are you?\n"
            "- I love you"
        )
    
    with col2:
        st.info(
            "⚙️ **How it works:**\n"
            "1. Google Translate converts English → Armenian\n"
            "2. Azure TTS speaks the Armenian text\n"
            "3. Pronunciation hacks applied for Western dialect"
        )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def show_tool_placeholder(tool_name: str):
    """
    Show a placeholder for tools that aren't implemented yet.
    
    Args:
        tool_name: Name of the tool
    """
    st.info(f"🚧 {tool_name} coming soon!")
    st.markdown(
        "This tool is planned for a future update. "
        "Check back later for more learning resources!"
    )
