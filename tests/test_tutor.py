"""English Tutor tests — no mic, no network, no API key needed.
Run: python tests/test_tutor.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tutor.brain import DemoBrain, TutorBrain, build_system_prompt, load_api_key


def test_prompt_mentions_level_topic_and_one_question():
    p = build_system_prompt("B1", "Travel", True)
    assert "B1" in p and "Travel" in p
    assert "ONE question" in p


def test_demo_opening_and_reply():
    b = DemoBrain("B1", "Daily life")
    assert b.opening()
    r = b.reply("I am tired today", [])
    assert "tired" in r.lower() or "?" in r


def test_brain_without_key_is_demo_not_crash():
    # Ensure no key leaks from the test environment into the brain.
    os.environ.pop("GEMINI_API_KEY", None)
    brain = TutorBrain(level="A2", topic="Work")
    # On this VM google-genai is absent, so online must be False and
    # reply must still work via demo.
    assert brain.reply("hello", []) != ""


def test_no_key_hardcoded_in_brain_source():
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "tutor", "brain.py"), encoding="utf-8").read()
    assert "AIza" not in src, "API keys must never be hard-coded"




def test_clarification_rephrases_last_ai_not_new_question():
    from tutor.brain import DemoBrain
    b = DemoBrain("B1", "Daily life")
    hist = [{"role": "ai", "text": "How was your day today? Tell me one thing you did."}]
    r = b.reply("wtf u mean", hist)
    assert "How was your day" in r, r
    assert "simpler" in r.lower()

def test_answer_acknowledges_what_user_said():
    from tutor.brain import DemoBrain
    b = DemoBrain("B1", "Daily life")
    r = b.reply("I played football with my friends", [])
    assert "football" in r.lower(), r



def test_onefile_settings_looks_next_to_exe_first():
    import sys
    from tutor.brain import settings_paths
    old_frozen = getattr(sys, "frozen", None)
    old_exe = sys.executable
    try:
        sys.frozen = True
        sys.executable = "/fake/Desktop/EnglishTutor3D.exe"
        paths = settings_paths()
        assert paths[0] == "/fake/Desktop/settings.json", paths
    finally:
        if old_frozen is None:
            delattr(sys, "frozen")
        else:
            sys.frozen = old_frozen
        sys.executable = old_exe

if __name__ == "__main__":
    for fn in [v for k, v in list(globals().items()) if k.startswith("test_")]:
        fn()
        print("PASS", fn.__name__)
    print("All English Tutor tests passed")
