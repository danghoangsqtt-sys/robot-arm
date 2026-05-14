#include "web_server.h"
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <LittleFS.h>
#include <RobotArmCore.h>

static AsyncWebServer server(80);
static AsyncWebSocket ws("/ws");
static CmdParser* globalParser = nullptr;

static void wsOutputHook(const char* msg) {
    ws.textAll(msg);
}

void onWsEvent(AsyncWebSocket * server, AsyncWebSocketClient * client, AwsEventType type, void * arg, uint8_t *data, size_t len){
    if(type == WS_EVT_CONNECT){
        Serial.printf("WS Client %u connected\n", client->id());
        client->text("ARM READY");
    } else if(type == WS_EVT_DISCONNECT){
        Serial.printf("WS Client %u disconnected\n", client->id());
    } else if(type == WS_EVT_DATA){
        AwsFrameInfo * info = (AwsFrameInfo*)arg;
        if(info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT){
            data[len] = 0;
            if(globalParser) {
                for(size_t i=0; i<len; i++) {
                    globalParser->feed((char)data[i]);
                }
                globalParser->feed('\n');
            }
        }
    }
}

namespace WebControl {
    void begin(CmdParser* parser) {
        globalParser = parser;
        globalParser->setOutputHook(wsOutputHook);

        if(!LittleFS.begin(true)){
            Serial.println(F("LittleFS Mount Failed"));
            return;
        }

        WiFi.mode(WIFI_AP_STA);
        WiFi.begin(CFG_WIFI_SSID, CFG_WIFI_PASS);
        WiFi.softAP("RobotArm-HUD", "12345678");

        ws.onEvent(onWsEvent);
        server.addHandler(&ws);
        server.serveStatic("/", LittleFS, "/").setDefaultFile("index.html");
        server.begin();
    }

    void tick() {
        ws.cleanupClients();
    }
}
