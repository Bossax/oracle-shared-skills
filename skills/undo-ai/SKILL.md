---
name: undo-ai
description: >
  v1.0.0 | Strip AI signs of writing (WP:AISIGNS), eliminate exaggerations and
  unverified numbers, and rewrite chat output or files into plain, professional
  English via an independent general-subagent cold audit. Use when user says
  "undo-ai", "/undo-ai", "strip AI writing", "remove AI bullshit", "de-fluff",
  or "plain English".
metadata:
  origin: oracle-shared-skills
  installer: project
---

# /undo-ai — Strip AI Signs of Writing & Exaggerations

## Target Resolution
- **No path given** (`/undo-ai` or `/undo-ai this`): Target is the latest AI draft or response in the current chat.
- **File path or selection given** (`/undo-ai <path>`): Target is the specified file or section on disk.
- **`--apply` flag**: Skip the confirmation pause and apply the rewrite immediately after printing the subagent's Audit Table.

## Workflow (Option A: Subagent Cold Audit → Confirm → Rewrite)

### Step 1 — Cold Audit via Fresh General Subagent (Mandatory Forcing Function)
Do not grade your own drafting context. Launch the host's built-in **general subagent** (`invoke_subagent` with `TypeName: "self"` in Antigravity, or a general `Agent` in Claude Code / Codex) as a read-only **Cold Writing Auditor**:

- **What to pass in the subagent prompt**:
  1. **Target content**:
     - If auditing **in-chat output**: Paste the **verbatim target text** directly into the prompt (subagents cannot see parent chat history).
     - If auditing a **file on disk**: Pass the resolved file path (and section/line range if scoped).
  2. **Governing source facts**: Pass any relevant source file paths or verified numbers from the current task so the subagent can check numbers and denominators.
  3. **The 8 Audit Categories** (from this file) and instructions to return **only** the 4-column Markdown Audit Table below (no file edits by the subagent):

