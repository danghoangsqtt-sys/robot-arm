# Bài 9: Điều Khiển Cánh Tay Robot qua Bluetooth ESP32

## 🎯 Mục tiêu

- Hiểu nguyên lý Bluetooth Classic (SPP) và Bluetooth Low Energy (BLE) trên ESP32
- Lập trình ESP32 nhận lệnh điều khiển robot qua Bluetooth Serial
- Kết nối và điều khiển robot từ điện thoại Android bằng ứng dụng Bluetooth Terminal
- Xây dựng ứng dụng Python trên máy tính giao tiếp Bluetooth với robot

## 📦 Chuẩn bị

- Robot đã kết nối và firmware hoạt động tốt (đã hoàn thành Bài 1–6)
- ESP32 kết nối máy tính qua cáp USB
- Điện thoại Android có Bluetooth (hoặc máy tính có Bluetooth)
- Ứng dụng "Serial Bluetooth Terminal" trên Android (tải miễn phí từ Google Play)

## 📋 Kiến Thức Nền

### Bluetooth trên ESP32

ESP32 hỗ trợ cả Bluetooth Classic và BLE. Trong bài này sử dụng **Bluetooth Classic SPP** (Serial Port Profile) vì đơn giản và tương thích với nhiều thiết bị.

| Đặc điểm | Bluetooth Classic (SPP) | BLE |
|:---|:---|:---|
| Phạm vi | ~10m | ~50m |
| Tốc độ | Nhanh hơn | Tiết kiệm năng lượng |
| Tương thích | Android, PC | Android, iOS, PC |
| Độ phức tạp | Đơn giản (như Serial) | Phức tạp hơn (GATT) |

### Luồng hoạt động

```
Điện thoại / PC (Bluetooth Client)
    │
    ▼  Gửi lệnh text qua Bluetooth SPP
ESP32 (Bluetooth Server)
    │  Nhận lệnh → Xử lý giống Serial
    ▼
PCA9685 → Servo → Robot chuyển động
    │
    ▲  Gửi phản hồi qua Bluetooth
Client nhận và hiển thị
```

## 📝 Các Bước Thực Hành

### Phần A: Firmware Bluetooth trên ESP32

### Bước 1: Tạo project mới

- **Name**: `RobotArm_Bluetooth`
- **Board**: ESP32 Dev Module
- **Framework**: Arduino

### Bước 2: Cập nhật `platformio.ini`

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

> **Lưu ý**: Bluetooth Classic đã có sẵn trong ESP32 Arduino core, không cần thêm thư viện.

### Bước 3: Tạo file `bt_config.h`

```cpp
#ifndef BT_CONFIG_H
#define BT_CONFIG_H

// Tên thiết bị Bluetooth (hiển thị khi tìm kiếm trên điện thoại)
#define BT_DEVICE_NAME "RobotArm_BT"

// Cho phép điều khiển đồng thời qua cả Serial USB và Bluetooth
#define DUAL_CONTROL true

#endif
```

### Bước 4: Tạo file `main.cpp` — Chương trình chính

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

// Buffer cho lệnh Bluetooth
String btBuffer = "";

void processCommand(String cmd, Stream &output) {
    cmd.trim();
    if (cmd.length() == 0) return;

    String response = parser.execute(cmd);
    output.println(response);

    // Nếu DUAL_CONTROL, in ra cả Serial USB để debug
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

    // Khởi tạo I2C và servo
    Wire.begin(21, 22);
    sc.init();

    // Khởi tạo Bluetooth
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
    // === Xử lý lệnh từ Bluetooth ===
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

    // === Xử lý lệnh từ Serial USB (nếu DUAL_CONTROL) ===
    #if DUAL_CONTROL
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        processCommand(cmd, Serial);
    }
    #endif

    // === Cập nhật nội suy servo ===
    sc.update();
    delay(20);
}
```

### Bước 5: Biên dịch và nạp firmware

```
Ctrl+Alt+B  → Biên dịch
Ctrl+Alt+U  → Nạp vào ESP32
```

Mở Serial Monitor xác nhận:
```
Initializing...
ARM READY (Bluetooth Mode)
Bluetooth name: RobotArm_BT
Waiting for connection...
```

### Phần B: Kết nối từ điện thoại Android

### Bước 6: Ghép nối Bluetooth

1. Trên điện thoại Android, vào **Cài đặt → Bluetooth → Bật Bluetooth**
2. Nhấn **Tìm thiết bị mới** (Scan)
3. Tìm và chọn **"RobotArm_BT"**
4. Nếu yêu cầu mã PIN, nhập `1234` hoặc `0000`
5. Sau khi ghép nối thành công, trạng thái hiện "Đã kết nối" (Paired)

### Bước 7: Cài đặt ứng dụng Serial Bluetooth Terminal

1. Mở Google Play Store
2. Tìm và cài đặt: **"Serial Bluetooth Terminal"** (của Kai Morich)
3. Mở ứng dụng → Nhấn biểu tượng Bluetooth → Chọn "RobotArm_BT"
4. Khi kết nối thành công, thanh trạng thái chuyển sang "Connected"

### Bước 8: Gửi lệnh điều khiển

Trong ứng dụng, gõ và gửi các lệnh giống Serial Monitor:

```
T           → STA:90,70,90,90,90,90
M 0 45      → OK (đế xoay sang 45°)
M 5 60      → OK (mở kẹp)
H           → OK (về Home)
A 45 100 120 90 90 60  → OK (di chuyển đồng thời)
X           → OK (dừng khẩn cấp)
```

### Bước 9: Cấu hình nút tắt nhanh (Macro)

Trong Serial Bluetooth Terminal, thiết lập các nút macro:

| Nút | Lệnh | Chức năng |
|:---|:---|:---|
| M1 | `H` | Home |
| M2 | `T` | Trạng thái |
| M3 | `X` | Dừng khẩn cấp |
| M4 | `M 5 60` | Mở kẹp |
| M5 | `M 5 110` | Đóng kẹp |

### Phần C: Điều khiển từ Python qua Bluetooth

### Bước 10: Cài đặt thư viện

```bash
pip install pyserial
```

> **Lưu ý**: Trên Windows, sau khi ghép nối Bluetooth, ESP32 sẽ xuất hiện như 1 COM port ảo (ví dụ: COM5). Kiểm tra trong Device Manager → Ports → "Standard Serial over Bluetooth link".

### Bước 11: Tạo file `robot_bluetooth.py`

```python
import serial
import time

