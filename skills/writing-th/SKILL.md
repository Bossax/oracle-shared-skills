---
name: writing-th
description: >
  v6.2.0 L-SKLL | Draft, revise, and quality-gate Thai institutional writing.
  Use for Thai policy reports, executive summaries, articles, and formal letters
  when source fidelity, audience fit, and explicit merge approval matter.
metadata:
  origin: project-local/arun-creagy-oracles
  installer: project
---

# /writing-th — Thai Institutional Writing Harness v6.2

Turn technical evidence into decision-ready Thai prose without confusing a
mechanical lint pass with editorial quality — and without asking one context
to formulate arguments, retrieve facts, invent connective reasoning, and draft
formal Thai prose all at once. That overload is what v5.0 got wrong: it went
straight from a metadata contract to a one-shot prose pass, with no argument
artifact in between, and the result was knowledge-telling — facts stitched
together with no rhetorical tension, findings with no "so what."

v6.0's core move: insert `argument-map.json` between scope and prose, and
enforce it as a **context boundary**, not just an added file. Argument
construction gets sources and no style material. Verbalization gets the
approved map and a style kernel, never the raw sources. The parent session
holds only paths, hashes, and gate verdicts — never content.

## Non-negotiable invariants

1. **Draft isolation** — write only to `ψ/incubate/drafts/`, another approved
   scratch location, or the chat. Never overwrite the destination before the
   human explicitly says `Approve`, `Merge`, or `Execute`.
2. **One scoped unit at a time** — do not batch unrelated sections.
3. **No prose before an approved argument map** — physically enforced by the
   `PreToolUse` hook on `Write|Edit`: a write to `ψ/incubate/drafts/**/*draft*.md`
   is denied when the sibling `argument-map.json` is missing or its
   `approval.status` is not `approved`. This is not a convention to remember;
   it cannot be skipped.
4. **Source fidelity** — preserve required evidence, distinctions, tables,
   equations, and frameworks. Compression is governed by the transformation
   mode, not by a universal character ratio.
5. **Three different assurances** — mechanical checks detect encoded
   patterns; Tier 1 review judges whether the argument map's reasoning
   actually holds; Tier 2 review judges whether the prose faithfully
   verbalizes that map. Never call a mechanical pass an editorial approval,
   and never let a Tier 2 pass stand in for Tier 1.
6. **No ledger writes** — do not modify style memory, retrospectives, or the miss
   register except through their own explicitly invoked maintenance skill. The
   ordinary linter may log runs only when repository policy permits it.

## Stage → agent → context map

See [references/subagent-prompts.md](references/subagent-prompts.md) for canonical prompts, model tiers, and invocation snippets.

| Stage | Runs as | Loads | Must never load |
|---|---|---|---|
| 0 Contract | Parent + `AskUserQuestion` / `ask_question` | plan index, source paths, writing plan (if any) | sources, full style pack |
| 1 Argument map | Tier-dependent — orchestrator (small), `fork` (medium/large), or `th-argument-mapper` (`invoke_subagent` / fallback `Agent`) — see Claude Code execution tiers below | `plan_slice` sidecar if named (else writing plan), sources, argument schema, contract `target_altitude`, plus `prior_draft` + revision-mode reference when revising | style pack, lexicon, rubric |
| 2 Blueprint gate | Parent (Plan Mode / Markdown Artifact + `ask_question`) | rendered map summary | everything else |
| 3 Verbalization | Tier-dependent — orchestrator (small), `fork` (medium/large), or `th-verbalizer` (`invoke_subagent` / fallback `Agent`) — see Claude Code execution tiers below | `argument-map.json`, prose kernel, contract `report_specific_rules` & `target_altitude` | raw sources, full pack, rubric |
| 4 Mechanical gate | CLI only | — | nothing enters a model context |
| 5 Editorial review | `th-editorial-reviewer` (`invoke_subagent` / `Agent`) — fresh subagent, never fork, never inline, at every tier | draft, argument map, contract, rubric | sources, style pack, drafting reasoning |
| 6 Merge | CLI + parent | hashes, verdicts | — |

`LEXICON_TH.json` should never enter a model context at any stage —
`lint_thai_writing.py` reads it; only violations need to reach a model.

### Cross-Agent Runtime Mapping

| Primitive | Google Antigravity (AGY) | Claude Code | Codex / Headless CLI |
|---|---|---|---|
| **Human Decision Gates** | `ask_question` modal + Markdown Artifact | `AskUserQuestion` / `ExitPlanMode` | Interactive stdin / prompt |
| **Subagent Spawning** | `invoke_subagent(Role=..., Model="pro"|"flash")` | `Agent(subagent_type="...")` | Isolated prompt session |
| **PreToolUse Hook Gate** | Tool-Execution Reflection Lock + Pre-check script | `PreToolUse` hook (`settings.local.json`) | Shell wrapper / pre-commit |

