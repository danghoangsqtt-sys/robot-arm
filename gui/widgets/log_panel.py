"""
widgets/log_panel.py – Colour-coded serial log / terminal panel.

Displays all sent commands and received responses with syntax colouring:
  • Outgoing (→)  cyan
  • OK / DONE     green
  • ERR:*         red
  • STA: / VAL:   accent purple
  • System msgs   dim grey

Includes a manual send entry so you can type raw commands.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

from config import C, FONT_LOG, FONT_SMALL, FONT_BOLD


class LogPanel(tk.Frame):
    """
    Scrollable colour terminal showing all serial traffic.
    Call `log_send(cmd)` for outgoing and `log_recv(line)` for incoming.
    `send_fn` is called when the user submits a manual command.
    """

    MAX_LINES = 500   # trim when log exceeds this

    def __init__(self, master, send_fn, **kwargs):
        super().__init__(master, bg=C["surface"], **kwargs)
        self._send_fn  = send_fn
        self._paused   = False
        self._build()

    #  Build 

    def _build(self):
        #  Header 
        hdr = tk.Frame(self, bg=C["surface2"], pady=4)
        hdr.pack(fill="x")

        tk.Label(
            hdr, text="SERIAL LOG", bg=C["surface2"],
            fg=C["accent"], font=FONT_BOLD, padx=10
        ).pack(side="left")

        # Pause / clear buttons
        self._pause_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            hdr, text="Pause",
            variable=self._pause_var,
            bg=C["surface2"], fg=C["dim"],
            selectcolor=C["surface"], activebackground=C["surface2"],
            font=FONT_SMALL,
            command=self._on_pause_toggle,
        ).pack(side="right", padx=6)

        tk.Button(
            hdr, text="Clear", font=FONT_SMALL,
            bg=C["surface2"], fg=C["dim"], relief="flat",
            activebackground=C["border"], activeforeground=C["text"],
            cursor="hand2", command=self._clear,
        ).pack(side="right", padx=(0, 4))

        #  Text area 
        txt_frame = tk.Frame(self, bg=C["log_bg"])
        txt_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self._txt = tk.Text(
            txt_frame,
            bg=C["log_bg"], fg=C["log_tx"],
            font=FONT_LOG, relief="flat",
            insertbackground=C["text"],
            state="disabled",
            wrap="word",
            highlightthickness=0,
            cursor="arrow",
        )
        sb = ttk.Scrollbar(txt_frame, command=self._txt.yview)
        self._txt.configure(yscrollcommand=sb.set)

        sb.pack(side="right", fill="y")
        self._txt.pack(fill="both", expand=True)

        #  Colour tags 
        self._txt.tag_configure("send",   foreground=C["log_send"])
        self._txt.tag_configure("ok",     foreground=C["log_recv"])
        self._txt.tag_configure("err",    foreground=C["log_err"])
        self._txt.tag_configure("val",    foreground=C["accent"])
        self._txt.tag_configure("warn",   foreground=C["log_warn"])
        self._txt.tag_configure("dim",    foreground=C["dim"])
        self._txt.tag_configure("ts",     foreground=C["border"])

        #  Manual send bar 
        send_frame = tk.Frame(self, bg=C["surface2"], pady=6, padx=8)
        send_frame.pack(fill="x")

        tk.Label(
            send_frame, text="CMD:", bg=C["surface2"],
            fg=C["dim"], font=FONT_SMALL
        ).pack(side="left", padx=(0, 4))

        self._cmd_var = tk.StringVar()
        cmd_entry = tk.Entry(
            send_frame, textvariable=self._cmd_var,
            bg=C["entry_bg"], fg=C["text"],
            insertbackground=C["accent"],
            relief="flat", font=FONT_LOG,
            highlightthickness=1,
            highlightcolor=C["accent"],
            highlightbackground=C["border"],
        )
        cmd_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        cmd_entry.bind("<Return>", self._on_send)
        cmd_entry.bind("<Up>",   self._history_up)
        cmd_entry.bind("<Down>", self._history_down)

        tk.Button(
            send_frame, text="Send", font=FONT_SMALL,
            bg=C["accent"], fg=C["bg"], relief="flat",
            activebackground=C["accent_dk"], activeforeground=C["bg"],
            cursor="hand2", command=self._on_send, width=6,
        ).pack(side="left")

        #  Command history 
        self._history: list[str] = []
        self._hist_idx = -1

    #  Public logging API 

    def log_send(self, cmd: str):
        self._append(f"→ {cmd}", "send")

    def log_recv(self, line: str):
        if line.startswith("ERR:"):
            tag = "err"
        elif line in ("OK", "DONE", "ARM READY"):
            tag = "ok"
        elif line.startswith(("STA:", "VAL:", "CFG:")):
            tag = "val"
        elif line.startswith("ARM"):
            tag = "warn"
        else:
            tag = "dim"
        self._append(f"← {line}", tag)

    def log_system(self, msg: str):
        self._append(f"  {msg}", "warn")

    #  Private helpers 

    def _append(self, text: str, tag: str = "dim"):
        if self._pause_var.get():
            return
        ts = datetime.now().strftime("%H:%M:%S")
        self._txt.configure(state="normal")

        # Trim if too long
        lines = int(self._txt.index("end-1c").split(".")[0])
        if lines > self.MAX_LINES:
            self._txt.delete("1.0", f"{lines - self.MAX_LINES + 1}.0")

        self._txt.insert("end", f"[{ts}] ", "ts")
        self._txt.insert("end", text + "\n", tag)
        self._txt.configure(state="disabled")
        self._txt.see("end")

    def _clear(self):
        self._txt.configure(state="normal")
        self._txt.delete("1.0", "end")
        self._txt.configure(state="disabled")

    def _on_pause_toggle(self):
        self._paused = self._pause_var.get()

    def _on_send(self, _event=None):
        cmd = self._cmd_var.get().strip()
        if not cmd:
            return
        # Add to history
        if not self._history or self._history[-1] != cmd:
            self._history.append(cmd)
        self._hist_idx = -1
        self._cmd_var.set("")
        self._send_fn(cmd)

    def _history_up(self, _event):
        if not self._history:
            return
        if self._hist_idx == -1:
            self._hist_idx = len(self._history) - 1
        elif self._hist_idx > 0:
            self._hist_idx -= 1
        self._cmd_var.set(self._history[self._hist_idx])

    def _history_down(self, _event):
        if self._hist_idx == -1:
            return
        self._hist_idx += 1
        if self._hist_idx >= len(self._history):
            self._hist_idx = -1
            self._cmd_var.set("")
        else:
            self._cmd_var.set(self._history[self._hist_idx])
