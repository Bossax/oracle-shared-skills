# Oracle Inter-Op Protocol Specification (RFC)

## Overview
This specification defines the asynchronous, file-based ticket exchange protocol between sovereign Oracles communicating over `maw-js` (tmux/WSL). Any Oracle can initiate a ticket (as Requester) and any Oracle can service a ticket (as Responder).

---

## 1. The Inbound Ticket Schema (`[ORACLE TICKET]`)

When an Orchestrator dispatches a task to a peer Oracle via `maw hey <target>`, the message MUST follow this structure:

```markdown
# [ORACLE TICKET] <Slug>
- From: <requester_oracle_name>
- Requester Inbox: <requester_root>/ψ/inbox/from-<responder_name>/<timestamp>_<slug>.md
- Topic: <topic>
- Objective: <specific research/audit task with clear boundary>
- Wire Signal: maw hey <requester_oracle_name> "DONE: <slug>"
```

### Field Definitions:
1. **`<Slug>`**: A hyphenated unique slug identifying the inquiry (e.g., `2026-10-09_tmd-authority-audit`).
2. **`From`**: Canonical name of the requesting Oracle (e.g., `arun`, `keth`, `jiu`).
3. **`Requester Inbox`**: The exact target path where the deliverable markdown file must be written. This is dynamically provided by the requesting Oracle.
4. **`Topic`**: High-level subject area (e.g., `Civil Service Regulatory Authority`, `Climate Risk Downscaling`).
5. **`Objective`**: Concrete questions, statutory bounds, permitted databases, or specific deliverable formats requested.
6. **`Wire Signal`**: The exact terminal notification command the responder executes upon writing the file.

---

## 2. The Deliverable Brief Schema (Outbound Deliverable)

The responding Oracle investigates the query using its own sovereign tools, databases, and memory, and deposits a comprehensive markdown brief at the specified `Requester Inbox` path:

```markdown
# [DELIVERABLE BRIEF] <Slug>

**From**: <responder_oracle_name>  
**To**: <requester_oracle_name>  
**Date**: YYYY-MM-DD HH:MM  
**Topic**: <topic>  

---

## Executive Summary
[Concise 2-3 paragraph synthesis answering the core objective directly for human inspection in Obsidian]

## Detailed Analysis & Findings
[Structured analysis, including De Jure vs. De Facto distinctions, table comparisons, or technical models]

## Primary Citations & Evidentiary Grounding
- [Link or row reference to primary legal clause / database record / model file]

---
*Generated via /maw-serve by <responder_oracle_name>*
```

---

## 3. Data Sovereignty & Storage Invariants

1. **Encapsulation**: Requesters NEVER query a specialist's internal databases or raw vector stores across boundaries. Requesters dispatch questions; specialists return synthesized briefs.
2. **Dynamic Inboxes**: The deliverable destination is dynamic, determined exclusively by the requester.
3. **Outbox Archival**: The responding Oracle archives a copy of the sent deliverable in its own `<responder_root>/ψ/outbox/<timestamp>_<slug>.md` for local session accountability.
4. **Memory Preservation**: Responders MUST NOT write uncurated briefs to `ψ/memory/knowledge/`. That directory is reserved strictly for human-curated atomic knowledge. Responders may extract general rules into `ψ/memory/learnings/` only if a genuine universal pattern was discovered.
5. **Wire Notification**: Upon writing the deliverable, the responder executes the `Wire Signal` to wake the requester.
