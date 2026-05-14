# Lab 1: Getting Started with the Kit and Environment Setup

## 🎯 Objectives

- Identify and name the 3 main components of the IoT Robot Kit
- Successfully install VS Code and PlatformIO
- Successfully install the CP2102/CH340 driver for ESP32
- Confirm ESP32 is recognized on the computer (COM port)

## 📦 Preparation

- A computer with Internet connection
- Micro-USB cable (included in the Kit)
- 6DOF Robot Kit (no assembly needed yet)

## 📝 Lab Steps

### Step 1: Unbox and inspect the Kit

Take all components out of the box. Place them on a clean, dry surface. Check for all 3 main components:

- **ESP32 DevKit V1 Board**: A black board with a square metal chip in the center (WiFi/BT module), a Micro-USB port on the side, and 2 rows of pins on each side.
- **PCA9685 Module**: A blue board with a row of servo connectors (3-pin: brown-red-yellow) along the long edge, I2C input (4-pin) on the short edge, and a separate servo power terminal.
- **6DOF Robot Arm**: An aluminum/black plastic frame with 6 servo motors at each joint, each with a 3-wire connector (brown-red-orange).

### Step 2: Download and install Visual Studio Code

1. Open a web browser and go to: https://code.visualstudio.com
2. Click the "Download" button matching your operating system (Windows/macOS/Linux)
3. Run the installer, click "Next" until complete. Check "Add to PATH" if available.

### Step 3: Install PlatformIO Extension

1. Open the installed VS Code
2. Press `Ctrl+Shift+X` to open Extensions
3. In the search box, type: `PlatformIO IDE`
4. Click "Install" next to the "PlatformIO IDE" result
5. Wait for installation to complete (2-5 minutes). VS Code will prompt "Reload"

> **Note**: After reload, the PlatformIO icon (ant logo) will appear in the left sidebar. If you see this icon, installation was successful.

### Step 4: Install USB Driver for ESP32

The ESP32 DevKit V1 board uses a USB-to-UART converter chip (typically CP2102 or CH340):

- **For CP2102 chip**: Download driver at https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
- **For CH340 chip**: Download driver at https://sparks.gogo.co.nz/ch340.html

> **Note**: If you don't know which chip your board uses, install both drivers. They don't conflict.

### Step 5: Connect ESP32 to the computer

1. Plug the Micro-USB cable into the USB port on the ESP32 board
2. Plug the other end into the computer's USB port
3. The red LED on the ESP32 board should light up (indicating power)

### Step 6: Verify COM port

| Operating System | How to Check |
|:---|:---|
| **Windows** | Right-click Start, Device Manager, Ports (COM & LPT), look for "Silicon Labs CP210x" or "CH340" |
| **macOS** | Terminal: `ls /dev/cu.*`, look for a line containing "usbserial" |
| **Linux** | Terminal: `ls /dev/ttyUSB*`, should see `/dev/ttyUSB0` or similar |

> **Note**: If no COM port appears, try a different USB cable (some cables are charge-only and don't transfer data) or reinstall the driver.

📝 **Record your COM port**: ____________

### Step 7: Notes and Conclusions

*(Students write their observations here)*

## 🧩 Extension Exercises

1. How many GPIO pins does the ESP32 board have? What communication protocol do GPIO 21 and GPIO 22 serve?
2. Observe the PCA9685 module and count how many servo ports (3-pin) it has. Why is this module needed instead of connecting servos directly to the ESP32?

---

[Part 1: Introduction](../part-1-introduction/README.md) | [Lab 2: Hardware Connection](lab-02-hardware-connection.md)
