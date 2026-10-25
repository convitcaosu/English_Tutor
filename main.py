"""English AI Tutor — prototype v1 (standalone, NOT bot trade / GameBooster).

Loop: AI speaks first -> you speak back (mic) or type -> AI replies -> repeat.
The mic only listens inside a session you started. Press Stop and it stops.
Typed input always works as a fallback, so the loop can be tested even
without a microphone or an API key (demo brain, no key needed).
"""
import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk

from tutor.brain import LEVELS, TOPICS, TutorBrain
from tutor.voice import listen_once, speak

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("English AI Tutor — nói chuyện tiếng Anh")
        self.geometry("900x680")
        self.minsize(760, 560)
        self.brain = None
        self.history = []
        self.active = False
        self.voice_mode = ctk.BooleanVar(value=True)

        top = ctk.CTkFrame(self, corner_radius=14)
        top.pack(fill="x", padx=16, pady=(16, 8))
        ctk.CTkLabel(top, text="English AI Tutor", font=("Segoe UI", 20, "bold")).pack(
            anchor="w", padx=16, pady=(12, 0))
        ctk.CTkLabel(top, text="AI nói trước, bạn nói lại, AI nói tiếp. Mic chỉ nghe trong phiên bạn đã bấm Bắt đầu.",
                     font=("Segoe UI", 12), text_color="#a1a1aa", wraplength=850).pack(
            anchor="w", padx=16, pady=(0, 12))

        cfg = ctk.CTkFrame(self, corner_radius=14)
        cfg.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(cfg, text="Trình độ:").pack(side="left", padx=12)
        self.level_var = ctk.StringVar(value="B1")
        ctk.CTkOptionMenu(cfg, variable=self.level_var, values=LEVELS).pack(side="left", padx=4)
        ctk.CTkLabel(cfg, text="Chủ đề:").pack(side="left", padx=12)
        self.topic_var = ctk.StringVar(value="Daily life")
        ctk.CTkOptionMenu(cfg, variable=self.topic_var, values=TOPICS).pack(side="left", padx=4)
        ctk.CTkCheckBox(cfg, text="Dùng mic", variable=self.voice_mode).pack(side="left", padx=12)

        self.status = ctk.CTkLabel(self, text="Sẵn sàng. Bấm Bắt đầu phiên để AI mở chuyện.",
                                   font=("Segoe UI", 12))
        self.status.pack(fill="x", padx=16, pady=6)

        self.log = ctk.CTkTextbox(self, corner_radius=14, font=("Segoe UI", 13))
        self.log.pack(fill="both", expand=True, padx=16, pady=4)
        self.log.configure(state="disabled")

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=16, pady=8)
        ctk.CTkButton(btns, text="▶ Bắt đầu phiên", fg_color="#16a34a",
                      command=self.start_session).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btns, text="■ Dừng", fg_color="#ea580c",
                      command=self.stop_session).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btns, text="Tổng kết buổi học", command=self.summarize).pack(side="left")

        inp = ctk.CTkFrame(self, fg_color="transparent")
        inp.pack(fill="x", padx=16, pady=(0, 16))
        self.entry = ctk.CTkEntry(inp, placeholder_text="Nếu không dùng mic, gõ câu trả lời tiếng Anh vào đây rồi bấm Gửi...")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry.bind("<Return>", lambda _e: self.send_typed())
        ctk.CTkButton(inp, text="Gửi", command=self.send_typed).pack(side="left")

    # ------------------------------------------------------------ helpers
    def append(self, who: str, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", f"{who}: {text}\n\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def set_status(self, text: str):
        self.status.configure(text=text)

    def ai_say(self, text: str):
        self.history.append({"role": "ai", "text": text})
        self.append("AI", text)
        speak(text)

    def start_session(self):
        if self.active:
            return
        self.brain = TutorBrain(level=self.level_var.get(),
                                topic=self.topic_var.get())
        self.history = []
        self.active = True
        mode = "online (Gemini)" if self.brain.online else "demo (chưa có key, vẫn nói chuyện được)"
        self.set_status(f"Đang trong phiên — chế độ {mode}. AI sẽ mở chuyện trước.")
        threading.Thread(target=self._opening, daemon=True).start()

    def _opening(self):
        text = self.brain.opening()
        self.after(0, lambda: self.ai_say(text))
        self.after(0, self._after_ai)

    def _after_ai(self):
        if not self.active:
            return
        if self.voice_mode.get():
            self.set_status("Đang nghe bạn nói... (nói xong im 2-3 giây)")
            threading.Thread(target=self._listen, daemon=True).start()
        else:
            self.set_status("AI đã nói xong. Gõ câu trả lời vào ô dưới rồi bấm Gửi.")

    def _listen(self):
        try:
            text = listen_once()
        except RuntimeError as e:
            self.after(0, lambda: self.set_status(f"{e} Gõ tay vào ô dưới nhé."))
            return
        if not text:
            self.after(0, lambda: self.set_status(
                "Không nghe rõ. Nói lại, hoặc gõ tay vào ô dưới."))
            return
        self.after(0, lambda: self.on_user_text(text))

    def send_typed(self):
        text = self.entry.get().strip()
        if not text or not self.active:
            return
        self.entry.delete(0, "end")
        self.on_user_text(text)

    def on_user_text(self, text: str):
        if not self.active or not self.brain:
            return
        self.history.append({"role": "user", "text": text})
        self.append("Bạn", text)
        self.set_status("AI đang nghĩ...")
        threading.Thread(target=self._reply, args=(text,), daemon=True).start()

    def _reply(self, text: str):
        reply = self.brain.reply(text, self.history)
        self.after(0, lambda: self.ai_say(reply))
        self.after(0, self._after_ai)

    def stop_session(self):
        self.active = False
        self.set_status("Đã dừng phiên. Mic đã ngừng nghe.")

    def summarize(self):
        if not self.history:
            self.set_status("Chưa có buổi học nào để tổng kết.")
            return
        turns = sum(1 for h in self.history if h["role"] == "user")
        self.append("Tổng kết",
                    f"Bạn đã nói {turns} lượt trong chủ đề {self.topic_var.get()}. "
                    "Ôn lại các câu AI đã sửa trong đoạn chat phía trên và "
                    "thử nói lại chúng một lần nữa vào phiên sau.")
        self.set_status("Đã tổng kết. Bấm Bắt đầu phiên để học tiếp.")


if __name__ == "__main__":
    App().mainloop()
