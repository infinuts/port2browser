# HaxeFlixel → HTML5

Confirm Haxe, HaxeFlixel, Lime/OpenFL, addons, project descriptors and resource
versions. A compiled Flash SWF is a different input from editable Haxe source.

The [target documentation](https://haxeflixel.com/documentation/haxeflixel-targets/)
and [hello-world build instructions](https://haxeflixel.com/documentation/hello-world/),
reviewed 2026-10-17, provide an HTML5 target through OpenFL/Lime. Inspect the actual
project and its locked library setup before using a command such as `lime test
html5`. Keep compiler, target and addon revisions together.

Audit native extensions, conditional compilation, shader differences, fonts,
resource paths/casing, codecs and save APIs. Do not copy old target-specific
restrictions into a current version claim without a matching test.

First probe: a sprite/tilemap scene with collision, pickup, sound, state transition
and saved progress restored after full reload. Compare native behavior where
available and retain console/render evidence. A browser-rendered title screen or
a converted asset archive does not establish gameplay preservation. This is route
guidance, not a newly evaluated HaxeFlixel game.
