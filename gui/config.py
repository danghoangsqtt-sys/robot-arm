"""
config.py – Central configuration for the Robotic Arm GUI.

Keep JOINTS in sync with config.h  SERVO_TABLE on the firmware side.
"""

APP_TITLE   = "Robotic Arm Controller"
APP_VERSION = "1.0.0"
WINDOW_SIZE = "1180x740"
WINDOW_MIN  = (900, 600)

POSES_FILE  = "poses.json"

#  Joint definitions 
# (label,       min_ang, max_ang, home_ang, default_speed)
JOINTS = [
    ("Base",        0,   180,  90,  3),
    ("Shoulder",   15,   165,  90,  3),
    ("Elbow",       0,   150,  90,  3),
    ("Wrist Pitch", 0,   180,  90,  3),
    ("Wrist Roll",  0,   180,  90,  3),
    ("Gripper",     0,    90,  45,  2),
]

NUM_JOINTS   = len(JOINTS)
BAUD_RATES   = [9600, 57600, 115200, 230400, 250000]
DEFAULT_BAUD = 115200

#  Dracula-inspired dark palette 
C = {
    "bg":        "#1e1e2e",   # window background
    "surface":   "#2a2a3d",   # card / panel background
    "surface2":  "#313145",   # elevated surface
    "border":    "#44475a",   # widget borders
    "accent":    "#bd93f9",   # purple – primary accent
    "accent_dk": "#9a6fd8",   # darker accent (pressed)
    "green":     "#50fa7b",   # connected / ok
    "orange":    "#ffb86c",   # warning / moving
    "red":       "#ff5555",   # error / stop
    "text":      "#f8f8f2",   # primary text
    "dim":       "#6272a4",   # secondary / placeholder text
    "slider_tr": "#bd93f9",   # slider trough
    "entry_bg":  "#141421",   # text entry background
    "log_bg":    "#141421",   # log terminal background
    "log_tx":    "#f8f8f2",
    "log_send":  "#8be9fd",   # outgoing command colour
    "log_recv":  "#50fa7b",   # incoming response colour
    "log_warn":  "#ffb86c",   # warning colour
    "log_err":   "#ff5555",   # error colour
}

#  Font stack 
FONT_MONO  = ("Consolas", 10)
FONT_LABEL = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 11, "bold")
FONT_SMALL = ("Segoe UI", 9)
FONT_LOG   = ("Consolas", 9)
