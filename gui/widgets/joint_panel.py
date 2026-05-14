"""
widgets/joint_panel.py – Bảng điều khiển cho cả sáu khớp của cánh tay robot.

Mỗi hàng khớp bao gồm:
  • Thanh trượt góc (gửi lệnh M khi thả chuột / ở chế độ trực tiếp)
  • Trường nhập góc trực tiếp
  • Thanh trượt tốc độ
  • Đèn báo đang di chuyển
  • Nút đưa về gốc (Home) của từng khớp riêng biệt

Nút gạt "Live send" (gửi trực tiếp) trên cùng cho phép gửi lệnh trong khi đang kéo thanh trượt.
"""

import tkinter as tk
from tkinter import ttk

from config import C, JOINTS, NUM_JOINTS, FONT_LABEL, FONT_BOLD, FONT_SMALL, FONT_MONO


#  Hàng của một khớp đơn lẻ (Single joint row) 

class _JointRow(tk.Frame):
    """Một hàng: Các nút điều khiển cho một khớp duy nhất."""

    LIVE_THROTTLE_MS = 60   # số mili-giây tối thiểu giữa các lần gửi lệnh trực tiếp (live mode)

    def __init__(self, master, joint_id: int, send_fn, live_var: tk.BooleanVar, **kwargs):
        super().__init__(master, bg=C["surface"], **kwargs)
        self._id       = joint_id
        self._send     = send_fn
        self._live_var = live_var

        name, lo, hi, home, spd = JOINTS[joint_id]
        self._lo   = lo
        self._hi   = hi
        self._home = home

        self._angle_var = tk.IntVar(value=home)
        self._speed_var = tk.IntVar(value=spd)
        self._moving    = False
        self._throttle_id = None   # biến theo dõi hàm after() để giới hạn tốc độ gửi

        self._build(name, lo, hi, home, spd)
        self._angle_var.trace_add("write", self._on_angle_trace)

    #  Khởi tạo (Build) 

    def _build(self, name, lo, hi, home, spd):
        self.columnconfigure(2, weight=1)   # cột của thanh trượt sẽ tự dãn ra

        #  Nhãn ID khớp (J label) 
        tk.Label(
            self, text=f"J{self._id}", width=3,
            bg=C["surface"], fg=C["accent"], font=FONT_BOLD, anchor="e"
        ).grid(row=0, column=0, sticky="e", padx=(6, 2))

        #  Tên khớp (Joint name) 
        tk.Label(
            self, text=name, width=11,
            bg=C["surface"], fg=C["text"], font=FONT_LABEL, anchor="w"
        ).grid(row=0, column=1, sticky="w", padx=(0, 6))

        #  Thanh trượt góc (Angle slider) 
        self._slider = tk.Scale(
            self, from_=lo, to=hi, orient="horizontal",
            variable=self._angle_var, showvalue=False,
            bg=C["surface"], fg=C["text"], highlightthickness=0,
            troughcolor=C["border"], activebackground=C["accent"],
            sliderrelief="flat", bd=0, length=340,
        )
        self._slider.grid(row=0, column=2, sticky="ew", padx=4)
        self._slider.bind("<ButtonRelease-1>", self._on_slider_release)

        #  Nhãn Min / Max (Min / Max labels) 
        tk.Label(
            self, text=str(lo), width=3,
            bg=C["surface"], fg=C["dim"], font=FONT_SMALL, anchor="e"
        ).grid(row=0, column=3)
        tk.Label(
            self, text=str(hi), width=3,
            bg=C["surface"], fg=C["dim"], font=FONT_SMALL, anchor="w"
        ).grid(row=0, column=4)

        #  Khung nhập góc (Angle entry) 
        self._entry_var = tk.StringVar(value=str(home))
        entry = tk.Entry(
            self, textvariable=self._entry_var, width=4,
            bg=C["entry_bg"], fg=C["text"], insertbackground=C["text"],
            relief="flat", font=FONT_MONO, justify="center",
            highlightthickness=1, highlightcolor=C["accent"],
            highlightbackground=C["border"],
        )
        entry.grid(row=0, column=5, padx=(6, 2))
        entry.bind("<Return>",   self._on_entry_commit)
        entry.bind("<FocusOut>", self._on_entry_commit)
        entry.bind("<Up>",   lambda e: self._nudge(+1))
        entry.bind("<Down>", lambda e: self._nudge(-1))

        tk.Label(self, text="°", bg=C["surface"],
                 fg=C["dim"], font=FONT_SMALL).grid(row=0, column=6)

        #  Nhãn tốc độ + thanh trượt nhỏ (Speed label + mini-slider) 
        tk.Label(self, text="Spd", bg=C["surface"],
                 fg=C["dim"], font=FONT_SMALL).grid(row=0, column=7, padx=(10, 2))

        self._spd_slider = tk.Scale(
            self, from_=1, to=20, orient="horizontal",
            variable=self._speed_var, showvalue=False,
            bg=C["surface"], fg=C["text"], highlightthickness=0,
            troughcolor=C["border"], activebackground=C["orange"],
            sliderrelief="flat", bd=0, length=80,
        )
        self._spd_slider.grid(row=0, column=8)
        self._spd_slider.bind("<ButtonRelease-1>", self._on_speed_release)

        self._spd_lbl = tk.Label(
            self, textvariable=self._speed_var, width=2,
            bg=C["surface"], fg=C["orange"], font=FONT_MONO
        )
        self._spd_lbl.grid(row=0, column=9, padx=(2, 8))

        #  Đèn báo đang di chuyển (Moving indicator) 
        self._moving_lbl = tk.Label(
            self, text="", width=6,
            bg=C["surface"], fg=C["orange"], font=FONT_SMALL
        )
        self._moving_lbl.grid(row=0, column=10, padx=(0, 4))

        #  Nút về gốc (Home button) 
        tk.Button(
            self, text="⌂", font=FONT_BOLD, width=2,
            bg=C["surface2"], fg=C["accent"], relief="flat",
            activebackground=C["border"], activeforeground=C["accent"],
            cursor="hand2", command=self._do_home,
        ).grid(row=0, column=11, padx=(0, 8))

    #  Trình xử lý sự kiện (Event handlers) 

    def _on_angle_trace(self, *_):
        """Hàm trace được kích hoạt ở mỗi lần kéo thanh trượt – giới hạn tần suất trong chế độ trực tiếp."""
        if not self._live_var.get():
            return
        if self._throttle_id:
            self.after_cancel(self._throttle_id)
        self._throttle_id = self.after(self.LIVE_THROTTLE_MS, self._send_move)

    def _on_slider_release(self, _event):
        """Luôn luôn gửi khi nhả chuột (ngay cả trong chế độ không trực tiếp)."""
        if self._throttle_id:
            self.after_cancel(self._throttle_id)
            self._throttle_id = None
        self._send_move()

    def _on_speed_release(self, _event):
        self._send(f"S {self._id} {self._speed_var.get()}")

    def _on_entry_commit(self, _event):
        try:
            val = int(self._entry_var.get())
        except ValueError:
            self._entry_var.set(str(self._angle_var.get()))
            return
        val = max(self._lo, min(self._hi, val))
        self._angle_var.set(val)
        self._entry_var.set(str(val))
        self._send_move()

    def _nudge(self, delta: int):
        val = max(self._lo, min(self._hi, self._angle_var.get() + delta))
        self._angle_var.set(val)
        self._send_move()

    def nudge_quiet(self, delta: int) -> bool:
        """Thay đổi góc mà không gửi lệnh M riêng lẻ, dùng cho điều khiển bàn phím."""
        old_val = self._angle_var.get()
        val = max(self._lo, min(self._hi, old_val + delta))
        if val != old_val:
            self._angle_var.set(val)
            self._entry_var.set(str(val))
            return True
        return False

    def _send_move(self):
        ang = self._angle_var.get()
        self._entry_var.set(str(ang))
        self._send(f"M {self._id} {ang}")

    def _do_home(self):
        self._send(f"H {self._id}")

    #  Các hàm Public API (Public API) 

    def set_angle(self, angle: int):
        """Cập nhật giao diện (được gọi khi phản hồi STA/VAL đến)."""
        self._angle_var.set(angle)
        self._entry_var.set(str(angle))

    def set_moving(self, moving: bool):
        self._moving = moving
        self._moving_lbl.config(text="● moving" if moving else "")

    def get_angle(self) -> int:
        return self._angle_var.get()

    def get_speed(self) -> int:
        return self._speed_var.get()

    def set_limits(self, lo: int, hi: int, home: int, speed: int):
        """Cập nhật các giới hạn từ phản hồi CFG."""
        self._lo   = lo
        self._hi   = hi
        self._home = home
        self._slider.config(from_=lo, to=hi)
        self._speed_var.set(speed)


