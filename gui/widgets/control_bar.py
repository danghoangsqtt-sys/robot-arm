"""
widgets/control_bar.py – Thanh công cụ bên dưới với các hành động chung cho cánh tay robot.

Các nút chức năng:
  Home All  – gửi lệnh H (đưa tất cả về gốc)
  Stop      – gửi lệnh X (dừng khẩn cấp, được tô màu đỏ)
  Move All  – đọc tất cả thanh trượt và gửi lệnh A
  Query     – gửi lệnh T (làm mới tất cả các góc từ firmware)
  Wait      – gửi lệnh W (chặn cho đến khi cánh tay nhàn rỗi, sau đó nhận DONE)

Hiển thị trạng thái gồm: Idle (Nhàn rỗi) / Moving (Đang di chuyển) / Waiting (Đang chờ) / Disconnected (Mất kết nối).
"""

import tkinter as tk
from tkinter import ttk

from config import C, NUM_JOINTS, FONT_BOLD, FONT_LABEL, FONT_SMALL


class ControlBar(tk.Frame):
    """
    Thanh chức năng bên dưới. Hàm `get_angles_fn` được gọi khi ấn nút 'Move All'
    để thu thập các giá trị thanh trượt hiện tại.
    """

    def __init__(self, master, send_fn, get_angles_fn, **kwargs):
        super().__init__(master, bg=C["surface"], pady=8, padx=10, **kwargs)
        self._send       = send_fn
        self._get_angles = get_angles_fn
        self._status_var = tk.StringVar(value="Disconnected")
        self._build()

    def _build(self):
        #  Các nút điều khiển tay robot (Arm action buttons) 
        buttons = [
            ("⌂  Home All",   self._do_home,     C["accent"],  C["bg"]),
            ("■  Stop",        self._do_stop,     C["red"],     C["bg"]),
            ("▶  Move All",   self._do_move_all,  C["green"],   C["bg"]),
            ("↺  Query",      self._do_query,     C["surface2"],C["text"]),
            ("◷  Wait",       self._do_wait,      C["surface2"],C["text"]),
        ]

        for i, (label, cmd, bg, fg) in enumerate(buttons):
            tk.Button(
                self, text=label, command=cmd,
                font=FONT_BOLD, width=12,
                bg=bg, fg=fg, relief="flat",
                activebackground=C["border"],
                activeforeground=fg,
                cursor="hand2",
            ).grid(row=0, column=i, padx=6)

        #  Đường phân cách (Separator) 
        ttk.Separator(self, orient="vertical").grid(
            row=0, column=len(buttons), padx=16, sticky="ns"
        )

        #  Hiển thị trạng thái (Status display) 
        tk.Label(
            self, text="Status:", bg=C["surface"],
            fg=C["dim"], font=FONT_SMALL
        ).grid(row=0, column=len(buttons) + 1, padx=(0, 6))

        self._status_label = tk.Label(
            self, textvariable=self._status_var,
            bg=C["surface"], fg=C["dim"],
            font=FONT_BOLD, width=14, anchor="w"
        )
        self._status_label.grid(row=0, column=len(buttons) + 2)

    #  Các hành động của nút bấm (Button actions) 

    def _do_home(self):
        self._send("H")

    def _do_stop(self):
        self._send("X")
        self.set_status("Stopped", C["red"])

    def _do_move_all(self):
        angles = self._get_angles()
        cmd = "A " + " ".join(str(a) for a in angles)
        self._send(cmd)
        self.set_status("Moving…", C["orange"])

    def _do_query(self):
        self._send("T")

    def _do_wait(self):
        self._send("W")
        self.set_status("Waiting…", C["orange"])

    #  Các hàm Public API (Public API) 

    def set_status(self, text: str, color: str = C["text"]):
        self._status_var.set(text)
        self._status_label.config(fg=color)
