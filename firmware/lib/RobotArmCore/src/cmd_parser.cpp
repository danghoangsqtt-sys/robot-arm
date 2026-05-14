// =============================================================
//  cmd_parser.cpp  –  Triển khai bộ phân tích lệnh Serial
// =============================================================
#include "cmd_parser.h"
#include <Arduino.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

CmdParser::CmdParser(ServoCtrl& sc)
    : _sc(sc), _len(0), _waitDone(false) {}

// ── Các hàm Public (Public API) ───────────────────────────────────────────────

void CmdParser::feed(char c) {
    if (c == '\r') return;                    // bỏ qua CR (hỗ trợ \r\n)
    if (c == '\n') {
        _buf[_len] = '\0';
        if (_len > 0) process();
        _len = 0;
        return;
    }
    if (_len < CFG_RX_BUF - 1) {
        _buf[_len++] = c;
    }
    // âm thầm loại bỏ các byte tràn bộ đệm; bộ đệm sẽ reset vào lần xuống dòng tiếp theo
}

void CmdParser::tick() {
    if (_waitDone && !_sc.anyMoving()) {
        respond("DONE");
        _waitDone = false;
    }
}

// ── Phân phối lệnh ─────────────────────────────────────────

void CmdParser::process() {
    // Ký tự đầu tiên viết hoa = chữ cái lệnh
    // Phần văn bản còn lại sau dấu cách phân tách = chuỗi tham số
    char cmd = _buf[0];
    if (cmd >= 'a' && cmd <= 'z') cmd -= 32;   // chuyển thành chữ hoa, không phụ thuộc ctype

    // con trỏ tham số: bỏ qua ký tự lệnh và một dấu cách (nếu có)
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

// ── Các hàm xử lý lệnh ─────────────────────────────────────────

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
        while (*p == ' ') p++;            // bỏ qua khoảng trắng
        if (*p == '\0') { respondErr("ARGS"); return; }
        uint8_t angle = (uint8_t)strtol(p, &p, 10);
        _sc.moveTo(i, angle);             // việc giới hạn góc đã được xử lý trong moveTo
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

// H [id]   — không có tham số = home tất cả, có tham số = home một servo
void CmdParser::cmdHome(const char* args) {
    if (*args == '\0') {
        _sc.home();
    } else {
        uint8_t id = (uint8_t)strtol(args, nullptr, 10);
        _sc.homeOne(id);
    }
    respondOK();
}

// X — dừng mọi chuyển động ngay lập tức
void CmdParser::cmdStop() {
    _sc.stopAll();
    _waitDone = false;   // hủy mọi lệnh W đang chờ
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

// T — trạng thái tất cả các khớp
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

// I — in cấu hình từng servo (hữu ích cho việc khởi tạo GUI)
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

// W — phản hồi DONE khi (hoặc một khi) mọi chuyển động đã dừng
void CmdParser::cmdWait() {
    if (!_sc.anyMoving()) {
        respond("DONE");   // đã nhàn rỗi
    } else {
        _waitDone = true;  // sẽ được kích hoạt trong tick()
    }
}

// ── Các hàm hỗ trợ phản hồi ─────────────────────────────────────────

void CmdParser::respond(const char* msg) {
    Serial.println(msg);
    if (_hook) _hook(msg);
}

void CmdParser::respondOK() {
    Serial.println(F("OK"));
    if (_hook) _hook("OK");
}

void CmdParser::respondErr(const char* reason) {
    Serial.print(F("ERR:"));
    Serial.println(reason);
    if (_hook) {
        char buf[32];
        snprintf(buf, sizeof(buf), "ERR:%s", reason);
        _hook(buf);
    }
}
