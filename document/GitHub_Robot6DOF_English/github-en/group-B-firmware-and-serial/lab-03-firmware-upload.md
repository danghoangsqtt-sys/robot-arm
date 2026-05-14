# Lab 3: Firmware Upload and Basic Serial Communication

## 🎯 Objectives

- Create a PlatformIO project with the correct firmware directory structure
- Successfully compile (build) the firmware without errors
- Successfully upload firmware to the ESP32
- Verify hardware operation through Serial Monitor

## 📦 Preparation

- Hardware system correctly connected as per Lab 2
- ESP32 plugged into the computer via USB, COM port confirmed
- Firmware source code (provided)

## 📝 Lab Steps

### Step 1: Create a new project

1. Open VS Code, click the PlatformIO icon (ant logo) in the left sidebar
2. Select "New Project" (or Home, New Project)
3. Fill in the details:
   - **Name**: `RobotArm`
   - **Board**: type "ESP32 Dev Module" and select the result
   - **Framework**: Arduino
4. Click "Finish". Wait for PlatformIO to download required packages (first time may take 5-10 minutes)

### Step 2: Organize directory structure

```
RobotArm/
├── src/               ← source code directory
│   └── main.cpp
├── include/           ← header files directory
└── platformio.ini     ← project configuration file
```

### Step 3: Update `platformio.ini`

Open `platformio.ini`, delete all existing content, replace with:

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

### Step 4: Create source files

In the `src/` directory, create the following files:

| File | Function |
|:---|:---|
| `config.h` | General configuration (I2C pins, servo table) |
| `pca9685.h` + `pca9685.cpp` | PCA9685 driver |
| `servo_ctrl.h` + `servo_ctrl.cpp` | Servo motion controller |
| `cmd_parser.h` + `cmd_parser.cpp` | Serial command parser |
| `main.cpp` | Main program |

> **Note**: All `.h` and `.cpp` files must be in the same `src/` directory. If placed in the wrong directory, the compiler will report "file not found" errors.

### Step 5: Compile (Build)

1. On the status bar at the bottom of VS Code, click the checkmark button (Build) or press `Ctrl+Alt+B`
2. If successful, you'll see: **SUCCESS**

**Common errors:**
- `fatal error: config.h: No such file` - File not created or in wrong directory
- `undefined reference` - Missing the corresponding `.cpp` file

### Step 6: Upload firmware

1. Click the right arrow button on the status bar or press `Ctrl+Alt+U`
2. If successful, you'll see:
   ```
   Writing at 0x00010000... (100%)
   Hard resetting via RTS pin...
   ```

> **Note**: If you get "Failed to connect" error: hold the **BOOT** button on the ESP32, click Upload, then release BOOT when you see "Connecting..."

### Step 7: Open Serial Monitor

Click the plug icon on the status bar or press `Ctrl+Alt+M`. Ensure baud rate = **115200**.

### Step 8: Verify firmware operation

Press the **RST** (Reset) button on the ESP32 board. You should see:

```
ARM INIT
ARM READY
```

- If you see `ARM READY`, the firmware was uploaded and is running successfully!
- If you see `ERR:PCA9685`, re-check your I2C wiring (Lab 2)

### Step 9: Notes and Conclusions

*(Students write their observations here)*

## 🧩 Extension Exercises

1. Disconnect one SDA wire and press Reset. What error does Serial Monitor show? Reconnect and Reset to recover.
2. Open `config.h` and find `#define CFG_BAUD 115200`. If you change it to `9600`, what setting must you change in Serial Monitor?

---

[Lab 2: Hardware Connection](../group-A-hardware-setup/lab-02-hardware-connection.md) | [Lab 4: Single Joint Control](lab-04-single-joint-control.md)
