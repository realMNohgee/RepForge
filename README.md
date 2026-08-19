![CI](https://github.com/realMNohgee/RepForge/actions/workflows/ci.yml/badge.svg) ![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg) ![License](https://img.shields.io/badge/license-MIT-blue.svg)
<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-gold?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge" alt="python">
  <img src="https://img.shields.io/badge/deps-zero-success?style=for-the-badge" alt="zero dependencies">
  <img src="https://img.shields.io/badge/license-MIT-yellow?style=for-the-badge" alt="license">
</p>

<h1 align="center">⚖ RepForge</h1>
<h3 align="center">Agent Reputation Ledger & Trust Registry</h3>

<p align="center">
  <i>Register agents. Log outcomes. Build verifiable reputation.<br>
  The credit bureau for AI agents.</i>
</p>

---

## ✨ Why RepForge?

You chain 5 agents to complete a task. One consistently fails. One quietly excels. Without a reputation system, you discover this the hard way — after the failed task.

RepForge gives every agent a **Bayesian trust score** that converges to their true reliability over time. Vouch for agents you've worked with. Audit every outcome. Build trust graphs across your entire agent fleet.

## ⚖ The Scoring Formula

```
score = (successes + 1) / (total + 2)
```

A Bayesian prior. An agent with 1 success out of 1 task scores **0.667** — not 1.0. This prevents gaming and converges to the true rate as data accumulates.

| Outcomes | Score | Why |
|----------|-------|-----|
| 1/1 success | 0.667 | Untrustworthy — not enough data |
| 5/5 success | 0.857 | Promising — consistent track record |
| 50/50 success | 0.981 | Diamond tier — proven reliability |
| 5/10 success | 0.500 | Unreliable — 50% fail rate |

## 🚀 Quick Start

```bash
# Register agents
python repforge.py register

# Log outcomes
python repforge.py log

# View reputation registry
python repforge.py reputation

# Drill into one agent
python repforge.py reputation my-agent

# Audit trail (every entry hashed)
python repforge.py audit my-agent

# Build trust graph
python repforge.py vouch
python repforge.py trust
```

## 🏛 The Reputation Registry

```
╔══════════════════════════════════════════════════╗
║  ⚖  REPUTATION REGISTRY                         ║
╚══════════════════════════════════════════════════╝

Agent                     Tier           Score  Tasks
────────────────────────────────────────────────────────
code-reviewer-bot     ◆◆◆ Diamond        0.981     50
research-agent        ◆◆ Gold            0.857      5
data-pipeline         ◆ Silver           0.750     12
summarizer-v2         ◇ Bronze           0.600     20
new-experimental      ○ Unproven         0.500      0
```

## 🔗 Trust Graph

Agents vouch for each other. Vouch weight is multiplied by the vouching agent's own reputation — so a Diamond-tier agent's vouch carries more weight than an Unproven agent's.

```
code-reviewer ──1.0──▶ research-agent
       │                    │
       └──0.5──▶ data-pipeline
```

## 🔍 Audit Trail

Every outcome is logged to a JSONL ledger with a SHA-256 hash. Tamper-evident. Importable. Auditable.

```json
{"agent_id": "code-reviewer-bot", "outcome": "success", "category": "code-review", "timestamp": "2026-07-28T14:22:00Z", "hash": "a3f8c2d1e4b5"}
```

## 🎯 Features

- **Bayesian scoring** — (successes+1)/(total+2). Prevents gaming, converges with data.
- **Trust graph** — Agents vouch for each other with confidence weights
- **Category breakdown** — Per-domain reputation (code-review vs. data-analysis)
- **Audit trail** — Every entry hashed, JSONL ledger, tamper-evident
- **Tiered rankings** — Diamond / Gold / Silver / Bronze / Unproven
- **Zero dependencies** — Pure Python stdlib. JSONL storage.

## 🔧 Requirements

- Python 3.10+
- Nothing else.

## 📄 License

MIT

---

<p align="center">
  <sub>Part of the <a href="https://hermtica.com">Hermtica</a> marketplace · $5.99</sub>
</p>