# === CẤU HÌNH ===
# Windows: COM port ảo Bluetooth (kiểm tra Device Manager)
# Linux: /dev/rfcomm0
# macOS: /dev/tty.RobotArm_BT-SPP
BT_PORT = 'COM5'    # Thay bằng COM port Bluetooth thực tế
BAUD = 115200

print(f'Ket noi Bluetooth {BT_PORT}...')
robot = serial.Serial(BT_PORT, BAUD, timeout=3)
time.sleep(2)
print('Ket noi thanh cong!')

def send(cmd):
    robot.write((cmd + '\n').encode())
    resp = robot.readline().decode('utf-8', errors='ignore').strip()
    print(f'  [{cmd:30s}] -> {resp}')
    return resp

def wait_done():
    resp = send('W')
    if resp != 'DONE':
        print('  (Canh bao: chua nhan DONE)')

# === KIỂM TRA KẾT NỐI ===
print('\n--- Kiem tra ---')
send('T')
send('I')

# === ĐIỀU KHIỂN ===
print('\n--- Dieu khien qua Bluetooth ---')
send('H')
wait_done()

send('M 0 45')
wait_done()

send('M 0 135')
wait_done()

send('H')
wait_done()

print('\n=== HOAN THANH ===')
robot.close()
```

### Bước 12: Chạy script Python

```bash
python robot_bluetooth.py
```

### Bước 13: Nhận xét và kết luận

*(Sinh viên ghi nhận xét)*

## ⚠️ Xử Lý Lỗi Thường Gặp

| Lỗi | Nguyên nhân | Giải pháp |
|:---|:---|:---|
| Không tìm thấy "RobotArm_BT" | Bluetooth chưa bật hoặc firmware lỗi | Kiểm tra Serial Monitor, reset ESP32 |
| "Connection refused" | Đã có kết nối khác đang dùng | Ngắt kết nối cũ, thử lại |
| Ký tự lạ | Baud rate không khớp | Kiểm tra cả hai bên dùng 115200 |
| Timeout (không phản hồi) | Khoảng cách quá xa hoặc nhiễu | Lại gần, kiểm tra pin |
| COM port không xuất hiện (Windows) | Chưa ghép nối hoặc driver lỗi | Ghép nối lại trong Bluetooth Settings |

## 🧩 Bài Tập Mở Rộng

1. **Kết hợp WiFi + Bluetooth**: Sửa firmware để ESP32 vừa chạy Web Server (Bài 8) vừa nhận lệnh Bluetooth, ưu tiên lệnh Bluetooth khi có xung đột.
2. **Bluetooth Low Energy (BLE)**: Tìm hiểu thư viện `BLEDevice.h`, viết firmware BLE để điều khiển từ iOS (iPhone không hỗ trợ Bluetooth Classic SPP).
3. **Ứng dụng Android tự tạo**: Dùng MIT App Inventor hoặc Flutter để tạo app điều khiển robot qua Bluetooth với giao diện đồ họa đẹp hơn.
4. **Điều khiển bằng giọng nói**: Tích hợp module nhận dạng giọng nói trên điện thoại, chuyển đổi thành lệnh gửi qua Bluetooth.

---

[⬅️ Bài 8: Web Server](bai-08-webserver-esp32.md) | [🏠 Trang chính](../README.md)
