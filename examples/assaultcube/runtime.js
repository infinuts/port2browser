// The pinned Emscripten OpenAL context is observed; it is not a sound-quality test.
Module.audioState = () => AL.currentCtx?.audioCtx?.state || 'unavailable';
Module.activateAudio = () => AL.currentCtx?.audioCtx?.resume();
