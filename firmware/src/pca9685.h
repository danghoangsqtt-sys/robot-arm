// =============================================================
//  pca9685.h  –  Lightweight PCA9685 16-channel PWM driver
//  Talks directly to Wire; no Adafruit dependency.
// =============================================================
#pragma once
#include <stdint.h>

class PCA9685 {
public:
    explicit PCA9685(uint8_t addr = 0x40);

    // Call once in setup()
    bool begin(uint8_t sda, uint8_t scl, uint32_t i2cFreqHz);

    // Set output PWM frequency for all channels (call before setChannel)
    void setPWMFreq(uint16_t freqHz);

    // Low-level: set ON and OFF tick counts (0-4095) for one channel
    void setChannel(uint8_t ch, uint16_t onTick, uint16_t offTick);

    // High-level: set pulse width in microseconds for one channel
    void setPulseUs(uint8_t ch, uint16_t us);

    // Power management
    void sleep();
    void wake();

private:
    uint8_t _addr;

    void    writeReg(uint8_t reg, uint8_t val);
    uint8_t readReg (uint8_t reg);
};
