# Local evidence commands

Resolve the bundled `scripts/run.py` relative to this skill, then use its absolute
path from the delivery workspace. Python 3.9+ and local POSIX locks are required.
There is no network service, scheduler or account setup.

## Record an authorized command

```text
python3 -I /path/to/skill/scripts/run.py record /path/to/work --role engineering/build --inputs source --outputs report.json -- python3 existing-check.py
```

The command after `--` really executes with the caller's host permissions. Name
its indirect inputs with `--inputs`; existing files/directories named in its
arguments are also bound when supported by the recorder. Outputs and captured
logs are written locally. Do not put secret values in arguments or logs.

`--role` is a `department/role` label, not proof of membership in a staff roster.
`--worker` is also a label. Neither grants access or authenticates an identity.
Exit 1 counts as a disclosed gap only when explicitly permitted by `--ok-exit
0,1` and separately accepted in the claims file; it never becomes a clean GO.

## Verify a claim

```json
{
  "schema": "solaris.delivery-claims/1",
  "order": "order.json",
  "contributions": [
    {"role": "engineering/build", "outputs": ["report.json"]}
  ]
}
```

```text
python3 -I /path/to/skill/scripts/run.py verify /path/to/work --claims claims.json --json --strict
```

Read both the exit code and report:

| Strict exit | Meaning |
|---:|---|
| 0 | `GO`, with `clean_go: true` |
| 1 | `NO_GO`: inspect missing, stale, failed or altered evidence |
| 2 | Invalid request/input |
| 3 | `GO_WITH_GAPS`, not a clean delivery |
| 4 | `EVIDENCED_NO_ORDER`, not a completed delivery |

Use `--out FILE` only when you want the verifier to write a report. Ordinary
verification does not rerun specialist commands or complete missing work.

## Work-order receipts and the demo

The optional `order` references a local work order with a hashed intake file.
`work-order status ORDER --json` inspects it. `work-order run ORDER --worker
LABEL` actually runs activation, brief and delivery steps and can create local
scaffolding. Run only a work order authorized for that workspace.

For a disposable synthetic example, run the skill's `examples/demo.py` using
Python isolated mode. Its `intake.json` and `order.json` are public synthetic
fixtures. It checks real output hashes and local receipts, then changes an
output and verifies that the claim is refused. It uses no credentials, model
API or external service and cleans only the temporary directory it created.

The ledger is hash-linked self-consistency evidence. Replacing the entire ledger
and head defeats that check. Output correctness, worker identity and an OS or
credential sandbox need separate controls; they are not certified by this tool.
