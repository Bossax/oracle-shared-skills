# Revision Mode — Stage 1 Map Recovery from an Existing Draft

Load this only when the approved `writing-contract.json` names a `prior_draft`.

The ordinary Stage 1 path builds an argument map forward from sources. Revision
mode runs Stage 1 **backward from prose first, then forward from sources** — it
recovers the argument a finished draft is already making, repairs what that draft
left implicit, and adds what the writing plan requires but the draft skipped.

This exists because drafts written before the argument map was part of the harness
are frozen: `check_draft_preconditions.py` denies every `Write|Edit` on
`ψ/incubate/drafts/**/*draft*.md` without an approved sibling map, and its own
denial text says prose "cannot be written **or revised**". Recovering the map is
the only way through, and it is also the right way — the map is what makes the
draft's weaknesses inspectable.

## Why not just redraft

A prior draft is not only text. It carries decisions a human already made and
approved, recorded in the contract's `approval.basis`. Discarding the draft
discards those decisions silently, and the next draft re-litigates settled ground.
Recovery keeps them and makes each one visible as a unit that can be judged.

## What you read

Everything ordinary Stage 1 reads, plus the `prior_draft` named in the contract.
Read the prior draft **first**, before the sources — you are recovering an
argument, not writing a fresh one, and reading sources first pulls you toward
rebuilding from scratch.

Style material is still prohibited. `STYLE_PACK_TH.md` and `LEXICON_TH.json` have
no place here. The prior draft's diction is not your concern; its argument is.

## The three provenance tags

Every unit in the recovered map carries a `provenance` field:

- **`recovered`** — the prior draft already argues this, and the argument holds.
  Keep the claim's substance. You may sharpen wording, but a `recovered` claim is
  not silently redirected: if the claim is wrong, retag it `repaired` and say what
  changed, so the change is reviewable instead of invisible.
- **`repaired`** — the prior draft argues this, but incompletely. This is the
  common case. A v5-era paragraph typically carries a `claim` and its `grounds`
  and stops there, with the `warrant` left implicit and no
  `application_to_design` at all. Recover the claim and grounds from the draft,
  then supply the missing connective reasoning from the sources.
- **`new`** — the writing plan requires this and the prior draft does not have it.
  Build it the ordinary way, forward from sources.

`provenance` is advisory metadata. `argument_gate.py` does not check it; the
Stage 2 gate and the Stage 5 reviewer read it.

## What recovery must do

1. **Recover before you repair.** Walk the prior draft paragraph by paragraph and
   name the claim each one is making. A paragraph making no claim is itself a
   finding — report it rather than inventing a claim to cover it.
2. **Supply the missing warrant.** This is the main work. Ask of each recovered
   claim: why do these grounds compel it? If the sources do not answer, say so in
   your report instead of writing a plausible-sounding bridge.
3. **Supply `application_to_design`.** A finding with no stated consequence for the
   deliverable is the exact defect that produced this stage. Every unit needs one.
4. **Add what the plan requires and the draft skipped.** The writing plan's own
   consistency and acceptance tables are the checklist. Tag these `new`.
5. **Resolve duplication across sections.** When two sections of the same chapter
   carry the same argument, assign it to one and drop it from the other. Note the
   removal in your report.
6. **Apply the structural rules.** `STRUCTURAL_RULES_TH.json` applies exactly as it
   does in ordinary Stage 1. A prior draft that renders a countable parallel set as
   a running prose chain is violating a structural rule, not expressing a style
   preference.
7. **Validate.** Run `argument_gate.py validate` on your own output before
   reporting done.

## What recovery must not do

- Do not treat the prior draft as a source of fact. It is a source of *argument*.
  Every ground still has to trace to real source material.
- Do not preserve the prior draft's paragraph order as if it were the argument's
  order. `order` reflects the argument's logic, not the old text's layout.
- Do not carry a prior claim forward because it is already written. A claim that
  the sources do not support gets reported, not recovered.

## Report back

Alongside the map, report per section: how many units are `recovered`, `repaired`,
`new`; which claims from the prior draft you did **not** carry forward and why;
any warrant the sources would not support; and any duplication you resolved. This
list is what the human sees in place of reading two drafts side by side.

## Downstream effects

- **Stage 3** verbalizes the approved map fresh. It does not edit the prior text.
  The verbalizer never sees the prior draft — the map is the whole handoff.
- **Stage 4** does not gain a density check. Keep `transformation_mode` at
  `synthesis` or `new` as the section's actual transformation warrants;
  `rewrite` exists for source-to-prose transformation, and its 0.8/1.6 character
  ratio is measured against a source document, not a prior draft. Running
  `check_density.py` against the prior draft is a useful advisory reading of how
  much a section grew, and nothing more.
- **Stage 5** is where preservation is actually checked. `warrant_trace.py` must
  find every `recovered` unit's claim present in the new draft; a `recovered` unit
  reported `NOT FOUND` or `WEAK` means the rewrite dropped something a human had
  already approved. Tier 2's `source_fidelity` dimension judges the rest.
