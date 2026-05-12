// =============================================================
//  config.h  –  Single source of truth for all parameters
//  Edit this file to adapt the firmware to your hardware.
// =============================================================
#pragma once
#include <stdint.h>

// ── I2C bus ──────────────────────────────────────────────────
#define CFG_SDA_PIN      21
#define CFG_SCL_PIN      22
#define CFG_I2C_FREQ     400000UL   // 400 kHz fast-mode

// ── PCA9685 ──────────────────────────────────────────────────
#define CFG_PCA_ADDR     0x40       // default I2C address (A0-A5 = GND)
#define CFG_PWM_FREQ_HZ  50         // servo PWM frequency

// ── UART ─────────────────────────────────────────────────────
#define CFG_BAUD         115200
#define CFG_RX_BUF       64         // max command length (bytes)

// ── Arm ──────────────────────────────────────────────────────
#define CFG_NUM_SERVOS   6

// ── Motion ───────────────────────────────────────────────────
//  Each tick the servo steps 'speed' degrees toward the target.
//  Reduce CFG_STEP_MS for smoother motion (costs CPU).
#define CFG_STEP_MS      20         // motion update interval (ms)

// =============================================================
//  Servo descriptor
//  One entry per servo in SERVO_TABLE below.
// =============================================================
struct ServoDef {
    uint8_t  ch;        // PCA9685 output channel (0-15)
    uint8_t  minAng;    // mechanical minimum angle (degrees)
    uint8_t  maxAng;    // mechanical maximum angle (degrees)
    uint8_t  homeAng;   // angle at power-on / HOME command
    uint16_t minUs;     // pulse width at minAng (µs)
    uint16_t maxUs;     // pulse width at maxAng (µs)
    uint8_t  defSpeed;  // default step size (degrees / tick)
} __attribute__((packed));

// =============================================================
//  SERVO_TABLE  –  one row per joint
//
//   ch   minA  maxA  home  minUs  maxUs  speed
// =============================================================
static const ServoDef SERVO_TABLE[CFG_NUM_SERVOS] = {
    {  0,   0,  180,   90,   500,  2500,    1 },  // J0 – base rotation
    {  1,  70,  150,   70,   150,  1500,    1 },  // J1 – shoulder
    {  2,   0,  150,   90,   500,  2500,    1 },  // J2 – elbow
    {  3,   0,  180,   90,   500,  2500,    1 },  // J3 – wrist pitch
    {  4,   0,  180,   90,   500,  2500,    1 },  // J4 – wrist roll
    {  5,   60, 120,   90,   500,  2500,    1 },  // J5 – gripper (0=open, 90=closed)
};
