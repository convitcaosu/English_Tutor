"""English AI Tutor — REAL 3D avatar (Ursina, procedural low-poly).

This is NOT a 2D picture and NOT an HTML mockup. The character is built
from real 3D geometry (spheres / cylinders / cubes) with lighting and a
camera that slowly orbits, so you can see depth. It is low-poly and
procedural on purpose: no external model file, no copyright problem, no
huge download, and it runs on a normal Windows PC without a gaming GPU.

Honest limits (v3):
- Mouth moves in rhythm while the AI speaks, NOT phoneme-accurate lip
  sync. True lip sync needs per-phoneme audio analysis.
- The character is stylised low-poly, NOT a realistic human like
  Ready Player Me. A realistic model would need an external .glb file
  and a web/Unity build, which is a different project.
- Ursina runs its own window, so this is a SEPARATE window from the
  CustomTkinter app in main.py. Run CHAY_3D.bat, or after building,
  double-click dist/EnglishTutor3D/EnglishTutor3D.exe, for 3D.

Run on Windows: CHAY_3D.bat  (installs deps on first run, or runs the
built exe if it exists)
Controls (v3, mic is REAL now): press Start, AI speaks first, then the
app automatically listens on the mic. What the mic heard is shown on
screen, then the AI replies. If the mic fails, type in the box and
press Send — typed input always works as a fallback.
"""
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Panda3D for PyInstaller frozen runtime
if getattr(sys, "frozen", False):
    bundle_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
    panda_dir = os.path.join(bundle_dir, "panda3d")
    panda_etc = os.path.join(panda_dir, "etc")
    etc_root = os.path.join(bundle_dir, "etc")
    
    if os.path.isdir(panda_etc):
        os.environ["PANDA_PRC_DIR"] = panda_etc
        os.environ["PRC_DIR"] = panda_etc
    elif os.path.isdir(etc_root):
        os.environ["PANDA_PRC_DIR"] = etc_root
        os.environ["PRC_DIR"] = etc_root

    for p in (bundle_dir, panda_dir):
        if os.path.isdir(p):
            if hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(p)
                except Exception:
                    pass
            os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")

    try:
        from panda3d.core import load_prc_file_data
        b_posix = bundle_dir.replace("\\", "/")
        p_posix = panda_dir.replace("\\", "/")
        load_prc_file_data("", f"""
plugin-path {b_posix}
plugin-path {p_posix}
load-display pandagl
aux-display pandadx9
aux-display p3tinydisplay
notify-level warning
default-directnotify-level warning
""")
    except Exception:
        pass

from tutor.avatar_state import AvatarState
from tutor.brain import TutorBrain
from tutor.voice import listen_once, speak

try:
    from ursina import (Button, Entity, InputField, Text, Ursina, camera, color,
                        held_keys, mouse, window)
except ImportError as e:
    print("Chưa cài ursina. Chạy CHAY_3D.bat để cài, hoặc: pip install ursina")
    raise SystemExit(1) from e

app = Ursina(title="English AI Tutor — 3D Avatar", borderless=False)
window.color = color.rgb(20, 24, 32)

state = AvatarState()
brain = TutorBrain(level="B1", topic="Daily life")
history = []
speaking_until = 0.0
active = False
mic_on = True
listening = False

# Thread-safe dispatch variables for update() on main thread
pending_user_text = None
pending_ai_say = None
pending_mic_error = None
pending_status = None

# ---------------------------------------------------------------- 3D Scene
floor = Entity(model="plane", scale=(25, 1, 25), color=color.rgb(40, 44, 52), y=-1.6)

# Body & Limbs
body = Entity(model="cube", color=color.azure, scale=(0.85, 1.3, 0.6), y=0.1)
arm_l = Entity(model="cube", color=color.azure, scale=(0.22, 0.9, 0.22),
               position=(-0.65, 0.2, 0), rotation_z=15)
