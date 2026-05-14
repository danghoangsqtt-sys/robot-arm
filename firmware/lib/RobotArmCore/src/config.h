// =============================================================
//  config.h  –  Nguồn dữ liệu duy nhất cho tất cả các thông số
//  Chỉnh sửa file này để điều chỉnh firmware cho phù hợp với phần cứng.
// =============================================================
#pragma once
#include <stdint.h>

// ── Kênh giao tiếp I2C ──────────────────────────────────────────────────
#define CFG_SDA_PIN      21
#define CFG_SCL_PIN      22
#define CFG_I2C_FREQ     400000UL   // 400 kHz (chế độ nhanh)

// ── PCA9685 ──────────────────────────────────────────────────
#define CFG_PCA_ADDR     0x40       // địa chỉ I2C mặc định (A0-A5 = GND)
#define CFG_PWM_FREQ_HZ  50         // tần số băm xung (PWM) của servo

// ── UART ─────────────────────────────────────────────────────
#define CFG_BAUD         115200
#define CFG_RX_BUF       64         // độ dài tối đa của lệnh (byte)

// ── WiFi ─────────────────────────────────────────────────────
#define CFG_WIFI_SSID    "RobotArm_Network"
#define CFG_WIFI_PASS    "12345678"

// ── Cánh tay robot ──────────────────────────────────────────────────────
#define CFG_NUM_SERVOS   6

// ── Chuyển động ───────────────────────────────────────────────────
//  Sau mỗi chu kỳ, servo sẽ nhích 'speed' độ về phía góc mục tiêu.
//  Giảm CFG_STEP_MS để chuyển động mượt hơn (nhưng sẽ tốn CPU).
#define CFG_STEP_MS      20         // chu kỳ cập nhật chuyển động (ms)

// =============================================================
//  Cấu trúc dữ liệu Servo
//  Mỗi cấu trúc tương ứng với một servo trong bảng SERVO_TABLE.
// =============================================================
struct ServoDef {
    uint8_t  ch;        // Kênh đầu ra PCA9685 (0-15)
    uint8_t  minAng;    // Giới hạn góc quay tối thiểu (độ)
    uint8_t  maxAng;    // Giới hạn góc quay tối đa (độ)
    uint8_t  homeAng;   // Góc khởi động / lệnh HOME
    uint16_t minUs;     // Độ rộng xung ở góc tối thiểu (µs)
    uint16_t maxUs;     // Độ rộng xung ở góc tối đa (µs)
    uint8_t  defSpeed;  // Kích thước bước nhảy mặc định (độ / chu kỳ)
} __attribute__((packed));

// =============================================================
//  Bảng SERVO_TABLE  –  mỗi hàng là một khớp
//
//   kênh  góc_min  góc_max  home  minUs  maxUs  tốc_độ
// =============================================================
static const ServoDef SERVO_TABLE[CFG_NUM_SERVOS] = {
    {  0,   0,  180,   90,   500,  2500,    1 },  // J0 – xoay đế
    {  1,  70,  150,   70,   150,  1500,    1 },  // J1 – vai
    {  2,   0,  150,   90,   500,  2500,    1 },  // J2 – khuỷu tay
    {  3,   0,  180,   90,   500,  2500,    1 },  // J3 – gập/duỗi cổ tay
    {  4,   0,  180,   90,   500,  2500,    1 },  // J4 – xoay cổ tay
    {  5,   60, 120,   90,   500,  2500,    1 },  // J5 – kẹp (0=mở, 90=đóng)
};
