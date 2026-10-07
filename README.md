[![CI](https://github.com/realMNohgee/RepForge/actions/workflows/smoke.yml/badge.svg)](https://github.com/realMNohgee/RepForge/actions/workflows/smoke.yml)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)

# ⚖ RepForge

**A local, signed, tamper-evident reputation ledger for AI agents — register agents, log outcomes, and compute Bayesian trust scores backed by an Ed25519-signed, hash-chained audit trail. One dependency (PyNaCl).**

RepForge is the credit bureau for your agent fleet — and the trust layer for the "check any agent's Rep" future. Every task outcome is appended to a hash-chained JSONL ledger and signed with your Ed25519 identity; every agent gets a Bayesian trust score; agents vouch for one another to form a weighted trust graph; and `repforge verify` proves the whole thing was never tampered with.

---

## ✨ Why RepForge?

You chain five agents to complete a task. One consistently fails. One quietly excels. Without a reputation system, you find out the hard way — *after* the task breaks.

RepForge turns "which agent should I trust?" into a number you can audit *and* prove you didn't fake:

- **Bayesian scoring** — `(successes + 1) / (total + 2)`. A single success is *not* 100%; the score converges to the true success rate as data accumulates, so agents can't game it with one lucky run.
- **Ed25519-signed** — every ledger entry and vouch is signed with your identity key. You can't quietly rewrite a `failure` into a `success` without `verify` catching the broken signature.
- **Hash-chained** — each entry carries a `prev_hash` linking it to the one before. Insert, delete, or reorder anything and the chain breaks.
- **`verify` command** — walks the ledger and vouches, recomputes every hash, checks every signature, and reports exactly which line was tampered with.
- **Weighted trust graph** — agents vouch for each other; a vouch's weight is scaled by the voucher's own reputation (PageRank-style).
- **Per-category breakdowns** — separate reliability for `code-review` vs `research` vs anything else.
- **Tiered rankings** — Unproven → Bronze → Silver → Gold → Diamond.
- **One dependency** — PyNaCl (libsodium Ed25519). Everything else is Python standard library.

## ⚖ The Security Model

RepForge keeps three integrity guarantees over every entry:

1. **Non-repudiation** — each entry is signed by a single Ed25519 identity (`~/.repforge/identity.key`), generated automatically on first use. The signature proves *you* attested the outcome; nobody can forge an entry in your name without the private key.
2. **Tamper-evidence** — every entry's `hash` covers its full contents *plus* the previous entry's hash (`prev_hash`). Editing, inserting, deleting, or reordering any line breaks the hash chain downstream.
3. **Verifiability** — `repforge verify` recomputes the entire chain and every signature against the stored public key, then exits non-zero if anything is off. Wire it into CI to gate on an unbroken ledger.

The private key lives in `identity.key` (mode 600) and is your trust anchor. Rotate it with `repforge keygen --rotate` — old entries stay verifiable because each carries the public key that signed it.

Set `REPFORGE_HOME` to point the ledger at any directory (default `~/.repforge/`):

```bash
export REPFORGE_HOME=/path/to/ledger
```

## ⚖ The Scoring Formula

```
score = (successes + 1) / (total + 2)
```

A Bayesian prior (Beta(1,1)) over the success rate. It prevents "1 for 1 = perfect" gaming and tightens toward the true rate with more evidence:

| Outcomes | Score | Reading |
|----------|-------|---------|
| 1 / 1 | 0.667 | Untrustworthy — not enough data |
| 5 / 5 | 0.857 | Promising — consistent track record |
| 3 / 3 | 0.800 | Gold-ish — small sample |
| 50 / 50 | 0.981 | Diamond tier — proven reliability |
| 5 / 10 | 0.500 | Unreliable — coin-flip |

## 🚀 Quick Start

```bash
git clone https://github.com/realMNohgee/RepForge.git
cd RepForge
pip install -r requirements.txt     # installs PyNaCl
python3 repforge.py --help
```

```
┌─────────────────────────────────────────────────┐
│  ⚖  REPFORGE  v2.0 — Agent Reputation Ledger        │
│  Register. Log. Score. Trust. Verify.               │
└─────────────────────────────────────────────────┘

USAGE
  repforge <command> [args]

COMMANDS
  keygen        Generate (or show) your Ed25519 signing identity
  register     Register a new agent
  log          Log a task outcome (signed)
  reputation   Show the rep registry [agent_id]
  vouch         Vouch for another agent (signed)
  verify        Verify chain integrity + signatures
  audit         Show audit trail [agent_id]
  trust         Display trust graph

EXAMPLES
  # Mint your signing identity (auto-created on first log):
  repforge keygen

  # Register an agent:
  repforge register

  # Log a task outcome:
  repforge log

  # Check an agent's rep:
  repforge reputation gpt-assistant-1

  # Prove nothing was tampered with:
  repforge verify
```

## 🧭 Command Tour

Every block below is real captured output (ANSI colors stripped; the `REPFORGE` banner is omitted after the first command for brevity).

### `keygen` — your signing identity

The identity key is generated automatically the first time you `log` or `vouch`. `keygen` shows it, or mints a fresh one with `--rotate`:

```console
$ python3 repforge.py keygen

  Signing Identity

  Public key: 0f790f6e562ed75dec2db11142b0c3e9a0cc85057e0e845d883e1a2d084e9977
  Already have an identity. Use `keygen --rotate` to mint a new one
  (old entries stay verifiable — each is signed with the key embedded in it).
```

### `register` — add an agent

```console
$ python3 repforge.py register

  Register Agent

  Agent ID:   Display name:   Provider/creator (optional):   URL or repo (optional):
  ✓ Agent 'alice' registered.
  Log outcomes with: repforge log alice
```

> Prompts read `Agent ID`, `Display name`, `Provider/creator`, and `URL or repo`. Here the answers were `alice`, `Alice`, `TestCo`, `https://example.com/alice`.

### `log` — record a task outcome (signed)

```console
$ python3 repforge.py log

  Log Task Outcome

  Registered agents:
  • alice (Alice)
  • bob (Bob)

  Agent ID:
  Outcome:
  1) success
  2) failure
  3) partial
  Choice [1]:   Category [general]:   Task description (optional):   Cost (credits) (optional):
  Generated new signing identity (Ed25519).
  Public key:  0f790f6e562ed75dec2db11142b0c3e9a0cc85057e0e845d883e1a2d084e9977
  Private key: /Users/you/.repforge/identity.key — your trust anchor. Losing it invalidates new entries.

  ✓ Outcome logged.
  Updated rep: ◇ Bronze (0.667)
```

> Choices were `alice` → `success` → category `code-review` → task `"Review PR #142 for race conditions"` → cost `0.5`. The identity key is generated on this first write, and the updated tier prints immediately.

### `reputation` — the registry

```console
$ python3 repforge.py reputation

  ╔══════════════════════════════════════════════════╗
  ║  ⚖  REP REGISTRY                                 ║
  ╚══════════════════════════════════════════════════╝

  Agent                                     Tier    Score  Tasks
  ────────────────────────────────────────────────────────────
  bob                       ◇ Bronze    0.667      1
  alice                     ◇ Bronze    0.500      2
```

### `reputation <agent_id>` — a single agent's profile

```console
$ python3 repforge.py reputation alice

  ╔══════════════════════════════════════════════════╗
  ║  ⚖  AGENT PROFILE                                 ║
  ╚══════════════════════════════════════════════════╝

  Agent ID:      alice
  Name:          Alice
  Provider:      TestCo
  Registered:    2026-10-07T22:07:34

  Rep:            ◇ Bronze (0.5000)
  Tasks:          2 total
  ├─ Success:      1
  ├─ Failure:      1
  └─ Partial:      0

  Trust Graph
  ├─ Vouched by:   0 agents
  └─ Vouched for:  1 agents

  By Category
  code-review          ██████████░░░░░░░░░░ 0.500
```

### `vouch` — build the trust graph (signed)

```console
$ python3 repforge.py vouch

  Vouch for an Agent

  Registered agents:
  • alice (score: 0.500)
  • bob (score: 0.667)

  Your agent ID (vouching):   Agent ID (being vouched for):   Confidence weight [1.0] (0.0-2.0):
  ✓ alice → bob (weight: 0.8)
```

### `trust` — render the trust graph

```console
$ python3 repforge.py trust

  ╔══════════════════════════════════════════════════╗
  ║  ⚖  TRUST GRAPH                                   ║
  ╚══════════════════════════════════════════════════╝

  alice ──0.8──▶ bob  (source rep: 0.500)
```

### `verify` — prove integrity

```console
$ python3 repforge.py verify

  ╔══════════════════════════════════════════════════╗
  ║  ⚖  LEDGER VERIFY                                 ║
  ╚══════════════════════════════════════════════════╝

  Ledger entries: 3   Vouches: 1
  Identity key:  0f790f6e562ed75d…

  ✓ Integrity OK — chain intact, all signatures valid.
```

Tamper with any line and `verify` exits non-zero and names the exact problem:

```console
$ python3 repforge.py verify

  Ledger entries: 2   Vouches: 0
  Identity key:  6c4ec2d9ca8010d5…

  ✗ 2 integrity problem(s) detected:
  • ledger[0]: content hash mismatch
  • ledger[0]: invalid signature
```

### `audit` — the hashed audit trail

```console
$ python3 repforge.py audit alice

  Audit Trail: alice
  2 entries

    1. success  2026-10-07T22:07:34  code-review
      Review PR #142 for race conditions
      hash: 5687f289bdebc965…

    2. failure  2026-10-07T22:07:34  code-review
      Review PR #143 refactor
      hash: 1724b8fda7bbe7bd…
```

## 🗄 Data Format

Everything lives under `~/.repforge/` (or `$REPFORGE_HOME`):

| File | Purpose |
|------|---------|
| `agents.json` | Registered agents (id → name, provider, url, status) |
| `ledger.jsonl` | Append-only outcome log; one signed, hash-chained JSON object per line |
| `vouches.jsonl` | Append-only signed vouch edges (`source → target`, weight, timestamp) |
| `identity.key` | Your Ed25519 private key (mode 600) — the trust anchor |
| `identity.pub` | Your Ed25519 public key |

Each ledger line is self-describing, signed, and chained:

```json
{
  "agent_id": "alice",
  "outcome": "success",
  "category": "code-review",
  "task": "Review PR #142 for race conditions",
  "timestamp": "2026-10-07T22:07:34.833985+00:00",
  "cost": 0.5,
  "prev_hash": "",
  "pubkey": "0f790f6e562ed75dec2db11142b0c3e9a0cc85057e0e845d883e1a2d084e9977",
  "hash": "5687f289bdebc96539930852a1bcc8a29b330696c93391318b6d200f454d79b2",
  "sig": "pg159uIYCLHyErB1QGvPyjcO…"
}
```

## 🧪 Testing / CI

The [`smoke` workflow](.github/workflows/smoke.yml) runs on every push and PR. It installs PyNaCl, compiles the script, prints `--help`, then drives a full local smoke sequence in a throwaway `REPFORGE_HOME` — register agents, log outcomes, vouch, verify, and assert the ledger was written. No network required.

To reproduce it locally:

```bash
set -euo pipefail
export REPFORGE_HOME="$(mktemp -d)"   # isolate the ledger

printf 'smoke-agent\nSmoke Agent\nCI\nhttps://example.com/smoke\n' | python3 repforge.py register
printf 'smoke-agent\n1\nsmoke\nCI smoke success\n0.0\n'             | python3 repforge.py log
printf 'smoke-agent\n2\nsmoke\nCI smoke failure\n0.0\n'             | python3 repforge.py log
python3 repforge.py verify                                          # exits 0 on intact ledger
python3 repforge.py reputation smoke-agent
python3 repforge.py audit smoke-agent
```

## 🔧 Requirements

- Python 3.8+
- [PyNaCl](https://pynacl.readthedocs.io/) (libsodium Ed25519) — `pip install -r requirements.txt`

## 📄 License

MIT — see [LICENSE](LICENSE).

---

🧰 **[Tool on Hermtica Marketplace](https://hermtica.com/marketplace)**