arm_r = Entity(model="cube", color=color.azure, scale=(0.22, 0.9, 0.22),
               position=(0.65, 0.2, 0), rotation_z=-15)

# Head pivot entity so head, eyes, mouth and hair rotate and tilt together
head_pivot = Entity(position=(0, 1.55, 0))
head = Entity(parent=head_pivot, model="sphere", color=color.peach, scale=1.1, position=(0, 0, 0))
hair = Entity(parent=head_pivot, model="sphere", color=color.rgb(50, 35, 25),
              scale=(1.14, 0.55, 1.14), position=(0, 0.42, -0.05))
eye_l = Entity(parent=head_pivot, model="sphere", color=color.black, scale=(0.14, 0.14, 0.08),
               position=(-0.22, 0.13, 0.52))
eye_r = Entity(parent=head_pivot, model="sphere", color=color.black, scale=(0.14, 0.14, 0.08),
               position=(0.22, 0.13, 0.52))
cheek_l = Entity(parent=head_pivot, model="sphere", color=color.rgb(255, 160, 160),
                 scale=(0.15, 0.09, 0.05), position=(-0.35, -0.05, 0.46))
cheek_r = Entity(parent=head_pivot, model="sphere", color=color.rgb(255, 160, 160),
                 scale=(0.15, 0.09, 0.05), position=(0.35, -0.05, 0.46))
mouth = Entity(parent=head_pivot, model="cube", color=color.rgb(180, 50, 60),
               scale=(0.35, 0.05, 0.05), position=(0, -0.23, 0.53))

camera_x = 0.0

# ---------------------------------------------------------------- UI (Ursina)
ai_text = Text(
    text="Welcome! Press [Start] to begin your 3D English conversation.",
    position=(-0.80, 0.45),
    scale=1.2,
    color=color.white
)
ai_text.wordwrap = 50

status_text = Text(
    text="Status: Ready | Mic: ON | Press [Start] to speak with Tutor.",
    position=(-0.80, 0.35),
    scale=1.0,
    color=color.azure
)
status_text.wordwrap = 55

user_text_display = Text(
    text=" ",
    position=(-0.80, 0.27),
    scale=1.1,
    color=color.lime
)
user_text_display.wordwrap = 50

answer_input = InputField(
    default_value="",
    position=(-0.15, -0.42),
    scale=(0.75, 0.06)
)


def on_user_input(text: str):
    """Called when user submits text via mic or keyboard."""
    global pending_user_text
    if not text or not text.strip():
        return
    pending_user_text = text.strip()


def start_listen():
    """Start ONE mic listen in background thread."""
    global listening, pending_status
    if listening:
        return
    if not mic_on:
        pending_status = ("Mic is currently OFF. Click 'Mic ON/OFF' to enable.", color.orange)
        return

    listening = True
    state.set_mode("listening")
    pending_status = ("Listening... Please speak in English now (or type below)", color.lime)

    def _listen():
        global listening, pending_user_text, pending_mic_error, pending_status
        try:
            recognized = listen_once()
            if recognized:
                pending_user_text = recognized
            else:
                pending_status = ("Mic heard silence. Speak again, click 'Mic: Speak', or type below.", color.yellow)
        except RuntimeError as e:
            pending_mic_error = str(e)
        finally:
            listening = False

    threading.Thread(target=_listen, daemon=True).start()


def toggle_mic():
    global mic_on, pending_status
    mic_on = not mic_on
    if mic_on:
        pending_status = ("Mic: ON — Tutor will auto-listen after speaking.", color.lime)
        btn_mic.text = "Mic: ON"
        btn_mic.color = color.dark_gray
    else:
        pending_status = ("Mic: OFF — You can type your answers below.", color.orange)
        btn_mic.text = "Mic: OFF"
        btn_mic.color = color.red


def start_session():
    global active, pending_status
    active = True
    pending_status = ("Session started — AI speaks first...", color.azure)

    def _open():
        global pending_ai_say
        opening_text = brain.opening()
        pending_ai_say = opening_text

    threading.Thread(target=_open, daemon=True).start()


