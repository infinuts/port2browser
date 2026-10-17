//! Original MIT regression game: actual Macroquad input/rendering with a small platform boundary.
use macroquad::prelude::*;
use std::sync::atomic::{AtomicI32, Ordering::Relaxed};
static X: AtomicI32 = AtomicI32::new(24);
static COLLECTED: AtomicI32 = AtomicI32::new(0);
static STARTED: AtomicI32 = AtomicI32::new(0);
static SOUNDS: AtomicI32 = AtomicI32::new(0);
static SAVING: AtomicI32 = AtomicI32::new(0);
static SAVES: AtomicI32 = AtomicI32::new(0);
#[no_mangle] pub extern "C" fn p2b_x() -> i32 { X.load(Relaxed) }
#[no_mangle] pub extern "C" fn p2b_collected() -> i32 { COLLECTED.load(Relaxed) }
#[no_mangle] pub extern "C" fn p2b_started() -> i32 { STARTED.load(Relaxed) }
#[no_mangle] pub extern "C" fn p2b_sounds() -> i32 { SOUNDS.load(Relaxed) }
#[no_mangle] pub extern "C" fn p2b_saving() -> i32 { SAVING.load(Relaxed) }
#[no_mangle] pub extern "C" fn p2b_saves() -> i32 { SAVES.load(Relaxed) }
#[no_mangle] pub extern "C" fn p2b_start() { STARTED.store(1, Relaxed); }
#[no_mangle] pub extern "C" fn p2b_saved(ok:i32) { SAVING.store(if ok==1 {0} else {-1},Relaxed);if ok==1 { SAVES.fetch_add(1,Relaxed); } }
#[cfg(target_arch="wasm32")]
extern "C" { fn p2b_load_x()->i32;fn p2b_load_collected()->i32;fn p2b_save(x:i32,collected:i32);fn p2b_sound(); }
#[cfg(not(target_arch="wasm32"))]
fn save_path()->std::path::PathBuf { std::env::var_os("P2B_SAVE_PATH").map(Into::into).unwrap_or_else(||"macroquad-beacon-save.txt".into()) }
fn restore() {
    #[cfg(target_arch="wasm32")] let values=unsafe {Some((p2b_load_x(),p2b_load_collected()))};
    #[cfg(not(target_arch="wasm32"))] let values=std::fs::read_to_string(save_path()).ok().and_then(|s|{let v:Vec<_>=s.split_whitespace().collect();Some((v.first()?.parse().ok()?,v.get(1)?.parse().ok()?))});
    if let Some((x,c))=values { if (0..=288).contains(&x) && (0..=1).contains(&c) {X.store(x,Relaxed);COLLECTED.store(c,Relaxed);} }
}
fn save() {
    SAVING.store(1,Relaxed);
    #[cfg(target_arch="wasm32")] unsafe {p2b_save(p2b_x(),p2b_collected());}
    #[cfg(not(target_arch="wasm32"))] {p2b_saved(std::fs::write(save_path(),format!("{} {}",p2b_x(),p2b_collected())).is_ok() as i32);}
}
#[cfg(not(target_arch="wasm32"))]
fn tone_wav()->Vec<u8> {
    let rate=22050u32;let count=rate/5;let bytes=count*2;
    let mut v=b"RIFF".to_vec();v.extend((36+bytes).to_le_bytes());v.extend(b"WAVEfmt ");v.extend(16u32.to_le_bytes());v.extend(1u16.to_le_bytes());v.extend(1u16.to_le_bytes());v.extend(rate.to_le_bytes());v.extend((rate*2).to_le_bytes());v.extend(2u16.to_le_bytes());v.extend(16u16.to_le_bytes());v.extend(b"data");v.extend(bytes.to_le_bytes());
    for i in 0..count {let sample=((i as f32*440.0*std::f32::consts::TAU/rate as f32).sin()*5000.0) as i16;v.extend(sample.to_le_bytes());}v
}
fn config()->Conf {Conf{window_title:"Macroquad Beacon".into(),window_width:640,window_height:360,window_resizable:false,..Default::default()}}
#[macroquad::main(config)]
async fn main() {
    restore();
    #[cfg(not(target_arch="wasm32"))] let tone=macroquad::audio::load_sound_from_bytes(&tone_wav()).await.unwrap();
    loop {
        if is_key_pressed(KeyCode::Enter) {p2b_start();}
        if p2b_started()==1 {
            if is_key_pressed(KeyCode::Right) {X.store((p2b_x()+12).min(288),Relaxed);}
            if is_key_pressed(KeyCode::Left) {X.store((p2b_x()-12).max(0),Relaxed);}
            if is_key_pressed(KeyCode::Space) && (p2b_x()-120).abs()<=12 && p2b_collected()==0 {
                COLLECTED.store(1,Relaxed);SOUNDS.fetch_add(1,Relaxed);
                #[cfg(target_arch="wasm32")] unsafe {p2b_sound();}
                #[cfg(not(target_arch="wasm32"))] macroquad::audio::play_sound_once(&tone);
            }
            if is_key_pressed(KeyCode::S) {save();}
        }
        clear_background(Color::from_rgba(15,23,42,255));
        draw_rectangle(240.0,128.0,48.0,48.0,if p2b_collected()==1 {GREEN} else {GOLD});
        draw_rectangle(p2b_x() as f32*2.0,200.0,48.0,48.0,Color::from_rgba(56,189,248,255));
        draw_text(&format!("Macroquad Beacon | x={} | collected={} | saves={}",p2b_x(),p2b_collected(),p2b_saves()),16.0,30.0,22.0,WHITE);
        draw_text("Enter: start  Arrows: move  Space: collect  S: save",16.0,340.0,19.0,WHITE);
        next_frame().await;
    }
}
