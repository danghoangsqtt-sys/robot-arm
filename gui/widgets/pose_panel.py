"""
widgets/pose_panel.py – Named pose save / load / sequence manager.

Poses are persisted to poses.json in the working directory.
Each pose stores all joint angles and speeds.

Features:
  • Save current slider positions as a named pose
  • Load a pose (moves arm to stored angles)
  • Delete a pose
  • Sequence player: play through selected poses with a delay
  • Import / Export JSON
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

from config import C, POSES_FILE, NUM_JOINTS, FONT_LABEL, FONT_BOLD, FONT_SMALL, FONT_MONO


class PosePanel(tk.Frame):
    """
    Right-side panel for pose management.

    `get_angles_fn`  – callable returning list[int] of current slider angles
    `get_speeds_fn`  – callable returning list[int] of current speeds
    `send_fn`        – callable(str) to send a serial command
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

    #  Build 

    def _build(self):
        #  Header 
        hdr = tk.Frame(self, bg=C["surface2"], pady=4)
        hdr.pack(fill="x")
        tk.Label(
            hdr, text="POSE MANAGER", bg=C["surface2"],
            fg=C["accent"], font=FONT_BOLD, padx=10
        ).pack(side="left")

        #  Pose list 
        list_frame = tk.Frame(self, bg=C["surface"])
        list_frame.pack(fill="both", expand=True, padx=6, pady=6)

        sb = ttk.Scrollbar(list_frame)
        sb.pack(side="right", fill="y")

        self._listbox = tk.Listbox(
            list_frame, yscrollcommand=sb.set,
            bg=C["entry_bg"], fg=C["text"], font=FONT_MONO,
            selectbackground=C["accent"], selectforeground=C["bg"],
            relief="flat", highlightthickness=1,
            highlightcolor=C["accent"], highlightbackground=C["border"],
            activestyle="none",
        )
        self._listbox.pack(fill="both", expand=True)
        sb.config(command=self._listbox.yview)
        self._listbox.bind("<Double-Button-1>", lambda _e: self._do_load())

        #  Pose angle preview 
        self._preview_var = tk.StringVar(value="Select a pose to preview")
        tk.Label(
            self, textvariable=self._preview_var,
            bg=C["surface"], fg=C["dim"], font=FONT_SMALL,
            wraplength=200, justify="left", padx=6,
        ).pack(fill="x", pady=(0, 4))
        self._listbox.bind("<<ListboxSelect>>", self._on_select)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=6)

        #  Pose action buttons 
        btn_frame = tk.Frame(self, bg=C["surface"], pady=6)
        btn_frame.pack(fill="x", padx=6)

        for col, (label, cmd, bg, fg) in enumerate([
            ("💾 Save",   self._do_save,   C["accent"],  C["bg"]),
            ("▶ Load",   self._do_load,   C["green"],   C["bg"]),
            ("✕ Delete", self._do_delete, C["red"],     C["bg"]),
        ]):
            tk.Button(
                btn_frame, text=label, command=cmd,
                font=FONT_SMALL, width=8,
                bg=bg, fg=fg, relief="flat",
                activebackground=C["border"], activeforeground=fg,
                cursor="hand2",
            ).grid(row=0, column=col, padx=3)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=6, pady=(4, 0))

        #  Sequence player 
        seq_hdr = tk.Frame(self, bg=C["surface2"], pady=3)
        seq_hdr.pack(fill="x", pady=(4, 2))
        tk.Label(
            seq_hdr, text="SEQUENCE", bg=C["surface2"],
            fg=C["dim"], font=FONT_SMALL, padx=10
        ).pack(side="left")

        seq_ctrl = tk.Frame(self, bg=C["surface"], pady=4)
        seq_ctrl.pack(fill="x", padx=6)

        tk.Label(seq_ctrl, text="Delay(ms):", bg=C["surface"],
                 fg=C["dim"], font=FONT_SMALL).grid(row=0, column=0, padx=(0, 4))

        self._delay_var = tk.IntVar(value=1500)
        tk.Spinbox(
            seq_ctrl, from_=200, to=10000, increment=100,
            textvariable=self._delay_var, width=6,
            bg=C["entry_bg"], fg=C["text"],
            buttonbackground=C["surface2"], relief="flat",
            font=FONT_MONO,
        ).grid(row=0, column=1, padx=(0, 8))

        self._seq_btn = tk.Button(
            seq_ctrl, text="▶ Run Seq", font=FONT_SMALL, width=10,
            bg=C["orange"], fg=C["bg"], relief="flat",
            activebackground=C["border"], activeforeground=C["bg"],
            cursor="hand2", command=self._toggle_sequence,
        )
        self._seq_btn.grid(row=0, column=2)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=6, pady=(4, 0))

        #  Import / Export 
        io_frame = tk.Frame(self, bg=C["surface"], pady=4)
        io_frame.pack(fill="x", padx=6)

        tk.Button(
            io_frame, text="Export…", font=FONT_SMALL,
            bg=C["surface2"], fg=C["text"], relief="flat",
            activebackground=C["border"], activeforeground=C["text"],
            cursor="hand2", command=self._do_export, width=8,
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            io_frame, text="Import…", font=FONT_SMALL,
            bg=C["surface2"], fg=C["text"], relief="flat",
            activebackground=C["border"], activeforeground=C["text"],
            cursor="hand2", command=self._do_import, width=8,
        ).pack(side="left")

    #  Pose actions 

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
        sel = self._listbox.curselection()
        if not sel:
            return
        name = self._listbox.get(sel[0])
        pose = self._poses.get(name)
        if not pose:
            return
        # Send speeds first, then angles
        for i, spd in enumerate(pose.get("speeds", [])):
            self._send(f"S {i} {spd}")
        angles = pose["angles"]
        self._send("A " + " ".join(str(a) for a in angles))

    def _do_delete(self):
        sel = self._listbox.curselection()
        if not sel:
            return
        name = self._listbox.get(sel[0])
        if messagebox.askyesno("Delete", f"Delete pose '{name}'?", parent=self):
            del self._poses[name]
            self._refresh_list()
            self._save_to_disk()

    def _on_select(self, _event):
        sel = self._listbox.curselection()
        if not sel:
            return
        name  = self._listbox.get(sel[0])
        pose  = self._poses.get(name)
        if pose:
            ang  = pose.get("angles", [])
            text = f"{name}\n" + "  ".join(f"J{i}:{a}°" for i, a in enumerate(ang))
            self._preview_var.set(text)

    #  Sequence player 

    def _toggle_sequence(self):
        if self._seq_running:
            self._stop_sequence()
        else:
            self._start_sequence()

    def _start_sequence(self):
        items = list(self._listbox.get(0, "end"))
        if len(items) < 2:
            messagebox.showinfo("Sequence", "Add at least 2 poses to run a sequence.", parent=self)
            return
        self._seq_items   = items
        self._seq_idx     = 0
        self._seq_running = True
        self._seq_btn.config(text="■ Stop Seq", bg=C["red"])
        self._play_next()

    def _play_next(self):
        if not self._seq_running or not self._seq_items:
            return
        idx  = self._seq_idx % len(self._seq_items)
        name = self._seq_items[idx]
        pose = self._poses.get(name)
        if pose:
            self._listbox.selection_clear(0, "end")
            self._listbox.selection_set(idx)
            self._listbox.see(idx)
            angles = pose["angles"]
            self._send("A " + " ".join(str(a) for a in angles))
        self._seq_idx += 1
        delay = max(self.SEQUENCE_MIN_DELAY_MS, self._delay_var.get())
        self._seq_after = self.after(delay, self._play_next)

    def _stop_sequence(self):
        self._seq_running = False
        if self._seq_after:
            self.after_cancel(self._seq_after)
            self._seq_after = None
        self._seq_btn.config(text="▶ Run Seq", bg=C["orange"])

    #  Import / Export 

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

    #  Persistence 

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
        self._listbox.delete(0, "end")
        for name in self._poses:
            self._listbox.insert("end", name)
