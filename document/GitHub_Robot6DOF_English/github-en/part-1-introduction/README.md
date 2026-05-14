# Part 1: Introduction to the Lab Kit and Programming Environment

## 1.1. Introduction

This manual provides hands-on lab sessions using an IoT Kit for controlling a 6-Degree-of-Freedom (6DOF) Robot Arm. The labs are designed for students to apply theoretical knowledge to real-world servo motor programming and control.

### The Kit consists of 3 main components

- **ESP32 DevKit V1 Board**: A 32-bit microcontroller with built-in WiFi/Bluetooth, serving as the central processing brain. Students apply Microprocessor Engineering concepts (MCU architecture, GPIO, I2C, UART) to program the robot.
- **PCA9685 Module**: A 16-channel PWM driver IC using I2C communication, enabling precise simultaneous control of multiple servos.
- **6DOF Robot Arm**: A mechanical structure with 6 rotary joints (J0-J5) driven by 6 servos, allowing flexible movement in 3D space.

## 1.2. General Objectives

### Knowledge
- Directly verify Digital Electronics concepts: observe PWM signals controlling servos, I2C communication between MCU and peripheral ICs.
- Reinforce Microprocessor Engineering knowledge: ESP32 architecture, GPIO configuration, UART/I2C communication, firmware upload process.
- Understand Embedded IoT Programming models: data flow from user command to microcontroller to I2C bus to PWM to mechanical robot structure.

### Skills
- Correctly connect hardware: I2C bus, servo power supply, PWM channel mapping for each robot joint.
- Compile, upload embedded firmware and communicate via Serial UART with the microcontroller.
- Program individual joint control, simultaneous multi-joint control, and automated action sequences for the robot.
- Build robot control applications using Python (automation scripts + GUI interface).

### Practical Applications
- Program and control the robot arm to perform tasks: pick up, move, and place objects as required.
- Apply embedded development workflow (write code, compile, upload, debug) to other microcontroller projects.
- Design basic IoT systems: device control via Serial, expandable to WiFi/Bluetooth.

## 1.3. Prerequisites

- **Knowledge**: Students should have studied Digital Electronics (digital signals, PWM, I2C protocol), Microprocessor Engineering (MCU architecture, GPIO, UART), and Embedded IoT Programming (IoT models, basic C/C++ programming).
- **Equipment**: A computer (Windows/macOS/Linux) with a USB port.

## 1.4. Robot Joint Specifications

| Joint | Name | Function | Min Angle | Max Angle | Home Angle |
|:---:|:---|:---|:---:|:---:|:---:|
| J0 | Base | Rotates entire arm | 0deg | 180deg | 90deg |
| J1 | Shoulder | Raises/lowers upper arm | 70deg | 150deg | 70deg |
| J2 | Elbow | Extends/retracts forearm | 0deg | 150deg | 90deg |
| J3 | Wrist Pitch | Tilts gripper up/down | 0deg | 180deg | 90deg |
| J4 | Wrist Roll | Rotates gripper | 0deg | 180deg | 90deg |
| J5 | Gripper | Opens/closes gripper | 60deg | 120deg | 90deg |

---

[Back to Main Page](../README.md) | [Group A: Hardware Setup](../group-A-hardware-setup/lab-01-getting-started.md)
