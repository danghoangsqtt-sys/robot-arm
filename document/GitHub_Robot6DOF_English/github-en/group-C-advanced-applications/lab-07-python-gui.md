# Lab 7: Building a Python and GUI Robot Control Application

## 🎯 Objectives

- Understand the principles of Serial communication between Python and ESP32 firmware
- Install Python 3.x and the pyserial library
- Write a Python script to connect via Serial, send commands, and receive responses
- Write an automation script for pick-move-place sequences
- Build a GUI interface using tkinter with sliders, Home button, and Emergency Stop button

## 📦 Preparation

- Robot working normally, Labs 1-6 completed
- ESP32 connected to computer via USB cable
- Note your COM port (e.g.: `COM3`, `/dev/ttyUSB0`)

> :warning: **Important**: Close Serial Monitor in VS Code before running Python scripts. Two programs cannot share the same COM port simultaneously.

## 📝 Lab Steps

### Part A: Python Environment Setup

**Step 1**: Check Python
```bash
python --version
# If it shows: Python 3.10.12 -> Skip to Step 3
```

**Step 2**: Install Python 3.x (if not installed)
- Visit: https://www.python.org/downloads/
- **On Windows**: Check "Add Python to PATH" before clicking Install

**Step 3**: Install the pyserial library
```bash
pip install pyserial
# If "pip not recognized" error:
python -m pip install pyserial
```

**Step 4**: Verify pyserial
```bash
python -c "import serial.tools.list_ports; [print(p.device, '-', p.description) for p in serial.tools.list_ports.comports()]"
```

**Step 5**: Create working directory
```bash
mkdir robot_python
cd robot_python
```

### Part B: Basic Connection Script

**Step 6**: Create file `robot_basic.py`

```python
import serial
import time

# === SERIAL CONNECTION ===
PORT = 'COM3'       # Replace with your actual COM port
BAUD = 115200

print(f'Connecting to {PORT}...')
robot = serial.Serial(PORT, BAUD, timeout=2)
time.sleep(2)       # Wait for ESP32 to boot
print('Connected successfully!')

# Read startup messages
while robot.in_waiting:
    line = robot.readline().decode('utf-8', errors='ignore').strip()
    print(f'  ESP32: {line}')

# === SEND COMMAND FUNCTION ===
def send(cmd):
    robot.write((cmd + '\n').encode())
    response = robot.readline().decode('utf-8', errors='ignore').strip()
    print(f'  Sent: {cmd:30s} -> Received: {response}')
    return response

# === TEST ===
print('\n--- Connection test ---')
send('I')
send('T')

print('\n--- Robot control ---')
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
print('\nConnection closed. Done!')
```

**Step 7**: Code explanation

| Code Line | Explanation |
|:---|:---|
| `serial.Serial('COM3', 115200, timeout=2)` | Open Serial connection, baud rate matches firmware |
| `time.sleep(2)` | Wait for ESP32 reset and boot |
| `robot.write((cmd + '\n').encode())` | Send command as text + newline character |
| `robot.readline().decode()` | Read one response line |
| `robot.in_waiting` | Number of bytes waiting in buffer |
| `robot.close()` | Close connection, release COM port |

**Step 8**: Run the script
```bash
python robot_basic.py
```

### Part C: Automated Action Sequence Script

**Steps 9-10**: Create file `robot_sequence.py`

```python
import serial
import time

PORT = 'COM3'
BAUD = 115200

print(f'Connecting to {PORT}...')
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
        print('  (Warning: DONE not received)')

# === ACTION SEQUENCE ===
sequence = [
    ('H',                         'Return to Home'),
    ('S 0 3',                     'Speed J0 = 3'),
    ('S 1 2',                     'Speed J1 = 2'),
    ('S 2 2',                     'Speed J2 = 2'),
    ('S 5 5',                     'Speed J5 = 5'),
    ('M 5 60',                    'Open gripper wide'),
    ('A 90 120 130 90 90 60',     'Approach object'),
    ('A 90 140 140 90 90 60',     'Lower to object level'),
    ('M 5 110',                   'Grip object'),
    ('A 90 100 90 90 90 110',     'Lift up'),
    ('M 0 45',                    'Rotate base to left'),
    ('A 45 130 130 90 90 110',    'Lower to release position'),
    ('M 5 60',                    'Release object'),
    ('A 45 100 90 90 90 60',      'Raise arm'),
    ('H',                         'Return to Home'),
]

print('\n=== START ===\n')
for i, (cmd, desc) in enumerate(sequence):
    print(f'Step {i+1}/{len(sequence)}: {desc}')
    send(cmd)
    wait_done()
    print()

print('=== COMPLETE! ===')
robot.close()
```

### Part D: GUI Interface

**Steps 13-19**: Create file `robot_gui.py`