#  Khung chứa tất cả các hàng khớp (Container for all joint rows) 

class JointsPanel(tk.Frame):
    """
    Bảng cuộn chứa tất cả các _JointRow cho mỗi khớp.
    Cung cấp các hàm set_angle() / set_all() để ứng dụng chính
    có thể đẩy phản hồi từ firmware lên giao diện.
    """

    def __init__(self, master, send_fn, **kwargs):
        super().__init__(master, bg=C["surface"], **kwargs)
        self._send = send_fn

        # Nút gạt chế độ trực tiếp (chia sẻ qua tất cả các hàng)
        self._live_var = tk.BooleanVar(value=False)

        self._build()

    def _build(self):
        #  Phần đầu (Header) 
        hdr = tk.Frame(self, bg=C["surface2"], pady=4)
        hdr.pack(fill="x", padx=0, pady=(0, 4))

        tk.Label(
            hdr, text="JOINT CONTROLS", bg=C["surface2"],
            fg=C["accent"], font=FONT_BOLD, padx=10
        ).pack(side="left")

        live_chk = tk.Checkbutton(
            hdr, text="Live send",
            variable=self._live_var,
            bg=C["surface2"], fg=C["dim"],
            selectcolor=C["surface"], activebackground=C["surface2"],
            font=FONT_SMALL,
        )
        live_chk.pack(side="right", padx=10)

        #  Đường phân cách (Separator) 
        col_hdr = tk.Frame(self, bg=C["surface"], pady=2)
        col_hdr.pack(fill="x")
        for col, txt, w in [
            (0, "ID",    4), (1, "Joint",   12), (2, "Angle", 36),
            (3, "",      4), (4, "",         4), (5, "Value",  5),
            (6, "",      1), (7, "",         4), (8, "Speed", 12),
        ]:
            tk.Label(col_hdr, text=txt, bg=C["surface"],
                     fg=C["dim"], font=FONT_SMALL, width=w
                     ).grid(row=0, column=col, sticky="w")

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=2)

        #  Danh sách hàng (Joint rows) 
        self._rows: list[_JointRow] = []
        for i in range(NUM_JOINTS):
            row = _JointRow(
                self, joint_id=i,
                send_fn=self._send,
                live_var=self._live_var,
            )
            row.pack(fill="x", pady=3)
            self._rows.append(row)

            # Tô màu nền xen kẽ nhau
            if i % 2 == 1:
                row.config(bg=C["surface2"])
                for child in row.winfo_children():
                    try:
                        child.config(bg=C["surface2"])
                    except tk.TclError:
                        pass

            ttk.Separator(self, orient="horizontal").pack(fill="x")

    #  Public API 

    def set_angle(self, joint_id: int, angle: int):
        if 0 <= joint_id < NUM_JOINTS:
            self._rows[joint_id].set_angle(angle)

    def set_all(self, angles: list[int]):
        for i, ang in enumerate(angles[:NUM_JOINTS]):
            self._rows[i].set_angle(ang)

    def set_moving(self, joint_id: int, moving: bool):
        if 0 <= joint_id < NUM_JOINTS:
            self._rows[joint_id].set_moving(moving)

    def set_joint_config(self, joint_id: int, lo: int, hi: int, home: int, spd: int):
        if 0 <= joint_id < NUM_JOINTS:
            self._rows[joint_id].set_limits(lo, hi, home, spd)

    def get_all_angles(self) -> list[int]:
        return [r.get_angle() for r in self._rows]

    def nudge_joints(self, deltas: dict[int, int]):
        """Nudge nhiều khớp cùng lúc và chỉ gửi 1 lệnh A."""
        changed = False
        for j_id, d in deltas.items():
            if 0 <= j_id < NUM_JOINTS:
                if self._rows[j_id].nudge_quiet(d):
                    changed = True
        if changed:
            angles = self.get_all_angles()
            self._send("A " + " ".join(str(a) for a in angles))
