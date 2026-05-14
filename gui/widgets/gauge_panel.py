import tkinter as tk
import math
from config import C, FONT_BOLD, FONT_SMALL

class GaugeWidget(tk.Canvas):
    def __init__(self, master, joint_id, name, lo, hi, val, color, send_fn, **kwargs):
        super().__init__(master, bg=C["surface"], highlightthickness=0, **kwargs)
        self.joint_id = joint_id
        self.name = name
        self.lo = lo
        self.hi = hi
        self.val = val
        self.color = color
        self._send = send_fn
        self._is_dragging = False

        self.bind("<Configure>", self._on_resize)
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)

    def set_angle(self, val):
        if not self._is_dragging:
            self.val = val
            self._draw()

    def set_limits(self, lo, hi, home, spd):
        self.lo = lo
        self.hi = hi
        self._draw()

    def get_angle(self):
        return self.val

    def nudge(self, delta):
        new_val = max(self.lo, min(self.hi, self.val + delta))
        if new_val != self.val:
            self.val = new_val
            self._draw()
            return True
        return False

    def _on_resize(self, event):
        self._draw()

    def _val_to_angle(self, val):
        # 0..180 maps to 180..0 degrees on canvas
        # Actually lo..hi maps to 180..0
        span = self.hi - self.lo
        if span == 0: return 90
        ratio = (val - self.lo) / span
        return 180 - ratio * 180

    def _angle_to_val(self, angle_deg):
        # angle_deg from 180 to 0
        angle_deg = max(0, min(180, angle_deg))
        ratio = (180 - angle_deg) / 180
        span = self.hi - self.lo
        return int(self.lo + ratio * span)

    def _get_xy(self, cx, cy, r, angle_deg):
        rad = math.radians(angle_deg)
        return cx + r * math.cos(rad), cy - r * math.sin(rad)

    def _on_click(self, event):
        self._is_dragging = True
        self._update_from_mouse(event.x, event.y)

    def _on_drag(self, event):
        self._update_from_mouse(event.x, event.y)

    def _on_release(self, event):
        self._is_dragging = False
        self._update_from_mouse(event.x, event.y)
        self._send(f"M {self.joint_id} {self.val}")

    def _update_from_mouse(self, x, y):
        w, h = self.winfo_width(), self.winfo_height()
        cx, cy = w / 2, h * 0.75
        dx, dy = x - cx, cy - y
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        if angle_deg < 0: angle_deg = 0 if angle_deg > -90 else 180
        new_val = self._angle_to_val(angle_deg)
        if new_val != self.val:
            self.val = new_val
            self._draw()
            if self._is_dragging:
                # To prevent spamming, we could throttle, but for now just send
                # Or wait until release. Let's send live for smooth control.
                self._send(f"M {self.joint_id} {self.val}")

    def _draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10 or h < 10: return

        cx, cy = w / 2, h * 0.75
        r = min(w / 2 - 20, h * 0.6)

        # Draw track
        self.create_arc(cx-r, cy-r, cx+r, cy+r, start=0, extent=180, style=tk.ARC, outline=C["border"], width=10)
        
        # Draw fill
        angle_deg = self._val_to_angle(self.val)
        extent = 180 - angle_deg
        self.create_arc(cx-r, cy-r, cx+r, cy+r, start=angle_deg, extent=extent, style=tk.ARC, outline=self.color, width=10)
        
        # Draw needle
        nx, ny = self._get_xy(cx, cy, r, angle_deg)
        self.create_line(cx, cy, nx, ny, fill="#ffffff", width=3)
        
        # Draw center pivot
        self.create_oval(cx-8, cy-8, cx+8, cy+8, fill="#ff5555", outline="")
        
        # Draw handle
        self.create_oval(nx-6, ny-6, nx+6, ny+6, fill=self.color, outline="")

