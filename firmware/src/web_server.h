#pragma once

#include <Arduino.h>
#include <RobotArmCore.h>

namespace WebControl {
    void begin(CmdParser* parser);
    void tick();
}
