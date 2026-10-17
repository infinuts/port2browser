---
name: port2browser-release
description: Prepare and document a browser game release after a verified port. Use for static hosting, MIME/compression/isolation, distribution rights, source/data separation and versioned port reports.
license: MIT
---

# Package the verified output

Start from the tested build artifact, not the project directory. Record the game,
engine/backend/SDK and source revisions, browser matrix, known regressions and
unavailable checks. Keep one report in the port workspace with routes rejected,
commands, source patches, evidence paths and the smallest remaining blocker.

Publish only allowlisted runtime/asset files with established distribution
permissions. Preserve engine, code, asset, font and middleware notices separately.
Exclude source-private data, credentials, saves, extracted commercial archives
and development dependencies. If the port loads user-supplied files, publish the
loader and its data contract without bundling those files.

Verify the chosen host's URL/base-path behavior, Wasm MIME, gzip/Brotli headers,
isolation requirements, worker/CORS paths, cache invalidation and storage origin.
GitHub Pages and itch.io have different constraints; check the host's current
primary documentation instead of assuming custom headers. A threaded build may
require a different host or a tested single-thread variant. Treat a service-worker
isolation workaround as a versioned dependency with navigation/cache tests.

Replay the gameplay sequence on the deployed artifact when deployment is in the
user's scope. Record its revision and failures; a successful upload/build job is
not a deployed gameplay test. Keep local-only results labeled local. Respect any
required final publishing approval while completing the reviewable package first.

Handoff a source/license manifest, build/install/update steps, scoped port report,
evidence and artifact integrity information. Release tags and evidence refer to
specific revisions; new route guidance or an engine upgrade does not inherit
old browser results. Add reusable findings with their exact versions and failed
alternatives, after reviewing logs for private paths/account information.
