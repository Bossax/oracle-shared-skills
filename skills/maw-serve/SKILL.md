---
name: maw-serve
description: >
  Specialist Inbound Responder for MAW tickets. Enables any Oracle to parse inbound
  [ORACLE TICKET] messages, conduct sovereign domain investigation, deposit deliverables
  directly into the requester's inbox, archive an outbox copy, and fire the completion wire signal.
  Use when receiving an inquiry or task from a peer Oracle via MAW.
metadata:
  origin: oracle-shared-skills
  installer: project
---

# /maw-serve — Sovereign Inbound Responder for MAW

> "Investigate autonomously. Deliver directly. Archive locally."

## 1. When to Use
Use `/maw-serve` when you receive a task or message from a peer Oracle via `maw hey` or find an incoming ticket in `ψ/inbox/`.

---

## 2. Inbound Ticket Recognition

An inbound ticket follows the standard protocol schema:
```markdown
# [ORACLE TICKET] <Slug>
- From: <requester_oracle_name>
- Requester Inbox: <requester_root>/ψ/inbox/from-<responder_name>/<timestamp>_<slug>.md
- Topic: <topic>
- Objective: <specific research/audit task>
- Wire Signal: maw hey <requester_oracle_name> "DONE: <slug>"
```

---

## 3. The 4-Step Servicing Workflow

### Step 1: Parse Objective & Bounds
Extract:
- Who is asking? (`From`)
- Where must the output be delivered? (`Requester Inbox`)
- What specific questions or boundaries were set? (`Objective`)

### Step 2: Conduct Sovereign Investigation
Query your internal tools, local databases, and specialized memory without leaking raw databases:
- **Keth**: Query `src/data/bureaucrazy.sqlite`, NotebookLM regulatory collections.
- **Jiu**: Query CRI models, disaster rasters, DaLA/PDNA analysis templates.
- **Lauren**: Inspect Common Data Model entities, database schemas.
- **Creagy-Writing**: Apply institutional writing guidelines, prose polish.

### Step 3: Author the Deliverable Brief
Structure your response as a standalone Markdown deliverable:
```markdown
# [DELIVERABLE BRIEF] <Slug>

**From**: <your_oracle_name>  
**To**: <requester_oracle_name>  
**Date**: YYYY-MM-DD HH:MM  
**Topic**: <topic>  

---

## Executive Summary
[Direct, clear 2-3 paragraph answer to the objective]

## Detailed Analysis & Findings
[Deep statutory, technical, or analytical breakdown with De Jure vs. De Facto distinctions]

## Primary Citations & Evidentiary Grounding
- [Explicit link/reference to laws, database tables, or models used]
```

### Step 4: Deposit, Archive & Signal
Run `complete_ticket.ps1`:
```powershell
pwsh -File .agents/skills/maw-serve/scripts/complete_ticket.ps1 `
    -Requester "<requester>" `
    -Slug "<slug>" `
    -DeliverableFile "<path_to_drafted_brief>" `
    -RequesterInboxPath "<requester_inbox_path_from_ticket>" `
    -ResponderRoot (Get-Location).Path
```
This automatically:
1. Copies the brief into the requester's inbox.
2. Archives a permanent copy in your own `ψ/outbox/<timestamp>_<slug>.md`.
3. Fires `maw hey <requester> 'DONE: <slug>'` across WSL.

---

## 4. Hard Rules
1. **Never Write to `ψ/memory/knowledge/`**: That folder is reserved exclusively for human-curated atomic knowledge. Use `ψ/outbox/` for archival.
2. **Encapsulation**: Answer with synthesized findings, not raw database dumps.
3. **Always Fire Wire Signal**: Ensure the requester knows the task is complete so their OS waiter terminates cleanly.
