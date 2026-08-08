#!/usr/bin/env python3
"""FlowTimer — 极简番茄钟 / Minimal Pomodoro Timer"""
import tkinter as tk
from tkinter import ttk, messagebox
import time, threading, winsound

TR = {
    "zh": {
        "title": "FlowTimer · 番茄钟",
        "start": "▶ 开始",
        "pause": "⏸ 暂停",
        "reset": "↺ 重置",
        "minutes": "分钟",
        "work": "专注",
        "break": "休息",
        "long_break": "长休息",
        "done": "时间到!",
        "help_text": ("FlowTimer 使用说明\n\n"
            "1. 默认 25 分钟专注 + 5 分钟休息\n"
            "2. 点击「▶ 开始」倒计时\n"
            "3. 结束后自动播放提示音\n"
            "4. 预设按钮快速切换时长\n\n"
            "纯本地运行，零隐私风险。"),
        "disclaimer": ("免责声明\n\n"
            "1. FlowTimer 是纯本地计时工具。\n"
            "2. 按原样（AS-IS）提供，不提供任何担保。\n\n© 永远的兰兰"),
        "about": ("FlowTimer v1.0\n\n极简番茄钟\n"
            "Python 3 + tkinter\n单文件 ~10MB\n\n"
            "GitHub: https://github.com/podcatcher962/FlowTimer\n© 永远的兰兰"),
    },
    "en": {
        "title": "FlowTimer · Pomodoro",
        "start": "▶ Start",
        "pause": "⏸ Pause",
        "reset": "↺ Reset",
        "minutes": "min",
        "work": "Focus",
        "break": "Break",
        "long_break": "Long Break",
        "done": "Time's up!",
        "help_text": ("FlowTimer Help\n\n"
            "1. Default: 25 min focus + 5 min break\n"
            "2. Click ▶ Start to begin\n"
            "3. Beep on completion\n"
            "4. Preset buttons for quick switching\n\nPure local."),
        "disclaimer": ("Disclaimer\n\n"
            "1. Pure local timer tool.\n"
            "2. AS-IS without warranty.\n\n© forever-chitanda"),
        "about": ("FlowTimer v1.0\n\nMinimal Pomodoro Timer\n"
            "Python 3 + tkinter\nSingle-file ~10MB\n\n"
            "GitHub: https://github.com/podcatcher962/FlowTimer\n© forever-chitanda"),
    },
}

PRESETS = [25, 15, 5, 45, 10]

