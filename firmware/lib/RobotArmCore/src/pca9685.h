// =============================================================
//  pca9685.h  –  Driver điều khiển băm xung (PWM) 16 kênh PCA9685 gọn nhẹ
//  Giao tiếp trực tiếp qua thư viện Wire; không phụ thuộc thư viện Adafruit.
// =============================================================
#pragma once
#include <stdint.h>

class PCA9685 {
public:
    explicit PCA9685(uint8_t addr = 0x40);

    // Gọi một lần trong hàm setup()
    bool begin(uint8_t sda, uint8_t scl, uint32_t i2cFreqHz);

    // Thiết lập tần số PWM đầu ra cho tất cả các kênh (gọi trước hàm setChannel)
    void setPWMFreq(uint16_t freqHz);

    // Cấp thấp: thiết lập số tick BẬT và TẮT (0-4095) cho một kênh
    void setChannel(uint8_t ch, uint16_t onTick, uint16_t offTick);

    // Cấp cao: thiết lập độ rộng xung tính bằng micro-giây cho một kênh
    void setPulseUs(uint8_t ch, uint16_t us);

    // Quản lý năng lượng
    void sleep();
    void wake();

private:
    uint8_t _addr;

    void    writeReg(uint8_t reg, uint8_t val);
    uint8_t readReg (uint8_t reg);
};
