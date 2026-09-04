---
name: style-capture
description: Incrementally learns and refines writing styles from individual samples or draft/edit pairs. Maintains a persistent cumulative "Style-Pack" in project memory.
---

# /style-capture

> A cumulative learning engine for writing style mimicry. It extracts linguistic patterns, structural DNA, and lexicon preferences from single samples or "Draft vs. Edited" comparisons, merging them into a persistent context-specific **Style-Pack**.

## When to use this skill

- When you have a **single gold-standard sample** and want to start a new style context.
- When you have a **Draft vs. Edited pair** and want to capture "Corrective Patterns" (what to fix/avoid).
- When you want to **incrementally improve** an existing style guide as more examples become available.
- When you want to generate a **Master Implementation Prompt** for a specific writing style.

## When NOT to use this skill

- For general project retrospectives (use `/rrr`).
- For simple file editing without stylistic extraction goals.
- For learning technical facts or code patterns (use `oracle_learn` directly).

## Inputs required

1) **Context**: (e.g., `Thai-Institutional`, `Tech-Blog`, `Executive-Summary`). This determines which `Style-Pack` to update.
2) **Source Type**:
    - `Sample`: A single file path representing the target style.
    - `In-Place / Single File (Smart Diff Resolver)`: A single file path representing an edit. The agent automatically resolves the diff using the fallback ladder: working copy `git diff` → latest commit history (`git log -p -1` / `HEAD~1..HEAD`) → sibling baseline (`.pre-*.md`, `.draft.md`).
    - `Refinement (Two-File)`: An explicit pair of file paths (Draft vs. Edited) representing separate versions.
3) **Paths**:
    - For `Sample`: `sample_path`.
    - For `In-Place / Single File`: `file_path`.
    - For `Refinement`: `draft_path` and `edited_path`.
4) (Optional) **Focus**: Specific stylistic area to focus on (e.g., "Hedging," "Paragraph transitions").

---

## Workflow

1) **Initialization & Context Loading**
    - Check for existing artifacts in `ψ/memory/style/`:
        - `STYLE_PACK_<CONTEXT>.md`
        - `LEXICON_<CONTEXT>.json`
        - `STRUCTURAL_RULES_<CONTEXT>.json`
    - If they do not exist, initialize them using the "Cold Start" template.

2) **Reading & Pre-processing (Smart Diff Resolver)**
    - If `Sample` mode: Read the file.
    - If `In-Place / Single File` mode: Resolve the edit delta using this strict resolution ladder:
        1. **Working Copy**: Run `git diff <file_path>`. If non-empty, use deleted lines as draft and added lines as human edits.
        2. **Committed Revision**: If working copy diff is empty, inspect Git commit history: run `git log -p -1 <file_path>` or `git diff HEAD~1..HEAD -- <file_path>`. If changes were committed, extract the delta from that commit.
        3. **Sibling Baseline**: If git history shows no recent edit, search the sibling directory for baseline files (e.g. `*.pre-*.md`, `*.draft.md`, `02_th_draft.pre-1.1-revision.md`). If found, run `git diff --no-index <sibling_baseline> <file_path>`.
        4. **CRITICAL GUARD**: NEVER switch or wander off to an unrelated dirty file in `git status`. If no diff is found on the requested file across steps 1–3, halt and explicitly ask the user for the commit hash or baseline comparison path.
    - If `Refinement (Two-File)` mode: Read both files and perform a semantic comparison to identify specifically **what the human changed** (Word choice, re-ordering, tone shifts, structural restructuring).

