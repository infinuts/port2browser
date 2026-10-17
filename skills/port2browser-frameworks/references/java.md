# Java / libGDX

Identify the game's framework, Gradle modules, dependency versions and source.
A desktop JVM or JAR is not a browser runtime. LWJGL, Java2D/Swing, JNI and arbitrary
JVM libraries do not become web-compatible by choosing a Java transpiler.

For a libGDX project, investigate its matching HTML/GWT backend and translatable
library subset. The [primary HTML5/GWT guide](https://libgdx.com/wiki/html5-backend-and-gwt-specifics)
reviewed on 2026-10-17 documents `html:dist` for projects with that actual module.
Inspect Gradle scripts and task names first. Audit reflection, threads, JNI,
numeric behavior, native physics/font modules and asset loading.

Build a scene with real textures, an interaction and audio, then test menus and
persistence across a new page instance. A desktop content pipeline may need a
host-side build while runtime content must remain compatible with the HTML backend.
Keep audio/codec and browser differences explicit; test generated output served
from its actual base path, not only the development server.

If the project uses a different Java engine, find a maintained matching browser
backend before planning code migration. A decompiler or JVM emulator that starts
some bytecode is not evidence that graphics/gameplay dependencies work.
Record toolchain/backend revisions and any unsupported library as a blocker.
Guidance only; no Java game is newly evaluated by this guide.
