import tkinter as tk
from tkinter import ttk

from config import (
    APP_TITLE, APP_VERSION, WINDOW_SIZE, WINDOW_MIN,
    C, NUM_JOINTS, FONT_BOLD, FONT_SMALL,
)
from serial_comm import SerialComm
from widgets.connection_bar import ConnectionBar
from widgets.control_bar    import ControlBar
from widgets.pose_panel     import PosePanel
from widgets.gauge_panel    import GaugeGridPanel


#  Tùy chỉnh giao diện ttk (ttk style customisation) 

def _apply_theme(root: tk.Tk) -> None:
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".",
        background=C["surface"], foreground=C["text"],
        fieldbackground=C["entry_bg"], troughcolor=C["border"],
        bordercolor=C["border"], darkcolor=C["surface"],
        lightcolor=C["surface"], selectbackground=C["accent"],
        selectforeground=C["bg"], font=("Segoe UI", 10),
    )
    style.configure("TCombobox",
        fieldbackground=C["entry_bg"], background=C["surface2"],
        foreground=C["text"], arrowcolor=C["accent"],
        selectbackground=C["accent"], selectforeground=C["bg"],
    )
    style.map("TCombobox",
        fieldbackground=[("readonly", C["entry_bg"])],
        foreground=[("readonly", C["text"])],
    )
    style.configure("TScrollbar",
        background=C["surface2"], troughcolor=C["surface"],
        arrowcolor=C["dim"], bordercolor=C["border"],
    )
    style.configure("TSeparator", background=C["border"])
    style.configure("TSpinbox",
        fieldbackground=C["entry_bg"], foreground=C["text"],
        arrowcolor=C["accent"],
    )


#  Lớp ứng dụng chính (Application class) 

