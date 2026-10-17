// Browser adaptation, not part of the original AssaultCube distribution.
#include "cube.h"
#include "bot/bot.h"
#include <emscripten.h>

int web_sound_starts = 0;
extern "C" {
EMSCRIPTEN_KEEPALIVE const char *ac_snapshot()
{
    static char data[2048];
    int count = 0, shots = 0;
    float bot_motion = 0;
    loopv(bots) if(bots[i]) { count++; bot_motion += bots[i]->o.x + 3*bots[i]->o.y; }
    loopi(NUMGUNS) shots += player1->pstatshots[i];
    snprintf(data, sizeof(data), "{\"x\":%.3f,\"y\":%.3f,\"z\":%.3f,\"yaw\":%.3f,\"pitch\":%.3f,\"health\":%d,\"state\":%d,\"mode\":%d,\"map_bytes\":%d,\"bots\":%d,\"bot_motion\":%.3f,\"shots\":%d,\"magazine\":%d,\"gun\":%d,\"sounds\":%d,\"millis\":%d,\"moving\":%d}",
        player1->o.x, player1->o.y, player1->o.z, player1->yaw, player1->pitch,
        player1->health, player1->state, gamemode, maploaded, count, bot_motion, shots,
        player1->mag[player1->gunselect], player1->gunselect, web_sound_starts, lastmillis, player1->move);
    return data;
}
EMSCRIPTEN_KEEPALIVE const char *ac_player_name() { return player1->name; }
EMSCRIPTEN_KEEPALIVE void ac_command(const char *command) { execute(command); }
EMSCRIPTEN_KEEPALIVE void ac_start_match()
{
    closemenu(NULL);
    execute("kickallbots");
    clearvote();
    callvote(SA_MAP, "ac_desert", "8", "0");
    execute("sleep 1000 [kickallbots; addnbot 3 random good]");
}
EMSCRIPTEN_KEEPALIVE void ac_write_settings() { writecfg(); }
EMSCRIPTEN_KEEPALIVE void ac_release_input()
{
    player1->move = player1->strafe = 0;
    player1->attacking = player1->jumpnext = false;
    player1->k_up = player1->k_down = player1->k_left = player1->k_right = false;
    // SDL focus events also release key state through the regular event loop.
}
}
