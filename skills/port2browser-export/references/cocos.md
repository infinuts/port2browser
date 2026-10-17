# Cocos Creator → Web

Establish Creator generation/version, complete assets/scripts/import settings,
plugins and custom engine/native code. Cocos Creator and native Cocos2d-x are
different inputs; a native C++ project needs its own web-backend assessment.

Use matching editor build settings and a Web target. The
[Creator 3.8 LTS Web guide](https://docs.cocos.com/creator/3.8/manual/en/editor/publish/publish-web.html)
was reviewed on 2026-10-17; select documentation for the actual project version.
Audit native-only services, JSB calls, shaders/custom rendering, physics modules,
codec/texture choices and remote asset bundles. Inspect project build hooks before
executing them. Pin engine and extension versions instead of rewriting the project
against an unrelated current template.

Milestone: load a representative scene and complete an interaction with audio,
then change scene and restore a save after page reload. Compare URL/base-path
behavior, file casing and loading errors on the packaged Web output. Detect the
required browser graphics capabilities explicitly; a successful editor preview
is not evidence for the hosted release.

Report exact exporter settings, file manifest, hosting contract, tested browsers
and unresolved plugins. Guidance only; no Cocos game is certified by this guide.
