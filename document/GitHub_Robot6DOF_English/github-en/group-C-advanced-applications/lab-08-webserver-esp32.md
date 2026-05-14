# Lab 8: Controlling the Robot Arm via ESP32 Web Server

## 🎯 Objectives

- Understand how a Web Server works on ESP32 (WiFi SoftAP and Station mode)
- Program ESP32 to create a Web Server serving an HTML control interface
- Build a responsive web page with 6 sliders to control each joint
- Control the robot from a browser on a phone or computer on the same LAN

## 📦 Preparation

- Robot connected and firmware working properly (Labs 1-6 completed)
- ESP32 connected to computer via USB cable
- A phone or another computer on the same WiFi network (for Station mode)
- WiFi credentials: network name (SSID) and password

## 📋 Background Knowledge

### Web Server on ESP32

The ESP32 has a built-in WiFi module that can operate in 2 modes:

| Mode | Description | Advantages | Disadvantages |
|:---|:---|:---|:---|
| **SoftAP** | ESP32 creates its own WiFi network | No router needed, works anywhere | Limited range, no Internet |
| **Station** | ESP32 connects to existing WiFi | Wide range, Internet access | Requires SSID/password |

### Operation Flow

```
Browser (Client)
    |
    v  HTTP Request (GET /move?j=0&a=90)
ESP32 Web Server
    |
    v  Sends command via I2C
PCA9685 -> Servo -> Robot moves
    |
    ^  HTTP Response (JSON: {"status":"ok"})
Browser updates UI
```

## 📝 Lab Steps

### Step 1: Create a new PlatformIO project

Create a new project or copy an existing one:
- **Name**: `RobotArm_WebServer`
- **Board**: ESP32 Dev Module
- **Framework**: Arduino

### Step 2: Update `platformio.ini`

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

### Step 3: Create `wifi_config.h`

```cpp
#ifndef WIFI_CONFIG_H
#define WIFI_CONFIG_H

// === WIFI MODE ===
// Set true to use SoftAP (ESP32 creates its own WiFi)
// Set false to connect to an existing WiFi network (Station)
#define USE_SOFTAP true

// --- SoftAP Configuration ---
#define AP_SSID     "RobotArm_AP"
#define AP_PASSWORD "12345678"

// --- Station Configuration (connect to existing WiFi) ---
#define STA_SSID     "YOUR_WIFI_NAME"
#define STA_PASSWORD "YOUR_WIFI_PASSWORD"

#endif
```

### Step 4: Create `web_page.h` - HTML Interface

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
        <h1>Robot Arm 6DOF</h1>
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
                    <span class="joint-value" id="val${j.ch}">${j.home}deg</span>
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
            document.getElementById('val'+ch).textContent = val + 'deg';
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                fetch(`/move?j=${ch}&a=${val}`)
                    .then(r => r.json())
                    .then(d => log(`M ${ch} ${val} -> ${d.status}`))
                    .catch(e => log('ERR: ' + e));
            }, 50);
        }

        function sendHome() {
            fetch('/home').then(r => r.json()).then(d => {
                log('HOME -> ' + d.status);
                joints.forEach(j => {
                    document.getElementById('slider'+j.ch).value = j.home;
                    document.getElementById('val'+j.ch).textContent = j.home+'deg';
                });
            });
        }

        function sendStop() {
            fetch('/stop').then(r => r.json()).then(d => log('STOP -> '+d.status));
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

### Step 5: Create `main.cpp` - Main Program

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
extern ServoController sc;  // From servo_ctrl

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
    // Home page
    server.on("/", HTTP_GET, [](AsyncWebServerRequest *req){
        req->send(200, "text/html", index_html);
    });

    // Move single joint: /move?j=0&a=90
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

    // Return to Home
    server.on("/home", HTTP_GET, [](AsyncWebServerRequest *req){
        sc.homeAll();
        req->send(200, "application/json", "{\"status\":\"ok\"}");
    });

    // Emergency Stop
    server.on("/stop", HTTP_GET, [](AsyncWebServerRequest *req){
        sc.emergencyStop();
        req->send(200, "application/json", "{\"status\":\"ok\"}");
    });

    // Status
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
    sc.update();  // Update servo interpolation
    delay(20);
}
```

### Step 6: Compile and upload firmware

```
Ctrl+Alt+B  -> Compile
Ctrl+Alt+U  -> Upload to ESP32
```

### Step 7: Connect and test

**SoftAP mode (default):**
1. Open Serial Monitor and note the IP address (usually `192.168.4.1`)
2. On your phone/computer, connect to WiFi: `RobotArm_AP`, password: `12345678`
3. Open a browser and navigate to: `http://192.168.4.1`

**Station mode:**
1. Edit `wifi_config.h`: set `USE_SOFTAP false`, enter your WiFi SSID and password
2. Re-upload firmware. Serial Monitor will display the IP (e.g.: `192.168.1.105`)
3. Open a browser on any device on the same network and navigate to that IP

### Step 8: Web interface testing

- Drag sliders to move the corresponding servos
- Click **Home** to return all joints to default positions
- Click **STOP** for emergency stop
- Click **Status** to display current angles in the Log

### Step 9: Notes and Conclusions

*(Students write their observations here)*

## 🧩 Extension Exercises

1. Add a Record/Play feature on the web interface to save and replay action sequences.
2. Add a virtual gamepad (joystick) control mode on the web page.
3. Integrate mDNS so you can access via `http://robotarm.local` instead of an IP address.
4. Replace HTTP polling with WebSocket for real-time communication.

---

[Lab 7: Python & GUI](lab-07-python-gui.md) | [Lab 9: Bluetooth](lab-09-bluetooth-esp32.md)
