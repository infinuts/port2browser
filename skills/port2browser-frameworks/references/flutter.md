# Flutter / Flame → web

Establish Dart, Flutter, Flame, plugin and resource versions from the editable
project and lockfile. Native mobile binaries do not supply this project.

Use the version-matching [Flutter web build guide](https://docs.flutter.dev/platform-integration/web/building)
and [Flame platform notes](https://docs.flame-engine.org/latest/flame/platforms.html),
reviewed 2026-10-17. `flutter build web` is a starting point for compatible source;
keep the generated loader, rendering backend, assets and base URL together.
Review [Wasm requirements](https://docs.flutter.dev/platform-integration/web/wasm)
before choosing `--wasm`: browser/renderer and JS interop constraints are separate
from the default build, and can change with releases. Test the requested matrix.

Audit platform channels, FFI, file access, native plugins, texture/shader features,
audio gestures, IndexedDB/storage wrappers and lifecycle behavior. A supported
Flutter web target does not establish that every game plugin has a web backend.

First probe: a real Flame scene with input/collision, an objective, audio, element
and window-focus handling, and durable progress after reload. Test touch controls
explicitly; viewport emulation is not physical-device evidence. Record changed
rendering/physics behavior and missing plugin implementations. Guidance only; no
new Flutter/Flame game result is bundled with this playbook.
