// =============================================================
//  cmd_parser.cpp  –  Serial command parser implementation
// =============================================================
#include "cmd_parser.h"
#include <Arduino.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

CmdParser::CmdParser(ServoCtrl& sc)
    : _sc(sc), _len(0), _waitDone(false) {}

// ── Public API ───────────────────────────────────────────────

void CmdParser::feed(char c) {
    if (c == '\r') return;                    // ignore CR (handles \r\n)
    if (c == '\n') {
        _buf[_len] = '\0';
        if (_len > 0) process();
        _len = 0;
        return;
    }
    if (_len < CFG_RX_BUF - 1) {
        _buf[_len++] = c;
    }
    // silently drop overflow bytes; buffer resets on next newline
}

void CmdParser::tick() {
    if (_waitDone && !_sc.anyMoving()) {
        respond("DONE");
        _waitDone = false;
    }
}

// ── Command dispatch ─────────────────────────────────────────

void CmdParser::process() {
    // Upper-case first char = command letter
    // Remaining text after the separating space = args string
    char cmd = _buf[0];
    if (cmd >= 'a' && cmd <= 'z') cmd -= 32;   // to upper, no ctype dep

    // args pointer: skip command char and optional space
    const char* args = (_len > 1) ? _buf + 2 : _buf + 1;
    if (_len <= 1) args = "";

    switch (cmd) {
        case 'M': cmdMove (args); break;
        case 'A': cmdAll  (args); break;
        case 'S': cmdSpeed(args); break;
        case 'H': cmdHome (args); break;
        case 'X': cmdStop ();     break;
        case 'G': cmdGet  (args); break;
        case 'T': cmdStatus();    break;
        case 'I': cmdInfo ();     break;
        case 'W': cmdWait ();     break;
        default:  respondErr("UNK"); break;
    }
}

// ── Command handlers ─────────────────────────────────────────

// M <id> <angle>
void CmdParser::cmdMove(const char* args) {
    char*   end;
    uint8_t id    = (uint8_t)strtol(args, &end, 10);
    uint8_t angle = (uint8_t)strtol(end,  nullptr, 10);
    _sc.moveTo(id, angle) ? respondOK() : respondErr("ID");
}

// A <a0> <a1> <a2> <a3> <a4> <a5>
void CmdParser::cmdAll(const char* args) {
    char* p = (char*)args;
    for (uint8_t i = 0; i < CFG_NUM_SERVOS; i++) {
        while (*p == ' ') p++;            // skip whitespace
        if (*p == '\0') { respondErr("ARGS"); return; }
        uint8_t angle = (uint8_t)strtol(p, &p, 10);
        _sc.moveTo(i, angle);             // clamping handled inside moveTo
    }
    respondOK();
}

// S <id> <speed>
void CmdParser::cmdSpeed(const char* args) {
    char*   end;
    uint8_t id    = (uint8_t)strtol(args, &end, 10);
    uint8_t speed = (uint8_t)strtol(end,  nullptr, 10);
    _sc.setSpeed(id, speed) ? respondOK() : respondErr("ID");
}

// H [id]   — no arg = home all, arg = home one
void CmdParser::cmdHome(const char* args) {
    if (*args == '\0') {
        _sc.home();
    } else {
        uint8_t id = (uint8_t)strtol(args, nullptr, 10);
        _sc.homeOne(id);
    }
    respondOK();
}

// X — stop all motion immediately
void CmdParser::cmdStop() {
    _sc.stopAll();
    _waitDone = false;   // cancel any pending W
    respondOK();
}

// G <id>
void CmdParser::cmdGet(const char* args) {
    uint8_t id = (uint8_t)strtol(args, nullptr, 10);
    if (id >= CFG_NUM_SERVOS) { respondErr("ID"); return; }
    char out[16];
    snprintf(out, sizeof(out), "VAL:%u:%u", id, _sc.getAngle(id));
    respond(out);
}

// T — status of all joints
void CmdParser::cmdStatus() {
    // STA:<a0>,<a1>,<a2>,<a3>,<a4>,<a5>
    char out[32];
    int  n = snprintf(out, sizeof(out), "STA:");
    for (uint8_t i = 0; i < CFG_NUM_SERVOS; i++) {
        if (i) out[n++] = ',';
        n += snprintf(out + n, sizeof(out) - n, "%u", _sc.getAngle(i));
    }
    respond(out);
}

// I — print per-servo config (useful for GUI initialisation)
void CmdParser::cmdInfo() {
    char out[40];
    for (uint8_t i = 0; i < CFG_NUM_SERVOS; i++) {
        const ServoDef& d = SERVO_TABLE[i];
        // CFG:<id>:<minAng>,<maxAng>,<homeAng>,<speed>
        snprintf(out, sizeof(out), "CFG:%u:%u,%u,%u,%u",
                 i, d.minAng, d.maxAng, d.homeAng, _sc.getSpeed(i));
        respond(out);
    }
    respondOK();
}

// W — reply DONE when (or once) all motion has stopped
void CmdParser::cmdWait() {
    if (!_sc.anyMoving()) {
        respond("DONE");   // already idle
    } else {
        _waitDone = true;  // will fire in tick()
    }
}

// ── Response helpers ─────────────────────────────────────────

void CmdParser::respond(const char* msg) {
    Serial.println(msg);
}

void CmdParser::respondOK() {
    Serial.println(F("OK"));
}

void CmdParser::respondErr(const char* reason) {
    Serial.print(F("ERR:"));
    Serial.println(reason);
}