class GaugeTile(tk.Frame):
    def __init__(self, master, joint_id, name, lo, hi, val, color, send_fn, **kwargs):
        super().__init__(master, bg=C["surface"], highlightbackground=C["border"], highlightthickness=1, **kwargs)
        self.joint_id = joint_id
        self._send = send_fn

        # Header
        hdr = tk.Frame(self, bg=C["surface"])
        hdr.pack(fill="x", padx=10, pady=5)
        
        tk.Label(hdr, text=name, bg=C["surface"], fg=C["text"], font=FONT_BOLD).pack(side="left")
        self.lim_lbl = tk.Label(hdr, text=f"{lo}° - {hi}°", bg=C["surface"], fg=C["dim"], font=FONT_SMALL)
        self.lim_lbl.pack(side="right")

        # Gauge Canvas
        self.gauge = GaugeWidget(self, joint_id, name, lo, hi, val, color, send_fn)
        self.gauge.pack(fill="both", expand=True)

        # Value Entry
        val_frame = tk.Frame(self, bg=C["surface"])
        val_frame.pack(side="bottom", pady=10)
        
        self.val_var = tk.StringVar(value=str(val))
        self.entry = tk.Entry(val_frame, textvariable=self.val_var, font=("Segoe UI", 16, "bold"), width=4,
                              bg=C["entry_bg"], fg=color, justify="center", relief="flat", insertbackground=color)
        self.entry.pack()
        self.entry.bind("<Return>", self._on_entry)
        self.entry.bind("<FocusOut>", self._on_entry)

    def _on_entry(self, event):
        try:
            val = int(self.val_var.get())
            val = max(self.gauge.lo, min(self.gauge.hi, val))
            self.gauge.set_angle(val)
            self.val_var.set(str(val))
            self._send(f"M {self.joint_id} {val}")
        except ValueError:
            self.val_var.set(str(self.gauge.get_angle()))

    def set_angle(self, val):
        self.gauge.set_angle(val)
        self.val_var.set(str(val))

    def set_limits(self, lo, hi, home, spd):
        self.gauge.set_limits(lo, hi, home, spd)
        self.lim_lbl.config(text=f"{lo}° - {hi}°")

    def get_angle(self):
        return self.gauge.get_angle()

    def nudge_quiet(self, delta):
        if self.gauge.nudge(delta):
            self.val_var.set(str(self.gauge.get_angle()))
            return True
        return False

    def set_active(self, is_active):
        color = C["green"] if is_active else C["border"]
        self.config(highlightbackground=color, highlightthickness=2 if is_active else 1)

class GaugeGridPanel(tk.Frame):
    def __init__(self, master, send_fn, **kwargs):
        super().__init__(master, bg=C["bg"], **kwargs)
        self._send = send_fn
        self.tiles = []
        
        # Colors for the 6 joints based on the image
        colors = ["#bd93f9", "#8be9fd", "#50fa7b", "#ffb86c", "#ff79c6", "#f1fa8c"]
        from config import JOINTS
        
        for i, joint in enumerate(JOINTS):
            name, lo, hi, home, spd = joint
            r = i // 3
            c = i % 3
            tile = GaugeTile(self, i, name, lo, hi, home, colors[i], send_fn)
            tile.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
            self.tiles.append(tile)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

    def set_angle(self, joint_id, angle):
        if 0 <= joint_id < len(self.tiles):
            self.tiles[joint_id].set_angle(angle)

    def set_all(self, angles):
        for i, ang in enumerate(angles[:len(self.tiles)]):
            self.tiles[i].set_angle(ang)

    def set_joint_config(self, joint_id, lo, hi, home, spd):
        if 0 <= joint_id < len(self.tiles):
            self.tiles[joint_id].set_limits(lo, hi, home, spd)

    def get_all_angles(self):
        return [t.get_angle() for t in self.tiles]

    def nudge_joints(self, deltas):
        changed = False
        for j_id, d in deltas.items():
            if 0 <= j_id < len(self.tiles):
                if self.tiles[j_id].nudge_quiet(d):
                    changed = True
        if changed:
            angles = self.get_all_angles()
            self._send("A " + " ".join(str(a) for a in angles))

    def set_active(self, joint_id):
        for i, tile in enumerate(self.tiles):
            tile.set_active(i == joint_id)
