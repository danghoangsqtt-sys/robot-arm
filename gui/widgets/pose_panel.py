"""
widgets/pose_panel.py – Trình quản lý tư thế lưu / tải / và chạy theo chuỗi.

Các tư thế (pose) được lưu trữ vào file poses.json tại thư mục làm việc.
Mỗi tư thế lưu trữ toàn bộ các góc khớp và tốc độ.

Tính năng:
  • Lưu các vị trí thanh trượt hiện tại thành một tư thế có tên
  • Tải một tư thế (di chuyển cánh tay robot tới các góc đã lưu)
  • Xóa một tư thế
  • Bộ phát chuỗi: chạy lần lượt các tư thế đã chọn với một khoảng thời gian chờ
  • Xuất / Nhập file JSON
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

from config import C, POSES_FILE, NUM_JOINTS, FONT_LABEL, FONT_BOLD, FONT_SMALL, FONT_MONO


class PosePanel(tk.Frame):
    """
    Bảng khung điều khiển lưu tư thế bên phải.

    `get_angles_fn`  – hàm có thể gọi, trả về danh sách các góc thanh trượt (list[int])
    `get_speeds_fn`  – hàm có thể gọi, trả về danh sách các tốc độ hiện hành (list[int])
    `send_fn`        – hàm callable(str) dùng để gửi lệnh serial
    """

    SEQUENCE_MIN_DELAY_MS = 200

    def __init__(self, master, get_angles_fn, get_speeds_fn, send_fn, **kwargs):
        super().__init__(master, bg=C["surface"], **kwargs)
        self._get_angles = get_angles_fn
        self._get_speeds = get_speeds_fn
        self._send       = send_fn
        self._poses: dict[str, dict] = {}
        self._seq_running = False
        self._seq_items:  list[str]  = []
        self._seq_idx     = 0
        self._seq_after   = None

        self._build()
        self._load_from_disk()

    #  Khởi tạo (Build) 

    def _build(self):
        # Thiết kế dạng thanh ngang
        ctrl_frame = tk.Frame(self, bg=C["surface"], pady=6, padx=10)
        ctrl_frame.pack(fill="x", side="left")

        # Record / Play
        self._seq_btn = tk.Button(
            ctrl_frame, text="● Record", font=FONT_BOLD, width=10,
            bg=C["surface2"], fg=C["text"], relief="flat",
            activebackground=C["border"], activeforeground=C["text"],
            cursor="hand2", command=self._do_save,
        )
        self._seq_btn.pack(side="left", padx=4)

        self._play_btn = tk.Button(
            ctrl_frame, text="▶ Play", font=FONT_BOLD, width=10,
            bg=C["surface2"], fg=C["text"], relief="flat",
            activebackground=C["border"], activeforeground=C["text"],
            cursor="hand2", command=self._toggle_sequence,
        )
        self._play_btn.pack(side="left", padx=4)

        tk.Label(ctrl_frame, text="  |  ", bg=C["surface"], fg=C["border"]).pack(side="left")

        # Nút Import / Export
        tk.Button(
            ctrl_frame, text="💾 Save", font=FONT_SMALL, width=8,
            bg=C["surface2"], fg=C["text"], relief="flat",
            command=self._do_export, cursor="hand2"
        ).pack(side="left", padx=4)

        tk.Button(
            ctrl_frame, text="📂 Load", font=FONT_SMALL, width=8,
            bg=C["surface2"], fg=C["text"], relief="flat",
            command=self._do_import, cursor="hand2"
        ).pack(side="left", padx=4)

        # Trình chọn tư thế (Combobox)
        self._pose_var = tk.StringVar()
        self._cb = ttk.Combobox(
            ctrl_frame, textvariable=self._pose_var, state="readonly", width=15, font=FONT_SMALL
        )
        self._cb.pack(side="left", padx=(10, 4))
        self._cb.bind("<<ComboboxSelected>>", lambda e: self._do_load())

        tk.Button(
            ctrl_frame, text="✕", font=FONT_SMALL, bg=C["red"], fg=C["bg"], relief="flat",
            command=self._do_delete, cursor="hand2"
        ).pack(side="left")

        # Status text
        self._status_var = tk.StringVar(value="Ready")
        tk.Label(
            self, textvariable=self._status_var, bg=C["surface"], fg=C["dim"], font=FONT_SMALL
        ).pack(side="right", padx=10)

    #  Các chức năng của tư thế (Pose actions) 

    def _do_save(self):
        name = simpledialog.askstring(
            "Save Pose", "Pose name:",
            parent=self, initialvalue=f"pose_{len(self._poses)+1}"
        )
        if not name:
            return
        name = name.strip()
        if not name:
            return
        self._poses[name] = {
            "angles": self._get_angles(),
            "speeds": self._get_speeds(),
        }
        self._refresh_list()
        self._save_to_disk()

    def _do_load(self):
        name = self._pose_var.get()
        if not name: return
        pose = self._poses.get(name)
        if not pose: return
        for i, spd in enumerate(pose.get("speeds", [])):
            self._send(f"S {i} {spd}")
        angles = pose["angles"]
        self._send("A " + " ".join(str(a) for a in angles))
        self._status_var.set(f"Loaded: {name}")

    def _do_delete(self):
        name = self._pose_var.get()
        if not name: return
        if messagebox.askyesno("Delete", f"Delete pose '{name}'?", parent=self):
            del self._poses[name]
            self._pose_var.set("")
            self._refresh_list()
            self._save_to_disk()
            self._status_var.set(f"Deleted: {name}")

    def _on_select(self, _event):
        pass

    #  Trình phát chuỗi (Sequence player) 

    def _toggle_sequence(self):
        if self._seq_running:
            self._stop_sequence()
        else:
            self._start_sequence()

    def _start_sequence(self):
        items = list(self._poses.keys())
        if len(items) < 2:
            messagebox.showinfo("Sequence", "Add at least 2 poses to run a sequence.", parent=self)
            return
        self._seq_items   = items
        self._seq_idx     = 0
        self._seq_running = True
        self._play_btn.config(text="■ Stop", bg=C["red"], fg="white")
        self._status_var.set("Playing sequence...")
        self._play_next()

    def _play_next(self):
        if not self._seq_running or not self._seq_items: return
        idx  = self._seq_idx % len(self._seq_items)
        name = self._seq_items[idx]
        pose = self._poses.get(name)
        if pose:
            self._pose_var.set(name)
            angles = pose["angles"]
            self._send("A " + " ".join(str(a) for a in angles))
            self._status_var.set(f"Playing: {name} ({idx+1}/{len(self._seq_items)})")
        self._seq_idx += 1
        # Delay cứng 1500ms cho đơn giản, hoặc lấy từ config
        self._seq_after = self.after(1500, self._play_next)

    def _stop_sequence(self):
        self._seq_running = False
        if self._seq_after:
            self.after_cancel(self._seq_after)
            self._seq_after = None
        self._play_btn.config(text="▶ Play", bg=C["surface2"], fg=C["text"])
        self._status_var.set("Stopped")

    #  Nhập / Xuất (Import / Export) 

    def _do_export(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*")],
            initialfile="poses.json",
            parent=self,
        )
        if path:
            with open(path, "w") as f:
                json.dump(self._poses, f, indent=2)

    def _do_import(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*")],
            parent=self,
        )
        if not path:
            return
        try:
            with open(path) as f:
                data = json.load(f)
            self._poses.update(data)
            self._refresh_list()
            self._save_to_disk()
        except (json.JSONDecodeError, OSError) as e:
            messagebox.showerror("Import Error", str(e), parent=self)

    #  Lưu trữ cố định (Persistence) 

    def _save_to_disk(self):
        try:
            with open(POSES_FILE, "w") as f:
                json.dump(self._poses, f, indent=2)
        except OSError:
            pass

    def _load_from_disk(self):
        if os.path.exists(POSES_FILE):
            try:
                with open(POSES_FILE) as f:
                    self._poses = json.load(f)
                self._refresh_list()
            except (json.JSONDecodeError, OSError):
                self._poses = {}

    def _refresh_list(self):
        items = list(self._poses.keys())
        self._cb.config(values=items)
        if items and not self._pose_var.get():
            self._pose_var.set(items[0])
