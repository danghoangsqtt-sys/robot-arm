import tkinter as tk
from tkinter import ttk

from config import (
    APP_TITLE, APP_VERSION, WINDOW_SIZE, WINDOW_MIN,
    C, NUM_JOINTS, FONT_BOLD, FONT_SMALL,
)
from serial_comm import SerialComm
from widgets.connection_bar import ConnectionBar
from widgets.joint_panel    import JointsPanel
from widgets.control_bar    import ControlBar
from widgets.log_panel      import LogPanel
from widgets.pose_panel     import PosePanel


#  ttk style customisation 

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


#  Application class 

class ArmControlApp(tk.Tk):

    POLL_MS = 40   # serial queue poll interval

    def __init__(self):
        super().__init__()

        self.title(f"{APP_TITLE}  v{APP_VERSION}")
        self.geometry(WINDOW_SIZE)
        self.minsize(*WINDOW_MIN)
        self.configure(bg=C["bg"])
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        _apply_theme(self)

        self._comm = SerialComm()
        self._build_ui()
        self._start_serial_poll()

    #  UI construction 

    def _build_ui(self):
        #  Connection bar (top) 
        self._conn_bar = ConnectionBar(
            self, self._comm,
            on_connect=self._on_connected,
            on_disconnect=self._on_disconnected,
        )
        self._conn_bar.pack(fill="x", side="top")

        ttk.Separator(self, orient="horizontal").pack(fill="x")

        #  Control bar (bottom) 
        self._ctrl_bar = ControlBar(
            self,
            send_fn=self._send,
            get_angles_fn=lambda: self._joints.get_all_angles(),
        )
        self._ctrl_bar.pack(fill="x", side="bottom")

        ttk.Separator(self, orient="horizontal").pack(fill="x", side="bottom")

        #  Main body 
        body = tk.PanedWindow(
            self, orient="horizontal",
            bg=C["bg"], sashwidth=6, sashrelief="flat",
            sashpad=0,
        )
        body.pack(fill="both", expand=True)

        # Left: joints panel
        self._joints = JointsPanel(body, send_fn=self._send)
        body.add(self._joints, minsize=560, stretch="always")

        # Right: log + pose stacked vertically
        right_pane = tk.PanedWindow(
            body, orient="vertical",
            bg=C["bg"], sashwidth=6, sashrelief="flat",
        )
        body.add(right_pane, minsize=300, stretch="always")

        self._log = LogPanel(right_pane, send_fn=self._send)
        right_pane.add(self._log, minsize=200, stretch="always")

        self._pose = PosePanel(
            right_pane,
            get_angles_fn=lambda: self._joints.get_all_angles(),
            get_speeds_fn=lambda: [self._joints._rows[i].get_speed()
                                   for i in range(NUM_JOINTS)],
            send_fn=self._send,
        )
        right_pane.add(self._pose, minsize=280, stretch="never")

    #  Serial poll loop 

    def _start_serial_poll(self):
        self._poll_serial()

    def _poll_serial(self):
        line = self._comm.poll()
        if line:
            self._handle_response(line)
        self.after(self.POLL_MS, self._poll_serial)

    #  Response dispatcher 

    def _handle_response(self, line: str):
        # Unexpected disconnect sentinel from reader thread
        if line == "__DISCONNECTED__":
            self._log.log_system("⚠  Port disconnected unexpectedly")
            self._conn_bar.force_disconnect()
            self._ctrl_bar.set_status("Disconnected", C["red"])
            return

        self._log.log_recv(line)

        if line == "OK":
            pass   # nothing extra needed

        elif line == "DONE":
            self._ctrl_bar.set_status("Idle", C["green"])

        elif line in ("ARM READY", "ARM INIT"):
            self._ctrl_bar.set_status("Ready", C["green"])
            # Sync positions from firmware
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

    #  Send helper 

    def _send(self, cmd: str):
        if not self._comm.is_connected:
            self._log.log_system("⚠  Not connected – command ignored")
            return
        self._log.log_send(cmd)
        self._comm.send(cmd)

        # Optimistically mark as moving for M and A commands
        if cmd.startswith(("M ", "A ", "H")):
            self._ctrl_bar.set_status("Moving…", C["orange"])

    #  Connection callbacks 

    def _on_connected(self, port: str, baud: int):
        self._log.log_system(f"Connected → {port}  @  {baud} baud")
        self._ctrl_bar.set_status("Connected", C["green"])
        self._comm.flush_rx()

    def _on_disconnected(self):
        self._log.log_system("Disconnected")
        self._ctrl_bar.set_status("Disconnected", C["dim"])

    #  Clean shutdown 

    def _on_close(self):
        self._comm.disconnect()
        self.destroy()


#  Entry point 

if __name__ == "__main__":
    app = ArmControlApp()
    app.mainloop()
