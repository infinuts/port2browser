# Inspection JSON contract (schema version 1)

`inspect_game.py DIRECTORY [--max-entries N] [--max-depth N]` writes one JSON
object to stdout. Exit 0 means a report was produced, including partial reports;
exit 2 means invalid arguments or an unusable root. Diagnostics for invocation
failures go to stderr. Scan warnings are in the report. Input files are never
executed and archives are not opened. Python 3.10+; no dependencies.

Existing fields retain their meanings. Consumers must tolerate additive fields.
A breaking change requires a schema version bump.

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer `1` |
| `root` | Absolute input directory; review before sharing |
| `limits` | Entry/depth budgets and per-file header/manifest byte limits |
| `inventory` | Counts of visited entries, regular files, bytes, skipped directories/links; extension and source-extension counts |
| `candidates` | Engine leads sorted by engine; `confidence` is always `inferred`; evidence paths/reasons and total `evidence_count` |
| `build_files` | Up to 100 matching paths, sorted |
| `binaries` | Up to 100 detected header formats with paths and architecture descriptions, sorted by path |
| `truncated` | Entry/depth traversal limit reached; unchanged meaning |
| `warnings` | Up to 100 diagnostic strings |
| `limitations` | Human-readable interpretation boundaries |
| `metadata` | Up to 100 observed `{engine, path, field, value}` records, sorted by engine/path/field |
| `omitted` | Counts for `evidence`, `build_files`, `binaries`, `warnings`, `metadata` omitted by output caps |
| `scan_errors` | Counts of failed `stat`, `read`, and `directory` operations |
| `completeness` | Separate traversal, readability, output cap and metadata sample limit indicators |

Each candidate additionally has `evidence_omitted`, equal to `evidence_count`
minus the number of retained evidence records. Top-level `omitted.evidence`
is the sum across candidates. `omitted.binaries` counts **uninspected binary
candidates after the detection output fills**, not known omitted binary formats.
Header reads stop at that cap, preserving the helper's bounded behavior.

`traversal_complete` means no traversal limit or stat/directory error within the
configured exclusions. It does not mean all game files or dependencies were
analyzed. `samples_readable` means no attempted sample read failed. `output_capped`
means at least one omission counter is nonzero. `metadata_sample_limits` counts
metadata files skipped because their sizes exceed 65,536 bytes. Parse warnings
can exist even when traversal is complete and samples are readable.

Observed fields:

- Unity `editor_version`: literal editor version from `ProjectSettings/ProjectVersion.txt`.
- Godot `config_version`: descriptor format number as a string, **not an engine version**.
- Godot `features`: strings declared in `config/features`; a version feature is an observation, not verified runtime compatibility.
- JavaScript `dependencies.NAME` / `devDependencies.NAME`: literal declarations for the existing recognized packages, including ranges and URLs. These are not resolved installed versions.

Unity/Godot descriptors and package manifests are bounded by the same manifest
byte limit. Malformed/oversized metadata yields warnings; other files continue.
Conflicting values from different paths remain separate. No candidate becomes
confirmed, and no metadata record establishes source completeness, licensing,
or web support. Metadata has a separate cap of 100 records.

Traversal and retained subsets use filesystem order; sorting the final arrays
does not make limited scans deterministic across machines. Keep the input tree
unchanged. See the complete and limited JSON snapshots under `tests/reports/`.

## Task navigation (additive)

`task_hints` is a list of `{engine, skill, status}` objects for observed candidates
with a documented task skill. `status` is always `investigate`; `skill` is an Agent
Skill name, not an executable path. Hints neither confirm the engine nor assert
web compatibility, project completeness or installation. Unknown inputs may have
no hints. Consumers may ignore this field and keep using `schema_version: 1`.

Defold project/bootstrap sections, Construct project suffixes, GDevelop-style
JSON fields and Bevy/Macroquad dependency declarations add inferred clues. Text
reads retain the 64 KiB bound, scan-error accounting and malformed-input warnings.
Rust parsing is deliberately a declaration heuristic, not a TOML resolver; it
can miss aliases, dependency subtables and workspace inheritance. Archive contents
and build instructions are never executed to infer a route.
