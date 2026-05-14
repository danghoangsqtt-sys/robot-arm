# Lab 6: Programming Automated Action Sequences

## 🎯 Objectives

- Design a command sequence for the robot to pick up, move, and place an object
- Master the combination of A, M, S, W commands to create sequential movements
- Send multiple commands sequentially via Serial for continuous robot operation

## 📦 Preparation

- Robot connected and firmware working properly
- A small, lightweight object for gripping test (eraser, small wooden block, pen cap)
- Place the object in front of the robot, within reach

## 📝 Lab Steps

### Step 1: Plan the phases

Task: "Pick up object from position A, place it at position B":

| Phase | Action | Description |
|:---:|:---|:---|
| 1 | Prepare | Return to Home, open gripper |
| 2 | Approach | Move above the object |
| 3 | Lower | Lower the arm to object level |
| 4 | Grip | Close gripper |
| 5 | Lift | Raise the arm |
| 6 | Move | Rotate base to position B |
| 7 | Lower & Release | Lower arm, open gripper |
| 8 | Retract | Raise arm, return to Home |

### Step 2: Preparation (set appropriate speeds)

```
S 0 3
S 1 2
S 2 2
S 3 3
S 4 3
S 5 5
H
W
-> Wait for DONE
```

### Step 3: Open gripper and approach object

```
M 5 60
W
A 90 120 130 90 90 60
W
-> Wait for DONE. Gripper open, arm positioned above the object.
```

> **Note**: The angles below are sample values. Adjust according to actual object position.

### Step 4: Lower and grip

```
A 90 140 140 90 90 60
W
M 5 110
W
-> Gripper closes, firmly gripping the object.
```

### Step 5: Lift and move

```
A 90 100 90 90 90 110
W
M 0 45
W
-> Robot rotates base to position B (45 degrees) while holding the object.
```

### Step 6: Lower and release

```
A 45 130 130 90 90 110
W
M 5 60
W
-> Gripper opens, releasing the object at position B.
```

### Step 7: Retract to Home

```
A 45 100 90 90 90 90
W
H
W
-> Robot returns to initial position. Task complete!
```

### Step 8: Notes and Conclusions

*(Students write their observations here)*

## 🧩 Extension Exercises

1. Write all commands into a `.txt` file, copy and paste into Serial Monitor for automated execution.
2. Change positions A and B, find suitable angles using the M command to test each joint.
3. Program an action sequence to have the robot stack 2-3 objects on top of each other.

---

[Lab 5: Multi-Joint Control](../group-B-firmware-and-serial/lab-05-multi-joint-control.md) | [Lab 7: Python & GUI](lab-07-python-gui.md)
