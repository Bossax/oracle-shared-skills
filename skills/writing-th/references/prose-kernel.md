# Prose Kernel (TH) — Stage 3 Verbalization Only

Compressed from `STYLE_PACK_TH.md` §1 (Core Kernel), §6 (Thai Sentence Shape
Guardrails), and §7 (Anti-AI Shield). This is what Stage 3 loads instead of
the full 57 KB pack — it is enough to verbalize an approved argument map into
Thai institutional prose. It is not a substitute for the lexicon: mechanical
term-level violations are caught by `lint_thai_writing.py` at Stage 4, not by
reading this file. If a rule here and a Stage 4 lint finding conflict, the
lint finding wins — it is checking the live lexicon, this file is a snapshot.

## Core Kernel (80/20)

1. **Section job first** — before writing, state the section's job in one
   sentence. Reject text that repeats the previous section's job or drifts
   into the next section's.
2. **Evidence-first opening** — begin with the audit scale, named service,
   blocked task, or concrete finding. No literary hook, no scene-setting
   filler, no abstract thesis line.
3. **Analytical payload** — every substantive paragraph carries a claim, a
   concrete example or variable, a consequence, and a mechanism. This is
   already structured into the argument map's `claim` / `grounds` / `warrant`
   / `application_to_design` — your job is to state them, not invent them.
4. **Evidence-to-action chain** — default paragraph logic moves observed
   evidence → operational consequence → institutional cause → proposed
   mechanism.
5. **Name the deliverable, owner, or artifact** — not only the activity.
6. **One paragraph, one main job** — define, diagnose, compare, or conclude.
   Do not mix jobs unless the section explicitly requires it.
7. **Thai institutional voice over design-memo tone** — rewrite anything that
   sounds like a translated design memo or English argumentative skeleton.
8. **Active institutional agency when the actor is known** — `กรมฯ จัดทำ...`,
   `บริการนี้ทำหน้าที่...`, not `ถูกออกแบบให้...`.
9. **Banish direct English jargon** when a functional Thai equivalent exists.
10. **Simplified technical prose** — cut prestige descriptors (`ขั้นสูง`,
    `ที่สำคัญที่สุด`) unless the distinction is materially necessary.

## Thai Sentence Shape Guardrails

- Start with the real subject, institution, dataset, or finding.
- When the actor is known, prefer active-duty phrasing over passive intention
  language.
- Never open a sentence by denying what something is not before stating what
  it is.
- Ban pseudo-balanced translated contrast scaffolding: `...ไม่ได้...แต่...`,
  `ไม่ใช่เพียง...แต่ยัง...`, `ไม่ควรถูกมองเป็น...แต่ควรถูกมองเป็น...` — these are
  now `kind: regex` lexicon entries and will block at Stage 4, but avoid them
  at the source: state the actual function first, then the limitation or
  contrast in the next clause or sentence.
- Avoid: `บริการนี้ถูกออกแบบให้ทำหน้าที่...` → Prefer: `บริการนี้ทำหน้าที่...`
- Direct Forward Syntax: Never use inverted negative conditionals ("จะยังไม่...จนกว่า..."). State the direct active action ("โครงสร้างข้อมูล X จะต้องถูกนำไปพัฒนาเป็น...").
- Domain Subject Anchoring in Titles: Never drop the core domain noun in H1/H2 headings for brevity ("...สำหรับการประเมินความสูญเสียและความเสียหาย..." not bare "...และปัญหา...").
- Acronym First-Occurrence Protocol: Full English Name + Acronym + Thai Functional Definition on first mention.
- Ban colons (`:`) in Thai headings/subheadings.

## Anti-AI Shield

- Don't open with "อย่างไรก็ตาม..." or "แม้ว่า..." unless the contrast does
  real analytical work.
- Don't use "ระบบ" without naming which system.
- Don't use hyperbolic marketing words ("ไร้รอยต่อ", "สมบูรณ์แบบ") — describe
  the actual operational workflow or constraint.
- Don't use empty academic filler like "เชิงประจักษ์" when stating test results ("ผลการทดสอบชี้ให้เห็นว่า" is complete).
- Don't use theatrical melodrama like "อย่างสิ้นเชิง" (use "แตกต่างกัน").
- Don't use awkward framework term "แกน" when "องค์ประกอบ" or "ข้อมูลหลัก" is meant.
- Don't write abstract gap statements without a concrete blocked task,
  service, or example.
- Don't name only a direction in a recommendation — name the artifact, owner,
  or mechanism.
- Don't append repetitive case study names to universal recommendation lists.
- Don't compress multiple service gaps into one dense paragraph when the
  distinctions matter to the reader.
- Don't pile up composite nouns ("ระดับโครงสร้างข้อมูล", "ชั้นข้อมูลส่วนขยาย")
  when simpler Thai names the same function.
- Don't explain by negation first if the point can be stated directly.
- Don't use passive/pseudo-passive agency ("ถูกออกแบบให้...") when the actor
  is already known and can be named.
- Don't compress by deleting governance content — cut scaffolding first, not
  institutional duties, evidence, or conditions of use.
- Don't cite internal artifact locators (slide/page numbers) in reader-facing
  sentences — sourcing belongs in the traceability sidecar only.
- Don't render a called-for diagram as an inline arrow-chain sentence — flag
  it as a figure placeholder instead.
- Don't write meta-commentary about what the document's own sections cover.

## Master Prompt

Write in a punchy, authoritative Thai institutional voice. Start from the
evidence, blocked task, or service function — never a literary hook. Make
each paragraph do one clear job, verbalizing its argument unit's claim,
grounds, consequence, and mechanism. Name the deliverable, owner, or service
artifact directly. Prefer active institutional agency when the actor is
known. Remove translated contrast scaffolding, prestige filler, and
design-memo tone. Never let micro-style optimization outrank the argument
map's content logic — you are translating an approved argument, not
re-arguing it.
