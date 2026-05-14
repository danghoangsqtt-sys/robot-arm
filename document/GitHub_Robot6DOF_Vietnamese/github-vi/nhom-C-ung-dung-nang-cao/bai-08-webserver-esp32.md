# Bài 8: Điều Khiển Cánh Tay Robot qua Web Server ESP32

## 🎯 Mục tiêu

- Hiểu nguyên lý hoạt động của Web Server trên ESP32 (WiFi SoftAP và Station mode)
- Lập trình ESP32 tạo Web Server phục vụ giao diện HTML điều khiển robot
- Xây dựng trang web responsive với 6 thanh trượt điều khiển các khớp
- Điều khiển robot từ trình duyệt trên điện thoại hoặc máy tính trong cùng mạng LAN

## 📦 Chuẩn bị

- Robot đã kết nối và firmware hoạt động tốt (đã hoàn thành Bài 1–6)
- ESP32 kết nối máy tính qua cáp USB
- Điện thoại hoặc máy tính khác kết nối cùng mạng WiFi (cho Station mode)
- Thông tin WiFi: tên mạng (SSID) và mật khẩu

## 📋 Kiến Thức Nền

### Web Server trên ESP32

ESP32 có module WiFi tích hợp, có thể hoạt động ở 2 chế độ:

| Chế độ | Mô tả | Ưu điểm | Nhược điểm |
|:---|:---|:---|:---|
| **SoftAP** | ESP32 tự tạo mạng WiFi riêng | Không cần router, hoạt động mọi nơi | Phạm vi hẹp, không có Internet |
| **Station** | ESP32 kết nối vào mạng WiFi có sẵn | Phạm vi rộng, có Internet | Cần biết SSID/password |

### Luồng hoạt động

```
Trình duyệt (Client)
    │
    ▼  HTTP Request (GET /move?j=0&a=90)
ESP32 Web Server
    │
    ▼  Gửi lệnh qua I2C
PCA9685 → Servo → Robot chuyển động
    │
    ▲  HTTP Response (JSON: {"status":"ok"})
Trình duyệt cập nhật UI
```

## 📝 Các Bước Thực Hành

### Bước 1: Tạo project mới trên PlatformIO

Tạo project mới hoặc copy project cũ:
- **Name**: `RobotArm_WebServer`
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
lib_deps =
    ESP Async WebServer
    AsyncTCP
build_flags =
    -Os
    -DCORE_DEBUG_LEVEL=0
```

### Bước 3: Tạo file `wifi_config.h`

```cpp
#ifndef WIFI_CONFIG_H
#define WIFI_CONFIG_H

// === CHẾ ĐỘ WIFI ===
// Đặt true để dùng SoftAP (ESP32 tự phát WiFi)
// Đặt false để kết nối vào mạng WiFi có sẵn (Station)
#define USE_SOFTAP true

// --- Cấu hình SoftAP ---
#define AP_SSID     "RobotArm_AP"
#define AP_PASSWORD "12345678"

// --- Cấu hình Station (kết nối WiFi có sẵn) ---
#define STA_SSID     "TEN_WIFI_CUA_BAN"
#define STA_PASSWORD "MAT_KHAU_WIFI"

#endif
```

### Bước 4: Tạo file `web_page.h` — Giao diện HTML

```cpp
#ifndef WEB_PAGE_H
#define WEB_PAGE_H

