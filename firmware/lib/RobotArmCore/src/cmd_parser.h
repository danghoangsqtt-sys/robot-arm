// =============================================================
// =============================================================
//  cmd_parser.h  –  Bộ phân tích lệnh Serial
//
//  Giao thức ASCII, kết thúc lệnh bằng ký tự xuống dòng.
//
//  TÀI LIỆU LỆNH
//  ─────────────────────────────────────────────────────────────
//  Lệnh             Tham số              Mô tả
//  ─────────────────────────────────────────────────────────────
//  M <id> <ang>     id=0-5, ang=0-180    Di chuyển một servo
//  A <a0..a5>       6 góc cách nhau      Di chuyển tất cả servo
//  S <id> <spd>     id=0-5, spd=1-20    Cài đặt tốc độ (độ/chu kỳ)
//  H                –                    Đưa tất cả servo về gốc (home)
//  H <id>           id=0-5               Đưa một servo về gốc (home)
//  X                –                    Dừng mọi chuyển động
//  G <id>           id=0-5               Lấy góc hiện tại
//  T                –                    Trạng thái: tất cả các góc
//  I                –                    Thông tin: cấu hình toàn bộ
//  W                –                    Chờ; trả về DONE khi nhàn rỗi
//  ─────────────────────────────────────────────────────────────
//
//  TÀI LIỆU PHẢN HỒI
//  ─────────────────────────────────────────────────────────────
//  OK                         Đã chấp nhận lệnh
//  ERR:<lý do>                Lỗi (ID, ARGS, RANGE)
//  VAL:<id>:<góc>             Góc của một servo
//  STA:<a0>,<a1>,...,<a5>     Tất cả góc của servo
//  CFG:<id>:<min>,<max>,<home>,<spd>  Cấu hình của từng servo
//  DONE                       Đã hoàn thành di chuyển (phản hồi cho W)
//  ─────────────────────────────────────────────────────────────
// =============================================================
#pragma once
#include "servo_ctrl.h"

typedef void (*OutputHook)(const char* msg);

class CmdParser {
public:
    explicit CmdParser(ServoCtrl& sc);

    void feed(char c);   // đưa vào một byte dữ liệu nhận được
    void tick();         // gọi ở mỗi loop() – xử lý thông báo DONE

private:
    ServoCtrl& _sc;
    char       _buf[CFG_RX_BUF];
    uint8_t    _len;
    bool       _waitDone;  // true trong lúc chờ di chuyển hoàn tất
    OutputHook _hook = nullptr;

    void setOutputHook(OutputHook hook) { _hook = hook; }

    void process();

    // Các hàm xử lý lệnh
    void cmdMove  (const char* args);
    void cmdAll   (const char* args);
    void cmdSpeed (const char* args);
    void cmdHome  (const char* args);
    void cmdStop  ();
    void cmdGet   (const char* args);
    void cmdStatus();
    void cmdInfo  ();
    void cmdWait  ();

    // Các hàm hỗ trợ phản hồi (dùng F() để lưu chuỗi trong flash)
    void respond   (const char* msg);
    void respondOK ();
    void respondErr(const char* reason);
};
