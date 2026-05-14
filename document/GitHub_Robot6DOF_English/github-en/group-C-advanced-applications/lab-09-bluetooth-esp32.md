# Lab 9: Controlling the Robot Arm via ESP32 Bluetooth

## 🎯 Objectives

- Understand Bluetooth Classic (SPP) and Bluetooth Low Energy (BLE) principles on ESP32
- Program ESP32 to receive robot control commands via Bluetooth Serial
- Connect and control the robot from an Android phone using a Bluetooth Terminal app
- Build a Python application on PC for Bluetooth communication with the robot

## 📦 Preparation

- Robot connected and firmware working properly (Labs 1-6 completed)
- ESP32 connected to computer via USB cable
- An Android phone with Bluetooth (or a computer with Bluetooth)
- "Serial Bluetooth Terminal" app on Android (free on Google Play)

## 📋 Background Knowledge

### Bluetooth on ESP32

ESP32 supports both Bluetooth Classic and BLE. This lab uses **Bluetooth Classic SPP** (Serial Port Profile) because it is simple and widely compatible.

| Feature | Bluetooth Classic (SPP) | BLE |
|:---|:---|:---|
| Range | ~10m | ~50m |
| Speed | Faster | Power-efficient |
| Compatibility | Android, PC | Android, iOS, PC |
| Complexity | Simple (like Serial) | More complex (GATT) |

### Operation Flow

```
Phone / PC (Bluetooth Client)
    |
    v  Send text command via Bluetooth SPP
ESP32 (Bluetooth Server)
    |  Receive command -> Process same as Serial
    v
PCA9685 -> Servo -> Robot moves
    |
    ^  Send response via Bluetooth
Client receives and displays
```

## 📝 Lab Steps

### Part A: Bluetooth Firmware on ESP32

### Step 1: Create a new project

- **Name**: `RobotArm_Bluetooth`
- **Board**: ESP32 Dev Module
- **Framework**: Arduino

### Step 2: Update `platformio.ini`

```ini
[env:esp32dev]
platform       = espressif32
board          = esp32dev
framework      = arduino
monitor_speed  = 115200
upload_speed   = 921600
build_flags =
    -Os
    -DCORE_DEBUG_LEVEL=0
```

> **Note**: Bluetooth Classic is built into the ESP32 Arduino core; no additional libraries needed.

### Step 3: Create `bt_config.h`

```cpp
#ifndef BT_CONFIG_H
#define BT_CONFIG_H

// Bluetooth device name (shown when scanning from phone)
#define BT_DEVICE_NAME "RobotArm_BT"

// Allow simultaneous control via both Serial USB and Bluetooth
#define DUAL_CONTROL true

#endif
```

### Step 4: Create `main.cpp` - Main Program

```cpp
#include <Arduino.h>
#include <BluetoothSerial.h>
#include <Wire.h>
#include "config.h"
#include "bt_config.h"
#include "pca9685.h"
#include "servo_ctrl.h"
#include "cmd_parser.h"

BluetoothSerial SerialBT;
extern ServoController sc;
extern CmdParser parser;

// Bluetooth command buffer
String btBuffer = "";

void processCommand(String cmd, Stream &output) {
    cmd.trim();
    if (cmd.length() == 0) return;

    String response = parser.execute(cmd);
    output.println(response);

    // If DUAL_CONTROL, also print to Serial USB for debugging
    #if DUAL_CONTROL
    Serial.print("[BT] ");
    Serial.print(cmd);
    Serial.print(" -> ");
    Serial.println(response);
    #endif
}

void setup() {
    Serial.begin(115200);
    Serial.println("Initializing...");

    // Initialize I2C and servo
    Wire.begin(21, 22);
    sc.init();

    // Initialize Bluetooth
    if (!SerialBT.begin(BT_DEVICE_NAME)) {
        Serial.println("ERR: Bluetooth init failed!");
        return;
    }

    Serial.println("ARM READY (Bluetooth Mode)");
    Serial.print("Bluetooth name: ");
    Serial.println(BT_DEVICE_NAME);
    Serial.println("Waiting for connection...");
}

void loop() {
    // === Process Bluetooth commands ===
    while (SerialBT.available()) {
        char c = SerialBT.read();
        if (c == '\n' || c == '\r') {
            if (btBuffer.length() > 0) {
                processCommand(btBuffer, SerialBT);
                btBuffer = "";
            }
        } else {
            btBuffer += c;
        }
    }

    // === Process Serial USB commands (if DUAL_CONTROL) ===
    #if DUAL_CONTROL
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        processCommand(cmd, Serial);
    }
    #endif

    // === Update servo interpolation ===
    sc.update();
    delay(20);
}
```

### Step 5: Compile and upload firmware