const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Robot Arm 6DOF Control</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #1a1a2e; color: #eee;
            min-height: 100vh; padding: 20px;
        }
        .container { max-width: 500px; margin: 0 auto; }
        h1 {
            text-align: center; font-size: 1.4em;
            color: #00d2ff; margin-bottom: 20px;
        }
        .joint-card {
            background: #16213e; border-radius: 12px;
            padding: 12px 16px; margin-bottom: 10px;
            border: 1px solid #0f3460;
        }
        .joint-header {
            display: flex; justify-content: space-between;
            align-items: center; margin-bottom: 8px;
        }
        .joint-name { font-weight: bold; font-size: 0.95em; }
        .joint-value {
            background: #0f3460; padding: 4px 12px;
            border-radius: 20px; font-size: 0.9em;
            color: #00d2ff; font-weight: bold;
        }
        input[type="range"] {
            width: 100%; height: 6px; -webkit-appearance: none;
            background: #0f3460; border-radius: 3px; outline: none;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none; width: 24px; height: 24px;
            background: #00d2ff; border-radius: 50%; cursor: pointer;
        }
        .btn-group {
            display: flex; gap: 10px; margin-top: 15px;
        }
        .btn {
            flex: 1; padding: 14px; border: none; border-radius: 10px;
            font-size: 1em; font-weight: bold; cursor: pointer;
            color: white; text-transform: uppercase;
        }
        .btn-home { background: #2e86de; }
        .btn-stop { background: #e74c3c; }
        .btn-status { background: #404040; }
        .log {
            background: #0d1117; border-radius: 10px;
            padding: 12px; margin-top: 15px; height: 120px;
            overflow-y: auto; font-family: monospace;
            font-size: 0.8em; color: #8b949e;
            border: 1px solid #30363d;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Robot Arm 6DOF</h1>
        <div id="joints"></div>
        <div class="btn-group">
            <button class="btn btn-home" onclick="sendHome()">Home</button>
            <button class="btn btn-status" onclick="sendStatus()">Status</button>
            <button class="btn btn-stop" onclick="sendStop()">STOP</button>
        </div>
        <div class="log" id="log"></div>
    </div>
    <script>
        const joints = [
            {name:'J0 Base',    ch:0, min:0,  max:180, home:90},
            {name:'J1 Shoulder',ch:1, min:70, max:150, home:70},
            {name:'J2 Elbow',   ch:2, min:0,  max:150, home:90},
            {name:'J3 Wrist P', ch:3, min:0,  max:180, home:90},
            {name:'J4 Wrist R', ch:4, min:0,  max:180, home:90},
            {name:'J5 Gripper', ch:5, min:60, max:120, home:90},
        ];
        const container = document.getElementById('joints');
        joints.forEach(j => {
            const card = document.createElement('div');
            card.className = 'joint-card';
            card.innerHTML = `
                <div class="joint-header">
                    <span class="joint-name">${j.name}</span>
                    <span class="joint-value" id="val${j.ch}">${j.home}°</span>
                </div>
                <input type="range" min="${j.min}" max="${j.max}" value="${j.home}"
                       id="slider${j.ch}"
                       oninput="onSlide(${j.ch}, this.value)">
            `;
            container.appendChild(card);
        });

        function log(msg) {
            const el = document.getElementById('log');
            el.innerHTML += msg + '<br>';
            el.scrollTop = el.scrollHeight;
        }

        let timeout = null;
        function onSlide(ch, val) {
            document.getElementById('val'+ch).textContent = val + '°';
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                fetch(`/move?j=${ch}&a=${val}`)
                    .then(r => r.json())
                    .then(d => log(`M ${ch} ${val} → ${d.status}`))
                    .catch(e => log('ERR: ' + e));
            }, 50);
        }

        function sendHome() {
            fetch('/home').then(r => r.json()).then(d => {
                log('HOME → ' + d.status);
                joints.forEach(j => {
                    document.getElementById('slider'+j.ch).value = j.home;
                    document.getElementById('val'+j.ch).textContent = j.home+'°';
                });
            });
        }

        function sendStop() {
            fetch('/stop').then(r => r.json()).then(d => log('STOP → '+d.status));
        }

        function sendStatus() {
            fetch('/status').then(r => r.json()).then(d => log('STA: '+JSON.stringify(d)));
        }
    </script>
</body>
</html>
)rawliteral";

#endif
```

### Bước 5: Tạo file `main.cpp` — Chương trình chính

```cpp
#include <Arduino.h>
#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <Wire.h>
#include "config.h"
#include "wifi_config.h"
#include "web_page.h"
#include "pca9685.h"
#include "servo_ctrl.h"

AsyncWebServer server(80);
extern ServoController sc;  // Từ servo_ctrl

void setupWiFi() {
#if USE_SOFTAP
    WiFi.softAP(AP_SSID, AP_PASSWORD);
    Serial.print("AP IP: ");
    Serial.println(WiFi.softAPIP());
#else
    WiFi.begin(STA_SSID, STA_PASSWORD);
    Serial.print("Connecting to WiFi");
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    if (WiFi.status() == WL_CONNECTED) {
        Serial.print("\nIP: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\nWiFi FAILED! Falling back to SoftAP...");
        WiFi.softAP(AP_SSID, AP_PASSWORD);
        Serial.print("AP IP: ");
        Serial.println(WiFi.softAPIP());
    }
#endif
}

void setupServer() {
    // Trang chủ
    server.on("/", HTTP_GET, [](AsyncWebServerRequest *req){
        req->send(200, "text/html", index_html);
    });

    // Di chuyển 1 khớp: /move?j=0&a=90
    server.on("/move", HTTP_GET, [](AsyncWebServerRequest *req){
        if (req->hasParam("j") && req->hasParam("a")) {
            int joint = req->getParam("j")->value().toInt();
            int angle = req->getParam("a")->value().toInt();
            sc.moveTo(joint, angle);
            req->send(200, "application/json", "{\"status\":\"ok\"}");
        } else {
            req->send(400, "application/json", "{\"status\":\"error\",\"msg\":\"missing params\"}");
        }
    });

    // Về Home
    server.on("/home", HTTP_GET, [](AsyncWebServerRequest *req){
        sc.homeAll();
        req->send(200, "application/json", "{\"status\":\"ok\"}");
    });

    // Dừng khẩn cấp
    server.on("/stop", HTTP_GET, [](AsyncWebServerRequest *req){
        sc.emergencyStop();
        req->send(200, "application/json", "{\"status\":\"ok\"}");
    });

    // Trạng thái
    server.on("/status", HTTP_GET, [](AsyncWebServerRequest *req){
        String json = "{\"joints\":[";
        for (int i = 0; i < 6; i++) {
            if (i > 0) json += ",";
            json += String(sc.getAngle(i));
        }
        json += "]}";
        req->send(200, "application/json", json);
    });

    server.begin();
    Serial.println("Web Server started!");
}

void setup() {
    Serial.begin(115200);
    Wire.begin(21, 22);
    sc.init();
    setupWiFi();
    setupServer();
    Serial.println("ARM READY (Web Mode)");
}

void loop() {
    sc.update();  // Cập nhật nội suy servo
    delay(20);
}
```

### Bước 6: Biên dịch và nạp firmware

```
Ctrl+Alt+B  → Biên dịch
Ctrl+Alt+U  → Nạp vào ESP32
```

### Bước 7: Kết nối và kiểm tra

**Chế độ SoftAP (mặc định):**
1. Mở Serial Monitor → ghi lại địa chỉ IP (thường là `192.168.4.1`)
2. Trên điện thoại/máy tính, kết nối WiFi: `RobotArm_AP`, mật khẩu: `12345678`
3. Mở trình duyệt, truy cập: `http://192.168.4.1`

**Chế độ Station:**
1. Sửa `wifi_config.h`: `USE_SOFTAP false`, nhập SSID và password WiFi
2. Nạp lại firmware → Serial Monitor hiển thị IP (ví dụ: `192.168.1.105`)
3. Mở trình duyệt trên thiết bị cùng mạng, truy cập IP đó

### Bước 8: Thao tác kiểm tra trên Web

- Kéo thanh trượt → robot xoay servo tương ứng
- Nhấn **Home** → tất cả khớp về vị trí mặc định
- Nhấn **STOP** → dừng khẩn cấp
- Nhấn **Status** → hiển thị góc hiện tại trong Log

### Bước 9: Nhận xét và kết luận

*(Sinh viên ghi nhận xét)*

## 🧩 Bài Tập Mở Rộng

1. Thêm tính năng lưu/phát lại chuỗi hành động trên giao diện web (Record/Play).
2. Thêm chế độ điều khiển bằng gamepad ảo trên web (joystick).
3. Tích hợp mDNS để truy cập bằng tên `http://robotarm.local` thay vì IP.
4. Thêm WebSocket thay vì HTTP polling để phản hồi real-time.

---

[⬅️ Bài 7: Python & GUI](bai-07-python-gui.md) | [➡️ Bài 9: Bluetooth](bai-09-bluetooth-esp32.md)
