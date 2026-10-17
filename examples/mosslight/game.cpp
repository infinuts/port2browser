// Original MIT game. All artwork and audio are generated here; no asset downloads.
#include <SDL.h>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#define API extern "C" EMSCRIPTEN_KEEPALIVE
#else
#define API extern "C"
#endif
static SDL_Window* window;
static SDL_Renderer* renderer;
static SDL_AudioDeviceID audio;
static int x=2,y=11,mask=0,health=3,steps=0,won=0,started=0,sounds=0,saves=0,saving=0,running=1;
static float px=80,py=368,clock_s=0,repeat_s=0;
static bool held[4]={false,false,false,false};
static char save_path[2048];
static const int cores[3][2]={{5,11},{12,4},{20,10}};
static const int walls[][2]={{7,8},{8,8},{9,8},{16,7},{17,7},{18,7},{6,5},{7,5},{8,5},{9,5},{17,2},{17,3},{3,2},{4,2},{5,2},{4,7},{14,10},{15,10},{16,10},{11,2},{12,2},{13,2},{3,9},{10,12},{11,12},{18,11}};
static bool wall(int a,int b){
    if(a<1||a>22||b<1||b>12)return true;
    for(const auto& w:walls)if(w[0]==a&&w[1]==b)return true;
    return false;
}
static bool thorn(int a,int b){return (a==8&&b==11)||(a==10&&b==7)||(a==18&&b==5);}
API int run_x(){return x;} API int run_y(){return y;} API int run_mask(){return mask;}
API int run_health(){return health;} API int run_steps(){return steps;} API int run_won(){return won;}
API int run_started(){return started;} API int run_sounds(){return sounds;} API int run_saves(){return saves;}
API int run_saving(){return saving;} API int run_queued(){return static_cast<int>(SDL_GetQueuedAudioSize(audio));}
API void run_save_complete(int failed){saving=failed?-1:0;if(!failed)++saves;}
static void tone(float hz){
    float pcm[9600];for(int i=0;i<9600;i++){float t=i/48000.f;pcm[i]=.12f*std::sin(6.2831853f*hz*t)*std::exp(-14.f*t);}
    if(SDL_QueueAudio(audio,pcm,sizeof(pcm))==0)++sounds;
}
static void load(){
    FILE* f=std::fopen(save_path,"r");if(!f)return;
    int a,b,c,d,e,g;char version[24];
    if(std::fscanf(f,"%23s %d %d %d %d %d %d",version,&a,&b,&c,&d,&e,&g)==7&&std::strcmp(version,"MOSSLIGHT_1")==0&&
       !wall(a,b)&&!thorn(a,b)&&c>=0&&c<=7&&d>=1&&d<=3&&e>=0&&e<=1000000&&g>=0&&g<=1&&(!g||c==7)){
        x=a;y=b;mask=c;health=d;steps=e;won=g;
    }
    std::fclose(f);px=x*32.f+16;py=y*32.f+16;
}
static void save(){
    saving=1;FILE* f=std::fopen(save_path,"w");if(!f){saving=-1;return;}
    int n=std::fprintf(f,"MOSSLIGHT_1 %d %d %d %d %d %d\n",x,y,mask,health,steps,won);int closed=std::fclose(f);
    if(n<0||closed){saving=-1;return;}
#ifdef __EMSCRIPTEN__
    EM_ASM({FS.syncfs(false,error=>Module._run_save_complete(error?1:0));});
#else
    run_save_complete(0);
#endif
}
API void run_start(){started=1;SDL_PauseAudioDevice(audio,0);}
API void run_reset(){if(saving==1)return;x=2;y=11;mask=0;health=3;steps=0;won=0;px=80;py=368;std::memset(held,0,sizeof(held));save();}
static void move(int dx,int dy){
    if(!started||won||wall(x+dx,y+dy))return;
    x+=dx;y+=dy;steps++;if(steps>1000000)steps=1000000;
    if(thorn(x,y)){tone(130);health--;if(health<1)health=3;x=2;y=11;px=80;py=368;std::memset(held,0,sizeof(held));}
}
static void interact(){
    if(!started||won)return;
    for(int i=0;i<3;i++)if(!(mask&(1<<i))&&std::abs(x-cores[i][0])+std::abs(y-cores[i][1])<=1){mask|=1<<i;tone(440.f+i*165.f);return;}
    if(mask==7&&std::abs(x-21)+std::abs(y-2)<=1){won=1;tone(880);save();}
}
static void color(int r,int g,int b,int a=255){SDL_SetRenderDrawColor(renderer,r,g,b,a);}
static void rect(int a,int b,int w,int h){SDL_Rect r={a,b,w,h};SDL_RenderFillRect(renderer,&r);}
static void disk(int a,int b,int r){for(int j=-r;j<=r;j++){int w=static_cast<int>(std::sqrt(static_cast<float>(r*r-j*j)));rect(a-w,b+j,w*2+1,1);}}
static void draw(){
    color(13,36,44);SDL_RenderClear(renderer);
    for(int b=0;b<14;b++)for(int a=0;a<24;a++){
        int sx=a*32,sy=b*32;unsigned n=(a*371+b*173+71)%29;
        if(a<1||a>22||b<1||b>12){color(18,52,62);rect(sx,sy,32,32);color(31,76,80);int shift=static_cast<int>(clock_s*7+a*3)%18;rect(sx+shift,sy+12,10,2);rect(sx+3,sy+25,8,1);continue;}
        color(39+n/3,65+n/3,57+n/4);rect(sx,sy,32,32);color(57,84,67);rect(sx+5+n%17,sy+6+n%19,2,3);
        if((a*13+b*7)%23==0&&!wall(a,b)&&!thorn(a,b)){
            color(92,126,79);rect(sx+12,sy+19,2,7);color(218,192,129);rect(sx+9,sy+17,8,3);rect(sx+12,sy+14,2,9);
        }
        if(wall(a,b)){
            color(20,39,38);rect(sx+2,sy+14,29,18);color(76,98,87);rect(sx+2,sy+5,28,23);
            color(112,130,105);rect(sx+3,sy+4,26,4);color(49,76,61);rect(sx+2,sy+22,28,6);
            color(131,156,94);rect(sx+5,sy+3,11,4);rect(sx+23,sy+14,4,10);color(31,55,47);rect(sx+15,sy+10,2,13);
        }
        if(thorn(a,b)){
            color(57,42,42);disk(sx+16,sy+18,13);color(225,116,97);
            for(int k=0;k<4;k++){rect(sx+6+k*6,sy+12-(k%2)*4,3,13);rect(sx+4+k*6,sy+13,7,3);}
        }
    }
    // Camp, stone route, and the beacon tower give the island clear landmarks.
    color(192,156,100);rect(58,358,14,9);color(221,184,116);rect(60,354,10,4);
    for(int i=0;i<3;i++){
        int a=cores[i][0]*32+16,b=cores[i][1]*32+16;
        color(24,43,40);disk(a,b+7,13);color(113,123,88);rect(a-9,b+1,18,9);
        if(mask&(1<<i)){color(105,206,164);disk(a,b,5);color(200,241,174);rect(a-2,b-2,4,4);}
        else {int bob=static_cast<int>(std::sin(clock_s*3+i)*3);color(243,192,103);disk(a,b-5+bob,7);color(255,235,166);rect(a-2,b-10+bob,4,9);}
    }
    int tx=21*32+16,ty=2*32+16;
    color(20,40,37);disk(tx,ty+8,19);color(105,126,107);rect(tx-13,ty-15,26,31);color(161,173,128);rect(tx-9,ty-21,18,8);
    color(mask==7?166:72,mask==7?236:101,mask==7?177:86);disk(tx,ty-11,6);
    if(won){SDL_SetRenderDrawBlendMode(renderer,SDL_BLENDMODE_BLEND);color(184,240,172,35);rect(tx-23,32,46,ty-30);SDL_SetRenderDrawBlendMode(renderer,SDL_BLENDMODE_NONE);}
    // Explorer: shadow, teal raincoat, satchel, warm helmet and face.
    int a=static_cast<int>(px),b=static_cast<int>(py);color(20,36,35);rect(a-9,b+10,20,5);
    color(19,40,43);rect(a-7,b+7,5,7);rect(a+2,b+7,5,7);
    color(41,196,190);rect(a-8,b-3,16,13);color(97,224,195);rect(a-7,b-3,3,10);
    color(176,121,76);rect(a+7,b,5,8);color(245,211,163);rect(a-6,b-12,12,10);
    color(233,176,84);rect(a-9,b-14,18,6);rect(a-6,b-18,12,6);color(39,55,51);rect(a+2,b-9,2,3);
    SDL_RenderPresent(renderer);
}
static void frame(){
    static Uint64 last=SDL_GetPerformanceCounter();Uint64 now=SDL_GetPerformanceCounter();float dt=static_cast<float>(now-last)/SDL_GetPerformanceFrequency();last=now;if(dt>.05f)dt=.05f;clock_s+=dt;
    SDL_Event e;bool pressed=false;
    while(SDL_PollEvent(&e)){
        if(e.type==SDL_QUIT)running=0;
        if(e.type==SDL_WINDOWEVENT&&e.window.event==SDL_WINDOWEVENT_FOCUS_LOST)std::memset(held,0,sizeof(held));
        if(e.type==SDL_KEYDOWN||e.type==SDL_KEYUP){
            SDL_Keycode k=e.key.keysym.sym;int d=k==SDLK_LEFT||k==SDLK_a?0:k==SDLK_RIGHT||k==SDLK_d?1:k==SDLK_UP||k==SDLK_w?2:k==SDLK_DOWN?3:-1;
            if(d>=0){held[d]=e.type==SDL_KEYDOWN;if(held[d]&&!e.key.repeat){move(d==0?-1:d==1?1:0,d==2?-1:d==3?1:0);repeat_s=.17f;pressed=true;}}
            if(e.type==SDL_KEYDOWN&&!e.key.repeat){if(k==SDLK_RETURN)run_start();if(k==SDLK_SPACE)interact();if(k==SDLK_s&&started&&saving!=1)save();}
        }
    }
    if(!pressed){repeat_s-=dt;if(repeat_s<=0){for(int d=0;d<4;d++)if(held[d]){move(d==0?-1:d==1?1:0,d==2?-1:d==3?1:0);break;}repeat_s=.14f;}}
    float t=1-std::exp(-20*dt);px+=(x*32+16-px)*t;py+=(y*32+16-py)*t;draw();
}
int main(int argc,char** argv){
    if(SDL_Init(SDL_INIT_VIDEO|SDL_INIT_AUDIO)){std::fprintf(stderr,"%s\n",SDL_GetError());return 1;}
    window=SDL_CreateWindow("Mosslight | Enter starts | arrows move | Space interacts | S saves",SDL_WINDOWPOS_UNDEFINED,SDL_WINDOWPOS_UNDEFINED,768,448,0);
    renderer=window?SDL_CreateRenderer(window,-1,SDL_RENDERER_SOFTWARE):nullptr;
    SDL_AudioSpec spec={};spec.freq=48000;spec.format=AUDIO_F32SYS;spec.channels=1;spec.samples=1024;audio=SDL_OpenAudioDevice(nullptr,0,&spec,nullptr,0);
    if(!renderer||!audio){std::fprintf(stderr,"%s\n",SDL_GetError());return 1;}
#ifdef __EMSCRIPTEN__
    std::snprintf(save_path,sizeof(save_path),"/saves/mosslight.txt");
#else
    const char* override=std::getenv("P2B_SAVE_PATH");char* pref=SDL_GetPrefPath("port2browser","mosslight");if(!override&&!pref)return 1;
    std::snprintf(save_path,sizeof(save_path),"%s%s",override?override:pref,override?"":"mosslight.txt");SDL_free(pref);
#endif
    load();
#ifndef __EMSCRIPTEN__
    if(argc==2&&std::strcmp(argv[1],"--smoke")==0){
        run_reset();run_start();for(int i=0;i<3;i++)move(1,0);interact();if(mask!=1)return 2;
        for(int i=0;i<3;i++)move(1,0);if(health!=2||x!=2||y!=11)return 3;
        for(int i=0;i<3;i++)move(1,0);for(int i=0;i<7;i++)move(0,-1);for(int i=0;i<7;i++)move(1,0);interact();
        for(int i=0;i<8;i++)move(1,0);for(int i=0;i<6;i++)move(0,1);interact();
        for(int i=0;i<8;i++)move(0,-1);move(1,0);interact();if(mask!=7||!won||sounds!=5)return 4;
        save();x=2;y=11;mask=0;won=0;load();if(!won||mask!=7||x!=21||y!=2||saving)return 5;
        draw();std::puts("Mosslight native smoke: collect, thorns, restore tower, audio submission and save/reload passed");running=0;
    }
    while(running){frame();SDL_Delay(16);}SDL_CloseAudioDevice(audio);SDL_DestroyRenderer(renderer);SDL_DestroyWindow(window);SDL_Quit();
#else
    (void)argc;(void)argv;emscripten_set_main_loop(frame,0,1);
#endif
    return 0;
}
