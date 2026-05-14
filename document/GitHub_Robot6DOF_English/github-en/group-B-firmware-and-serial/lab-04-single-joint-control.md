# Lab 4: Single Joint Servo Control

## 🎯 Objectives

- Use the **M** command to move individual servo joints to a desired angle
- Use the **G** command to read the current angle of each joint
- Use the **T** command to view the status of all 6 joints
- Use the **H** command to return the robot to the Home position
- Understand angle limits for each joint and the effect of angle clamping

## 📦 Preparation

- Lab 4 firmware uploaded to the ESP32
- Servo power supply connected (5-6V adapter)

> :warning: Ensure the robot arm is placed on a stable surface with no obstacles nearby.

## 📋 Command Reference

| Command | Syntax | Function | Example |
|:---:|:---|:---|:---|
| **M** | `M <id> <angle>` | Move 1 joint to specified angle | `M 0 45` |
| **G** | `G <id>` | Read current angle of 1 joint | `G 0` returns `VAL:0:90` |
| **T** | `T` | View status of all 6 joints | `STA:90,70,90,90,90,90` |
| **H** | `H` or `H <id>` | Return to Home (all or 1 joint) | `H` or `H 0` |
| **I** | `I` | View configuration info | CFG for each joint |

## 📝 Lab Steps

### Part A: Moving Joint J0 (Base - Rotation)

**Step 1**: Check current angle
```
G 0
-> VAL:0:90   (joint 0 is at 90 degrees, Home position)
```

**Step 2**: Rotate base to the right (decrease angle)
```
M 0 45
-> OK   (Base slowly rotates right to 45 degrees)
```

**Step 3**: Rotate base to the left (increase angle)
```
M 0 135
-> OK   (Base rotates left to 135 degrees)
```

**Step 4**: Return joint J0 to Home
```
H 0
-> OK   (Base returns to 90 degrees)
```

### Part B: Controlling other joints

**Step 5**: Control joint J1 (Shoulder)
```
M 1 100     -> raise shoulder
M 1 70      -> lower shoulder to min
```

> **Note**: Joint J1 has limits of 70-150 degrees. If you enter `M 1 30`, the firmware will automatically clamp to 70 degrees.

**Step 6**: Control joint J5 (Gripper)
```
M 5 60      -> open gripper fully
M 5 120     -> close gripper fully
M 5 90      -> close gripper moderately
```

### Part C: Status Check

**Step 7**: Check overall status
```
T
-> STA:90,70,90,90,90,90
```

**Step 8**: View configuration info
```
I
-> (6 CFG lines: min angle, max angle, Home, current speed)
```

**Step 9**: Return all joints to Home
```
H
-> OK   (All 6 joints return to Home position)
```

### Step 10: Notes and Conclusions

*(Students write their observations here)*

## 🧩 Extension Exercises

1. Create a table: move each joint J0-J5 to its min and max angles. Observe and describe the actual movements.
2. Try entering invalid commands, e.g.: `M 9 90` (non-existent ID), `M` (missing parameters). Observe the ERR responses from the firmware.

---

[Lab 3: Firmware Upload](lab-03-firmware-upload.md) | [Lab 5: Multi-Joint Control](lab-05-multi-joint-control.md)
