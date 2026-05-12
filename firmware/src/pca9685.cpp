// =============================================================
//  pca9685.cpp  –  PCA9685 driver implementation
// =============================================================
#include "pca9685.h"
#include <Wire.h>

// ── Register map ─────────────────────────────────────────────
#define REG_MODE1       0x00
#define REG_MODE2       0x01
#define REG_LED0_ON_L   0x06   // first channel register (4 bytes/ch)
#define REG_ALL_ON_L    0xFA   // broadcast to all channels
#define REG_PRESCALE    0xFE

// MODE1 bit masks
#define M1_RESTART      0x80
#define M1_AI           0x20   // auto-increment register pointer
#define M1_SLEEP        0x10

// ── Constants ────────────────────────────────────────────────
#define PCA_OSC_HZ      25000000UL  // internal oscillator (25 MHz)
#define PWM_STEPS       4096UL      // 12-bit resolution
#define PERIOD_US       20000UL     // 50 Hz → 20 ms period

// ─────────────────────────────────────────────────────────────

PCA9685::PCA9685(uint8_t addr) : _addr(addr) {}

bool PCA9685::begin(uint8_t sda, uint8_t scl, uint32_t i2cFreqHz) {
    Wire.begin(sda, scl, i2cFreqHz);

    // Reset to known state: sleep + auto-increment
    writeReg(REG_MODE1, M1_SLEEP | M1_AI);
    writeReg(REG_MODE2, 0x04);   // output change on STOP, totem-pole

    return (readReg(REG_MODE1) & M1_SLEEP);   // true if chip responded
}

void PCA9685::setPWMFreq(uint16_t freqHz) {
    // prescale = round(OSC / (4096 * freq)) - 1
    uint32_t denom = PWM_STEPS * (uint32_t)freqHz;
    uint8_t  pre   = (uint8_t)((PCA_OSC_HZ + denom / 2) / denom) - 1;

    uint8_t mode = readReg(REG_MODE1);

    // 1. Put chip to sleep (required before changing prescaler)
    writeReg(REG_MODE1, (mode & ~M1_RESTART) | M1_SLEEP);

    // 2. Set prescaler (only writable while SLEEP = 1)
    writeReg(REG_PRESCALE, pre);

    // 3. Clear SLEEP to start the oscillator
    writeReg(REG_MODE1, mode & ~M1_SLEEP);

    // 4. Datasheet: wait ≥ 500 µs for oscillator to stabilise before RESTART
    delayMicroseconds(500);

    // 5. Set RESTART (SLEEP must be 0 first – this was the bug)
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
    // counts = us * 4096 / 20000  (rounded)
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

// ── Private helpers ──────────────────────────────────────────

void PCA9685::writeReg(uint8_t reg, uint8_t val) {
    Wire.beginTransmission(_addr);
    Wire.write(reg);
    Wire.write(val);
    Wire.endTransmission();
}

uint8_t PCA9685::readReg(uint8_t reg) {
    Wire.beginTransmission(_addr);
    Wire.write(reg);
    Wire.endTransmission(false);                 // repeated start
    Wire.requestFrom(_addr, (uint8_t)1);
    return Wire.available() ? Wire.read() : 0;
}
