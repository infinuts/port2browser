# Ren'Py → Web

Confirm the matching SDK, editable script/project, Python/native extensions,
codecs and required services. Compiled `.rpyc` and `.rpa` files alone do not prove
an editable, redistributable project.

The [Web guide](https://www.renpy.org/doc/html/web.html), reviewed on 2026-10-17
at documentation version 8.5.4, describes the launcher Web build and its runtime
limits. Use the project's version. Audit Python threading/network requests and
movie/audio behavior against that runtime before porting a large visual novel.

First export a short route with choices, a screen/menu, audio and save/load.
Retain translations and text/font shaping. Serve the complete generated output
over HTTP(S), test audio activation and browser codec fallbacks, and confirm
persistent/save data after a full document reload. If using progressive downloads,
check late images/voice/music and distinguish startup bytes from the entire work.

Preserve the original build. Replacing unsupported Python extensions or network
services requires equivalent tested behavior or an explicit blocker. Export
success is build-only until the route actually runs in the stated browsers.
Guidance only; this repository adds no Ren'Py gameplay result with these docs.
