"""Avatar state tests — no Ursina, no window, deterministic.
Run: python tests/test_avatar_state.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tutor.avatar_state import AvatarState


def test_speaking_opens_mouth_listening_closes():
    s = AvatarState()
    s.set_mode("speaking")
    assert s.update(now=1000.0)["mouth_open"] > 0.1
    s.set_mode("listening")
    assert s.update(now=1001.0)["mouth_open"] == 0.0


def test_thinking_tilts_head():
    s = AvatarState()
    s.set_mode("thinking")
    assert s.update(now=1000.0)["head_tilt"] != 0.0


def test_duration_estimate_scales_with_words():
    s = AvatarState()
    short = s.speaking_duration_estimate("Hi there")
    long = s.speaking_duration_estimate(" ".join(["word"] * 100))
    assert long > short and short >= 1.5


if __name__ == "__main__":
    for fn in [v for k, v in list(globals().items()) if k.startswith("test_")]:
        fn()
        print("PASS", fn.__name__)
    print("All avatar state tests passed")
