"""English tutor brain — prompt + Gemini (if key) + offline demo fallback.

Key rule: the API key is NEVER hard-coded and NEVER sent in chat.
It is read from tutor/settings.json (gitignored, created on the user's
Windows machine) or the GEMINI_API_KEY environment variable.
Without a key the app still runs in demo mode, so the conversation
loop can be tested without spending anything.
"""
import json
import os
import sys

LEVELS = ["A2", "B1", "B2"]
TOPICS = ["Daily life", "Travel", "Work", "Interview", "Free talk"]


def build_system_prompt(level: str, topic: str, explain_vietnamese: bool) -> str:
    vn = ("If the user says 'explain in Vietnamese', explain briefly in "
          "Vietnamese, then continue in English.") if explain_vietnamese else (
          "Stay in English even if the user struggles; use simpler words.")
    return (
        f"You are a friendly English speaking tutor for a {level} learner. "
        f"Topic: {topic}. Speak only in clear, natural English at {level} level. "
        "Ask ONE question at a time and wait for the answer. "
        "If the user makes a grammar mistake, correct it gently in one short "
        "sentence, then continue the conversation — do not lecture. "
        "CRITICAL LOGIC RULE: if the user asks what you mean, says 'wtf', "
        "'huh', 'pardon', 'repeat' or 'I don't understand', DO NOT ask a new "
        "unrelated question. Rephrase your LAST message in simpler words, "
        "give one short example, and ask if that part is clear now. "
        "If the user answers a question, acknowledge what they actually said "
        "before asking the next question. "
        f"{vn} Keep every reply under 60 words so it is easy to listen to."
    )


def settings_paths() -> list:
    """All places a settings.json may live, in priority order.

    Onefile gotcha: when PyInstaller packs to ONE file, __file__ points
    into a temp _MEI folder, NOT next to the exe. If we only looked
    there, a key placed next to EnglishTutor3D.exe would never be found.
    So when frozen, look next to sys.executable FIRST, then the old
    project layout (for running from source).
    """
    paths = []
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        paths.append(os.path.join(exe_dir, "settings.json"))
        paths.append(os.path.join(exe_dir, "tutor", "settings.json"))
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths.append(os.path.join(base, "tutor", "settings.json"))
    return paths


def settings_path() -> str:
    return settings_paths()[0]


def load_api_key() -> str:
    for path in settings_paths():
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and data.get("gemini_api_key"):
                return str(data["gemini_api_key"]).strip()
        except Exception:
            continue
    return os.environ.get("GEMINI_API_KEY", "").strip()


CLARIFY_WORDS = (
    "what do you mean", "what u mean", "wtf", "huh", "pardon",
    "don't understand", "dont understand", "not understand",
    "repeat", "say again", "what?", "i don't get", "confused",
)


def _last_ai(history: list) -> str:
    for h in reversed(history or []):
        if h.get("role") == "ai" and h.get("text"):
            return h["text"]
    return ""


class DemoBrain:
    """Offline tutor — scripted, but WITH conversation logic.

    The v2 bug was here: it ignored what the user actually said and
    rotated generic questions, so 'wtf u mean' got an unrelated question
    back. Fixed rules, in order:
    1. Clarification -> rephrase the LAST AI message, never a new topic.
    2. Direct question from the user -> answer it first, then one follow-up.
    3. Otherwise -> acknowledge what the user actually said, then follow up
       on THAT, not on a rotating list.
    This is still scripted (no LLM), so with a Gemini key the real brain
    above is much smarter. Demo mode can never be as smart as an LLM.
    """

    def __init__(self, level="B1", topic="Daily life"):
        self.level = level
        self.topic = topic
        self.turn = 0

    def opening(self) -> str:
        return (f"Hi! Let's talk about {self.topic.lower()}. "
                "How was your day today? Tell me one thing you did.")

    def reply(self, user_text: str, history: list) -> str:
        self.turn += 1
        raw = (user_text or "").strip()
        t = raw.lower()
        # 1. Clarification — the reported bug.
        if any(w in t for w in CLARIFY_WORDS):
            last = _last_ai(history)
            if last:
                return (f"Sorry, let me say it simpler. {last} "
                        "Do you understand this part now?")
            return ("Sorry, can you tell me which part you did not "
                    "understand? I will explain that part again.")
        # 2. User asks a question — answer it first.
        if raw.endswith("?"):
            if "how are you" in t:
                return "I am good, thank you! And how are you today?"
            if "your name" in t:
                return ("I am your English tutor. You can call me Tutor. "
                        "What is your name?")
            return (f"Good question. About '{raw}' — I think the best way "
                    "is to try it in a simple sentence first. "
                    "What do you think?")
        # 3. Acknowledge what was actually said, then follow up on it.
        if any(w in t for w in ["hello", "hi", "hey"]) and len(t) < 12:
            return "Hello! Nice to hear from you. What did you do today?"
        if "tired" in t:
            return ("Oh, you feel tired. Why are you tired today? "
                    "Did you work a lot, or did you sleep late?")
        if len(raw.split()) <= 3:
            return (f"You said '{raw}'. Can you say that in a full sentence? "
                    "For example, start with 'I ...' and tell me more.")
        return (f"You said: '{raw}'. Nice! Why do you say that? "
                "Tell me one more detail about it.")


class TutorBrain:
    def __init__(self, level="B1", topic="Daily life", explain_vietnamese=True):
        self.level = level
        self.topic = topic
        self.demo = DemoBrain(level, topic)
        self._client = None
        self._model = "gemini-2.5-flash"
        key = load_api_key()
        if key:
            try:
                from google import genai
                self._client = genai.Client(api_key=key)
            except Exception:
                self._client = None

    @property
    def online(self) -> bool:
        return self._client is not None

    def opening(self) -> str:
        if self.online:
            return self.reply("__START__", [])
        return self.demo.opening()

    def reply(self, user_text: str, history: list) -> str:
        if not self.online:
            return self.demo.reply(user_text, history)
        try:
            prompt = build_system_prompt(self.level, self.topic, True)
            chat_text = "\n".join(
                f"{'User' if h['role'] == 'user' else 'Tutor'}: {h['text']}"
                for h in history[-10:])
            full = (f"{prompt}\n\nConversation so far:\n{chat_text}\n"
                    f"User: {user_text}\nTutor:")
            resp = self._client.models.generate_content(
                model=self._model, contents=full)
            text = (resp.text or "").strip()
            return text if text else self.demo.reply(user_text, history)
        except Exception:
            # Never show a raw API error to a learner mid-conversation;
            # fall back to demo so the session keeps going.
            return self.demo.reply(user_text, history)
