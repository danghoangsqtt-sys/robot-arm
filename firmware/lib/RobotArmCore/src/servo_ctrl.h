// =============================================================
//  servo_ctrl.h  –  Bộ điều khiển chuyển động Servo
//
//  Quản lý trạng thái từng khớp và điều khiển chuyển động
//  nội suy mượt mà bằng cách nhích dần từ hiện tại → mục tiêu mỗi chu kỳ.
// =============================================================
#pragma once
#include "config.h"
#include "pca9685.h"

// Trạng thái thời gian thực của từng servo (kích thước nhỏ – cấu trúc packed)
struct ServoState {
    uint8_t current;    // vị trí hiện tại (độ)
    uint8_t target;     // vị trí mục tiêu (độ)
    uint8_t speed;      // kích thước bước nhảy (độ mỗi chu kỳ)
    bool    moving;     // true khi hiện tại != mục tiêu
} __attribute__((packed));

class ServoCtrl {
public:
    explicit ServoCtrl(PCA9685& pca);

    // Khởi tạo tất cả servo và đưa chúng về vị trí gốc (home)
    void begin();

    // ── Lệnh chuyển động ─────────────────────────────────────
    // Trả về false nếu id nằm ngoài phạm vi
    bool moveTo  (uint8_t id, uint8_t angle);
    bool setSpeed(uint8_t id, uint8_t degPerTick);
    void stopAll ();           // dừng mọi chuyển động (mục tiêu = hiện tại)
    void home    ();           // di chuyển tất cả các khớp về homeAng
    void homeOne (uint8_t id);

    // ── Truy vấn trạng thái ────────────────────────────────────────
    uint8_t getAngle (uint8_t id) const;
    uint8_t getTarget(uint8_t id) const;
    uint8_t getSpeed (uint8_t id) const;
    bool    isMoving (uint8_t id) const;
    bool    anyMoving()           const;

    // ── Được gọi bởi vòng lặp chính theo bộ đếm thời gian cố định ────────────────
    void update();

private:
    PCA9685&   _pca;
    ServoState _st[CFG_NUM_SERVOS];

    void     applyAngle  (uint8_t id, uint8_t angle);
    uint16_t angleToUs   (uint8_t id, uint8_t angle) const;
    bool     validId     (uint8_t id) const { return id < CFG_NUM_SERVOS; }
    uint8_t  clampAngle  (uint8_t id, uint8_t angle) const;
};
