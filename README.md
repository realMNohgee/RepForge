[![CI](https://github.com/realMNohgee/RepForge/actions/workflows/smoke.yml/badge.svg)](https://github.com/realMNohgee/RepForge/actions/workflows/smoke.yml)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)

# ⚖ RepForge

**A local, file-based reputation ledger for AI agents — register agents, log outcomes, and compute tamper-evident Bayesian trust scores. Zero dependencies.**

RepForge is the credit bureau for your agent fleet. Every task outcome is written to an append-only, SHA-256-hashed JSONL ledger; every agent gets a Bayesian trust score that converges to its true reliability as evidence accumulates; and agents can vouch for one another to form a weighted trust graph. It runs entirely offline — no server, no account, no network.

---

## ✨ Why RepForge?

You chain five agents to complete a task. One consistently fails. One quietly excels. Without a reputation system, you find out the hard way — *after* the task breaks.

RepForge turns "which agent should I trust?" into a number you can audit:

- **Bayesian scoring** — `(successes + 1) / (total + 2)`. A single success is *not* 100%; the score converges to the true success rate as data accumulates, so agents can't game it with one lucky run.
- **Tamper-evident audit trail** — every outcome is appended to a JSONL ledger with a SHA-256 hash.
- **Weighted trust graph** — agents vouch for each other; a vouch's weight is scaled by the voucher's own reputation.
- **Per-category breakdowns** — separate reliability for `code-review` vs. `research` vs. anything else.
- **Tiered rankings** — Unproven → Bronze → Silver → Gold → Diamond.
- **Zero dependencies** — pure Python 3.8+ standard library. Data lives in `~/.repforge/`.

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

No install, no dependencies — clone and run:

```bash
git clone https://github.com/realMNohgee/RepForge.git
cd RepForge
python3 repforge.py --help
```

```
┌─────────────────────────────────────────────────┐
│  ⚖  REPFORGE  v1.0 — Agent Reputation Ledger        │
│  Register. Log. Score. Trust. Audit.                  │
└─────────────────────────────────────────────────┘


USAGE
  repforge <command> [args]

COMMANDS
  register     Register a new agent
  log          Log a task outcome
  reputation   Show reputation registry [agent_id]
  vouch         Vouch for another agent
  audit         Show audit trail [agent_id]
  trust         Display trust graph

EXAMPLES
  # Register an agent:
  repforge register

  # Log a task outcome:
  repforge log

  # Check reputation:
  repforge reputation gpt-assistant-1

  # Audit trail:
  repforge audit gpt-assistant-1

REPUTATION FORMULA
  Bayesian score: (successes + 1) / (total + 2)
  Prevents 1/1 from being 100%. Converges with data.

DATA
  Stored in ~/.repforge/
  JSONL ledger for auditability. Every entry hashed.
```

## 🧭 Command Tour

Every block below is real captured output (ANSI colors stripped; the `REPFORGE` banner is omitted after the first command for brevity).

### `register` — add an agent

```console
$ python3 repforge.py register

  Register Agent

  Agent ID:   Display name:   Provider/creator (optional):   URL or repo (optional): 
  ✓ Agent 'code-reviewer-bot' registered.
  Log outcomes with: repforge log code-reviewer-bot
```

> Prompts read `Agent ID`, `Display name`, `Provider/creator`, and `URL or repo`. Here the answers were `code-reviewer-bot`, `Code Reviewer Bot`, `Nous Research`, `https://github.com/realMNohgee/RepForge`.

### `log` — record a task outcome

```console
$ python3 repforge.py log

  Log Task Outcome

  Registered agents:
  • code-reviewer-bot (Code Reviewer Bot)
  • research-agent (Research Agent)

  Agent ID: 
  Outcome:
  1) success
  2) failure
  3) partial
  Choice [1]:   Category [general]:   Task description (optional):   Cost (credits) (optional): 
  ✓ Outcome logged.
  Updated reputation: ◇ Bronze (0.667)
```

> Choices were `code-reviewer-bot` → `success` → category `code-review` → task `"Review PR #142 for race conditions"` → cost `0.5`. The updated tier is printed immediately after logging.

### `reputation` — the registry

```console
$ python3 repforge.py reputation

  ╔══════════════════════════════════════════════════╗
  ║  ⚖  REPUTATION REGISTRY                            ║
  ╚══════════════════════════════════════════════════╝

  Agent                                     Tier    Score  Tasks
  ────────────────────────────────────────────────────────────
  research-agent            ◇ Bronze    0.667      1
  code-reviewer-bot         ◇ Bronze    0.600      3
```

### `reputation <agent_id>` — a single agent's profile

```console
$ python3 repforge.py reputation code-reviewer-bot

  ╔══════════════════════════════════════════════════╗
  ║  ⚖  AGENT PROFILE                                 ║
  ╚══════════════════════════════════════════════════╝

  Agent ID:      code-reviewer-bot
  Name:          Code Reviewer Bot
  Provider:      Nous Research
  Registered:    2026-10-07T18:09:04

  Reputation:     ◇ Bronze (0.6000)
  Tasks:          3 total
  ├─ Success:      2
  ├─ Failure:      0
  └─ Partial:      1

  Trust Graph
  ├─ Vouched by:   0 agents
  └─ Vouched for:  1 agents

  By Category
  code-review          ████████████░░░░░░░░ 0.600
```

### `vouch` — build the trust graph

```console
$ python3 repforge.py vouch

  Vouch for an Agent

  Registered agents:
  • code-reviewer-bot (score: 0.600)
  • research-agent (score: 0.667)

  Your agent ID (vouching):   Agent ID (being vouched for):   Confidence weight [1.0] (0.0-2.0): 
  ✓ code-reviewer-bot → research-agent (weight: 0.8)
```

### `trust` — render the trust graph

```console
$ python3 repforge.py trust

  ╔══════════════════════════════════════════════════╗
  ║  ⚖  TRUST GRAPH                                   ║
  ╚══════════════════════════════════════════════════╝

  code-reviewer-bot ──0.8──▶ research-agent  (source rep: 0.600)
```

### `audit` — the hashed audit trail

```console
$ python3 repforge.py audit code-reviewer-bot

  Audit Trail: code-reviewer-bot
  3 entries

    1. success  2026-10-07T18:09:04  code-review    
      Review PR #142 for race conditions
      hash: 75671a46e510dcf8

    2. success  2026-10-07T18:09:04  code-review    
      Review PR #143 refactor
      hash: 75e1d8f25ba3e6a9

    3. partial  2026-10-07T18:09:04  code-review    
      Review docs-only PR
      hash: 19491546e0afb791
```

## 🗄 Data Format

Everything lives under `~/.repforge/`:

| File | Purpose |
|------|---------|
| `agents.json` | Registered agents (id → name, provider, url, status) |
| `ledger.jsonl` | Append-only outcome log; one JSON object per line, each with a SHA-256 `hash` |
| `vouches.jsonl` | Append-only vouch edges (`source → target`, weight, timestamp) |

Each ledger line is self-describing and importable:

```json
{"agent_id": "code-reviewer-bot", "outcome": "success", "category": "code-review", "task": "Review PR #142 for race conditions", "timestamp": "2026-10-07T18:09:04.626454+00:00", "cost": 0.5, "hash": "75671a46e510dcf8"}
```

## 🧪 Testing / CI

The [`smoke` workflow](.github/workflows/smoke.yml) runs on every push and PR. It compiles the script, prints `--help`, then drives a full local smoke sequence in a throwaway `HOME` — register an agent, log outcomes, and compute trust — so the runner's real home stays clean. No network required.

To reproduce it locally:

```bash
set -euo pipefail
export HOME="$(mktemp -d)"            # isolate the ledger
printf 'smoke-agent\nSmoke Agent\nCI\nhttps://example.com/smoke\n' | python3 repforge.py register
printf 'smoke-agent\n1\nsmoke\nCI smoke success\n0.0\n'             | python3 repforge.py log
python3 repforge.py reputation smoke-agent
```

## 🔧 Requirements

- Python 3.8+ (standard library only)
- Nothing else.

## 📄 License

MIT — see [LICENSE](LICENSE).

---

🧰 **[Tool on Hermtica Marketplace](https://hermtica.com/marketplace)**
