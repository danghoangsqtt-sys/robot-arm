# Bài 7: Xây Dựng Ứng Dụng Điều Khiển Robot qua Python và GUI

## 🎯 Mục tiêu

- Hiểu nguyên lý giao tiếp Serial giữa Python và firmware ESP32
- Cài đặt Python 3.x và thư viện pyserial
- Viết script Python kết nối Serial, gửi lệnh và nhận phản hồi
- Viết script tự động gửi chuỗi lệnh gắp–di chuyển–thả
- Xây dựng giao diện GUI bằng tkinter với thanh trượt, nút Home, nút Dừng khẩn cấp

## 📦 Chuẩn bị

- Robot hoạt động bình thường, đã hoàn thành Bài 1–6
- ESP32 kết nối máy tính qua cáp USB
- Ghi nhớ COM port (ví dụ: `COM3`, `/dev/ttyUSB0`)

> ⚠️ **Quan trọng**: Đóng Serial Monitor trong VS Code trước khi chạy script Python. Hai chương trình không thể dùng chung 1 COM port cùng lúc.

## 📝 Các Bước Thực Hành

### Phần A: Cài đặt môi trường Python

**Bước 1**: Kiểm tra Python
```bash
python --version
# Nếu hiện: Python 3.10.12 → Chuyển sang Bước 3
```

**Bước 2**: Cài đặt Python 3.x (nếu chưa có)
- Truy cập: https://www.python.org/downloads/
- **Trên Windows**: Tích chọn "Add Python to PATH" trước khi nhấn Install

**Bước 3**: Cài đặt thư viện pyserial
```bash
pip install pyserial
# Nếu lỗi "pip not recognized":
python -m pip install pyserial
```

**Bước 4**: Kiểm tra pyserial
```bash
python -c "import serial.tools.list_ports; [print(p.device, '-', p.description) for p in serial.tools.list_ports.comports()]"
```

**Bước 5**: Tạo thư mục làm việc
```bash
mkdir robot_python
cd robot_python
```

### Phần B: Script kết nối cơ bản

**Bước 6**: Tạo file `robot_basic.py`

```python
import serial
import time

# === KẾT NỐI SERIAL ===
PORT = 'COM3'       # Thay COM port thực tế
BAUD = 115200

print(f'Dang ket noi voi {PORT}...')
robot = serial.Serial(PORT, BAUD, timeout=2)
time.sleep(2)       # Đợi ESP32 khởi động
print('Ket noi thanh cong!')

# Đọc thông báo khởi động
while robot.in_waiting:
    line = robot.readline().decode('utf-8', errors='ignore').strip()
    print(f'  ESP32: {line}')

# === HÀM GỬI LỆNH ===
def send(cmd):
    robot.write((cmd + '\n').encode())
    response = robot.readline().decode('utf-8', errors='ignore').strip()
    print(f'  Gui: {cmd:30s} -> Nhan: {response}')
    return response

# === KIỂM TRA ===
print('\n--- Kiem tra ket noi ---')
send('I')
send('T')

print('\n--- Dieu khien robot ---')
send('H')
send('W')
send('M 0 45')
send('W')
send('M 0 135')
send('W')
send('G 0')
send('H')
send('W')

robot.close()
print('\nDong ket noi. Xong!')
```

**Bước 7**: Giải thích code

| Dòng code | Giải thích |
|:---|:---|
| `serial.Serial('COM3', 115200, timeout=2)` | Mở kết nối Serial, baud rate khớp firmware |
| `time.sleep(2)` | Đợi ESP32 reset và khởi động |
| `robot.write((cmd + '\n').encode())` | Gửi lệnh dạng text + ký tự xuống dòng |
| `robot.readline().decode()` | Đọc 1 dòng phản hồi |
| `robot.in_waiting` | Số bytes đang chờ trong buffer |
| `robot.close()` | Đóng kết nối, giải phóng COM port |

**Bước 8**: Chạy script
```bash
python robot_basic.py
```

### Phần C: Script chuỗi hành động tự động

