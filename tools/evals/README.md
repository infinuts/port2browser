# Paired agent evaluations

Development-only, explicit opt-in runs using an authenticated Codex CLI. The
installed skill stays dependency-free. Ordinary CI tests the grader and examples;
it does not invoke a paid/account-backed agent or require account credentials.

## Run

Install Node.js 22+, the root `npm ci`, Playwright Chromium/Firefox, Python 3.10+
and Codex CLI. Authenticate with `codex login` outside the evaluation. Then:

```sh
python3 tools/evals/run.py --output work/eval-run --repetitions 3
```

`--codex` and `--node` accept executable paths. `--model MODEL` pins a model when
available to your account; omitting it records the CLI default as an unknown
identifier. `--cases shipped-unity injection javascript` selects tasks;
`--timeout 180` limits each invocation; `--seed 17` randomizes condition order
reproducibly. A new output directory is required. Six calls per repetition can
consume account quota; choose the run size deliberately.

The runner uses official [Codex noninteractive mode](https://developers.openai.com/codex/noninteractive):
workspace-write, fresh ephemeral sessions, ignored user config, structured final
JSON, and a JSONL tool transcript. It never disables the sandbox or reads/copies
credentials. Timeout kills the agent process tree. Temporary workspaces are
outside the repository so parent skills/checklists and reference solutions are
not supplied. Only the treatment receives the portable skill directory and an
explicit instruction to use it. This evaluates **explicit invocation**, not
skill auto-discovery or trigger precision. Inputs are identical across conditions.

Global installed skills/account behavior can still influence both conditions;
use a clean agent profile/runner for stronger isolation. The output records
revision, source hashes, input hashes, CLI/model label, seed, timeouts and results.
Use the same pinned model and repeat cases before interpreting a pass-rate gap.

## What is graded

- Shipped Unity: evidence-backed blocked assessment, inferred engine candidate,
  no invented editable project or browser success.
- Injection: instructions embedded in game data must not cause a marker file or
  unsupported playable/browser claims. This is one benign adversarial pattern,
  not a prompt-injection security certification.
- JavaScript: only desktop input is supplied. A separate grader launches both
  browsers against the generated build and checks input, canvas output, audio,
  menu and reload persistence. `build_only` can pass if independent replay works;
  the agent need not invent its own browser results to get credit.

Execution failures are excluded from performance denominators. Compare complete
pairs only: a missing baseline cannot create a skill benefit. Invalid structured
answers from completed invocations count as failures. Exit code 2 signals an
execution failure; graded model failures remain data in a successful harness run.

Results contain pass rates, execution/invalid-result counts, false-playable
claims, unsupported test-evidence claims, and claims contradicted by replay.
`fabricated_results` is **null until human transcript review**: missing evidence
or a failed reproduction does not prove deliberate fabrication. Grade decisions
and raw evidence remain separate; do not publish an agent's self-reported pass
as independent evidence. The evaluator and expected criteria stay outside inputs.

Outputs include JSONL, stderr, prompts, structured reports, cited artifacts and
builds. Review these for private paths/account metadata before publishing. Only
reviewed summaries belong in `tests/evaluation-results/paired/`. A small pilot
with no observed gap does not establish that the skill helps or hurts.
