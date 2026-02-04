# Loki-Desktop-Voice-Assistant
A futuristic Desktop Voice Assistant powered by Google Gemini AI. Features a modern dark-mode GUI, system automation (opening apps/sites), and full conversational intelligence. Built with Python & CustomTkinter.

# 🟢 LOKI - Desktop Voice Assistant

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![AI](https://img.shields.io/badge/AI-Google%20Gemini-orange)
![License](https://img.shields.io/badge/License-MIT-green)

**Loki** is a next-generation Desktop Voice Assistant that bridges the gap between system automation and Generative AI. Unlike traditional assistants that only perform basic tasks, Loki uses the **Google Gemini API** to understand natural language, answer complex queries, and converse intelligently, while retaining the ability to control your PC.

Wrapped in a beautiful, futuristic **Dark Mode GUI**, Loki is designed to be your always-on desktop companion.

---

## ✨ Key Features

* **🧠 Advanced Intelligence:** Powered by Google's **Gemini**, Loki can answer questions, summarize text, and engage in conversation.
* **💻 System Control:** Open applications (Notepad, Calculator, etc.) and websites (YouTube, Google) via voice commands.
* **🎨 Modern GUI:** Built with `CustomTkinter` for a sleek, high-DPI, dark-themed interface.
* **⚡ Real-Time Threading:** Keeps the interface responsive. The GUI never freezes while Loki is listening or thinking.
* **🗣️ Voice Interaction:** Uses `SpeechRecognition` for input and `pyttsx3` for offline text-to-speech output.

---

## 🛠️ Tech Stack

* **Language:** Python
* **AI Engine:** Google Generative AI (Gemini)
* **Interface:** CustomTkinter (Modern UI wrapper for Tkinter)
* **Audio:** SpeechRecognition, PyAudio, Pyttsx3

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.9+ installed on your machine.
* A working microphone and speakers.

### Step 1: Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/Loki-Desktop-Voice-Assistant.git
cd Loki-Desktop-Voice-Assistant
```

### Step 2: Install Dependencies
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

> **Note:** If PyAudio fails to install on Windows, try:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

### Step 3: Get a Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **Get API Key** → **Create API key**.
4. Copy the key.

### Step 4: Set the API Key
**Windows (PowerShell):**
```powershell
setx GEMINI_API_KEY "YOUR_API_KEY"
```

**macOS/Linux:**
```bash
export GEMINI_API_KEY="YOUR_API_KEY"
```

### Step 5: Run Loki
```bash
python main.py
```

---

## 🧠 Voice Commands Examples

* "Open Chrome"
* "Open Notepad"
* "Open youtube.com"
* "Summarize the latest AI trends"
* "What is quantum computing?"

---

## 📄 Project Structure

```
Loki-Desktop-Voice-Assistant/
├── main.py
├── requirements.txt
└── README.md
```

---

## ✅ Notes on Stability

* Loki uses background threads for listening, speaking, and AI responses to keep the GUI smooth.
* Errors (such as missing microphones or invalid API keys) are reported directly in the conversation log.

---

## 📜 License

MIT License - feel free to modify and extend.
