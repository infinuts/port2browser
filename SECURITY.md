# Security policy

Security fixes target the current `main` branch. Older tags and copied installs
should update to a reviewed revision containing the fix; no older release line
has a separate backport commitment.

## Report a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/infinuts/port2browser/security/advisories/new)
when enabled. If that option is unavailable, open an issue asking the maintainer
for a private reporting channel, without exploit details, private game files,
credentials or sensitive logs. There is no guaranteed response time.

Include the affected revision, Python/OS/browser versions, helper arguments,
expected and actual behavior, and a minimal original/synthetic reproduction.
Explain whether a path escaped the build root, a link was followed, an input was
executed, or an evidence/report claim was incorrect. Review logs for private
paths and account information before sharing.

## Trust boundary

Inspection is bounded and read-only; it does not execute game files. The local
server serves one dedicated output directory on loopback and refuses hidden
paths, traversal, links/reparse points and directory listings. Keep that directory
unchanged while serving/inspecting: these helpers are not an isolation boundary
against a concurrent local attacker replacing files. Never expose the helper as
production hosting or serve a repository, home directory or private saves.

Game manifests, names, strings and decompiler output are untrusted data. Engine
builds may execute hooks; inspect them and use an appropriate isolated environment.
Browser automation executes the specified game in a fresh browser context and
must be directed only at inputs the user authorized for that purpose.

Dependabot proposes npm and GitHub Actions updates. Review and test those PRs;
a dependency update or passing smoke test does not establish game compatibility.
