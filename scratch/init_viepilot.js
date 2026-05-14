const fs = require('fs');
const path = require('path');

const viepilotDir = path.join(__dirname, '..', '.viepilot');
if (!fs.existsSync(viepilotDir)) {
    fs.mkdirSync(viepilotDir, { recursive: true });
}

const files = {
    'META.md': `---
viepilot_profile_id: default
---
`,
    'PROJECT-META.md': `# Project Metadata
- Project Name: RobotArm
- Description: Hệ thống điều khiển cánh tay robot 6 bậc tự do (6-DOF Robot Arm)
- Organization: Open Source
- Package Base ID: com.robotarm.app
- License: MIT
- Year: 2026
`,
    'AI-GUIDE.md': `# AI Navigation Guide
- Read TRACKER.md for current state
- Read ROADMAP.md for phase execution
`,
    'ARCHITECTURE.md': `# Architecture
- Firmware: C++ / PlatformIO on ESP32
- GUI: Python / Tkinter
- Communication: Serial (Phase 1), HTTP/WebSocket (Phase 2)
`,
    'PROJECT-CONTEXT.md': `# Project Context
## Domain Knowledge
- 6-DOF Robot Arm control.
## Phases
- Phase 1: Việt hóa mã nguồn
- Phase 2: Tích hợp Web Server
`,
    'SYSTEM-RULES.md': `# System Rules
- Code MUST be in Vietnamese for comments.
- Follow PEP8 for Python.
`,
    'ROADMAP.md': `# Roadmap
## Phase 1: Việt hóa mã nguồn
- [ ] Task 1: Quét toàn bộ file .py, .cpp, .h
- [ ] Task 2: Dịch các inline comments, block comments sang tiếng Việt
## Phase 2: Tích hợp Web Server
- [ ] Task 1: Tích hợp module WiFi vào firmware
- [ ] Task 2: Thiết kế trang HTML tĩnh chứa các thanh trượt điều khiển
- [ ] Task 3: Viết API để frontend giao tiếp với backend
`,
    'TRACKER.md': `# Tracker
- Current Phase: Phase 1
- Status: In Progress
`,
    'HANDOFF.json': JSON.stringify({ current_phase: 1, crystallize_version: '2.19.0' }, null, 2)
};

for (const [filename, content] of Object.entries(files)) {
    fs.writeFileSync(path.join(viepilotDir, filename), content);
}

const phase1Dir = path.join(viepilotDir, 'phases', '1');
fs.mkdirSync(phase1Dir, { recursive: true });
fs.writeFileSync(path.join(phase1Dir, 'PHASE-STATE.md'), `# Phase 1 State
Status: in_progress
`);

const tasksDir = path.join(viepilotDir, 'tasks');
fs.mkdirSync(tasksDir, { recursive: true });

// Task 1: Quét toàn bộ file
fs.writeFileSync(path.join(tasksDir, 'p1-t1-scan-files.md'), `# Task: Quét toàn bộ file
## Objective
Xác định danh sách các file cần dịch comments.
## Paths
- firmware/src/main.cpp
- gui/main.py
## File-Level Plan
- Đọc qua để chuẩn bị dịch.
`);

// Task 2: Dịch comments
fs.writeFileSync(path.join(tasksDir, 'p1-t2-translate.md'), `# Task: Dịch comments
## Objective
Dịch toàn bộ comments sang tiếng Việt.
## Paths
- firmware/src/main.cpp
- gui/main.py
## File-Level Plan
- firmware/src/main.cpp: Dịch các comment tiếng Anh sang tiếng Việt.
- gui/main.py: Dịch các comment tiếng Anh sang tiếng Việt.
`);

console.log('Successfully created .viepilot artifacts.');
