# Editorial Rubric v6.0.0

This rubric governs semantic review. It is not a replacement for source
verification or the mechanical linter.

As of v6.0 review has two tiers. Tier 1 judges the approved argument map
itself — apply it before reading the draft, so a bad argument is not
laundered by good prose. Tier 2 is the original per-draft rubric below,
renamed but unchanged in substance, and now judges fidelity to the map rather
than fidelity to a brief alone.

## Tier 1 — Argument-map integrity (v6.0)

`argument_gate.py validate` already checks structure (every `warrant`
non-empty, `supports` values partition `governing_thought_components`, no
duplicate `unit_id`). This tier checks what the script cannot: whether the
reasoning actually holds.

1. **warrant_soundness** — Read each unit's `claim`, `grounds`, and
   `warrant`. Does the warrant actually connect the grounds to the claim, or
   does it restate the claim in different words? A warrant that just repeats
   its claim passes `argument_gate.py`'s non-empty check but fails this
   dimension.
2. **mece_coverage** — `governing_thought_components` are structurally
   covered by `argument_gate.py`; confirm they are *substantively* covered —
   the components genuinely partition the governing thought rather than
   restating one idea under different names to satisfy the mechanical check.
3. **application_grounded** — Each unit's `application_to_design` must follow
   from its own `warrant`, not from a different unit's reasoning or from
   background knowledge the map never states.

A `pass` on Tier 1 is required before Tier 2 review proceeds. If Tier 1
fails, return the map to the Stage 2 human gate rather than reviewing prose
built on it — this is what stops a passing editorial receipt from certifying
a causal bridge that was never actually established (see `STYLE_PACK_TH.md`'s
2026-08-28 entry on the Section 1.2 ownership-distribution inference).

## Tier 2 — Prose fidelity (core dimensions)

Every review must decide each dimension with `pass`, `fail`, or, where allowed,
`not_applicable` and cite a location or concrete reason.

1. **section_job** — The section performs the one job approved in the contract
   and does not repeat adjacent sections or drift into excluded work.
2. **audience_decision_value** — The prose foregrounds what the intended reader
   needs to understand, decide, fund, govern, or do; it does not foreground the
   consultant's workflow without a reader-facing reason.
3. **evidence_payload** — Each substantive argument unit contains enough claim,
   concrete evidence, consequence, and mechanism to support its purpose. These
   elements may span more than one paragraph.
4. **causal_logic** — Evidence, interpretation, consequence, and response are
   connected without reversed causality, unsupported leaps, or decorative
   transitions.
5. **argument_fidelity** (v6.0) — The draft verbalizes the approved
   `argument-map.json` faithfully: every unit's claim and warrant appears in
   the prose (not necessarily verbatim), no unit is silently dropped, and no
   claim in the draft is absent from the map. `warrant_trace.py`, where run,
   gives partial mechanical coverage of this dimension; the reviewer's own
   read is still required for genuine fidelity, not just claim presence.
6. **reader_facing_appropriateness** — No sourcing metadata, prompt residue,
   internal artifact locators, fake diagrams, or commentary about the document's
   upcoming structure remains in final prose.
7. **terminology_agency** — Terms remain stable and comprehensible; named actors
   perform the actions they actually own; project, consultant, client, and system
   are not substituted for one another.
8. **source_fidelity** — Required concepts, caveats, distinctions, quantitative
   values, and technical structures survive according to the contract. Only
   `new` mode may use `not_applicable`.
9. **form_readability** — Paragraphs, lists, tables, and figure placeholders
   match the information shape. No rule against rhetorical enumeration may be
   misapplied as a ban on useful lists.

## Executive-summary profile

Apply these additional dimensions when `profile` is `executive-summary`:

1. **altitude** — The section stays at decision-maker depth. It synthesizes
   detail instead of reproducing full-report methods, per-platform treatment,
   or evidence tables excluded by the contract.
2. **headline_conclusion** — The reader can identify the governing finding or
   decision consequence without reconstructing it from project activities.
3. **findings_over_process** — National or institutional stakes, findings, and
   resulting decisions take priority over descriptions of how the team worked.

An executive-summary opening should normally establish a concrete stake or
finding, interpret why it matters, and position the deliverable as the response.
Generic scene setting such as “ในปัจจุบัน...” is insufficient unless followed
immediately by concrete evidence that earns it.

## Other profiles

- **report** — Require complete technical distinctions, traceable evidence,
  explicit limitations, and sufficient implementation detail for the section's
  approved job.
- **article** — Require a clear thesis, reader-oriented progression, evidence
  attribution, and accessible explanation without weakening factual precision.
- **letter** — Require an explicit purpose, recipient-relevant context, requested
  action, responsible actor, and deadline or next step when applicable.

## Review protocol

1. Read the approved contract before the draft.
2. Read the draft once for the reader's experience, then again against every
   inclusion, exclusion, and required concept.
3. Locate findings precisely. Do not accept the drafting agent's summary as
   evidence of compliance.
4. Classify findings:
   - `critical`: fabricated evidence, wrong audience/artifact, reversed core
     logic, or content that makes the deliverable unsafe to use.
   - `major`: scope/altitude failure, missing governing conclusion, lost required
     substance, internal artifact leakage, or systematic reader confusion.
   - `minor`: local clarity, grammar, formatting, or terminology defect that does
     not change the governing meaning.
5. A `pass` receipt may contain only resolved critical/major findings. Minor
   findings may be unresolved only when their disposition explicitly accepts
   them for human review.
6. If the draft changes, discard the verdict and review the new hash.

