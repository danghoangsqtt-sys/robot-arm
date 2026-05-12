// =============================================================
//  main.cpp  –  Robotic arm controller entry point
//
//  Architecture
//  ┌───────────────────────────────────────────────────────┐
//  │  Serial RX  →  CmdParser  →  ServoCtrl  →  PCA9685  │
//  │                                  ↑                    │
//  │              millis() timer ─────┘  (motion update)  │
//  └───────────────────────────────────────────────────────┘
//
//  No RTOS tasks; everything runs cooperatively in loop().
//  The motion update fires every CFG_STEP_MS (default 20 ms).
// =============================================================
#include <Arduino.h>
#include "config.h"
#include "pca9685.h"
#include "servo_ctrl.h"
#include "cmd_parser.h"

// ── Module instances (static = no heap allocation) ──────────
static PCA9685   pca(CFG_PCA_ADDR);
static ServoCtrl servos(pca);
static CmdParser parser(servos);

static uint32_t lastStepMs = 0;

// ─────────────────────────────────────────────────────────────

void setup() {
    Serial.begin(CFG_BAUD);
    Serial.println(F("ARM INIT"));

    // Bring up I2C and PCA9685
    if (!pca.begin(CFG_SDA_PIN, CFG_SCL_PIN, CFG_I2C_FREQ)) {
        Serial.println(F("ERR:PCA9685"));
        // Halt – nothing else will work without the driver
        while (true) delay(1000);
    }
    pca.setPWMFreq(CFG_PWM_FREQ_HZ);

    // Drive all servos to home positions
    servos.begin();

    Serial.println(F("ARM READY"));
}

void loop() {
    // ── 1. Feed incoming serial bytes to the command parser ──
    while (Serial.available()) {
        parser.feed((char)Serial.read());
    }

    // ── 2. Advance servo motion on fixed timer ───────────────
    uint32_t now = millis();
    if (now - lastStepMs >= CFG_STEP_MS) {
        lastStepMs = now;
        servos.update();
    }

    // ── 3. Fire pending notifications (e.g. DONE for W cmd) ──
    parser.tick();
}