### Claude Code execution tiers (Stage 1 / Stage 3 only)

This subsection applies to the Claude Code lane only — Antigravity and Codex
invocation is unchanged from the table above.

Stage 1 and Stage 3's "must never load" restrictions are about *content*, not
about whether the stage runs in a fresh subagent. Stage 5's restriction is about
*not sharing the drafting agent's own reasoning* — a fork inherits that
reasoning by design, so Stage 5 stays a fresh, non-fork `Agent()` call at every
tier, no exception. Full detail and invocation snippets are in
[references/subagent-prompts.md](references/subagent-prompts.md) §3.

| Batch | Stage 1 | Stage 3 | Stage 5 |
|---|---|---|---|
| **Small** (1–2 sections) | orchestrator runs it directly, no subagent | orchestrator runs it directly, no subagent | fresh `Agent()` |
| **Medium** (3–6 sections) | `fork` | `fork` | fresh `Agent()` |
| **Large** (7+, or spanning sessions) | `fork`, checkpoint between sections | `fork` | fresh `Agent()` |

At Stage 0, after the contract is approved: count the sections in this batch,
recommend the matching tier, and present it via `AskUserQuestion` — recommended
tier first, the other two as alternatives, each labelled with its expected
subagent-call count. This is the pre-batch check-in — confirming with the human
before launching an expensive multi-section run, not just picking silently.
Record the answer in the contract's `execution_tier`.

**Precondition, checked every time, overrides the tier**: fork or inline is only
safe when the orchestrator's own context is clean of `STYLE_PACK_TH.md`,
`LEXICON_TH.json`, and `editorial-rubric.md`. If the orchestrator has read any of
that material for its own reasoning this session, Stage 1/3 fall back to fresh
`Agent()` calls regardless of tier — record `orchestrator_clean: false` and say
so before proceeding.

**What this does not fix**: there is no way to check remaining 5-hour quota from
inside a session — the tier table bounds the damage of a limit hit (a clean
stopping point between sections instead of several simultaneous mid-write
failures), it cannot predict one. And the large-batch checkpoint is guidance,
not a mechanical gate — nothing stops every call firing in one burst except the
Stage 0 prompt actually running and being honored.

**Exploration scoping**: default to one Explore agent at moderate depth for
pre-Stage-0 reconnaissance; escalate to more only if it returns insufficient.
Three parallel maximum-thoroughness Explore agents before Stage 0 have been the
single largest cost block in at least one prior run, before any drafting began.

### Stage 0 — Contract & Hard Triad Checklist: Ask, Don't Assume

**Execution Boundary**: Stage 0 is executed strictly in the host's native **Plan Mode** (Claude Code `Plan Mode` / Antigravity `/plan` gating mode / Codex conversational plan-stop). No drafting subagents or state-mutating draft writes may run until the plan is frozen and approved.

Before advancing to Stage 1, the orchestrator MUST verify the **Stage 0 Hard Triad Checklist**:
1. **The Outline**: Section scope, heading hierarchy, narrative arc, and paragraph jobs.
2. **The Evidence Base (Macro Grounding)**: Bounded source files (reports, tables, data catalogs) and relevant **trace logs** in `ψ/memory/traces/` discovered via `/trace` or prior sessions.
3. **The Session-Specific Rules**: Active actor (e.g. "คณะที่ปรึกษา" vs "กรมฯ"), target altitude (e.g. executive summary vs technical report), tone/register, and banned framing tropes.

#### The Interactive Plan Co-Creation Protocol
A writing plan may or may not already exist for this unit. Use `AskUserQuestion` (Claude), `ask_question` (Antigravity), or a conversational prompt (Codex) to establish whether one does, and its path — never assume.

- **If an existing writing plan satisfies all 3 checklist items**: It is the primary input. Use `/trace` or `oracle_search` / `oracle_trace` to retrieve the relevant slice and check corresponding trace logs. **MANDATORY**: Explicitly scan for global/section rules (e.g. Section 10 rules, active actor identity, altitude constraints).
  **Write the extracted slice** — the section's brief, the global rules block, relevant trace logs, and evidence-table rows — to a `plan-slice.md` sidecar beside the contract, and record its path in the contract's `plan_slice` field.
