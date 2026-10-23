# Solaris Delivery Evidence

One focused, local workflow for checking whether a claimed software delivery has
current evidence. It records real command exits, input/output digests and logs,
then identifies stale files, missing contributions, altered receipts or an
incomplete work order. It derives five runtime modules from
[Solaris Dev Shop 0.64](https://github.com/Shaisolaris/solaris-dev-shop/tree/3a577e42c48473f6ef8680950dd55c067820d5d3).

Four runtime modules are unchanged. The recorder's role check is adapted to syntax-checked caller labels, with the exact source and resulting hashes recorded in PROVENANCE.json. Role labels do not authenticate a person or grant authority.

This optional companion exposes one skill; it does not install a staff/persona
hierarchy. The full Solaris DevShop remains 61 specialists plus its coordinator.
Its purpose is evidence consistency, not generic code-review advice or an
automatic claim that a deliverable is correct.

## Native plugin

The repository root contains an Agent Plugins v1 `plugin.json`, and
`skills/delivery-evidence/SKILL.md` is the discoverable entry. Public catalog
submission and provider approval are separate from publishing this source.

Requirements: Python 3.9+ and a macOS/Linux filesystem with local POSIX locks.
No third-party Python dependencies, MCP servers, hooks, lifecycle installers,
accounts, network service or background scheduler are configured. Installing
does not execute the helpers or grant permissions.

Resolve the skill's bundled `scripts/run.py` to an absolute path. Examples:

```text
python3 -I /path/to/plugin/skills/delivery-evidence/scripts/run.py --context
python3 -I /path/to/plugin/skills/delivery-evidence/scripts/run.py verify /path/to/work --claims claims.json --json --strict
```

## Try it

Run `python3 -I skills/delivery-evidence/examples/demo.py` from this checkout for a synthetic, disposable
local demonstration. It exercises the actual recorder, work-order runner and
verifier, then changes an output and confirms that acceptance is invalidated.

Prompts for the host:

1. "Use delivery-evidence to check this claims file. Report stale or missing
   evidence without rerunning commands or changing the work order."
2. "Record this already-authorized test command and its named inputs/outputs;
   then check whether its contribution is still current."
3. "Run the synthetic delivery-evidence demo and explain why changing an output
   invalidates the delivery claim."

## Data and execution

`record` runs the exact caller-provided command under the caller's normal host
permissions. It writes `.delivery/` receipts and captured command logs in the
selected workspace. Logs can contain command output and paths; select suitable
inputs and storage. `verify` reads these files and writes a report only when
`--out` is requested. `work-order run` creates local project scaffolding, a brief
and delivery receipts. Use `work-order status` for inspection instead of running
it. Nothing automatically uploads data to Solaris. The host/model provider may
process prompts and files under its own settings and policy.

You control local output retention and deletion. Removing the plugin does not
erase workspace receipts. Do not post secrets or private source in public
support issues. Contact shehryar@solaristek.com or
[GitHub issues](https://github.com/Shaisolaris/solaris-delivery-evidence/issues).

## Evidence limits

Only a strict exit 0 with `clean_go: true` is a clean delivery GO. Accepted gaps,
missing work orders and skipped work remain distinct outcomes. Worker labels
are unauthenticated claims. Hash chains show consistency; someone who replaces
all receipts and the head can create a different self-consistent history. The
tool cannot independently prove that a command's output is correct, enforce a
sandbox or replace a reviewer's judgment. Host tools and credential scopes are
the operator's responsibility.

MIT licensed. See LICENSE, NOTICE.md, SOURCE-NOTICE.md and PROVENANCE.json.
