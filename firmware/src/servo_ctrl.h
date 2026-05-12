// =============================================================
//  servo_ctrl.h  –  Servo motion controller
//
//  Manages per-joint state and drives smooth interpolated
//  motion by stepping current → target each tick.
// =============================================================
#pragma once
#include "config.h"
#include "pca9685.h"

// Per-servo runtime state (kept small – packed struct)
struct ServoState {
    uint8_t current;    // current position (degrees)
    uint8_t target;     // target  position (degrees)
    uint8_t speed;      // step size (degrees per tick)
    bool    moving;     // true while current != target
} __attribute__((packed));

class ServoCtrl {
public:
    explicit ServoCtrl(PCA9685& pca);

    // Initialise all servos and drive them to home positions
    void begin();

    // ── Motion commands ─────────────────────────────────────
    // Returns false if id is out of range
    bool moveTo  (uint8_t id, uint8_t angle);
    bool setSpeed(uint8_t id, uint8_t degPerTick);
    void stopAll ();           // halt all motion (target = current)
    void home    ();           // move all joints to homeAng
    void homeOne (uint8_t id);

    // ── State queries ────────────────────────────────────────
    uint8_t getAngle (uint8_t id) const;
    uint8_t getTarget(uint8_t id) const;
    uint8_t getSpeed (uint8_t id) const;
    bool    isMoving (uint8_t id) const;
    bool    anyMoving()           const;

    // ── Called by main loop on a fixed timer ────────────────
    void update();

private:
    PCA9685&   _pca;
    ServoState _st[CFG_NUM_SERVOS];

    void     applyAngle  (uint8_t id, uint8_t angle);
    uint16_t angleToUs   (uint8_t id, uint8_t angle) const;
    bool     validId     (uint8_t id) const { return id < CFG_NUM_SERVOS; }
    uint8_t  clampAngle  (uint8_t id, uint8_t angle) const;
};
