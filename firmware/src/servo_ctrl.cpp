// =============================================================
//  servo_ctrl.cpp  –  Servo motion controller implementation
// =============================================================
#include <Arduino.h>
#include "servo_ctrl.h"

ServoCtrl::ServoCtrl(PCA9685& pca) : _pca(pca) {}

// ── Public API ───────────────────────────────────────────────

void ServoCtrl::begin() {
    for (uint8_t i = 0; i < CFG_NUM_SERVOS; i++) {
        _st[i].speed   = SERVO_TABLE[i].defSpeed;
        _st[i].current = SERVO_TABLE[i].homeAng;
        _st[i].target  = SERVO_TABLE[i].homeAng;
        _st[i].moving  = false;
        applyAngle(i, _st[i].current);
        delay(30);   // stagger startup to limit inrush current
    }
}

bool ServoCtrl::moveTo(uint8_t id, uint8_t angle) {
    if (!validId(id)) return false;
    _st[id].target = clampAngle(id, angle);
    _st[id].moving = (_st[id].current != _st[id].target);
    return true;
}

bool ServoCtrl::setSpeed(uint8_t id, uint8_t degPerTick) {
    if (!validId(id)) return false;
    if (degPerTick < 1)  degPerTick = 1;
    if (degPerTick > 20) degPerTick = 20;
    _st[id].speed = degPerTick;
    return true;
}

void ServoCtrl::stopAll() {
    for (uint8_t i = 0; i < CFG_NUM_SERVOS; i++) {
        _st[i].target = _st[i].current;
        _st[i].moving = false;
    }
}

void ServoCtrl::home() {
    for (uint8_t i = 0; i < CFG_NUM_SERVOS; i++) homeOne(i);
}

void ServoCtrl::homeOne(uint8_t id) {
    if (validId(id)) moveTo(id, SERVO_TABLE[id].homeAng);
}

uint8_t ServoCtrl::getAngle (uint8_t id) const { return validId(id) ? _st[id].current : 0; }
uint8_t ServoCtrl::getTarget(uint8_t id) const { return validId(id) ? _st[id].target  : 0; }
uint8_t ServoCtrl::getSpeed (uint8_t id) const { return validId(id) ? _st[id].speed   : 0; }
bool    ServoCtrl::isMoving (uint8_t id) const { return validId(id) && _st[id].moving;      }

bool ServoCtrl::anyMoving() const {
    for (uint8_t i = 0; i < CFG_NUM_SERVOS; i++)
        if (_st[i].moving) return true;
    return false;
}

// ── Motion update (call on fixed timer) ─────────────────────

void ServoCtrl::update() {
    for (uint8_t i = 0; i < CFG_NUM_SERVOS; i++) {
        ServoState& s = _st[i];
        if (!s.moving) continue;

        int16_t diff = (int16_t)s.target - (int16_t)s.current;

        // Check if we can reach target in this step
        if ((diff > 0 ? diff : -diff) <= (int16_t)s.speed) {
            s.current = s.target;
            s.moving  = false;
        } else {
            s.current = (uint8_t)((int16_t)s.current + (diff > 0 ? s.speed : -(int8_t)s.speed));
        }

        applyAngle(i, s.current);
    }
}

// ── Private helpers ──────────────────────────────────────────

void ServoCtrl::applyAngle(uint8_t id, uint8_t angle) {
    _pca.setPulseUs(SERVO_TABLE[id].ch, angleToUs(id, angle));
}

uint16_t ServoCtrl::angleToUs(uint8_t id, uint8_t angle) const {
    const ServoDef& d = SERVO_TABLE[id];
    // Linear map:  us = minUs + (angle - minAng) * (maxUs - minUs) / (maxAng - minAng)
    uint16_t rangeAng = d.maxAng - d.minAng;
    uint16_t rangeUs  = d.maxUs  - d.minUs;
    return d.minUs + (uint16_t)(((uint32_t)(angle - d.minAng) * rangeUs + rangeAng / 2) / rangeAng);
}

uint8_t ServoCtrl::clampAngle(uint8_t id, uint8_t angle) const {
    const ServoDef& d = SERVO_TABLE[id];
    if (angle < d.minAng) return d.minAng;
    if (angle > d.maxAng) return d.maxAng;
    return angle;
}