**Bước 9–10**: Tạo file `robot_sequence.py`

```python
import serial
import time

PORT = 'COM3'
BAUD = 115200

print(f'Ket noi {PORT}...')
robot = serial.Serial(PORT, BAUD, timeout=5)
time.sleep(2)
print('OK!')

def send(cmd):
    robot.write((cmd + '\n').encode())
    resp = robot.readline().decode('utf-8', errors='ignore').strip()
    print(f'  [{cmd:30s}] -> {resp}')
    return resp

def wait_done():
    resp = send('W')
    if resp != 'DONE':
        print('  (Canh bao: chua nhan DONE)')

# === CHUỖI HÀNH ĐỘNG ===
sequence = [
    ('H',                         'Ve vi tri Home'),
    ('S 0 3',                     'Toc do J0 = 3'),
    ('S 1 2',                     'Toc do J1 = 2'),
    ('S 2 2',                     'Toc do J2 = 2'),
    ('S 5 5',                     'Toc do J5 = 5'),
    ('M 5 60',                    'Mo kep rong'),
    ('A 90 120 130 90 90 60',     'Tiep can vat the'),
    ('A 90 140 140 90 90 60',     'Ha xuong sat vat the'),
    ('M 5 110',                   'Gap vat the'),
    ('A 90 100 90 90 90 110',     'Nang len'),
    ('M 0 45',                    'Xoay de sang trai'),
    ('A 45 130 130 90 90 110',    'Ha xuong vi tri tha'),
    ('M 5 60',                    'Tha vat the'),
    ('A 45 100 90 90 90 60',      'Nang tay len'),
    ('H',                         'Ve Home'),
]

print('\n=== BAT DAU ===\n')
for i, (cmd, desc) in enumerate(sequence):
    print(f'Buoc {i+1}/{len(sequence)}: {desc}')
    send(cmd)
    wait_done()
    print()

print('=== HOAN THANH! ===')
robot.close()
```

### Phần D: Giao diện GUI

**Bước 13–19**: Tạo file `robot_gui.py`

Giao diện bao gồm: 6 thanh trượt cho 6 khớp, nút HOME, nút TRẠNG THÁI, nút DỪNG KHẨN CẤP, vùng Log.