3) **Intermediate Evidence Materialization (Diff Log)**
    - If `In-Place / Single File` or `Refinement` mode: **run the computed
      word-diff first, before writing anything by hand**:
      `python .agents/skills/writing-th/scripts/diff_word_table.py --git <file_path>`
      (or `--before <draft_path> --after <edited_path>` for `Refinement`
      mode). This is a forcing function, not a nice-to-have — on 2026-08-30
      the "scan every word by hand" instruction below was skipped on a live
      run (only paragraph-level cuts were caught; every word-level swap
      inside a rewritten sentence was missed) until the user asked directly.
      A computed table can't be silently skipped the way a prose reminder
      can. Every row it prints must be dispositioned in step 4 — mapped to a
      lexical category, or explicitly marked "not lexical — structural."
    - Save a date-stamped diff evidence file to `ψ/memory/style/evidence/<YYYY-MM-DD>_<HH-MM>_<CONTEXT>_diff-evidence.md`.
    - This file records the specific delta of this run, preserving the project history for future statistical aggregation.
    - The file must document:
        - **Metadata**: Timestamp, session ID, source mode (In-Place Single File or Two-File Refinement), file paths, and context.
        - **Concrete Diff Log**: Direct line-by-line word-for-word changes, formatting transformations, and annotations (`%%...%%`).
        - **Exhaustive Word-by-Word Lexicon Table**: Build this FROM the `diff_word_table.py` output rows, not by re-reading the diff by eye. A structured markdown table enumerating EVERY changed token/phrase pair with columns: `Banned/Draft`, `Preferred/Edit`, `Category`, `Institutional Rationale`.
        - **Linguistic Shift**: Specific grammar, tone, or structural changes observed.
        - **Candidate Rules**: Categorized by layer (`lexical`, `regex`, or `structural`).

4) **Pattern Extraction (Research Phase — Mandatory Zero-Drop Lexical Audit)**
    - **CRITICAL DIRECTIVE: ZERO-DROP LEXICAL SCAN**
      Never summarize only high-level structural patterns while ignoring granular word-by-word edits. Working row-by-row from step 3's `diff_word_table.py` output (not from re-reading prose), classify EVERY changed word, term, particle, or phrase across 5 lexical categories:
        1. **Domain Collocation & Calque Banning**: Catch literal translations from English that sound awkward in institutional Thai (e.g., `กำหนดหลักร่วม` ➔ `กำหนดหลักการ`, `ขีดความสามารถรองรับ` ➔ `กลไกข้อมูลเพื่อสนับสนุน`).
        2. **Institutional Domain Precision**: Catch domain terms used inappropriately in the agency's operational context (e.g., `ผู้รับคำเตือน` ➔ `ผู้รับการแจ้งเตือน`, `เลือกหลักฐาน` ➔ `เลือกใช้ข้อมูล`).
        3. **Formality & Gravitas Elevation**: Elevate conversational or unspecific phrasing into precise policy/planning diction (e.g., `แจ้งค่า` ➔ `รายงานค่าหรือระดับความรุนแรง`, `งานวิเคราะห์` ➔ `ขั้นตอนการวิเคราะห์ข้อมูล`).
        4. **Passive/Defeatist Syntax Elimination**: Convert passive or defeatist administrative phrases into positive-conditional development framing (e.g., `ถูกเลื่อนออกเนื่องจาก...` ➔ `มีความสำคัญสูง แต่ยังต้องพัฒนาองค์ความรู้...`).
        5. **Filler & Redundant Particle Pruning**: Catch and eliminate unnecessary padding particles and connective fluff (e.g., stripping redundant `ร่วม`, `ในแง่ของ`).
    - Analyze the higher layers:
        - **L3 Micro-Structural / Tone**: Parallelism in bulleted lists (nominal parallel headings), Anti-AI Shield counter-examples (negation-first framing, double negatives).
        - **L4/L5 Structural & Rhetorical**: Document architecture, high-altitude tables, framework enumeration, finding-to-design bridges, and strategic driver framing. (Currently sourced only from human diffs seen here — `writing-th`'s own `editorial-review.json` L4/L5 rubric verdicts are a second, richer input channel for this layer, not yet wired in. Deferred by Boss 2026-08-30; see `ψ/inbox/2026-08-29_writing-harness-skill-architecture-analysis.md` §4 if picked back up.)

4b) **Miss Register (Promotion Threshold & Zero-Drop Registration)**
    - A single correction is a local edit. The same correction twice is a rule -- learning 2026-06-27 fixed that threshold at two, and the register is what counts to it.
    - **MANDATORY**: Every candidate pattern extracted in Step 4 (especially ALL lexical pairs from the Zero-Drop scan) that is not already in the lexicon or structural rules MUST be registered:
      `python .agents/skills/writing-th/scripts/register.py observe "<pattern>" --source <file> --layer <lexical|regex|structural> --fix "<what you changed it to>"`
    - **A candidate also needs a `--status`, and it gates promotion independently of the sighting count** (added 2026-08-30 after a real live-run failure — see step 4c):
        - A genuinely mechanical, meaning-invariant token swap (a pure synonym preference, no semantic content at stake) can pass `--status mechanical` directly. This is the one case allowed to skip step 4c and reach `ready` on the FIRST sighting — this is the concrete mechanism for "a new word-level replacement is always captured," not a license to skip asking about anything less obviously mechanical.
        - Anything else — a phrase, a structural pattern, a hedge, a softened/sharpened claim, a dropped/added detail — defaults to `--status unconfirmed` (or just omit the flag) and MUST go through step 4c before it can reach `ready`.
    - Then ask what has earned promotion:
      `python .agents/skills/writing-th/scripts/register.py ready [--layer <lexical|regex|structural>]`
    - Only patterns listed by `ready` should be promoted in step 5. A pattern seen once (and not `mechanical`) stays in the register and waits.
    - After writing a pattern into the pack, lexicon, or structural rules, close it out:
      `python .agents/skills/writing-th/scripts/register.py promoted "<pattern>" --layer <lexical|regex|structural>`
    - Nothing is deleted. A promoted pattern keeps its full observation history; it simply stops appearing in `ready`.

