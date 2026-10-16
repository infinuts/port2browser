/* Original MIT-licensed fixture. One scene, no external assets. */
#include <SDL.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#define API EMSCRIPTEN_KEEPALIVE
#else
#define API
#endif
static SDL_Window *window;
static SDL_Renderer *renderer;
static SDL_AudioDeviceID audio;
static int x = 24, collected, started, sounds, saving, saves, running = 1;
static char save_path[2048];
API int game_x(void) { return x; }
API int game_collected(void) { return collected; }
API int game_sounds(void) { return sounds; }
API int game_saves(void) { return saves; }
API int game_saving(void) { return saving; }
API int game_started(void) { return started; }
API int game_queued(void) { return (int)SDL_GetQueuedAudioSize(audio); }
API void game_save_complete(int failed) { saving = failed ? -1 : 0; if (!failed) ++saves; }
static void load(void) {
    FILE *file = fopen(save_path, "r");
    int saved_x, saved_collected;
    if (!file) return;
    if (fscanf(file, "%d %d", &saved_x, &saved_collected) == 2 &&
        saved_x >= 0 && saved_x <= 288 && (saved_collected == 0 || saved_collected == 1)) {
        x = saved_x; collected = saved_collected;
    }
    fclose(file);
}
static void save(void) {
    FILE *file = fopen(save_path, "w");
    saving = 1;
    if (!file) { saving = -1; return; }
    int written = fprintf(file, "%d %d\n", x, collected);
    int closed = fclose(file);
    if (written < 0 || closed != 0) { saving = -1; return; }
#ifdef __EMSCRIPTEN__
    EM_ASM({ FS.syncfs(false, function(error) { Module._game_save_complete(error ? 1 : 0); }); });
#else
    game_save_complete(0);
#endif
}
API void game_start(void) {
    started = 1;
    SDL_PauseAudioDevice(audio, 0);
}
static void sound(void) {
    float samples[12000];
    for (int i = 0; i < 12000; ++i)
        samples[i] = (float)(0.15 * sin(2.0 * 3.141592653589793 * 440.0 * i / 48000.0));
    if (SDL_QueueAudio(audio, samples, sizeof(samples)) == 0) ++sounds;
}
static void key(SDL_Keycode code) {
    if (!started) return;
    if (code == SDLK_RIGHT && x < 288) x += 12;
    if (code == SDLK_LEFT && x > 0) x -= 12;
    if (code == SDLK_SPACE && abs(x - 120) <= 12 && !collected) {
        collected = 1; sound();
    }
    if (code == SDLK_s && saving != 1) save();
}
static void frame(void) {
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        if (event.type == SDL_QUIT) running = 0;
        if (event.type == SDL_KEYDOWN && !event.key.repeat) {
            if (event.key.keysym.sym == SDLK_RETURN) game_start();
            else key(event.key.keysym.sym);
        }
    }
    SDL_SetRenderDrawColor(renderer, 15, 23, 42, 255); SDL_RenderClear(renderer);
    SDL_Rect beacon = {120, 64, 24, 24}, player = {x, 100, 24, 24};
    SDL_SetRenderDrawColor(renderer, collected ? 30 : 255, collected ? 180 : 190, 60, 255);
    SDL_RenderFillRect(renderer, &beacon);
    SDL_SetRenderDrawColor(renderer, 56, 189, 248, 255); SDL_RenderFillRect(renderer, &player);
    SDL_RenderPresent(renderer);
}
int main(int argc, char **argv) {
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO) != 0) { fprintf(stderr, "%s\n", SDL_GetError()); return 1; }
    window = SDL_CreateWindow("Beacon: Enter starts, arrows move, Space collects, S saves", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, 320, 180, 0);
    renderer = window ? SDL_CreateRenderer(window, -1, SDL_RENDERER_SOFTWARE) : NULL;
    SDL_AudioSpec desired = {0};
    desired.freq = 48000; desired.format = AUDIO_F32SYS; desired.channels = 1; desired.samples = 1024;
    audio = SDL_OpenAudioDevice(NULL, 0, &desired, NULL, 0);
    if (!renderer || !audio) { fprintf(stderr, "%s\n", SDL_GetError()); return 1; }
#ifdef __EMSCRIPTEN__
    snprintf(save_path, sizeof(save_path), "/saves/beacon.txt");
#else
    const char *override = getenv("P2B_SAVE_PATH");
    char *pref = SDL_GetPrefPath("port2browser", "beacon");
    if (!override && !pref) return 1;
    snprintf(save_path, sizeof(save_path), "%s%s", override ? override : pref, override ? "" : "beacon.txt");
    SDL_free(pref);
#endif
    load();
#ifndef __EMSCRIPTEN__
    if (argc == 2 && strcmp(argv[1], "--smoke") == 0) {
        x = 24; collected = 0; game_start();
        for (int i = 0; i < 8; ++i) key(SDLK_RIGHT);
        key(SDLK_SPACE); key(SDLK_s); frame();
        if (x != 120 || !collected || sounds != 1 || saving != 0) return 2;
        x = 0; collected = 0; load();
        if (x != 120 || !collected) return 3;
        puts("native smoke: movement, interaction, PCM queue, save/load passed");
        running = 0;
    }
    while (running) { frame(); SDL_Delay(16); }
    SDL_CloseAudioDevice(audio); SDL_DestroyRenderer(renderer); SDL_DestroyWindow(window); SDL_Quit();
#else
    (void)argc; (void)argv;
    emscripten_set_main_loop(frame, 0, 1);
#endif
    return 0;
}