```python
import tkinter as tk
from tkinter import scrolledtext
import serial
import time

# === KẾT NỐI ===
PORT = 'COM3'
BAUD = 115200
connected = False
try:
    robot = serial.Serial(PORT, BAUD, timeout=2)
    time.sleep(2)
    connected = True
except Exception as e:
    print(f'Loi ket noi: {e}')

# === CẤU HÌNH 6 KHỚP ===
joints = [
    {'name': 'J0 - De (Base)',       'channel': 0, 'min': 0,   'max': 180, 'home': 90},
    {'name': 'J1 - Vai (Shoulder)',   'channel': 1, 'min': 70,  'max': 150, 'home': 70},
    {'name': 'J2 - Khuyu (Elbow)',    'channel': 2, 'min': 0,   'max': 150, 'home': 90},
    {'name': 'J3 - Co tay (Wrist P)', 'channel': 3, 'min': 0,   'max': 180, 'home': 90},
    {'name': 'J4 - Xoay (Wrist R)',   'channel': 4, 'min': 0,   'max': 180, 'home': 90},
    {'name': 'J5 - Kep (Gripper)',    'channel': 5, 'min': 60,  'max': 120, 'home': 90},
]

# === HÀM GỬI LỆNH ===
def send_command(cmd):
    if not connected:
        log_message('LOI: Chua ket noi Serial!')
        return
    try:
        robot.write((cmd + '\n').encode())
        response = robot.readline().decode('utf-8', errors='ignore').strip()
        log_message(f'>> {cmd}  |  << {response}')
    except Exception as e:
        log_message(f'LOI gui lenh: {e}')

def log_message(msg):
    log_text.insert(tk.END, msg + '\n')
    log_text.see(tk.END)

# === XỬ LÝ SỰ KIỆN ===
def on_slider_change(channel, value):
    angle = int(float(value))
    send_command(f'M {channel} {angle}')

def on_home():
    send_command('H')
    for i, j in enumerate(joints):
        sliders[i].set(j['home'])
    log_message('--- Da ve HOME ---')

def on_stop():
    send_command('X')
    log_message('!!! DUNG KHAN CAP !!!')

def on_get_status():
    send_command('T')

# === GIAO DIỆN ===
root = tk.Tk()
root.title('Dieu Khien Robot 6DOF - Bai Thuc Hanh 7')
root.geometry('650x550')
root.resizable(False, False)

tk.Label(root, text='DIEU KHIEN CANH TAY ROBOT 6DOF',
         font=('Arial', 14, 'bold'), fg='#1F4E79').pack(pady=5)

frame_sliders = tk.LabelFrame(root, text='Dieu khien tung khop',
                               font=('Arial', 10, 'bold'), padx=10, pady=5)
frame_sliders.pack(fill='x', padx=10, pady=5)

sliders = []
for i, j in enumerate(joints):
    row = tk.Frame(frame_sliders)
    row.pack(fill='x', pady=2)
    tk.Label(row, text=j['name'], width=22, anchor='w', font=('Arial', 9)).pack(side='left')
    slider = tk.Scale(row, from_=j['min'], to=j['max'], orient='horizontal',
                      length=350, command=lambda v, ch=j['channel']: on_slider_change(ch, v))
    slider.set(j['home'])
    slider.pack(side='left', padx=5)
    sliders.append(slider)
    tk.Label(row, text=f'{j["min"]}°-{j["max"]}°', font=('Arial', 8), fg='gray').pack(side='left')

frame_buttons = tk.Frame(root)
frame_buttons.pack(fill='x', padx=10, pady=5)
tk.Button(frame_buttons, text='HOME', command=on_home,
          bg='#2E75B6', fg='white', font=('Arial', 10, 'bold'), width=12).pack(side='left', padx=5)
tk.Button(frame_buttons, text='TRANG THAI', command=on_get_status,
          bg='#404040', fg='white', font=('Arial', 10), width=12).pack(side='left', padx=5)
tk.Button(frame_buttons, text='DUNG KHAN CAP', command=on_stop,
          bg='#C00000', fg='white', font=('Arial', 10, 'bold'), width=15).pack(side='right', padx=5)

tk.Label(root, text='Nhat ky lenh (Log):', anchor='w',
         font=('Arial', 9, 'bold')).pack(fill='x', padx=10)
log_text = scrolledtext.ScrolledText(root, height=8, font=('Consolas', 9), state='normal')
log_text.pack(fill='both', padx=10, pady=5, expand=True)

if connected:
    log_message(f'Ket noi thanh cong: {PORT} @ {BAUD}')
else:
    log_message('CHUA KET NOI! Kiem tra COM port.')

def on_closing():
    if connected:
        robot.close()
    root.destroy()

root.protocol('WM_DELETE_WINDOW', on_closing)
root.mainloop()
```

**Bước 20**: Chạy GUI
```bash
python robot_gui.py
```

**Bước 21**: Thao tác kiểm tra
- Kéo thanh trượt → robot xoay, Log hiển thị lệnh + phản hồi
- Nhấn HOME → tất cả thanh trượt về Home
- Nhấn TRẠNG THÁI → hiển thị STA
- Nhấn DỪNG KHẨN CẤP → robot dừng ngay

### Bước 22: Nhận xét và kết luận

## 🧩 Bài Tập Mở Rộng

1. Thêm nút Record/Play: ghi lại vị trí 6 thanh trượt, phát lại để robot lặp chuỗi động tác.
2. Lưu/Tải chuỗi hành động vào file `.txt`.
3. Tìm hiểu Flask để tạo trang web điều khiển robot.

---

[⬅️ Bài 6: Chuỗi tự động](bai-06-chuoi-tu-dong.md) | [➡️ Bài 8: Web Server](bai-08-webserver-esp32.md)