The interface includes: 6 sliders for 6 joints, HOME button, STATUS button, EMERGENCY STOP button, and a Log area.

```python
import tkinter as tk
from tkinter import scrolledtext
import serial
import time

# === CONNECTION ===
PORT = 'COM3'
BAUD = 115200
connected = False
try:
    robot = serial.Serial(PORT, BAUD, timeout=2)
    time.sleep(2)
    connected = True
except Exception as e:
    print(f'Connection error: {e}')

# === 6 JOINT CONFIGURATION ===
joints = [
    {'name': 'J0 - Base',         'channel': 0, 'min': 0,   'max': 180, 'home': 90},
    {'name': 'J1 - Shoulder',     'channel': 1, 'min': 70,  'max': 150, 'home': 70},
    {'name': 'J2 - Elbow',        'channel': 2, 'min': 0,   'max': 150, 'home': 90},
    {'name': 'J3 - Wrist Pitch',  'channel': 3, 'min': 0,   'max': 180, 'home': 90},
    {'name': 'J4 - Wrist Roll',   'channel': 4, 'min': 0,   'max': 180, 'home': 90},
    {'name': 'J5 - Gripper',      'channel': 5, 'min': 60,  'max': 120, 'home': 90},
]

# === SEND COMMAND FUNCTION ===
def send_command(cmd):
    if not connected:
        log_message('ERROR: Serial not connected!')
        return
    try:
        robot.write((cmd + '\n').encode())
        response = robot.readline().decode('utf-8', errors='ignore').strip()
        log_message(f'>> {cmd}  |  << {response}')
    except Exception as e:
        log_message(f'ERROR sending command: {e}')

def log_message(msg):
    log_text.insert(tk.END, msg + '\n')
    log_text.see(tk.END)

# === EVENT HANDLERS ===
def on_slider_change(channel, value):
    angle = int(float(value))
    send_command(f'M {channel} {angle}')

def on_home():
    send_command('H')
    for i, j in enumerate(joints):
        sliders[i].set(j['home'])
    log_message('--- Returned to HOME ---')

def on_stop():
    send_command('X')
    log_message('!!! EMERGENCY STOP !!!')

def on_get_status():
    send_command('T')

# === GUI INTERFACE ===
root = tk.Tk()
root.title('6DOF Robot Arm Control - Lab 7')
root.geometry('650x550')
root.resizable(False, False)

tk.Label(root, text='6DOF ROBOT ARM CONTROL',
         font=('Arial', 14, 'bold'), fg='#1F4E79').pack(pady=5)

frame_sliders = tk.LabelFrame(root, text='Individual Joint Control',
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
    tk.Label(row, text=f'{j["min"]}deg-{j["max"]}deg', font=('Arial', 8), fg='gray').pack(side='left')

frame_buttons = tk.Frame(root)
frame_buttons.pack(fill='x', padx=10, pady=5)
tk.Button(frame_buttons, text='HOME', command=on_home,
          bg='#2E75B6', fg='white', font=('Arial', 10, 'bold'), width=12).pack(side='left', padx=5)
tk.Button(frame_buttons, text='STATUS', command=on_get_status,
          bg='#404040', fg='white', font=('Arial', 10), width=12).pack(side='left', padx=5)
tk.Button(frame_buttons, text='EMERGENCY STOP', command=on_stop,
          bg='#C00000', fg='white', font=('Arial', 10, 'bold'), width=15).pack(side='right', padx=5)

tk.Label(root, text='Command Log:', anchor='w',
         font=('Arial', 9, 'bold')).pack(fill='x', padx=10)
log_text = scrolledtext.ScrolledText(root, height=8, font=('Consolas', 9), state='normal')
log_text.pack(fill='both', padx=10, pady=5, expand=True)

if connected:
    log_message(f'Connected successfully: {PORT} @ {BAUD}')
else:
    log_message('NOT CONNECTED! Check COM port.')

def on_closing():
    if connected:
        robot.close()
    root.destroy()

root.protocol('WM_DELETE_WINDOW', on_closing)
root.mainloop()
```

**Step 20**: Run the GUI
```bash
python robot_gui.py
```

**Step 21**: Test operations
- Drag sliders to move joints; the Log shows commands and responses
- Click HOME to return all sliders to Home position
- Click STATUS to display current state (STA)
- Click EMERGENCY STOP to halt the robot immediately

### Step 22: Notes and Conclusions

## 🧩 Extension Exercises

1. Add Record/Play buttons: record 6 slider positions, play back to repeat action sequences.
2. Save/Load action sequences to/from a `.txt` file.
3. Explore Flask to create a web-based robot control page.

---

[Lab 6: Automated Sequences](lab-06-automated-sequences.md) | [Lab 8: Web Server](lab-08-webserver-esp32.md)