def stop_session():
    global active, pending_status
    active = False
    state.set_mode("idle")
    pending_status = ("Stopped. Press [Start] to begin again.", color.white)


def send_answer():
    text = answer_input.text.strip()
    if text:
        answer_input.text = ""
        on_user_input(text)


def input(key):
    """Handle keyboard input shortcuts."""
    if key == "enter":
        send_answer()


# Control Buttons
btn_start = Button(text="Start", position=(-0.75, -0.32), scale=(0.18, 0.055), color=color.azure, on_click=start_session)
btn_stop = Button(text="Stop", position=(-0.54, -0.32), scale=(0.18, 0.055), color=color.gray, on_click=stop_session)
btn_speak = Button(text="Mic: Speak", position=(-0.33, -0.32), scale=(0.20, 0.055), color=color.green, on_click=start_listen)
btn_mic = Button(text="Mic: ON", position=(-0.10, -0.32), scale=(0.20, 0.055), color=color.dark_gray, on_click=toggle_mic)
btn_send = Button(text="Send", position=(0.33, -0.42), scale=(0.18, 0.06), color=color.azure, on_click=send_answer)


def update():
    global camera_x, pending_user_text, pending_ai_say, pending_mic_error, pending_status, speaking_until

    now = time.time()

    # 1. Main-thread processing of User Text
    if pending_user_text is not None:
        user_msg = pending_user_text
        pending_user_text = None
        history.append({"role": "user", "text": user_msg})
        user_text_display.text = f"You: {user_msg}"
        state.set_mode("thinking")
        status_text.text = "AI is thinking..."
        status_text.color = color.yellow

        def _get_reply():
            global pending_ai_say
            reply = brain.reply(user_msg, history)
            pending_ai_say = reply

        threading.Thread(target=_get_reply, daemon=True).start()

    # 2. Main-thread processing of AI Reply
    if pending_ai_say is not None:
        ai_msg = pending_ai_say
        pending_ai_say = None
        history.append({"role": "ai", "text": ai_msg})
        ai_text.text = f"Tutor: {ai_msg}"
        state.set_mode("speaking")
        speaking_until = now + state.speaking_duration_estimate(ai_msg)
        status_text.text = "Tutor is speaking..."
        status_text.color = color.azure
        speak(ai_msg)

    # 3. Main-thread processing of Mic Errors / Status updates
    if pending_mic_error is not None:
        status_text.text = f"{pending_mic_error} (You can type below to answer)"
        status_text.color = color.red
        pending_mic_error = None

    if pending_status is not None:
        msg, col = pending_status
        status_text.text = msg
        status_text.color = col
        pending_status = None

    # 4. Camera gentle orbit for 3D depth perception
    camera_x += 0.12 * __import__("ursina").time.dt
    import math as _math
    camera.x = _math.sin(camera_x) * 2.2
    camera.z = -6.0 + _math.cos(camera_x) * 0.6
    camera.look_at(head_pivot)

    # 5. Speaking finished -> switch to listening and auto-trigger mic
    if state.mode == "speaking" and now >= speaking_until and speaking_until > 0:
        speaking_until = 0.0
        state.set_mode("listening" if active else "idle")
        if active and mic_on:
            status_text.text = "Listening... Speak in English now (or type below)"
            status_text.color = color.lime
            if not listening:
                start_listen()
        elif active:
            status_text.text = "Mic is OFF. Type your answer below and press Send."
            status_text.color = color.white

    # 6. Update 3D avatar animations (nod, tilt, mouth, blink)
    s = state.update(now)
    mouth.scale_y = 0.05 + s["mouth_open"] * 0.28
    eye_l.scale_y = 0.14 * s["eyes_open"]
    eye_r.scale_y = 0.14 * s["eyes_open"]
    head_pivot.rotation_z = s["head_tilt"] * 25
    head_pivot.rotation_x = s["head_nod"] * 25


app.run()

