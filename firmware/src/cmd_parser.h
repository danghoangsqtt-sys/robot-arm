// =============================================================
//  cmd_parser.h  –  Serial command parser
//
//  ASCII protocol, newline-terminated commands.
//
//  COMMAND REFERENCE
//  ─────────────────────────────────────────────────────────────
//  Command          Args                 Description
//  ─────────────────────────────────────────────────────────────
//  M <id> <ang>     id=0-5, ang=0-180    Move one servo
//  A <a0..a5>       six space-sep angles Move all servos
//  S <id> <spd>     id=0-5, spd=1-20    Set speed (deg/tick)
//  H                –                    Home all servos
//  H <id>           id=0-5               Home one servo
//  X                –                    Stop all motion
//  G <id>           id=0-5               Get current angle
//  T                –                    Status: all angles
//  I                –                    Info: all config
//  W                –                    Wait; replies DONE when idle
//  ─────────────────────────────────────────────────────────────
//
//  RESPONSE REFERENCE
//  ─────────────────────────────────────────────────────────────
//  OK                         Command accepted
//  ERR:<reason>               Error (ID, ARGS, RANGE)
//  VAL:<id>:<angle>           Single servo angle
//  STA:<a0>,<a1>,...,<a5>     All servo angles
//  CFG:<id>:<min>,<max>,<home>,<spd>  Per-servo config
//  DONE                       Motion complete (reply to W)
//  ─────────────────────────────────────────────────────────────
// =============================================================
#pragma once
#include "servo_ctrl.h"

class CmdParser {
public:
    explicit CmdParser(ServoCtrl& sc);

    void feed(char c);   // push one received byte
    void tick();         // call every loop() – drives DONE notification

private:
    ServoCtrl& _sc;
    char       _buf[CFG_RX_BUF];
    uint8_t    _len;
    bool       _waitDone;  // true while waiting for motion to complete

    void process();

    // Command handlers
    void cmdMove  (const char* args);
    void cmdAll   (const char* args);
    void cmdSpeed (const char* args);
    void cmdHome  (const char* args);
    void cmdStop  ();
    void cmdGet   (const char* args);
    void cmdStatus();
    void cmdInfo  ();
    void cmdWait  ();

    // Response helpers  (use F() to keep strings in flash)
    void respond   (const char* msg);
    void respondOK ();
    void respondErr(const char* reason);
};
