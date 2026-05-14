# Lab 2: Hardware Connection - ESP32, PCA9685, and Robot Arm

## 🎯 Objectives

- Identify the I2C pins on ESP32 and PCA9685
- Correctly connect 4 I2C wires between ESP32 and PCA9685
- Connect all 6 robot servos to the correct PCA9685 channels
- Safely power the system

## 📦 Preparation

- The 6DOF Robot Kit (identified in Lab 1)
- 4 female-to-female Dupont jumper wires (included in Kit or purchased separately)
- External power supply 5V-6V / 3A+ (adapter or battery) for servos

> :warning: **WARNING**: Never use USB power from the computer to power the servos. Servos draw high current (500mA-1A each) and can damage the USB port or ESP32 board.

## 📝 Lab Steps

### Step 1: I2C Circuit Connection

Connect the components using 4 female-to-female Dupont wires:

| PCA9685 | ESP32 | Suggested Wire Color | Function |
|:---:|:---:|:---:|:---|
| SDA | GPIO 21 | Green | I2C Data |
| SCL | GPIO 22 | Yellow | I2C Clock |
| GND | GND | Black | Common Ground |
| VCC | 3V3 | Red | Logic Power |

> :warning: **Note**: Double-check each wire before powering on. Swapping SDA/SCL only prevents communication, but swapping VCC or GND can permanently damage the boards.

### Step 2: Identify servo channels on PCA9685

The PCA9685 module has 16 servo ports (numbered 0-15). Each port has 3 pins: GND (outermost), VCC (middle), PWM (innermost). The firmware uses the first 6 channels:

| PCA9685 Channel | Robot Joint | Servo |
|:---:|:---|:---|
| 0 | J0 - Base | Base servo |
| 1 | J1 - Shoulder | Shoulder servo |
| 2 | J2 - Elbow | Elbow servo |
| 3 | J3 - Wrist Pitch | Wrist pitch servo |
| 4 | J4 - Wrist Roll | Wrist roll servo |
| 5 | J5 - Gripper | Gripper servo |

### Step 3: Plug servos into PCA9685

Insert each servo's 3-pin connector into the correct channel on the PCA9685:

- **Brown** wire (GND) goes to the outermost pin (near the board edge)
- **Red** wire (VCC) goes to the middle pin
- **Orange/Yellow** wire (Signal/PWM) goes to the innermost pin

> :warning: **Note**: If plugged in reverse (brown wire on Signal pin), the servo won't rotate but may be damaged over time. Always verify orientation: brown wire faces the board edge.

### Step 4: Connect external servo power

On the PCA9685 module, locate the green screw terminal marked **V+** and **GND**:

- Positive wire (+) goes to V+
- Negative wire (-) goes to GND

> **Note**: The system uses 2 power sources: USB from the computer powers the ESP32, and an external 5V-6V supply powers the servos through the PCA9685. Both sources share a common GND.

### Step 5: Pre-power-on checklist

Checklist:

- [ ] 4 I2C wires: SDA-SDA, SCL-SCL, GND-GND, 3V3-VCC
- [ ] 6 servos plugged into channels 0-5 with correct orientation (brown wire facing outward)
- [ ] Servo power (5-6V) connected to V+ and GND screw terminal
- [ ] USB cable connecting ESP32 to computer

### Step 6: Notes and Conclusions

*(Students write their observations here)*

## 🧩 Extension Exercises

1. What is I2C? Why can just 2 wires (SDA, SCL) control 16 servo channels?
2. If you wanted to control an additional robot arm (6 more servos), what hardware changes would be needed? *(Hint: PCA9685 has address jumpers to change the I2C address)*

---

[Lab 1: Getting Started](lab-01-getting-started.md) | [Lab 3: Firmware Upload](../group-B-firmware-and-serial/lab-03-firmware-upload.md)