class FlowTimer:
    def __init__(self):
        self.root = tk.Tk()
        self.lang = "zh"
        self.seconds = 25 * 60
        self.running = False
        self.paused = False
        self.root.title("FlowTimer")
        self.root.geometry("480x480")
        self.root.minsize(300, 400)
        self.root.configure(bg="#F5F5F5")
        self.accent = "#7C4DFF"
        self._build_menu()
        self._build_ui()
        self._toggle_lang()
        self.root.mainloop()

    def _t(self, k): return TR[self.lang].get(k, k)

    def _build_menu(self):
        mb = tk.Menu(self.root)
        hm = tk.Menu(mb, tearoff=0)
        hm.add_command(label=self._t("help_text")[:10], command=lambda: messagebox.showinfo("Help", self._t("help_text")))
        hm.add_command(label=self._t("disclaimer")[:10], command=lambda: messagebox.showinfo("Disclaimer", self._t("disclaimer")))
        hm.add_separator()
        hm.add_command(label=self._t("about")[:10], command=lambda: messagebox.showinfo("About", self._t("about")))
        mb.add_cascade(label="Help" if self.lang == "en" else "帮助", menu=hm)
        self.root.config(menu=mb)

    def _build_ui(self):
        # Title
        tb = tk.Frame(self.root, bg=self.accent, height=42)
        tb.pack(fill=tk.X, padx=8, pady=(8, 0))
        tb.pack_propagate(False)
        self.title_lbl = tk.Label(tb, text="", font=('Microsoft YaHei UI', 12, 'bold'), fg="white", bg=self.accent)
        self.title_lbl.pack(side=tk.LEFT, padx=(16, 4), pady=8)
        tk.Label(tb, text="永远的兰兰", font=('Microsoft YaHei UI', 8), fg="#D1C4E9", bg=self.accent).pack(side=tk.LEFT, pady=8)
        self.lang_btn = tk.Button(tb, text="中/EN", font=('Microsoft YaHei UI', 9, 'bold'), bg="#4A148C", fg="white",
                                   relief=tk.FLAT, cursor="hand2", command=self._toggle_lang, padx=10, pady=3)
        self.lang_btn.pack(side=tk.RIGHT, padx=12, pady=8)

        card = tk.Frame(self.root, bg="#FFF")
        card.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Timer display
        self.timer_label = tk.Label(card, text="25:00", font=('Consolas', 56, 'bold'),
                                    bg="#FFF", fg=self.accent)
        self.timer_label.pack(pady=(40, 10))

        self.status_label = tk.Label(card, text="", font=('Microsoft YaHei UI', 12),
                                     bg="#FFF", fg="#757575")
        self.status_label.pack(pady=(0, 20))

        # Preset buttons
        pf = tk.Frame(card, bg="#FFF")
        pf.pack()
        self.preset_btns = []
        for i, mins in enumerate(PRESETS):
            btn = tk.Button(pf, text=f"{mins}{self._t('minutes')}",
                font=('Microsoft YaHei UI', 10, 'bold'), bg="#F3E5FF", fg=self.accent,
                relief=tk.FLAT, cursor="hand2",
                command=lambda m=mins: self._set_time(m),
                padx=14, pady=6)
            btn.grid(row=0, column=i, padx=3, pady=3)
            self.preset_btns.append(btn)

        # Custom time
        cf = tk.Frame(card, bg="#FFF")
        cf.pack(pady=(10, 30))
        self.custom_entry = tk.Entry(cf, font=('Consolas', 12), width=5,
            bg="#F8F4FF", fg="#212121", relief=tk.FLAT, bd=1, justify=tk.CENTER)
        self.custom_entry.insert(0, "25")
        self.custom_entry.pack(side=tk.LEFT, padx=4)
        self.custom_btn = tk.Button(cf, text=self._t("minutes"),
            font=('Microsoft YaHei UI', 10, 'bold'), bg="#E0D0FF", fg=self.accent,
            relief=tk.FLAT, cursor="hand2",
            command=lambda: self._set_time(int(self.custom_entry.get() or "25")),
            padx=12, pady=4)
        self.custom_btn.pack(side=tk.LEFT)

        # Control buttons
        bf = tk.Frame(card, bg="#F3E5FF")
        bf.pack(fill=tk.X, padx=16, pady=(0, 20))
        self.start_btn = tk.Button(bf, text="", font=('Microsoft YaHei UI', 11, 'bold'),
            bg="#43A047", fg="white", relief=tk.FLAT, cursor="hand2",
            command=self._toggle_timer, padx=18, pady=8)
        self.start_btn.pack(side=tk.LEFT, padx=4, pady=5)
        self.reset_btn = tk.Button(bf, text="", font=('Microsoft YaHei UI', 11, 'bold'),
            bg="#FF5252", fg="white", relief=tk.FLAT, cursor="hand2",
            command=self._reset, padx=18, pady=8)
        self.reset_btn.pack(side=tk.RIGHT, padx=4, pady=5)

    def _set_time(self, mins):
        if self.running:
            return
        self.seconds = mins * 60
        self._update_display()

    def _update_display(self):
        m = self.seconds // 60
        s = self.seconds % 60
        self.timer_label.config(text=f"{m:02d}:{s:02d}")
        if self.running and not self.paused:
            color = "#E53935" if self.seconds < 60 else self.accent
            self.timer_label.config(fg=color)

    def _toggle_timer(self):
        if not self.running:
            self.running = True
            self.paused = False
            self.start_btn.config(text=self._t("pause"), bg="#FF9100")
            self.status_label.config(text="⏳ " + (self._t("work") if self.lang == "zh" else "Focusing..."))
            threading.Thread(target=self._countdown, daemon=True).start()
        elif not self.paused:
            self.paused = True
            self.start_btn.config(text=self._t("start"), bg="#43A047")
            self.status_label.config(text="⏸ " + ("已暂停" if self.lang == "zh" else "Paused"))
        else:
            self.paused = False
            self.start_btn.config(text=self._t("pause"), bg="#FF9100")
            self.status_label.config(text="⏳ " + (self._t("work") if self.lang == "zh" else "Focusing..."))

    def _countdown(self):
        while self.seconds > 0 and self.running:
            if not self.paused:
                time.sleep(1)
                self.seconds -= 1
                self.root.after(0, self._update_display)
            else:
                time.sleep(0.2)
        if self.seconds <= 0 and self.running:
            self.running = False
            self.root.after(0, self._on_done)

    def _on_done(self):
        self.timer_label.config(fg="#E53935")
        self.status_label.config(text="✅ " + self._t("done"))
        self.start_btn.config(text=self._t("start"), bg="#43A047")
        # Beep 3 times
        for _ in range(3):
            winsound.Beep(800, 300)
            time.sleep(0.3)

    def _reset(self):
        self.running = False
        self.paused = False
        self.start_btn.config(text=self._t("start"), bg="#43A047")
        self.status_label.config(text="")
        self.timer_label.config(fg=self.accent)
        self._update_display()

    def _toggle_lang(self):
        self.lang = "en" if self.lang == "zh" else "zh"
        self.root.title(self._t("title"))
        self.title_lbl.config(text=self._t("title"))
        self.lang_btn.config(text="EN/中" if self.lang == "zh" else "中/EN")
        self.start_btn.config(text=self._t("start") if not self.running else self._t("pause"))
        self.reset_btn.config(text=self._t("reset"))
        for i, mins in enumerate(PRESETS):
            self.preset_btns[i].config(text=f"{mins}{self._t('minutes')}")
        self.custom_btn.config(text=self._t("minutes"))
        self._build_menu()

if __name__ == "__main__":
    FlowTimer()