class ArmControlApp(tk.Tk):

    POLL_MS = 40   # khoảng thời gian chờ vòng lặp serial

    def __init__(self):
        super().__init__()
        self._active_joint = -1

        self.title(f"{APP_TITLE}  v{APP_VERSION}")
        self.geometry(WINDOW_SIZE)
        self.minsize(*WINDOW_MIN)
        self.configure(bg=C["bg"])
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        _apply_theme(self)

        self._comm = SerialComm()
        self._build_ui()
        self._init_keyboard()
        self._start_serial_poll()

    #  Điều khiển bàn phím (Keyboard control) 

    def _init_keyboard(self):
        self._keys_pressed = set()
        self.bind("<KeyPress>", self._on_key_press)
        self.bind("<KeyRelease>", self._on_key_release)
        self._key_poll()

    def _on_key_press(self, event):
        # Bỏ qua nếu đang gõ vào text box
        if isinstance(event.widget, (tk.Entry, tk.Text, tk.Spinbox)): return
        if event.keysym not in self._keys_pressed:
            self._keys_pressed.add(event.keysym)

    def _on_key_release(self, event):
        if event.keysym in self._keys_pressed:
            self._keys_pressed.remove(event.keysym)

    def _key_poll(self):
        delta = 2
        mapping = {
            'a': (0, delta), 'd': (0, -delta),
            'w': (1, delta), 's': (1, -delta),
            'Up': (2, delta), 'Down': (2, -delta),
            'i': (3, delta), 'k': (3, -delta),
            'j': (4, delta), 'l': (4, -delta),
            'q': (5, delta), 'e': (5, -delta),
            'A': (0, delta), 'D': (0, -delta),
            'W': (1, delta), 'S': (1, -delta),
            'I': (3, delta), 'K': (3, -delta),
            'J': (4, delta), 'L': (4, -delta),
            'Q': (5, delta), 'E': (5, -delta),
            
            # Bàn phím số Numpad
            'KP_4': (0, delta), 'KP_6': (0, -delta),
            'KP_Left': (0, delta), 'KP_Right': (0, -delta),
            
            'KP_8': (1, delta), 'KP_2': (1, -delta),
            'KP_Up': (1, delta), 'KP_Down': (1, -delta),
            
            'KP_7': (2, delta), 'KP_9': (2, -delta),
            'KP_Home': (2, delta), 'KP_Prior': (2, -delta),
            
            'KP_1': (3, delta), 'KP_3': (3, -delta),
            'KP_End': (3, delta), 'KP_Next': (3, -delta),
            
            'KP_Divide': (4, delta), 'KP_Multiply': (4, -delta),
            'KP_Subtract': (5, delta), 'KP_Add': (5, -delta),
            # Điều khiển Servo đang được chọn (Active)
            'Left': (-1, -delta), 'Right': (-1, delta),
        }
        deltas = {}
        for k in self._keys_pressed:
            if k in mapping:
                j_id, d = mapping[k]
                if j_id == -1: # Move active joint
                    if self._active_joint != -1:
                        deltas[self._active_joint] = deltas.get(self._active_joint, 0) + d
                else:
                    deltas[j_id] = deltas.get(j_id, 0) + d
                
        if deltas:
            self._joints.nudge_joints(deltas)
            
        self.after(40, self._key_poll)

    #  Khởi tạo giao diện người dùng (UI construction) 

    def _build_ui(self):
        #  Thanh kết nối (Connection bar - top) 
        self._conn_bar = ConnectionBar(
            self, self._comm,
            on_connect=self._on_connected,
            on_disconnect=self._on_disconnected,
        )
        self._conn_bar.pack(fill="x", side="top")

        ttk.Separator(self, orient="horizontal").pack(fill="x")

        #  Thanh điều khiển (Control bar - bottom) 
        self._ctrl_bar = ControlBar(
            self,
            send_fn=self._send,
            get_angles_fn=lambda: self._joints.get_all_angles(),
        )
        self._ctrl_bar.pack(fill="x", side="bottom")

        ttk.Separator(self, orient="horizontal").pack(fill="x", side="bottom")

        # Phần giữa: Lưới các Gauge và 3D View
        mid_pane = tk.PanedWindow(
            self, orient="horizontal",
            bg=C["bg"], sashwidth=6, sashrelief="flat",
        )
        mid_pane.pack(fill="both", expand=True, padx=10, pady=10)

        self._joints = GaugeGridPanel(mid_pane, send_fn=self._send)

        from widgets.arm_3d import RobotArm3D
        self._arm_3d = RobotArm3D(
            mid_pane, 
            get_angles_fn=lambda: self._joints.get_all_angles(),
            set_active_fn=self._set_active_joint
        )
        mid_pane.add(self._arm_3d, minsize=350, stretch="always")
        mid_pane.add(self._joints, minsize=600, stretch="always")

        # Phần dưới cùng: Pose Panel (Record/Play/Save)
        self._pose = PosePanel(
            self,
            get_angles_fn=lambda: self._joints.get_all_angles(),
            get_speeds_fn=lambda: [3]*6, # Tốc độ mặc định, Gauge chưa hỗ trợ chỉnh speed riêng
            send_fn=self._send,
        )
        self._pose.pack(fill="x", side="bottom")

    def _set_active_joint(self, joint_id):
        self._active_joint = joint_id
        self._joints.set_active(joint_id)
        if hasattr(self, '_arm_3d'):
            self._arm_3d.set_active(joint_id)

    #  Vòng lặp lấy mẫu dữ liệu Serial (Serial poll loop) 

    def _start_serial_poll(self):
        self._poll_serial()

    def _poll_serial(self):
        line = self._comm.poll()
        if line:
            self._handle_response(line)
        self.after(self.POLL_MS, self._poll_serial)

    #  Xử lý phản hồi (Response dispatcher) 

    def _handle_response(self, line: str):
        # Biến cờ ngắt kết nối đột ngột từ luồng đọc
        if line == "__DISCONNECTED__":
            # self._log.log_system("⚠  Port disconnected unexpectedly")
            self._conn_bar.force_disconnect()
            self._ctrl_bar.set_status("Disconnected", C["red"])
            return

        # self._log.log_recv(line)

        if line == "OK":
            pass   # không cần làm gì thêm

        elif line == "DONE":
            self._ctrl_bar.set_status("Idle", C["green"])

        elif line in ("ARM READY", "ARM INIT"):
            self._ctrl_bar.set_status("Ready", C["green"])
            # Đồng bộ vị trí từ firmware
            self.after(300, lambda: self._send("T"))
            self.after(400, lambda: self._send("I"))

        elif line.startswith("STA:"):
            # STA:<a0>,<a1>,...,<a5>
            try:
                angles = [int(x) for x in line[4:].split(",")]
                self._joints.set_all(angles)
            except ValueError:
                pass

        elif line.startswith("VAL:"):
            # VAL:<id>:<angle>
            try:
                _, id_s, ang_s = line.split(":")
                self._joints.set_angle(int(id_s), int(ang_s))
            except (ValueError, IndexError):
                pass

        elif line.startswith("CFG:"):
            # CFG:<id>:<min>,<max>,<home>,<spd>
            try:
                _, id_s, rest = line.split(":", 2)
                lo, hi, home, spd = (int(x) for x in rest.split(","))
                self._joints.set_joint_config(int(id_s), lo, hi, home, spd)
            except (ValueError, IndexError):
                pass

        elif line.startswith("ERR:"):
            self._ctrl_bar.set_status(f"Error: {line[4:]}", C["red"])

    #  Hàm hỗ trợ gửi lệnh (Send helper) 

    def _send(self, cmd: str):
        if not self._comm.is_connected:
            # self._log.log_system("⚠  Not connected – command ignored")
            return
        # self._log.log_send(cmd)
        self._comm.send(cmd)

        # Đánh dấu trạng thái là đang di chuyển cho các lệnh M, A, H
        if cmd.startswith(("M ", "A ", "H")):
            self._ctrl_bar.set_status("Moving…", C["orange"])

    #  Các hàm callback kết nối (Connection callbacks) 

    def _on_connected(self, port: str, baud: int):
        # self._log.log_system(f"Connected → {port}  @  {baud} baud")
        self._ctrl_bar.set_status("Connected", C["green"])
        self._comm.flush_rx()

    def _on_disconnected(self):
        # self._log.log_system("Disconnected")
        self._ctrl_bar.set_status("Disconnected", C["dim"])

    #  Tắt ứng dụng an toàn (Clean shutdown) 

    def _on_close(self):
        self._comm.disconnect()
        self.destroy()


#  Điểm bắt đầu chạy ứng dụng (Entry point) 

if __name__ == "__main__":
    app = ArmControlApp()
    app.mainloop()
