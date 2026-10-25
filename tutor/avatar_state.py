"""3D avatar state machine — pure logic, no Ursina import, so it is testable
on any machine (including this Linux VM where Ursina is absent).

Modes: idle / listening / thinking / speaking.
- speaking: mouth opens/closes in a rhythm (NOT phoneme-accurate lip sync;
  true phoneme sync needs audio analysis and is explicitly out of v2).
- listening: mouth closed, head nods slightly.
- thinking: head tilts.
- blink: eyes close briefly every few seconds in every mode.
"""
import math
import time


class AvatarState:
    def __init__(self):
        self.mode = "idle"
        self._t0 = time.time()
        self._blink_until = 0.0
        self._next_blink = self._t0 + 3.0

    def set_mode(self, mode: str):
        if mode in ("idle", "listening", "thinking", "speaking"):
            self.mode = mode

    def update(self, now: float = None) -> dict:
        now = time.time() if now is None else now
        t = now - self._t0
        mouth = 0.0
        head_tilt = 0.0
        head_nod = 0.0
        if self.mode == "speaking":
            # Rhythm mouth: 0.15 .. 0.95, about 5 syllables/sec feel.
            mouth = 0.55 + 0.40 * math.sin(t * 22.0)
            mouth = max(0.15, min(0.95, mouth))
        elif self.mode == "listening":
            head_nod = 0.06 * math.sin(t * 3.0)
        elif self.mode == "thinking":
            head_tilt = 0.18
        # Blink handling (deterministic-ish, driven by wall time in prod,
        # but testable by passing explicit `now`).
        if now >= self._next_blink:
            self._blink_until = now + 0.15
            self._next_blink = now + 3.0 + (t % 1.5)
        eyes_open = 0.15 if now < self._blink_until else 1.0
        return {
            "mode": self.mode,
            "mouth_open": round(mouth, 3),
            "eyes_open": eyes_open,
            "head_tilt": round(head_tilt, 3),
            "head_nod": round(head_nod, 3),
        }

    def speaking_duration_estimate(self, text: str) -> float:
        """Rough TTS duration: ~150 words/min, min 1.5s. Used only to
        keep the mouth moving for about as long as the voice plays."""
        words = max(1, len((text or "").split()))
        return max(1.5, words / 150.0 * 60.0)