```
Ctrl+Alt+B  -> Compile
Ctrl+Alt+U  -> Upload to ESP32
```

Open Serial Monitor to verify:
```
Initializing...
ARM READY (Bluetooth Mode)
Bluetooth name: RobotArm_BT
Waiting for connection...
```

### Part B: Connecting from Android Phone

### Step 6: Pair Bluetooth

1. On your Android phone, go to **Settings, Bluetooth, Enable Bluetooth**
2. Tap **Scan for devices**
3. Find and select **"RobotArm_BT"**
4. If a PIN is requested, enter `1234` or `0000`
5. After successful pairing, status shows "Paired"

### Step 7: Install Serial Bluetooth Terminal app

1. Open Google Play Store
2. Search and install: **"Serial Bluetooth Terminal"** (by Kai Morich)
3. Open the app, tap the Bluetooth icon, and select "RobotArm_BT"
4. When connected, the status bar changes to "Connected"

### Step 8: Send control commands

In the app, type and send the same commands as Serial Monitor:

```
T           -> STA:90,70,90,90,90,90
M 0 45      -> OK (base rotates to 45 degrees)
M 5 60      -> OK (open gripper)
H           -> OK (return to Home)
A 45 100 120 90 90 60  -> OK (simultaneous movement)
X           -> OK (emergency stop)
```

### Step 9: Configure quick-access macro buttons

In Serial Bluetooth Terminal, set up macro buttons:

| Button | Command | Function |
|:---|:---|:---|
| M1 | `H` | Home |
| M2 | `T` | Status |
| M3 | `X` | Emergency Stop |
| M4 | `M 5 60` | Open Gripper |
| M5 | `M 5 110` | Close Gripper |

### Part C: Controlling from Python via Bluetooth

### Step 10: Install library

```bash
pip install pyserial
```

> **Note**: On Windows, after Bluetooth pairing, the ESP32 appears as a virtual COM port (e.g.: COM5). Check in Device Manager, Ports, "Standard Serial over Bluetooth link".

### Step 11: Create `robot_bluetooth.py`

```python
import serial
import time

# === CONFIGURATION ===
# Windows: Virtual Bluetooth COM port (check Device Manager)
# Linux: /dev/rfcomm0
# macOS: /dev/tty.RobotArm_BT-SPP
BT_PORT = 'COM5'    # Replace with your actual Bluetooth COM port
BAUD = 115200

print(f'Connecting via Bluetooth {BT_PORT}...')
robot = serial.Serial(BT_PORT, BAUD, timeout=3)
time.sleep(2)
print('Connected successfully!')

def send(cmd):
    robot.write((cmd + '\n').encode())
    resp = robot.readline().decode('utf-8', errors='ignore').strip()
    print(f'  [{cmd:30s}] -> {resp}')
    return resp

def wait_done():
    resp = send('W')
    if resp != 'DONE':
        print('  (Warning: DONE not received)')

# === TEST CONNECTION ===
print('\n--- Connection test ---')
send('T')
send('I')

# === CONTROL ===
print('\n--- Control via Bluetooth ---')
send('H')
wait_done()

send('M 0 45')
wait_done()

send('M 0 135')
wait_done()

send('H')
wait_done()

print('\n=== COMPLETE ===')
robot.close()
```

### Step 12: Run the Python script

```bash
python robot_bluetooth.py
```

### Step 13: Notes and Conclusions

*(Students write their observations here)*

## :warning: Troubleshooting Common Errors

| Error | Cause | Solution |
|:---|:---|:---|
| Cannot find "RobotArm_BT" | Bluetooth not enabled or firmware error | Check Serial Monitor, reset ESP32 |
| "Connection refused" | Another connection is active | Disconnect the old connection, retry |
| Garbled characters | Baud rate mismatch | Ensure both sides use 115200 |
| Timeout (no response) | Too far away or interference | Move closer, check battery |
| COM port not visible (Windows) | Not paired or driver error | Re-pair in Bluetooth Settings |

## 🧩 Extension Exercises

1. **Combine WiFi + Bluetooth**: Modify firmware so ESP32 runs both Web Server (Lab 8) and Bluetooth, with Bluetooth commands taking priority on conflict.
2. **Bluetooth Low Energy (BLE)**: Explore the `BLEDevice.h` library and write BLE firmware for iOS control (iPhone does not support Bluetooth Classic SPP).
3. **Custom Android App**: Use MIT App Inventor or Flutter to create a robot control app with a polished graphical interface via Bluetooth.
4. **Voice Control**: Integrate phone-based voice recognition, converting spoken commands to Bluetooth commands.

---

[Lab 8: Web Server](lab-08-webserver-esp32.md) | [Home Page](../README.md)