| Location / Quote | Category (#1–#8) | Fact / Source Check | Plain-English Fix |
| :--- | :--- | :--- | :--- |

### Step 2 — Present Audit Table & Confirm
Show the subagent's Audit Table to the user and wait for confirmation (`ok` or row adjustments) before rewriting, unless `--apply` was passed.

### Step 3 — Rewrite in Plain, Professional English
- **If target is in-chat output**: Print the cleaned version directly in chat.
- **If target is a file**: Apply the approved fixes in place and verify `0` em dashes (`—`) and `0` unverified exaggerations remain.

---

## The 8 Audit Categories (`WP:AISIGNS` + Project Corrections)

### 1. Undue Emphasis, Promotional Hype & False Equivalence (`WP:AISIGNS`)
- **Inflated significance / legacy**: *"stands as a testament"*, *"plays a vital / pivotal / crucial role"*, *"watershed moment"*, *"indelible mark"*, *"underscores its importance"*.
- **Marketing / brochure adjectives**: *"seamless"*, *"robust"*, *"game-changing"*, *"comprehensive ecosystem"*, *"cutting-edge"*, *"unlock / unleash / elevate"*.
- **False equivalence & overclaiming**: Equating simple prompts with full technical systems or stretching scope beyond evidence.
  - *Bad*: `"Four Everyday Habits Bring Harness Discipline to Web Chat"` / `"You do not need CLI tools to copy what worked in the demo"`
  - *Plain*: `"Four Practical Habits for Everyday Web Chat"` / `"When you work in a normal chat window, these four steps help keep sources straight."`

### 2. Superficial Analyses & Trailing `-ing` Clauses (`WP:AISIGNS`)
- **Empty participial tack-ons** at the end of clauses that pretend to explain significance without adding facts: *"...highlighting the importance of..."*, *"...underscoring the need for..."*, *"...ensuring that..."*, *"...fostering a culture of..."*, *"...showcasing how..."*, *"...reflecting the broader trend of..."*.
- **Fix**: Delete the trailing `-ing` clause, or replace it with a concrete operational fact (who does what, or what breaks).

### 3. Overused AI Vocabulary, Copula Avoidance & Consultant Jargon (`WP:AISIGNS`)
- **AI word cluster**: *delve, tapestry, landscape (abstract), intricate, interplay, multifaceted, foster, garner, bolster, vibrant, pivotal, crucial, notably, importantly, moreover, furthermore, consequently*.
- **Copula avoidance**: Dodging plain **"is / are / has"** in favor of *"serves as"*, *"acts as"*, *"functions as"*, *"represents"*, *"boasts"*, *"stands as"*. Use **"is"** or **"has"**.
- **Opaque AI-blog / consultant labels**: Using engineering or buzzword labels where everyday verbs belong.
  - *Bad*: `"Map Before You Synthesize"`, `"Double Payoff"`, `"Diagnostic Focus"`, `"Cold Specialist Check"`, `"blocks memory leakage"`, `"drafting baggage"`.
  - *Plain*: `"Pull Quotes Into a Table Before Summarizing"`, `"Why it helps"`, `"What to ask AI to check first"`, `"Open a Fresh Chat for Important Fact Checks"`.

### 4. Invented Numbers, Distorted Stats & Weasel Attribution (`WP:AISIGNS` + Project Rule)
- **Every number, percentage, duration, and quantifier** must be checked against a real source:
  - Keep the exact source number and exact denominator/unit (`~45% of sessions`, never inflate to `"nearly half of all turns"`).
  - Delete invented rhetorical numbers (`"verify in 5 seconds"`, `"6+ Rework Turns"`, `"Most Habits Stopped in 2024"`, `"endless"`).
- **Weasel attribution**: Cut anonymous authority claims (*"observers note"*, *"experts agree"*, *"practitioners say"*, *"studies show"*) unless naming the specific source.

### 5. Rhetorical Formulas & Sentence Symmetry (`WP:AISIGNS`)
- **Negative parallelisms**: *"Not only X, but also Y"*, *"It is not merely X; it is Y"*, *"X doesn't just do A; it does B"*. State what X *does* directly (affirmative-first).
- **Two-clause `;` or `:` symmetry**: Breaking every sub-headline or sentence into a balanced two-part essay rhythm (*"Dumping X blends Y; doing A keeps B"*).
- **Forced Rule of Three**: Mechanically grouping adjectives or nouns into triads (*"speed, efficiency, and reliability"*).
- **False `"From X to Y"` ranges**: Fake spectrums (*"from high-level policy design to ground-level execution"*).

### 6. Structural Clichés & Formulaic Conclusions (`WP:AISIGNS`)
- **Editorial signposts**: *"It is important to note"*, *"It is worth mentioning"*, *"No discussion would be complete without"*.
- **Formulaic conclusion arcs**: Ending sections with preachy wrap-ups (*"In conclusion / Overall, by adopting these practices, organizations can ensure a more resilient future..."*). Stop when the last fact is stated.
- **Chatbot residue**: *"Here is a breakdown"*, *"Certainly!"*, *"Let's dive in"*.

### 7. Punctuation & Formatting Tells (`WP:AISIGNS`)
- **Em dashes (`—` or spaced `--`)**: Replace with a period, comma, or parentheses.
- **`**Bold Label:**` bullet inflation**: Avoid turning every list item into `**Invented Buzzword Noun:** sentence that repeats the bold label`.
- **Title Case headings & slide eyebrows**: Prefer sentence case in prose headings; strip decorative `- **Eyebrow**:` lines on slides; ban metaphors in technical/policy explanations.

### 8. Multi-Layer Redundancy
- Do not repeat the same claim in slightly different words across Headline, Sub-headline, Bullets, and Speaker Notes (or across adjacent paragraphs/slides). Each line must add a new fact or be cut.