- **If missing or incomplete (any of the 3 items missing)**: The orchestrator MUST pause and lead a step-by-step interactive walkthrough:
  1. *Step 1 (Outline)*: Agree on the section's job, core takeaway, and heading breakdown.
  2. *Step 2 (Evidence Base & Trace)*: Run `/trace` or search `ψ/memory/traces/` to identify and verify the exact physical source files and technical ancestry.
  3. *Step 3 (Session Rules)*: Clarify actor convention, target altitude, register, and specific exclusions.
  Write the resulting agreement to `plan-slice.md` and `writing-contract.json`.

Read [references/artifact-schemas.md](references/artifact-schemas.md) before creating `writing-contract.json`. It must lock the audience, decision use, section job, target altitude, report-specific rules, inclusions, exclusions, evidence policy, source paths, trace log paths, and reference samples.

Present a compact contract summary and stop for human approval. Record that approval in the contract (`approval.status: "approved"`).

**Claude Code only**: once approved, also decide the execution tier for Stage 1/3 (see "Claude Code execution tiers" above) and record it in the contract's `execution_tier`. This is a separate confirmation from the contract approval — it is about how the batch runs, not what it says. Once approved, exit Plan Mode to proceed to Stage 1.

### Stage 1 — Argument map

- **Claude Code**: run per `execution_tier.stage_1_3_mode` — the orchestrator performs this stage directly (small), `Agent(subagent_type: "fork", ...)` (medium/large with clean orchestrator context), or fall back to `Agent(subagent_type: "th-argument-mapper", ...)` when the precondition fails. See [references/subagent-prompts.md](references/subagent-prompts.md) §3.
- **Antigravity**: `invoke_subagent(Role="TH Argument Mapper", Model="pro")`, always fresh.
- **Codex**: execute directly in-line with strict context isolation (loading only contract, `plan_slice`, sources, trace logs, and argument schemas; never style files or lexicons).

**Argument Binding Model**:
Whichever runtime runs, it works from the approved contract, the `plan_slice` sidecar if one exists (else the writing plan), the **bounded source files**, and the **trace logs**.
- **Bounded Source Files**: Extract verified empirical metrics, table data, and quotes into Toulmin `grounds`.
- **Trace Logs**: Extract problem triggers `[T]`, technical lineage, and strategic decisions `[D]` into Toulmin `warrants` (the connective reasoning answering "why do these grounds compel this action?") and `application_to_design`.

It produces `argument-map.json`: a Minto governing thought, an SCQA narrative arc, and ordered Toulmin argument units — each with `claim`, `grounds`, `warrant`, `application_to_design`, and a `supports` value that must partition `governing_thought_components`.

**Altitude filter**: When `target_altitude` is `executive-summary`, grounds must prioritize synthesized findings and operational impacts over raw internal acronyms or micro-activity lists.

The mapper validates its own output with `argument_gate.py validate <map>` before reporting done. Do not accept a map that hasn't passed this check.

Do not economize on model or effort here — this is the stage where the thinking v5.0 skipped must actually happen.

**Revision branch**: when the contract names a `prior_draft` — an existing draft being upgraded rather than a section written for the first time — the subagent also loads [references/revision-mode.md](references/revision-mode.md) and follows it. Stage 1 then runs backward from the prior draft's prose before it runs forward from sources, and every unit carries a `recovered` / `repaired` / `new` `provenance` tag. Drafts predating v6.0 are frozen by the Stage 3 hook until this happens, so recovery is the only path that reaches them.

### Stage 2 — Blueprint gate (human)

- **In Claude Code**: Use plan mode: present the governing thought, the SCQA arc, and one line per argument unit, then `ExitPlanMode` for approval via `AskUserQuestion`.
- **In Antigravity**: Render the governing thought, SCQA arc, and argument units as a formatted Markdown Artifact in the workspace, then call `ask_question` with options (Approve, Amend, Reject).
- **In Codex**: Render the governing thought, SCQA arc, and argument units with warrants and design applications directly in the chat, then halt and await explicit human response (`Approve`, `Amend`, `Reject`).

Only once approved does `approval.status` become `"approved"` in `argument-map.json`. This is the field the `PreToolUse` hook / reflection lock checks; nothing else unlocks Stage 3.

### Stage 3 — Verbalization

- **Claude Code**: run per `execution_tier.stage_1_3_mode` decided at Stage 0 — orchestrator direct (small), `fork` (medium/large, clean context), or `Agent(subagent_type: "th-verbalizer", ...)`. Runs at medium reasoning effort.
- **Antigravity**: `invoke_subagent(Role="TH Verbalizer", Model="flash")`, always fresh.
- **Codex**: execute directly in-line, loading only approved `argument-map.json`, [references/prose-kernel.md](references/prose-kernel.md), and contract rules (never raw sources or full style pack).

