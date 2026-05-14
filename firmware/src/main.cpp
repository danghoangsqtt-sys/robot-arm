// =============================================================
//  main.cpp  –  Điểm bắt đầu của bộ điều khiển cánh tay robot
//
//  Kiến trúc
//  ┌───────────────────────────────────────────────────────┐
//  │  Serial RX  →  CmdParser  →  ServoCtrl  →  PCA9685  │
//  │                                  ↑                    │
//  │              millis() timer ─────┘  (cập nhật chuyển động)  │
//  └───────────────────────────────────────────────────────┘
//
//  Không dùng RTOS; mọi thứ chạy song song trong hàm loop().
//  Chuyển động được cập nhật sau mỗi CFG_STEP_MS (mặc định 20 ms).
// =============================================================
#include <Arduino.h>
#include <RobotArmCore.h>
#include "web_server.h"

// ── Các biến đối tượng module (static = không cấp phát heap) ──────────
static PCA9685   pca(CFG_PCA_ADDR);
static ServoCtrl servos(pca);
static CmdParser parser(servos);

static uint32_t lastStepMs = 0;

// ─────────────────────────────────────────────────────────────

void setup() {
    Serial.begin(CFG_BAUD);
    Serial.println(F("ARM INIT"));

    // Khởi tạo I2C và PCA9685
    if (!pca.begin(CFG_SDA_PIN, CFG_SCL_PIN, CFG_I2C_FREQ)) {
        Serial.println(F("ERR:PCA9685"));
        // Dừng lại – không có chức năng nào hoạt động được nếu thiếu driver
        while (true) delay(1000);
    }
    pca.setPWMFreq(CFG_PWM_FREQ_HZ);

    // Đưa tất cả các servo về vị trí gốc (home)
    servos.begin();

    // Khởi động Web Server
    WebControl::begin(&parser);

    Serial.println(F("ARM READY"));
}

void loop() {
    // ── 1. Nạp từng byte dữ liệu nhận được từ Serial vào bộ phân tích lệnh ──
    while (Serial.available()) {
        parser.feed((char)Serial.read());
    }

    // ── 2. Cập nhật chuyển động của servo theo bộ đếm thời gian cố định ───────────────
    uint32_t now = millis();
    if (now - lastStepMs >= CFG_STEP_MS) {
        lastStepMs = now;
        servos.update();
    }

    // ── 3. Kích hoạt các thông báo đang chờ xử lý (ví dụ: DONE cho lệnh W) ──
    parser.tick();

    // ── 4. Web Server cleanup
    WebControl::tick();
}
