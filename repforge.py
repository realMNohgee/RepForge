#!/usr/bin/env python3
"""
┌─────────────────────────────────────────────────┐
│  ⚖  REPFORGE  v1.0                              │
│  Agent Reputation Ledger & Trust Registry       │
└─────────────────────────────────────────────────┘

Register agents. Log outcomes. Compute Bayesian trust scores.
Build verifiable reputation graphs. Audit trails included.
Zero dependencies. Pure Python stdlib.
"""

import sys
import os
import json
import hashlib
import time
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

# ── Styling (registry / dark authoritative) ───────────────────
RST   = "\033[0m"
BLD   = "\033[1m"
DIM   = "\033[2m"
GOLD  = "\033[33m"
GRN   = "\033[32m"
RED   = "\033[31m"
CYN   = "\033[36m"
WHT   = "\033[97m"
GRAY  = "\033[90m"
AMBER = "\033[38;5;214m"

DATA_DIR = Path.home() / ".repforge"
AGENTS_FILE = DATA_DIR / "agents.json"
LEDGER_FILE = DATA_DIR / "ledger.jsonl"
VOUCH_FILE  = DATA_DIR / "vouches.jsonl"

# ── Data helpers ──────────────────────────────────────────────
def ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_agents():
    ensure_dir()
    if AGENTS_FILE.exists():
        return json.loads(AGENTS_FILE.read_text())
    return {}

def save_agents(agents):
    ensure_dir()
    AGENTS_FILE.write_text(json.dumps(agents, indent=2))

def load_ledger():
    ensure_dir()
    if LEDGER_FILE.exists():
        entries = []
        for line in LEDGER_FILE.read_text().strip().split("\n"):
            if line:
                entries.append(json.loads(line))
        return entries
    return []

