"""
widgets/log_panel.py – Bảng terminal / log Serial có tô màu.

Hiển thị toàn bộ lệnh được gửi đi và phản hồi nhận về với các màu đánh dấu cú pháp:
  • Gửi đi (→)        màu xanh lục lơ (cyan)
  • OK / DONE         màu xanh lá (green)
  • ERR:*             màu đỏ (red)
  • STA: / VAL:       màu tím nhấn (accent purple)
  • Tin nhắn hệ thống màu xám mờ (dim grey)

Bao gồm một ô nhập để người dùng có thể gửi các lệnh thủ công (raw commands).
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

from config import C, FONT_LOG, FONT_SMALL, FONT_BOLD


class LogPanel(tk.Frame):
    """
    Terminal màu có thể cuộn hiển thị toàn bộ luồng dữ liệu serial.
    Gọi `log_send(cmd)` cho lệnh gửi và `log_recv(line)` cho lệnh nhận.
    Hàm `send_fn` được gọi khi người dùng nhập và gửi lệnh thủ công.
    """

    MAX_LINES = 500   # cắt bớt khi dòng log vượt quá giới hạn này

    def __init__(self, master, send_fn, **kwargs):
        super().__init__(master, bg=C["surface"], **kwargs)
        self._send_fn  = send_fn
        self._paused   = False
        self._build()

    #  Khởi tạo (Build) 

    def _build(self):
        #  Phần đầu (Header) 
        hdr = tk.Frame(self, bg=C["surface2"], pady=4)
        hdr.pack(fill="x")

        tk.Label(
            hdr, text="SERIAL LOG", bg=C["surface2"],
            fg=C["accent"], font=FONT_BOLD, padx=10
        ).pack(side="left")

        # Các nút Dừng / Xóa
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

        #  Vùng hiển thị văn bản (Text area) 
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

        #  Các thẻ màu sắc (Colour tags) 
        self._txt.tag_configure("send",   foreground=C["log_send"])
        self._txt.tag_configure("ok",     foreground=C["log_recv"])
        self._txt.tag_configure("err",    foreground=C["log_err"])
        self._txt.tag_configure("val",    foreground=C["accent"])
        self._txt.tag_configure("warn",   foreground=C["log_warn"])
        self._txt.tag_configure("dim",    foreground=C["dim"])
        self._txt.tag_configure("ts",     foreground=C["border"])

        #  Thanh gửi lệnh thủ công (Manual send bar) 
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

        #  Lịch sử lệnh (Command history) 
        self._history: list[str] = []
        self._hist_idx = -1

    #  Các API Public cho việc ghi log (Public logging API) 

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

    #  Các hàm hỗ trợ nội bộ (Private helpers) 

    def _append(self, text: str, tag: str = "dim"):
        if self._pause_var.get():
            return
        ts = datetime.now().strftime("%H:%M:%S")
        self._txt.configure(state="normal")

        # Xóa bớt nếu quá dài
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
        # Thêm vào lịch sử
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
