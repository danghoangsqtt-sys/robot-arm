// =============================================================
//  pca9685.cpp  –  Triển khai các hàm của driver PCA9685
// =============================================================
#include "pca9685.h"
#include <Wire.h>

// ── Bản đồ thanh ghi (Register map) ─────────────────────────────────────────────
#define REG_MODE1       0x00
#define REG_MODE2       0x01
#define REG_LED0_ON_L   0x06   // thanh ghi của kênh đầu tiên (4 byte/kênh)
#define REG_ALL_ON_L    0xFA   // gửi broadcast tới tất cả các kênh
#define REG_PRESCALE    0xFE

// Các mask bit của MODE1
#define M1_RESTART      0x80
#define M1_AI           0x20   // tự động tăng con trỏ thanh ghi
#define M1_SLEEP        0x10

// ── Hằng số (Constants) ────────────────────────────────────────────────
#define PCA_OSC_HZ      25000000UL  // bộ dao động nội (25 MHz)
#define PWM_STEPS       4096UL      // độ phân giải 12-bit
#define PERIOD_US       20000UL     // 50 Hz → chu kỳ 20 ms

// ─────────────────────────────────────────────────────────────

PCA9685::PCA9685(uint8_t addr) : _addr(addr) {}

bool PCA9685::begin(uint8_t sda, uint8_t scl, uint32_t i2cFreqHz) {
    Wire.begin(sda, scl, i2cFreqHz);

    // Reset về trạng thái xác định: ngủ + tự động tăng thanh ghi
    writeReg(REG_MODE1, M1_SLEEP | M1_AI);
    writeReg(REG_MODE2, 0x04);   // thay đổi trạng thái đầu ra khi STOP, kiểu totem-pole

    return (readReg(REG_MODE1) & M1_SLEEP);   // trả về true nếu chip phản hồi
}

void PCA9685::setPWMFreq(uint16_t freqHz) {
    // prescale = round(OSC / (4096 * freq)) - 1
    uint32_t denom = PWM_STEPS * (uint32_t)freqHz;
    uint8_t  pre   = (uint8_t)((PCA_OSC_HZ + denom / 2) / denom) - 1;

    uint8_t mode = readReg(REG_MODE1);

    // 1. Đưa chip vào trạng thái ngủ (bắt buộc trước khi đổi bộ chia tần số)
    writeReg(REG_MODE1, (mode & ~M1_RESTART) | M1_SLEEP);

    // 2. Thiết lập bộ chia tần số (chỉ có thể ghi khi SLEEP = 1)
    writeReg(REG_PRESCALE, pre);

    // 3. Xóa bit SLEEP để khởi động lại bộ dao động
    writeReg(REG_MODE1, mode & ~M1_SLEEP);

    // 4. Theo datasheet: chờ ≥ 500 µs để bộ dao động ổn định trước khi RESTART
    delayMicroseconds(500);

    // 5. Thiết lập RESTART (SLEEP phải bằng 0 trước đó – đây là một lỗi thường gặp)
    writeReg(REG_MODE1, (mode & ~M1_SLEEP) | M1_RESTART | M1_AI);
}

void PCA9685::setChannel(uint8_t ch, uint16_t onTick, uint16_t offTick) {
    uint8_t reg = REG_LED0_ON_L + (ch * 4);
    Wire.beginTransmission(_addr);
    Wire.write(reg);
    Wire.write( onTick & 0xFF);
    Wire.write( onTick >> 8  );
    Wire.write(offTick & 0xFF);
    Wire.write(offTick >> 8  );
    Wire.endTransmission();
}

void PCA9685::setPulseUs(uint8_t ch, uint16_t us) {
    // số đếm (counts) = us * 4096 / 20000 (được làm tròn)
    uint16_t counts = (uint16_t)(((uint32_t)us * PWM_STEPS + PERIOD_US / 2) / PERIOD_US);
    setChannel(ch, 0, counts);
}

void PCA9685::sleep() {
    writeReg(REG_MODE1, readReg(REG_MODE1) | M1_SLEEP);
}

void PCA9685::wake() {
    uint8_t m = readReg(REG_MODE1) & ~M1_SLEEP;
    writeReg(REG_MODE1, m);
    delayMicroseconds(500);
    writeReg(REG_MODE1, m | M1_RESTART);
}

// ── Các hàm hỗ trợ nội bộ (Private helpers) ──────────────────────────────────────────

void PCA9685::writeReg(uint8_t reg, uint8_t val) {
    Wire.beginTransmission(_addr);
    Wire.write(reg);
    Wire.write(val);
    Wire.endTransmission();
}

uint8_t PCA9685::readReg(uint8_t reg) {
    Wire.beginTransmission(_addr);
    Wire.write(reg);
    Wire.endTransmission(false);                 // khởi động lại (repeated start)
    Wire.requestFrom(_addr, (uint8_t)1);
    return Wire.available() ? Wire.read() : 0;
}