4c) **Rationale Gate (required before any non-mechanical promotion)**

    On 2026-08-30 three patterns were promoted into `STYLE_PACK_TH.md` on
    inference alone, with no step for asking why the edit was made. One
    (naming a concrete mechanism — "API," "หนังสือที่เป็นลายลักษณ์อักษร")
    turned out to be the user filling in a domain fact he happened to know,
    not a style habit; generalizing it would have pushed future drafts
    toward *inventing* mechanism detail not grounded in sources — a direct
    violation of `writing-th`'s no-fabricated-sources rule. Another (dropping
    dimension-citation numbers, cutting a whole list item) turned out to be
    "it does not fit the report's objective" — a one-off scope edit for that
    document, not a reusable pattern. Both had to be reverted and re-asked.

    **Before calling `register.py confirm` or writing anything into a
    pack/lexicon/structural-rules file** for a candidate not tagged
    `mechanical`, ask the user why the edit was made — via `AskUserQuestion`
    (Claude Code) or `ask_question` / user prompt (Antigravity / Codex),
    not by inferring it from the diff. Frame the options around what's
    actually at stake for THAT candidate, not generic labels:
    - Tone/register correction, substance unchanged → confirm as `confirmed_generalizable`
    - Content/factual correction, not a style preference → confirm as `content_correction` (log only, never promote)
    - Domain knowledge or a fact specific to this document → confirm as `one_off` (log only — generalizing risks inducing fabricated detail in future drafts)
    - Scope decision specific to this document/report → confirm as `one_off`
    - General, repeatable style preference → confirm as `confirmed_generalizable`

    `python .agents/skills/writing-th/scripts/register.py confirm "<pattern>" --status <mechanical|confirmed_generalizable|one_off|content_correction>`

    If a pattern was already merged into the pack/lexicon before this
    question was asked, **revert that merge first**, ask, and only re-merge
    on a confirmed `confirmed_generalizable` (or `mechanical`) answer. Don't
    leave a guessed rule live while waiting for the answer.

