# Lab 5: Simultaneous Multi-Joint Control and Speed

## 🎯 Objectives

- Use the **A** command to move all 6 joints simultaneously to specified angles
- Use the **S** command to change the movement speed of individual joints
- Use the **W** command to wait for the robot to complete movement
- Use the **X** command for emergency stop

## 📦 Preparation

- Lab 5 firmware uploaded to the ESP32
- Servo power supply connected (5-6V adapter)

## 📋 New Command Reference

| Command | Syntax | Function |
|:---:|:---|:---|
| **A** | `A <a0> <a1> <a2> <a3> <a4> <a5>` | Move all 6 joints simultaneously |
| **S** | `S <id> <speed>` | Set speed for 1 joint (deg/tick) |
| **W** | `W` | Wait for all joints to finish, returns `DONE` |
| **X** | `X` | Emergency stop all joints |

### Background Knowledge

- **Simultaneous movement (A)**: Assigns target angles to all 6 joints at once, creating smooth coordinated motion.
- **Speed control (S)**: Speed = step size per 20ms tick. Default = 1 deg/tick. Setting to 10 = 10x faster.
- **Synchronization (W)**: Firmware only returns `DONE` when all joints have reached their targets.
- **Emergency stop (X)**: Forces target angle = current angle, so servos stop immediately without jerking.

## 📝 Lab Steps

### Step 1: Return robot to Home
```
H
```

### Step 2: Move all joints simultaneously
```
A 45 100 120 45 135 60
-> OK
```
All 6 joints move simultaneously: J0=45deg, J1=100deg, J2=120deg, J3=45deg, J4=135deg, J5=60deg.

### Step 3: Check status
```
T
-> Compare results with the angles sent
```

### Step 4: Increase speed of joint J0
```
S 0 10
M 0 180
-> J0 moves much faster (10 deg/tick instead of 1 deg/tick)
```

### Step 5: Compare different speeds
```
H
S 0 1
S 2 15
A 0 100 150 90 90 90
-> Observe: J2 reaches target before J0 because its speed is higher
```

### Step 6: Using the W (Wait) command
```
S 0 1
M 0 180
W
-> (no immediate response... waiting for robot to finish) -> DONE
```

### Step 7: Using the X (Emergency Stop) command
```
H
(wait for completion)
S 0 1
M 0 0
(while moving, quickly type:)
X
-> OK   (Robot stops immediately at current position)
T
-> (check stopped angles)
```

### Step 8: Notes and Conclusions

*(Students write their observations here)*

## 🧩 Extension Exercises

1. Write all commands into a `.txt` file, one command per line. Copy and paste into Serial Monitor for automated sequential execution.
2. Change positions A and B, find suitable angles using the M command to test each joint individually.
3. Program an action sequence to have the robot stack 2-3 objects on top of each other.

---

[Lab 4: Single Joint Control](lab-04-single-joint-control.md) | [Lab 6: Automated Sequences](../group-C-advanced-applications/lab-06-automated-sequences.md)