Whichever runtime runs, it works from the approved `argument-map.json`, [references/prose-kernel.md](references/prose-kernel.md), and the contract's `report_specific_rules`, `target_altitude`, and `terminology` — never the raw sources, never the full `STYLE_PACK_TH.md`. Treat each argument unit's `claim` / `grounds` / `warrant` / `application_to_design` as the paragraph's payload; enforce the contract's active actor identity and report rules. Do not force a four-part structure onto paragraphs the map does not call for. One dominant job per paragraph, matching the unit's `paragraph_job`.

**Bounded amendment path**: if verbalizing a unit reveals its `warrant` doesn't actually hold in real prose, halt and propose an amendment rather than papering over it or silently deviating. The amendment returns to the Stage 2 human gate, gets logged, and the map is re-approved. One bounded loop, not free revision.

Evidence-traceability notes, slide/page locators, prompt scaffolding, and report roadmaps belong outside audience-facing prose. A requested diagram becomes a figure placeholder or actual figure, never an inline arrow chain.

### Stage 4 — Mechanical checks

For report prose, run:

```text
python .agents/skills/writing-th/scripts/lint_thai_writing.py <draft> ψ/memory/style/LEXICON_TH.json --scope report
```

For `rewrite` mode only, also run:

```text
python .agents/skills/writing-th/scripts/check_density.py <source> <draft>
```

`check_density.py` now enforces both a floor (0.8, catches under-preservation) and a ceiling (1.6, catches padding that hides a thin argument). Override either with positional args if a section's transformation genuinely warrants it.

Fix blocking failures. Carry every non-blocking `[STRUCTURAL]`, `[PARENTHETICAL]`, `[ARTIFACT]`, or `[META]` review item into the editorial receipt with a disposition. A green result here means only **mechanical pass**.

### Stage 5 — Editorial review

- **Claude Code**: Always `Agent("th-editorial-reviewer")` run as an independent clean-context subagent call at every batch-size tier.
- **Antigravity**: Always `invoke_subagent(Role="TH Editorial Reviewer", Model="pro")` in a fresh conversation thread.
- **Codex**: If a separate clean Codex session/context is available, run independent review there (`--reviewer-mode independent`). If restricted to single-session linear execution, perform structured self-review and explicitly record `reviewer_mode: self`, `assurance: degraded` in `editorial-review.json` — never representing self-review as independent.

Give the reviewer only the approved contract, the approved argument map, the draft, the selected profile rubric, and a reference sample if one exists. Do not provide the intended verdict or the drafting agent's self-justification.

Read [references/editorial-rubric.md](references/editorial-rubric.md) beforehand. Review runs in two tiers: **Tier 1** judges the argument map's own reasoning (warrant causality, partitioning MECE). **Tier 2** is the per-draft rubric, including `argument_fidelity`.

Create a receipt scaffold with:

```text
python .agents/skills/writing-th/scripts/editorial_gate.py prepare <draft> <contract> --out <review> --reviewer-mode independent
```

Complete every required rubric dimension and record located findings. A
receipt passes only when its verdict is `pass`, all required dimensions pass
(or `source_fidelity` is legitimately `not_applicable` in `new` mode), and no
critical or major finding remains unresolved.

Optionally, run `warrant_trace.py <map> <draft>` first for partial mechanical
Tier 2 coverage — it checks that each approved warrant has a corresponding
claim present in the draft. Genuine semantic judgment still belongs to the
reviewer.

Verify it with:

```text
python .agents/skills/writing-th/scripts/editorial_gate.py verify <draft> <contract> <review>
```

Any draft or contract change invalidates the receipt. Review the new hashes.

### Stage 6 — Human bridge and merge

Present the draft with its editorial assurance and unresolved minor findings.
Merge only after explicit human approval:

```text
python .agents/skills/writing-th/scripts/merge_draft.py <draft> <dest> --lexicon ψ/memory/style/LEXICON_TH.json --contract <contract> --review <review> [--source <source>]
```

Merge reruns mechanical checks, verifies the exact receipt hashes, and
confirms that all emitted review items have dispositions. `--skip-gates`
remains a loud, deliberate override; never infer permission to use it.

## Maintenance

- After a style-capture round, validate the lexicon with
  `validate_lexicon.py`; do not edit style memory from this skill.
- After changing canonical `SKILL.md` or `references/`, run
  `check_skill_drift.py --sync`.
- Run `tests/run_tests.py` after any harness change.
- A behaviorally significant revision requires a blind forward test in an
  isolated temporary workspace. Use an independent reviewer when delegation is
  available; otherwise document that the test used degraded self-review.
