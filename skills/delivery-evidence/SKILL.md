---
name: delivery-evidence
description: 'Check a local delivery claim against recorded command exits, input/output hashes and work-order receipts. Use for stale evidence, interrupted work and missing proof; this does not independently prove output correctness.'
---

# Delivery evidence

Use the bundled [entrypoint](scripts/run.py) with an absolute path resolved from
this skill. Helpers require Python 3.9+ on macOS or Linux; they use local POSIX
locks, not distributed coordination. Run `--context` to inspect the package and
`--help` for command syntax.

`record ROOT ... -- COMMAND ...` actually runs the caller's command, writes its
local log and hash-linked contribution receipt. Use only a command already
authorized for this workspace. A work order does not grant shell/file/network
access. Name indirect input files with `--inputs` so later changes are checked.

`verify ROOT --claims FILE --json --strict` checks the local receipts, files and
optional work order. It does not run the recorded specialist commands again.
Treat only exit 0 plus `clean_go: true` as a clean delivery GO. Exit 3 means
accepted gaps and exit 4 means evidence without a completed work order; neither
is a clean GO. Report the named stale/missing/failed contribution rather than
turning a green-looking message into acceptance.

`work-order run ORDER --worker LABEL` runs the bundled local activation/brief/
delivery workflow; `work-order status ORDER --json` inspects it. Do not call `run`
merely to inspect a claim. It creates local project scaffolding and receipts.

Role and worker labels are unauthenticated claims, and the ledger provides self-consistency, not signed
identity or protection against an attacker replacing the entire ledger and head.
An exit code and matching artifact hash do not prove the artifact is correct.
Keep command logs and inputs free of credentials and private customer data unless
the chosen host and local storage are appropriate. No service receives them
automatically. See the [command reference](references/usage.md) and
[synthetic demonstration](examples/demo.py) for a reproducible starting point.
