<div align="center">

# 🤖 6DOF Robot Arm Lab Manual

### ESP32 + PCA9685 + Robot Arm 6DOF Practical Guide

[![ESP32](https://img.shields.io/badge/MCU-ESP32-blue?style=for-the-badge&logo=espressif)](https://www.espressif.com/)
[![PlatformIO](https://img.shields.io/badge/IDE-PlatformIO-orange?style=for-the-badge&logo=platformio)](https://platformio.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Language](https://img.shields.io/badge/Lang-English-blue?style=for-the-badge)](./)

*A complete hands-on lab course for controlling a 6-Degree-of-Freedom Robot Arm using ESP32, PCA9685, and Arduino Framework*

[Phien Ban Tieng Viet](../github-vi/README.md)

</div>

---

## 📋 Overview

This manual provides **9 progressive lab sessions**, from basic to advanced, helping students master embedded programming, IoT, and robot control through a real hardware kit.

### 🎯 Target Audience

- Students in Electronics Engineering, Computer Science, and Automation
- Instructors organizing lab sessions for Microprocessor Engineering, Embedded Programming, and IoT courses

### 🔧 Hardware Components

| Component | Description |
|:---|:---|
| **ESP32 DevKit V1** | 32-bit microcontroller with built-in WiFi/Bluetooth |
| **PCA9685 Module** | 16-channel PWM driver, I2C interface |
| **6DOF Robot Arm** | 6 rotary joints (J0-J5), servo-driven |
| **External Power** | 5V-6V / 3A+ adapter for servos |

---

## 📂 Repository Structure

```
📦 robot-arm-lab/
├── 📖 README.md                              ← You are here
├── 📁 part-1-introduction/
│   └── README.md                             ← Kit overview & software setup
├── 📁 group-A-hardware-setup/
│   ├── lab-01-getting-started.md             ← Lab 1: Kit familiarization & setup
│   └── lab-02-hardware-connection.md         ← Lab 2: ESP32-PCA9685-Robot wiring
├── 📁 group-B-firmware-and-serial/
│   ├── lab-03-firmware-upload.md             ← Lab 3: Firmware upload & Serial Monitor
│   ├── lab-04-single-joint-control.md        ← Lab 4: Individual servo joint control
│   └── lab-05-multi-joint-control.md         ← Lab 5: Simultaneous control & speed
├── 📁 group-C-advanced-applications/
│   ├── lab-06-automated-sequences.md         ← Lab 6: Automated action sequences
│   ├── lab-07-python-gui.md                  ← Lab 7: Python & GUI control
│   ├── lab-08-webserver-esp32.md             ← Lab 8: Web Server control
│   └── lab-09-bluetooth-esp32.md             ← Lab 9: Bluetooth control
└── 📁 firmware/
    └── README.md                             ← Firmware guide
```

---

## 🗺️ Learning Roadmap

```
┌─────────────────────────────────────────────────────────────────┐
│  GROUP A: HARDWARE SETUP                                        │
│  ┌──────────┐    ┌──────────────────┐                           │
│  │  Lab 1   │───▶│     Lab 2        │                           │
│  │ Kit Intro│    │ Hardware Wiring  │                           │
│  └──────────┘    └────────┬─────────┘                           │
├───────────────────────────┼─────────────────────────────────────┤
│  GROUP B: FIRMWARE & SERIAL                                     │
│               ┌───────────▼──────────┐                          │
│               │      Lab 3           │                          │
│               │  Firmware Upload     │                          │
│               └───────────┬──────────┘                          │
│          ┌────────────────┼────────────────┐                    │
│  ┌───────▼──────┐   ┌────▼─────────┐                           │
│  │    Lab 4     │   │    Lab 5     │                            │
│  │ Single Joint │   │ Multi-Joint  │                            │
│  └───────┬──────┘   └────┬─────────┘                           │
├──────────┼───────────────┼──────────────────────────────────────┤
│  GROUP C: ADVANCED APPLICATIONS                                 │
│  ┌───────▼───────────────▼──────────┐                           │
│  │      Lab 6: Automated Sequences  │                           │
│  └───────────────┬──────────────────┘                           │
│     ┌────────────┼────────────┬─────────────┐                   │
│  ┌──▼───┐    ┌───▼──┐    ┌───▼──┐                               │
│  │Lab 7 │    │Lab 8 │    │Lab 9 │                               │
│  │Python │    │ Web  │    │  BT  │                               │
│  └──────┘    └──────┘    └──────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Robot Joint Specifications

| Joint | Name | Function | Min Angle | Max Angle | Home Angle |
|:---:|:---|:---|:---:|:---:|:---:|
| J0 | Base | Rotates entire arm | 0deg | 180deg | 90deg |
| J1 | Shoulder | Raises/lowers upper arm | 70deg | 150deg | 70deg |
| J2 | Elbow | Extends/retracts forearm | 0deg | 150deg | 90deg |
| J3 | Wrist Pitch | Tilts gripper up/down | 0deg | 180deg | 90deg |
| J4 | Wrist Roll | Rotates gripper | 0deg | 180deg | 90deg |
| J5 | Gripper | Opens/closes gripper | 60deg | 120deg | 90deg |

---

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/robot-arm-lab.git

# 2. Install VS Code + PlatformIO
# See details at: part-1-introduction/README.md

# 3. Start with Lab 1
# Open: group-A-hardware-setup/lab-01-getting-started.md
```

---

## 🤝 Contributing

All contributions are welcome! Please create an **Issue** or **Pull Request**.

## 📄 License

This project is distributed under the [MIT](LICENSE) license.

---

<div align="center">

**Developed by Hoang** | *For engineering students*

</div>