5) **Cumulative Merging (Update Phase)**
    - **Merge Strategy by Layer**:
        - **L1/L2 (Lexical & Regex)**: Before writing a new entry, check for an existing conflicting mapping of the same concept:
          `python .agents/skills/writing-th/scripts/check_lexicon_conflict.py "<term-or-concept>"`
          If it reports an existing entry that maps the same concept to a *different* Thai term, confirm with the user which one is canonical before writing (don't let both stand — this is exactly how `เมทะดาตา`/`มาตรฐานข้อมูลกำกับ` vs `ข้อมูลอภิพันธ์` coexisted undetected on 2026-08-30). Then update `LEXICON_<CONTEXT>.json`. Every entry needs `banned`, `preferred`, `reason`, `kind`, `scope`, and `pattern` (for regex). After write, run:
          `python .agents/skills/writing-th/scripts/validate_lexicon.py ψ/memory/style/LEXICON_TH.json`
          If the new entry supersedes a previously-canonical term, check for stale usages elsewhere and report the affected files to the user rather than leaving them silently out of date:
          `python .agents/skills/writing-th/scripts/check_term_propagation.py "<old_term>" [...]`
        - **L4/L5 (Structural Rules)**: Update `STRUCTURAL_RULES_<CONTEXT>.json`. Every entry needs `id`, `name`, `scope`, `section_job`, `trigger_condition`, `mandatory_structure`, `counter_pattern`, and `status: "promoted"`. After write, run:
          `python .agents/skills/writing-th/scripts/validate_structural_rules.py ψ/memory/style/STRUCTURAL_RULES_TH.json`
        - **L3 (Anti-AI Shield)**: Append new **Examples** and **Counter-examples** to `STYLE_PACK_<CONTEXT>.md §7`.
6) **Artifact Materialization**
    - Write/Update the `STYLE_PACK_<CONTEXT>.md`.
    - Format (as of the 2026-08-29 v6.0 harness overhaul — `STYLE_PACK_TH.md`
      is the live example):
        - `## 1. Core Kernel (80/20)`
        - `## 2. Stage / Scale Activation Map`
        - `## 3. Secondary Pass Rules`
        - `## 4. Hierarchical Vetting Stack`
        - `## 5. Lexicon & Diction (Dos/Don'ts Table)`
        - `## 6. Structural DNA`
        - `## 7. Anti-AI Shield (Counter-examples)`
        - `## 8. Master Implementation Prompt`
        - `## 9. Incremental Capture Log` — **archived, not active**. This
          section grows unbounded and must never be loaded into a drafting or
          review model's context. Append new capture entries directly to
          `ψ/archive/style/capture_history/STYLE_PACK_TH_incremental-capture-log.md`,
          not to `STYLE_PACK_TH.md` itself; leave the short pointer note in
          §9 of the live pack undisturbed. Give every new entry its own
          heading level below `##` so a capture entry can never again collide
          with a real numbered section (this is what produced the stray
          duplicate `## 5.` heading fixed on 2026-08-29).
        - Sections 1–8 are what Stage 3 of `writing-th` v6.0 actually needs,
          and only a compressed extract of them —
          `.agents/skills/writing-th/references/prose-kernel.md` — is loaded
          during drafting. Do not assume a drafting agent has read this file.

7) **Master Prompt Synthesis**
    - Generate a concise, high-signal prompt that can be pasted into a new session to "activate" this style. It should include the Top 5 rules and a few critical Dos/Don'ts.

8) **oracle_learn Integration**
    - Call `oracle_learn` to index the new patterns.
    - Concepts: `writing-style`, `<CONTEXT>`, `style-capture`.
    - Pattern: A summary of the latest delta (e.g., "Added rule for formal Thai hedging using 'อาจพิจารณาได้ว่า'").

---

## Output Template: `STYLE_PACK_<CONTEXT>.md`

Follow the actual 9-section structure listed under step 6 above — this
template shows only the shape of the two sections a promotion round usually
touches, not the whole file:

```markdown
# Style-Pack: [Context]
**Samples Learnt**: [N] | **Last Updated**: [Date] | **Lexicon**: LEXICON_[CONTEXT].json v[X], [N] rules

## 5. Lexicon & Diction
| Banned/Common | Preferred | Reason |
| :--- | :--- | :--- |

## 7. Anti-AI Shield
- **DON'T**: [AI-sounding phrase]
- **DO**: [Human-sounding alternative]
```

A new capture entry belongs in the archived capture-history file (see step 6),
never appended to `## 9` of the live pack itself.