def append_ledger(entry):
    ensure_dir()
    entry["hash"] = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()[:16]
    with open(LEDGER_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def load_vouches():
    ensure_dir()
    if VOUCH_FILE.exists():
        vouches = []
        for line in VOUCH_FILE.read_text().strip().split("\n"):
            if line:
                vouches.append(json.loads(line))
        return vouches
    return []

def append_vouch(entry):
    ensure_dir()
    with open(VOUCH_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ── Reputation scoring ────────────────────────────────────────
def bayesian_score(successes, total):
    """Bayesian weighted score: (successes + 1) / (total + 2).
    Prevents 1/1 from being 100%. Converges to true rate with data."""
    return (successes + 1) / (total + 2)

def compute_reputation(agent_id):
    """Compute full reputation profile for an agent."""
    ledger = load_ledger()
    vouches = load_vouches()
    
    outcomes = [e for e in ledger if e.get("agent_id") == agent_id]
    total = len(outcomes)
    successes = sum(1 for e in outcomes if e.get("outcome") == "success")
    failures = sum(1 for e in outcomes if e.get("outcome") == "failure")
    
    score = bayesian_score(successes, total) if total > 0 else 0.5
    
    # Vouch graph
    vouched_by = [v for v in vouches if v.get("target") == agent_id]
    vouched_for = [v for v in vouches if v.get("source") == agent_id]
    
    # Weighted vouch score: each vouch from a high-rep agent counts more
    vouch_score = 0
    for v in vouched_by:
        source = v.get("source")
        source_rep = compute_reputation(source)["score"]
        vouch_score += source_rep * v.get("weight", 1.0)
    
    # Category breakdown
    by_category = defaultdict(lambda: {"total": 0, "successes": 0})
    for e in outcomes:
        cat = e.get("category", "general")
        by_category[cat]["total"] += 1
        if e.get("outcome") == "success":
            by_category[cat]["successes"] += 1
    
    categories = {}
    for cat, stats in by_category.items():
        categories[cat] = round(bayesian_score(stats["successes"], stats["total"]), 3)
    
    return {
        "agent_id": agent_id,
        "score": round(score, 4),
        "total_tasks": total,
        "successes": successes,
        "failures": failures,
        "vouched_by": len(vouched_by),
        "vouched_for": len(vouched_for),
        "vouch_weight": round(vouch_score, 2),
        "categories": categories
    }


def reputation_tier(score):
    """Human-readable reputation tier."""
    if score >= 0.95: return f"{AMBER}◆◆◆ Diamond{RST}"
    if score >= 0.85: return f"{GOLD}◆◆ Gold{RST}"
    if score >= 0.70: return f"{CYN}◆ Silver{RST}"
    if score >= 0.50: return f"{WHT}◇ Bronze{RST}"
    return f"{GRAY}○ Unproven{RST}"


# ── Commands ─────────────────────────────────────────────────
def cmd_register():
    """Register a new agent."""
    print(f"\n  {WHT}{BLD}Register Agent{RST}\n")
    
    agent_id = input(f"  {BLD}Agent ID{RST}: ").strip()
    if not agent_id:
        print(f"  {RED}Agent ID required.{RST}")
        return
    
    agents = load_agents()
    if agent_id in agents:
        print(f"  {GOLD}⚠ Agent '{agent_id}' already registered.{RST}")
        return
    
    name = input(f"  {BLD}Display name{RST}: ").strip()
    provider = input(f"  {BLD}Provider/creator{RST} {DIM}(optional){RST}: ").strip()
    url = input(f"  {BLD}URL or repo{RST} {DIM}(optional){RST}: ").strip()
    
    agents[agent_id] = {
        "name": name or agent_id,
        "provider": provider,
        "url": url,
        "registered": datetime.now(timezone.utc).isoformat(),
        "status": "active"
    }
    
    save_agents(agents)
    print(f"\n  {GRN}✓ Agent '{agent_id}' registered.{RST}")
    print(f"  {DIM}Log outcomes with: repforge log {agent_id}{RST}")


def cmd_log():
    """Log a task outcome for an agent."""
    agents = load_agents()
    
    if not agents:
        print(f"  {DIM}No agents registered. Register one first:{RST} repforge register")
        return
    
    print(f"\n  {WHT}{BLD}Log Task Outcome{RST}\n")
    
    print(f"  {DIM}Registered agents:{RST}")
    for aid, info in agents.items():
        print(f"  {CYN}•{RST} {aid} {DIM}({info.get('name', '')}){RST}")
    
    agent_id = input(f"\n  {BLD}Agent ID{RST}: ").strip()
    if agent_id not in agents:
        print(f"  {RED}Agent not found. Register first.{RST}")
        return
    
    print(f"\n  {DIM}Outcome:{RST}")
    print(f"  {GRN}1{RST}) success")
    print(f"  {RED}2{RST}) failure")
    print(f"  {GRAY}3{RST}) partial")
    
    choice = input(f"  {BLD}Choice{RST} {DIM}[1]{RST}: ").strip() or "1"
    outcome_map = {"1": "success", "2": "failure", "3": "partial"}
    outcome = outcome_map.get(choice, "success")
    
    category = input(f"  {BLD}Category{RST} {DIM}[general]{RST}: ").strip() or "general"
    task = input(f"  {BLD}Task description{RST} {DIM}(optional){RST}: ").strip()
    cost = input(f"  {BLD}Cost (credits){RST} {DIM}(optional){RST}: ").strip()
    
    entry = {
        "agent_id": agent_id,
        "outcome": outcome,
        "category": category,
        "task": task,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cost": float(cost) if cost else None
    }
    
    append_ledger(entry)
    
    rep = compute_reputation(agent_id)
    print(f"\n  {GRN}✓ Outcome logged.{RST}")
    print(f"  {DIM}Updated reputation: {reputation_tier(rep['score'])} {DIM}({rep['score']:.3f}){RST}")


def cmd_reputation():
    """Show agent reputation."""
    agents = load_agents()
    
    if not agents:
        print(f"  {DIM}No agents registered.{RST}")
        return
    
    # If agent ID provided as argument
    if len(sys.argv) > 2:
        agent_id = sys.argv[2]
        if agent_id not in agents:
            print(f"  {RED}Agent '{agent_id}' not found.{RST}")
            return
        _show_agent_reputation(agent_id, agents)
        return
    
    # Show all
    print(f"\n  {WHT}{BLD}╔══════════════════════════════════════════════════╗{RST}")
    print(f"  {WHT}{BLD}║{RST}  ⚖  REPUTATION REGISTRY{' ' * 28}{WHT}{BLD}║{RST}")
    print(f"  {WHT}{BLD}╚══════════════════════════════════════════════════╝{RST}")
    print()
    
    rows = []
    for agent_id in agents:
        rep = compute_reputation(agent_id)
        rows.append((agent_id, rep))
    
    # Sort by score descending
    rows.sort(key=lambda r: r[1]["score"], reverse=True)
    
    print(f"  {GRAY}{'Agent':<25} {'Tier':>20}  {'Score':>7}  {'Tasks':>5}{RST}")
    print(f"  {DIM}{'─'*60}{RST}")
    
    for agent_id, rep in rows:
        tier = reputation_tier(rep["score"])
        print(f"  {WHT}{agent_id:<25}{RST} {tier}  {rep['score']:>7.3f}  {rep['total_tasks']:>5}")


def _show_agent_reputation(agent_id, agents):
    """Detailed view for a single agent."""
    rep = compute_reputation(agent_id)
    info = agents.get(agent_id, {})
    
    print(f"\n  {WHT}{BLD}╔══════════════════════════════════════════════════╗{RST}")
    print(f"  {WHT}{BLD}║{RST}  ⚖  AGENT PROFILE{' ' * 33}{WHT}{BLD}║{RST}")
    print(f"  {WHT}{BLD}╚══════════════════════════════════════════════════╝{RST}")
    print()
    print(f"  {BLD}Agent ID:{RST}      {WHT}{agent_id}{RST}")
    print(f"  {BLD}Name:{RST}          {info.get('name', '—')}")
    print(f"  {BLD}Provider:{RST}      {info.get('provider', '—')}")
    print(f"  {BLD}Registered:{RST}    {info.get('registered', '—')[:19]}")
    print()
    print(f"  {BLD}Reputation:{RST}     {reputation_tier(rep['score'])} {DIM}({rep['score']:.4f}){RST}")
    print(f"  {BLD}Tasks:{RST}          {rep['total_tasks']} total")
    print(f"  {CYN}├─ Success:{RST}      {rep['successes']}")
    print(f"  {CYN}├─ Failure:{RST}      {rep['failures']}")
    print(f"  {CYN}└─ Partial:{RST}      {rep['total_tasks'] - rep['successes'] - rep['failures']}")
    print()
    print(f"  {BLD}Trust Graph{RST}")
    print(f"  {CYN}├─ Vouched by:{RST}   {rep['vouched_by']} agents")
    print(f"  {CYN}└─ Vouched for:{RST}  {rep['vouched_for']} agents")
    
    if rep["vouch_weight"] > 0:
        print(f"\n  {BLD}Vouch Weight:{RST}   {rep['vouch_weight']:.2f}")
    
    if rep["categories"]:
        print(f"\n  {BLD}By Category{RST}")
        for cat, score in sorted(rep["categories"].items()):
            bar = "█" * min(int(score * 20), 20) + "░" * max(20 - int(score * 20), 0)
            print(f"  {DIM}{cat:<20}{RST} {bar} {score:.3f}")


def cmd_vouch():
    """Vouch for an agent."""
    agents = load_agents()
    
    if len(agents) < 2:
        print(f"  {DIM}Need at least 2 registered agents to vouch.{RST}")
        return
    
    print(f"\n  {WHT}{BLD}Vouch for an Agent{RST}\n")
    
    print(f"  {DIM}Registered agents:{RST}")
    for aid in agents:
        rep = compute_reputation(aid)
        print(f"  {CYN}•{RST} {aid} {DIM}(score: {rep['score']:.3f}){RST}")
    
    source = input(f"\n  {BLD}Your agent ID (vouching){RST}: ").strip()
    if source not in agents:
        print(f"  {RED}Agent not found.{RST}")
        return
    
    target = input(f"  {BLD}Agent ID (being vouched for){RST}: ").strip()
    if target not in agents:
        print(f"  {RED}Agent not found.{RST}")
        return
    
    if source == target:
        print(f"  {RED}Cannot vouch for yourself.{RST}")
        return
    
    weight = input(f"  {BLD}Confidence weight{RST} {DIM}[1.0] (0.0-2.0){RST}: ").strip() or "1.0"
    
    vouch = {
        "source": source,
        "target": target,
        "weight": float(weight),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    append_vouch(vouch)
    print(f"\n  {GRN}✓ {source} → {target} (weight: {weight}){RST}")


def cmd_audit():
    """Show audit trail for an agent."""
    agents = load_agents()
    
    if len(sys.argv) > 2:
        agent_id = sys.argv[2]
    else:
        print(f"  {DIM}Registered agents:{RST}")
        for aid in agents:
            print(f"  {CYN}•{RST} {aid}")
        agent_id = input(f"\n  {BLD}Agent ID to audit{RST}: ").strip()
    
    ledger = load_ledger()
    entries = [e for e in ledger if e.get("agent_id") == agent_id]
    
    if not entries:
        print(f"  {DIM}No ledger entries for '{agent_id}'.{RST}")
        return
    
    print(f"\n  {WHT}{BLD}Audit Trail: {agent_id}{RST}")
    print(f"  {DIM}{len(entries)} entries{RST}\n")
    
    for i, e in enumerate(entries[-20:], 1):
        outcome_color = GRN if e.get("outcome") == "success" else (RED if e.get("outcome") == "failure" else GOLD)
        ts = e.get("timestamp", "")[:19]
        cat = e.get("category", "—")
        task = (e.get("task") or "")[:40]
        h = e.get("hash", "—")
        
        print(f"  {GRAY}{i:>3}.{RST} {outcome_color}{e.get('outcome', '?'):<8}{RST} {DIM}{ts}{RST}  {cat:<15}")
        if task:
            print(f"      {DIM}{task}{RST}")
        print(f"      {GRAY}hash: {h}{RST}")
        print()


def cmd_trust_graph():
    """Display the trust graph."""
    agents = load_agents()
    vouches = load_vouches()
    
    if not vouches:
        print(f"  {DIM}No vouches recorded yet.{RST}")
        return
    
    print(f"\n  {WHT}{BLD}╔══════════════════════════════════════════════════╗{RST}")
    print(f"  {WHT}{BLD}║{RST}  ⚖  TRUST GRAPH{' ' * 35}{WHT}{BLD}║{RST}")
    print(f"  {WHT}{BLD}╚══════════════════════════════════════════════════╝{RST}")
    print()
    
    for v in vouches:
        source_rep = compute_reputation(v["source"])["score"]
        print(f"  {WHT}{v['source']}{RST} {GOLD}──{v['weight']}──▶{RST} {WHT}{v['target']}{RST}  {DIM}(source rep: {source_rep:.3f}){RST}")


def print_banner():
    print(f"""
{GRAY}┌─────────────────────────────────────────────────┐
│{RST}  {BLD}⚖  REPFORGE{RST}  {DIM}v1.0 — Agent Reputation Ledger{GRAY}        │
│{RST}  {DIM}Register. Log. Score. Trust. Audit.{GRAY}                  │
└─────────────────────────────────────────────────┘{RST}
""")


def print_help():
    print(f"""
{WHT}USAGE{RST}
  repforge {DIM}<command> [args]{RST}

{WHT}COMMANDS{RST}
  {GOLD}register{RST}     Register a new agent
  {GOLD}log{RST}          Log a task outcome
  {GOLD}reputation{RST}   Show reputation registry [agent_id]
  {GOLD}vouch{RST}         Vouch for another agent
  {GOLD}audit{RST}         Show audit trail [agent_id]
  {GOLD}trust{RST}         Display trust graph

{WHT}EXAMPLES{RST}
  {DIM}# Register an agent:{RST}
  repforge register

  {DIM}# Log a task outcome:{RST}
  repforge log

  {DIM}# Check reputation:{RST}
  repforge reputation gpt-assistant-1

  {DIM}# Audit trail:{RST}
  repforge audit gpt-assistant-1

{WHT}REPUTATION FORMULA{RST}
  Bayesian score: {DIM}(successes + 1) / (total + 2){RST}
  Prevents 1/1 from being 100%. Converges with data.

{WHT}DATA{RST}
  Stored in {DIM}~/.repforge/{RST}
  JSONL ledger for auditability. Every entry hashed.
""")


def main():
    if len(sys.argv) < 2:
        print_banner()
        print_help()
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd in ('-h', '--help', 'help'):
        print_banner()
        print_help()
    elif cmd == 'register':
        print_banner()
        cmd_register()
    elif cmd == 'log':
        print_banner()
        cmd_log()
    elif cmd in ('rep', 'reputation', 'score'):
        print_banner()
        cmd_reputation()
    elif cmd == 'vouch':
        print_banner()
        cmd_vouch()
    elif cmd == 'audit':
        print_banner()
        cmd_audit()
    elif cmd in ('trust', 'graph'):
        print_banner()
        cmd_trust_graph()
    else:
        print(f"{RED}Unknown command: {cmd}{RST}")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
