import os
import queue
import re
import subprocess
import sys
import threading
import webbrowser

import customtkinter as ctk
import google.generativeai as genai
import pyttsx3
import speech_recognition as sr


ASSISTANT_NAME = "Loki"
MODEL_NAME = "gemini-1.5-flash"


class LokiApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{ASSISTANT_NAME} - Desktop Voice Assistant")
        self.geometry("900x600")
        self.minsize(800, 520)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.status_var = ctk.StringVar(value="Idle")
        self.conversation_lock = threading.Lock()

        self._build_ui()

        self.recognizer = sr.Recognizer()
        self.microphone = None
        self._init_microphone()

        self.tts_engine = pyttsx3.init()
        self.speech_queue: queue.Queue[str | None] = queue.Queue()
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()

        self.model = None
        self._init_model()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, corner_radius=16)
        header.pack(fill="x", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(
            header,
            text=f"{ASSISTANT_NAME}",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title.pack(side="left", padx=20, pady=10)

        status_label = ctk.CTkLabel(
            header,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=16),
            text_color="#7dd3fc",
        )
        status_label.pack(side="right", padx=20)

        self.history = ctk.CTkTextbox(self, wrap="word", corner_radius=16)
        self.history.pack(fill="both", expand=True, padx=20, pady=10)
        self.history.configure(state="disabled")

        controls = ctk.CTkFrame(self, corner_radius=16)
        controls.pack(fill="x", padx=20, pady=(10, 20))

        listen_btn = ctk.CTkButton(
            controls,
            text="Listen",
            command=self.start_listening,
            width=140,
            height=40,
        )
        listen_btn.pack(side="left", padx=20, pady=10)

        stop_btn = ctk.CTkButton(
            controls,
            text="Stop Speaking",
            command=self.stop_speaking,
            width=140,
            height=40,
        )
        stop_btn.pack(side="left", padx=10)

        exit_btn = ctk.CTkButton(
            controls,
            text="Exit",
            command=self.destroy,
            width=120,
            height=40,
        )
        exit_btn.pack(side="right", padx=20)

        self._append_message(
            ASSISTANT_NAME,
            "Hello! I'm Loki. Click Listen and ask me anything, or tell me to open apps and websites.",
        )

    def _init_microphone(self) -> None:
        try:
            self.microphone = sr.Microphone()
        except Exception as exc:  # noqa: BLE001
            self.microphone = None
            self._append_message(
                ASSISTANT_NAME,
                f"Microphone unavailable: {exc}. Check your audio drivers and PyAudio install.",
            )

    def _init_model(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self._append_message(
                ASSISTANT_NAME,
                "Gemini API key missing. Set GEMINI_API_KEY to enable AI responses.",
            )
            return
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(MODEL_NAME)

    def _speech_worker(self) -> None:
        while True:
            text = self.speech_queue.get()
            if text is None:
                break
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as exc:  # noqa: BLE001
                self._append_message(ASSISTANT_NAME, f"Speech error: {exc}")
            finally:
                self.speech_queue.task_done()

    def _append_message(self, speaker: str, message: str) -> None:
        with self.conversation_lock:
            self.history.configure(state="normal")
            self.history.insert("end", f"{speaker}: {message}\n\n")
            self.history.configure(state="disabled")
            self.history.see("end")

    def set_status(self, status: str) -> None:
        self.status_var.set(status)

    def start_listening(self) -> None:
        if self.microphone is None:
            self._append_message(
                ASSISTANT_NAME, "Microphone not available. Check your setup and restart."
            )
            return
        thread = threading.Thread(target=self._listen_and_respond, daemon=True)
        thread.start()

    def _listen_and_respond(self) -> None:
        self.set_status("Listening")
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                audio = self.recognizer.listen(
                    source, timeout=5, phrase_time_limit=12
                )
            self.set_status("Thinking")
            try:
                text = self.recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                self._append_message(ASSISTANT_NAME, "I couldn't understand that. Try again.")
                self.set_status("Idle")
                return
            except sr.RequestError as exc:
                self._append_message(
                    ASSISTANT_NAME, f"Speech service error: {exc}"
                )
                self.set_status("Idle")
                return

            self._append_message("You", text)
            response = self._handle_command(text)
            self._append_message(ASSISTANT_NAME, response)
            self.speak(response)
        except sr.WaitTimeoutError:
            self._append_message(ASSISTANT_NAME, "Listening timed out. Please try again.")
        except Exception as exc:  # noqa: BLE001
            self._append_message(ASSISTANT_NAME, f"Unexpected error: {exc}")
        finally:
            self.set_status("Idle")

    def speak(self, text: str) -> None:
        self.set_status("Speaking")
        self.speech_queue.put(text)

    def stop_speaking(self) -> None:
        try:
            self.tts_engine.stop()
            self.set_status("Idle")
        except Exception as exc:  # noqa: BLE001
            self._append_message(ASSISTANT_NAME, f"Unable to stop speech: {exc}")

    def _handle_command(self, text: str) -> str:
        cleaned = text.strip().lower()
        if cleaned.startswith("open ") or cleaned.startswith("launch "):
            return self._process_open_command(cleaned)
        if "open" in cleaned and self._looks_like_website(cleaned):
            return self._open_website(cleaned)
        return self._ask_llm(text)

    def _process_open_command(self, cleaned: str) -> str:
        target = cleaned.replace("launch", "open", 1).replace("open", "", 1).strip()
        if not target:
            return "Tell me what you'd like to open."
        if self._looks_like_website(target):
            return self._open_website(target)
        return self._open_application(target)

    def _looks_like_website(self, text: str) -> bool:
        return bool(re.search(r"\b\.com\b|\b\.org\b|\b\.net\b|\bwebsite\b", text))

    def _open_website(self, text: str) -> str:
        known_sites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "gmail": "https://mail.google.com",
            "github": "https://github.com",
            "stackoverflow": "https://stackoverflow.com",
        }
        for key, url in known_sites.items():
            if key in text:
                webbrowser.open(url)
                return f"Opening {key}."
        url_match = re.search(r"(https?://\S+|\b\w+\.(com|org|net)\b)", text)
        if url_match:
            url = url_match.group(0)
            if not url.startswith("http"):
                url = f"https://{url}"
            webbrowser.open(url)
            return f"Opening {url}."
        return "I couldn't detect a website. Please specify the site name or URL."

    def _open_application(self, app_name: str) -> str:
        app_map = {
            "chrome": ["chrome"],
            "google chrome": ["chrome"],
            "notepad": ["notepad"],
            "calculator": ["calc"],
            "terminal": ["cmd" if sys.platform.startswith("win") else "terminal"],
            "settings": ["start", "ms-settings:"] if sys.platform.startswith("win") else ["settings"],
        }
        command = None
        for key, value in app_map.items():
            if key in app_name:
                command = value
                break
        try:
            if command:
                self._launch_command(command)
                return f"Opening {app_name}."
            return self._try_platform_launch(app_name)
        except Exception as exc:  # noqa: BLE001
            return f"Couldn't open {app_name}: {exc}"

    def _launch_command(self, command: list[str]) -> None:
        if sys.platform.startswith("win"):
            subprocess.Popen(command, shell=True)
        else:
            subprocess.Popen(command)

    def _try_platform_launch(self, app_name: str) -> str:
        if sys.platform.startswith("win"):
            os.startfile(app_name)  # noqa: S606
            return f"Opening {app_name}."
        if sys.platform == "darwin":
            subprocess.Popen(["open", "-a", app_name])
            return f"Opening {app_name}."
        subprocess.Popen(["xdg-open", app_name])
        return f"Opening {app_name}."

    def _ask_llm(self, text: str) -> str:
        if not self.model:
            return "LLM is not configured. Please add a GEMINI_API_KEY to continue."
        prompt = (
            "You are Loki, a helpful desktop assistant with a friendly, intelligent personality "
            "similar to Gemini AI. Keep responses concise, actionable, and polite.\n"
            f"User: {text}"
        )
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip() if response.text else "I didn't get a response."
        except Exception as exc:  # noqa: BLE001
            return f"LLM error: {exc}"


if __name__ == "__main__":
    app = LokiApp()
    app.mainloop()
