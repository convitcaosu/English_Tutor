import threading


def speak(text: str):
    """Speak in a background thread. Returns immediately."""
    if not text or not text.strip():
        return

    def _run():
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", 160)
            try:
                for v in engine.getProperty("voices") or []:
                    name = (getattr(v, "name", "") or "").lower()
                    vid = (getattr(v, "id", "") or "").lower()
                    if "en" in name or "en-us" in vid or "english" in name or "david" in name or "zira" in name:
                        engine.setProperty("voice", v.id)
                        break
            except Exception:
                pass
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass
    threading.Thread(target=_run, daemon=True).start()


def listen_once(timeout: int = 7, phrase_time_limit: int = 15) -> str:
    """Listen once and return the recognised English text.
    Returns empty string if user was silent or speech was unclear.
    Raises RuntimeError ONLY if mic hardware cannot be opened or network fails."""
    try:
        import speech_recognition as sr
    except ImportError as e:
        raise RuntimeError("Chưa cài SpeechRecognition hoặc PyAudio — vui lòng kiểm tra cài đặt.") from e

    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.8

    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.4)
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except sr.WaitTimeoutError:
        # Timeout waiting for speech is normal silence, NOT a mic error
        return ""
    except Exception as e:
        raise RuntimeError(f"Lỗi thiết bị Mic: {e}") from e

    try:
        return (r.recognize_google(audio, language="en-US") or "").strip()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        raise RuntimeError(f"Lỗi kết nối Google Speech (cần Internet): {e}") from e
    except Exception:
        return ""

