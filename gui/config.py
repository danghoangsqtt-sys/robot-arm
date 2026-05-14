"""
config.py – Cấu hình trung tâm cho Giao diện điều khiển Cánh tay Robot (GUI).

Giữ JOINTS đồng bộ với cấu hình SERVO_TABLE bên phía firmware (config.h).
"""

APP_TITLE   = "Robotic Arm Controller"
APP_VERSION = "1.0.0"
WINDOW_SIZE = "1180x740"
WINDOW_MIN  = (900, 600)

POSES_FILE  = "poses.json"

#  Định nghĩa các khớp (Joints) 
# (tên_khớp, góc_min, góc_max, góc_mặc_định, tốc_độ_mặc_định)
JOINTS = [
    ("1 - Đế (Base)",        0,   180,  90,  3),
    ("2 - Vai (Shoulder)",   15,   165,  90,  3),
    ("3 - Khuỷu (Elbow)",    0,   150,  90,  3),
    ("4 - Gập (Pitch)",      0,   180,  90,  3),
    ("5 - Xoay (Roll)",      0,   180,  90,  3),
    ("6 - Kẹp (Gripper)",    0,    90,  45,  2),
]

NUM_JOINTS   = len(JOINTS)
BAUD_RATES   = [9600, 57600, 115200, 230400, 250000]
DEFAULT_BAUD = 115200

#  Bảng màu tối lấy cảm hứng từ Dracula 
C = {
    "bg":        "#1e1e2e",   # màu nền cửa sổ
    "surface":   "#2a2a3d",   # màu nền thẻ / bảng
    "surface2":  "#313145",   # màu nền nổi
    "border":    "#44475a",   # viền các thành phần
    "accent":    "#bd93f9",   # màu tím – màu nhấn chính
    "accent_dk": "#9a6fd8",   # màu nhấn đậm hơn (khi được nhấn)
    "green":     "#50fa7b",   # kết nối thành công / ok
    "orange":    "#ffb86c",   # cảnh báo / đang di chuyển
    "red":       "#ff5555",   # lỗi / dừng
    "text":      "#f8f8f2",   # màu chữ chính
    "dim":       "#6272a4",   # màu chữ phụ / chữ mờ
    "slider_tr": "#bd93f9",   # rãnh thanh trượt
    "entry_bg":  "#141421",   # màu nền ô nhập liệu
    "log_bg":    "#141421",   # màu nền terminal log
    "log_tx":    "#f8f8f2",
    "log_send":  "#8be9fd",   # màu chữ lệnh gửi đi
    "log_recv":  "#50fa7b",   # màu chữ phản hồi nhận được
    "log_warn":  "#ffb86c",   # màu chữ cảnh báo
    "log_err":   "#ff5555",   # màu chữ lỗi
}

#  Cấu hình Font chữ 
FONT_MONO  = ("Consolas", 10)
FONT_LABEL = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 11, "bold")
FONT_SMALL = ("Segoe UI", 9)
FONT_LOG   = ("Consolas", 9)
