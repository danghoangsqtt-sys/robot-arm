import tkinter as tk
import math
from config import C

class RobotArm3D(tk.Canvas):
    def __init__(self, master, get_angles_fn, set_active_fn, **kwargs):
        super().__init__(master, bg="#11111b", highlightthickness=1, highlightbackground=C["border"], **kwargs)
        self._get_angles = get_angles_fn
        self._set_active = set_active_fn
        self._active_id = -1
        
        self.bind("<Configure>", self._on_resize)
        self.bind("<Button-1>", self._on_click)
        
        self._joints_2d = [] # List of (x,y)
        
        # Chiều dài mô phỏng thực tế (Kinematic lengths)
        self.L1 = 50   # Base to Shoulder (ngắn)
        self.L2 = 120  # Shoulder to Elbow (cánh tay trên dài)
        self.L3 = 100  # Elbow to Wrist (cẳng tay)
        self.L4 = 30   # Wrist to Gripper (khớp nối ngắn)
        
        # Poll and draw
        self._poll()

    def set_active(self, joint_id):
        self._active_id = joint_id
        self._draw()

    def _poll(self):
        self._draw()
        self.after(50, self._poll)

    def _on_resize(self, event):
        self._draw()

    def _on_click(self, event):
        # Find closest joint
        if not self._joints_2d: return
        
        best_id = -1
        best_dist = 100000
        for i, (x,y) in enumerate(self._joints_2d):
            if i >= 6: continue # Ignore extra tip points
            dist = (event.x - x)**2 + (event.y - y)**2
            if dist < best_dist and dist < 600: # within ~24px
                best_dist = dist
                best_id = i
        
        if best_id != -1:
            self._set_active(best_id)

    def _project(self, x, y, z):
        # Isometric projection
        cos30 = 0.866
        sin30 = 0.5
        
        px = (x - z) * cos30
        py = y + (x + z) * sin30
        
        w = self.winfo_width()
        h = self.winfo_height()
        
        # scale
        scale = 0.8
        return w/2 + px*scale, h/2 + 120 - py*scale

    def _draw(self):
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or h < 10: return
        
        angles = self._get_angles()
        if not angles or len(angles) < 6: return
        
        a0 = math.radians(angles[0] - 90)
        a1 = math.radians(angles[1] - 90)
        a2 = math.radians(angles[2] - 90)
        a3 = math.radians(angles[3] - 90)
        
        points = []
        
        # 0. Base
        x0, y0, z0 = 0, 0, 0
        points.append((x0,y0,z0))
        
        # 1. Shoulder
        x1, y1, z1 = 0, self.L1, 0
        points.append((x1,y1,z1))
        
        # 2. Elbow
        r2 = self.L2 * math.cos(a1)
        y2 = y1 + self.L2 * math.sin(a1)
        x2 = x1 + r2 * math.cos(a0)
        z2 = z1 - r2 * math.sin(a0)
        points.append((x2,y2,z2))
        
        # 3. Wrist
        pitch3 = a1 + a2
        r3 = self.L3 * math.cos(pitch3)
        y3 = y2 + self.L3 * math.sin(pitch3)
        x3 = x2 + r3 * math.cos(a0)
        z3 = z2 - r3 * math.sin(a0)
        points.append((x3,y3,z3))
        
        # 4. Wrist Roll (use same position as pitch, just a joint marker)
        points.append((x3,y3,z3))
        
        # 5. Gripper Base
        pitch4 = pitch3 + a3
        r4 = self.L4 * math.cos(pitch4)
        y4 = y3 + self.L4 * math.sin(pitch4)
        x4 = x3 + r4 * math.cos(a0)
        z4 = z3 - r4 * math.sin(a0)
        points.append((x4,y4,z4))
        
        self.delete("all")
        
        # Draw floor grid
        grid_size = 50
        for i in range(-3, 4):
            p1x, p1y = self._project(-150, 0, i*grid_size)
            p2x, p2y = self._project(150, 0, i*grid_size)
            self.create_line(p1x, p1y, p2x, p2y, fill="#313145", dash=(2,4))
            
            p1x, p1y = self._project(i*grid_size, 0, -150)
            p2x, p2y = self._project(i*grid_size, 0, 150)
            self.create_line(p1x, p1y, p2x, p2y, fill="#313145", dash=(2,4))

        self._joints_2d = [self._project(x,y,z) for x,y,z in points]
        
        # Vẽ các đoạn cánh tay (Brackets)
        for i in range(len(self._joints_2d)-1):
            if i == 3: continue # 3 and 4 are the same point (Wrist Pitch & Roll)
            x1, y1 = self._joints_2d[i]
            x2, y2 = self._joints_2d[i+1]
            
            is_active_link = (i == self._active_id) or (i+1 == self._active_id)
            color = C["accent"] if is_active_link else "#2a2a3d" # Màu nhôm đen
            width = 12 if is_active_link else 10 # Dày hơn
            self.create_line(x1, y1, x2, y2, fill=color, width=width, capstyle=tk.ROUND)
            
            # Vẽ đường rãnh xẻ giữa ngàm (chi tiết nhỏ)
            if not is_active_link:
                self.create_line(x1, y1, x2, y2, fill="#11111b", width=2, capstyle=tk.ROUND)
            
        # Vẽ các khớp xoay (Servos)
        for i, (x, y) in enumerate(self._joints_2d):
            if i > 5: break
            
            is_active = (i == self._active_id)
            color = C["green"] if is_active else "#1e1e2e" # Servo màu đen
            r = 12 if is_active else 10
            
            # Viền glow
            if is_active:
                self.create_oval(x-r-6, y-r-6, x+r+6, y+r+6, fill="", outline=C["green"], width=2)
                
            # Thân servo
            self.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="#44475a", width=2)
            # Trục xoay servo (trục kim loại)
            self.create_oval(x-3, y-3, x+3, y+3, fill="#f8f8f2", outline="")
        
        # Title
        self.create_text(10, 10, text="> 3D KINEMATICS VIEW", fill=C["dim"], anchor="nw", font=("Segoe UI", 10, "bold"))
        self.create_text(10, 30, text="[CLICK JOINT TO SELECT]", fill=C["accent"], anchor="nw", font=("Segoe UI", 8))
