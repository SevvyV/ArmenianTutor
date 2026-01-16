# 🇦🇲 HyeTutor 2.0 beta
**A Custom AI-Powered Western Armenian Tutor for Language Mastery.**

HyeTutor is a specialized language learning platform designed to help students master Western Armenian through interactive drills, real-time translation, and AI-driven pronunciation feedback.

## ✨ Key Features
- **📅 Foundations Module:** Pre-built curriculum for Days of the Week, Numbers (1-10), and Months of the Year.
- **🔄 Verb Drill Master:** Dynamic conjugation engine for the "Top 50 Essential Verbs" and custom user-input verbs.
- **🗣️ Phrase Translator:** Instant English-to-Western Armenian translation with high-fidelity audio.
- **🐢 Slow-Motion Mode:** One-click toggle to slow down audio for deep phonetic study.
- **📊 AI Evaluation:** Real-time analysis of user recordings with a 1-10 pronunciation score and specific correction tips.

## 🚀 Technical Stack
- **Framework:** Streamlit (Python)
- **AI Engine:** Google Gemini 2.5 Flash-Lite (Optimized for speed)
- **TTS Engine:** Gemini Native Text-to-Speech (Western Armenian dialect)
- **Deployment:** Streamlit Cloud + GitHub Tier 1 Priority

## 📁 Project Structure
- `app.py`: The main application logic and UI.
- `audio_library/`: Persistent storage for foundation and verb audio files (Lightning-fast playback).
- `.streamlit/secrets.toml`: Secure storage for API keys (Not tracked in version control).

## 🛠️ Installation & Setup
To run this project locally:
1. Clone the repository: `git clone https://github.com/[YOUR_USERNAME]/Elite-Armenian-Tutor.git`
2. Install dependencies: `pip install streamlit google-genai`
3. Add your `GOOGLE_API_KEY` to your local environment secrets.
4. Run the app: `streamlit run app.py`

## 📈 Roadmap
- [ ] **V5.1:** Implement "Word of the Day" notifications.
- [ ] **V5.2:** Add "Progress Stickers" for mastered verbs.
- [ ] **V5.5:** Enable Family Chat Mode for saving common phrases.

---
*Created with ❤️ for Armenian Language preservation.*
