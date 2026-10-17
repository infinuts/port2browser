"""Bounded workaround for Emscripten 4.0.16's legacy texture-load optimizer."""
# The SDK's regex terminates at the texture matrix's inner ')', producing invalid
# GLSL when a combiner uses the sample twice. Match the complete sampling call.
OLD = (r'/(texture.*?\(.*?\))/g', r'/(texture.*\(.*\))/g')
NEW = r'/((?:texture2D|textureCube)\([^,\n]+,\s*(?:\([^()\n]*\)|[^()\n])*\))/g'


def fix_texture_jit(script):
    for pattern in OLD:
        if script.count(pattern) != 1:
            raise ValueError('Unexpected pinned SDK texture JIT; review before patching')
        script = script.replace(pattern, NEW)
    return script
