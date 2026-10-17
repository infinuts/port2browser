# Unofficial AssaultCube browser adaptation

AssaultCube 1.3.0.2 is created by **Rabid Viper Productions and contributors**.
The Cube engine is by **Wouter van Oortmerssen and contributors**. This is an
altered platform adaptation, not an official AssaultCube release or endorsement.

The engine retains its original zlib-like license, including Cube's additional
no-relicensing clause. The browser patch does not relicense upstream code under
port2browser's MIT license. Full original notices accompany the built client in
`licenses/AssaultCube.txt`, `licenses/Cube.txt`, and `licenses/ENet.txt`.

Emscripten 4.0.16 runtime code is distributed under its MIT/UIUC licenses (see
`licenses/Emscripten.txt`). SDL2 2.32.8, SDL_image 2.6.0 and zlib 1.3.1 use zlib
licenses; libogg 1.3.5 and libvorbis 1.3.7 use Xiph BSD-style licenses; libpng
1.6.39 uses the libpng license. JPEG 9f: **This software is based in part on the
work of the Independent JPEG Group.** OpenAL here is Emscripten's implementation.
The source locations and full dependency notices are linked below:

- [Emscripten](https://github.com/emscripten-core/emscripten/blob/4.0.16/LICENSE)
- [SDL](https://github.com/libsdl-org/SDL/blob/release-2.32.8/LICENSE.txt)
- [SDL_image](https://github.com/libsdl-org/SDL_image/blob/release-2.6.0/LICENSE.txt)
- [Xiph Ogg and Vorbis](https://xiph.org/licenses/bsd/)
- [zlib](https://zlib.net/zlib_license.html)
- [libpng](http://www.libpng.org/pub/png/src/libpng-LICENSE.txt)
- [Independent JPEG Group](https://www.ijg.org/)

## Stock game media are not included

The output directory contains **code, license notices and an asset hash manifest**.
It never contains upstream `packages/`, `config/`, `bot/`, a game archive or an
Emscripten `.data` preload. The media are read from a folder selected locally by
the player and never uploaded by the launcher. Authentication keys, profiles,
and files outside the pinned manifest are ignored.

[AssaultCube's licensing page](https://assault.cubers.net/docs/license.html)
allows redistribution of the entire unmodified package under its stated terms;
individual media files have separate terms. A source-code license does not give
permission to repackage all the game's artwork in a modified public web build.
Retain the original media and their notices in your local game folder. Review
rights separately before distributing any media or offering commercial hosting.

Internet sockets and host resolution are disabled in the browser adaptation.
The local server and bots communicate in-process. No multiplayer proxy, account,
remote game session or analytics service is part of this example.
