# Harness Artifact Schemas v1.0

Both artifacts are UTF-8 JSON files stored beside the isolated draft. Paths may
be absolute or repository-relative. Timestamps use ISO 8601.

## `drafting-plan.md` (Unified Human-Facing Planning Artifact)

`drafting-plan.md` replaces raw JSON review by inlining the entire writing contract, macro story arc, and paragraph blueprints into a single readable Markdown document stored in `ψ/writing/<chapter_id>/`:

```markdown
# 📋 แผนการร่างและพิมพ์เขียวบทความ (Drafting Plan): <Chapter ID / Title>

## ส่วนที่ 1: สัญญาข้อตกลงและขอบเขต (Contract & Constraints)
- **กลุ่มผู้อ่าน (Audience):** ผู้บริหาร DCCE และคณะกรรมการนโยบาย
- **ระดับความลึก (Target Altitude):** Executive Summary (เน้นข้อค้นพบเชิงปฏิบัติการ)
- **ภารกิจของบท (Section Job):** ชี้แจงช่องว่างข้อมูล 8 บริการและเสนอทางออกเร่งด่วน
- **ประธานผู้ดำเนินงาน (Active Actor):** คณะที่ปรึกษา
- **กฎเฉพาะของรายงาน:** ห้ามใช้คำย่อปฏิบัติการภายใน (AD&ADF), ยึดรูปแบบ Executive CRI
- **แหล่งข้อมูลอ้างอิง (Source Paths):** `ψ/incubate/.../WP6-Service-Narratives.md`
- **บันทึกการสืบค้น (Trace Paths):** `ψ/memory/traces/2026-09-29/1600_ch6-five-services.md`
- **สถานะการอนุมัติ (Approval Status):** pending / approved

---

## ส่วนที่ 2: โครงเรื่องระดับมหภาค (Macro Story Arc)
- **แกนนำทางความคิด (Governing Thought):** [Minto Top Takeaway]
- **สถานการณ์ (Situation):** [บริบทและฐานความจริงร่วม]
- **ความตึงเครียด (Complication):** [อุปสรรคและช่องว่างเชิงสถาบัน]
- **คำถามชี้นำ (Question):** [คำถามหลักที่ส่วนนี้ต้องตอบ]
- **คำตอบเชิงยุทธศาสตร์ (Answer):** [ข้อเสนอแนะหลัก]

---

## ส่วนที่ 3: พิมพ์เขียวรายย่อหน้า (Paragraph Blueprint & Decision Tree)

### ย่อหน้า 1: บริบทภายนอกและความจำเป็น
- **แม่แบบ (Archetype):** `R1` (ตัวเลขภายนอก → แม้...แต่ → ชี้ความจำเป็น)
- **ภารกิจ (Job):** diagnose
- **ประโยคทุบประเด็น (Landing Punchline):** ประเทศไทยจำเป็นต้องมีโครงสร้างข้อมูลเพื่อติดตามความเสี่ยงอย่างเป็นระบบ
- **ข้อมูลหลักฐานที่ต้องบรรจุ:** ดัชนี CRI ปี 2567 อันดับ 17

### ย่อหน้า 2: สถิติความเสียหายสู่นัยเชิงปฏิบัติการ
- **แม่แบบ (Archetype):** `R2` (ข้อค้นพบ → ตัวเลขจริง → เทียบฐาน → สะท้อนว่า → นัยต่อการลงมือ)
- **ภารกิจ (Job):** diagnose
- **ประโยคทุบประเด็น (Landing Punchline):** อุทกภัยปี 2567 สร้างผลกระทบผิดปกติและต้องใช้ทบทวนระบบเตือนภัย
- **ข้อมูลหลักฐานที่ต้องบรรจุ:** ผู้ได้รับผลกระทบ 3.63 ล้านคน
```

*Note: A companion `argument-map.json` is generated quietly beside `drafting-plan.md` for machine validation (`argument_gate.mjs`).*


Required profiles are `executive-summary`, `report`, `article`, or `letter`.
Required modes are `rewrite`, `synthesis`, or `new`. Every listed key is
required; lists, rules, and terminology may be empty only when the contract explains why
through the corresponding prose field. `report_specific_rules` must capture global
writing plan conventions (e.g., Section 10 rules, active actor identity, altitude constraints). `approval.status` must be `approved`
before review or merge.

`trace_log_paths` lists relevant trace markdown files in `ψ/memory/traces/` discovered during Stage 0 to ground technical ancestry and decisions.

`stage_0_checklist` records the verification of the Triad Checklist (Outline, Evidence Base, Session Rules) executed under Plan Mode.

`prior_draft` and `prior_approval` are optional and appear together when a section
is being upgraded rather than written for the first time. `prior_draft` names the
existing draft; its presence is what puts Stage 1 into revision mode (see
[revision-mode.md](revision-mode.md)). `prior_approval` carries forward what the
superseded contract's approval rested on, so earlier human decisions stay visible
after `approval` is reset for the new run.

`plan_slice` is optional: the path to a sidecar Stage 0 writes beside the contract,
holding the section's brief, the writing plan's global rules block, and the
relevant evidence-table rows it already extracted to populate
`report_specific_rules`. `null` when no writing plan existed for this run. When
present, Stage 1 reads it instead of re-deriving the same slice from the full
writing plan on every call; Stage 1 still falls back to the full plan if the slice
is visibly insufficient for a unit.

`execution_tier` records how Stage 1/3 actually ran, decided at Stage 0 (see the
Claude Code execution-tier table in `SKILL.md`) and confirmed with the human:
`tier` is `small` (1–2 sections), `medium` (3–6), or `large` (7+, or spanning
sessions); `stage_1_3_mode` is `inline`, `fork`, or `fresh`; `orchestrator_clean`
records whether the orchestrator's context was free of `STYLE_PACK_TH.md`,
`LEXICON_TH.json`, and `editorial-rubric.md` at the time of the decision —
`orchestrator_clean: false` forces `stage_1_3_mode: "fresh"` regardless of what
the tier alone would suggest. `stage_5_mode` is never a field here: Stage 5 is
always a fresh, non-fork, non-inline subagent call, at every tier.

## `editorial-review.json`

Create the initial file with `editorial_gate.py prepare`; do not type hashes by
hand.

```json
{
  "schema_version": "1.0",
  "rubric_version": "5.0.0",
  "draft_sha256": "generated",
  "contract_sha256": "generated",
  "profile": "executive-summary",
  "reviewer_mode": "independent",
  "assurance": "standard",
  "reviewer": "reviewer identifier",
  "reviewed_at": "2026-08-28T01:30:00+07:00",
  "dimensions": {
    "section_job": {"verdict": "pass", "evidence": "Opening and conclusion perform the approved job."},
    "audience_decision_value": {"verdict": "pass", "evidence": "..."},
    "evidence_payload": {"verdict": "pass", "evidence": "..."},
    "causal_logic": {"verdict": "pass", "evidence": "..."},
    "reader_facing_appropriateness": {"verdict": "pass", "evidence": "..."},
    "terminology_agency": {"verdict": "pass", "evidence": "..."},
    "source_fidelity": {"verdict": "pass", "evidence": "..."},
    "form_readability": {"verdict": "pass", "evidence": "..."},
    "altitude": {"verdict": "pass", "evidence": "..."},
    "headline_conclusion": {"verdict": "pass", "evidence": "..."},
    "findings_over_process": {"verdict": "pass", "evidence": "..."}
  },
  "findings": [
    {"severity": "minor", "location": "paragraph 3", "issue": "Local repetition", "status": "accepted", "disposition": "Flag for human review"}
  ],
  "mechanical_reviews": [
    {"message": "[PARENTHETICAL] exact linter message", "disposition": "Official term retained for traceability"}
  ],
  "verdict": "pass"
}
```

Allowed finding statuses are `resolved`, `accepted`, and `unresolved`.
Critical or major findings must be `resolved`. Mechanical review messages must
match the current linter output exactly; merge checks coverage.

## `argument-map.json` (v6.0)

Create the initial file with `argument_gate.py prepare`; validate with
`argument_gate.py validate` before reporting the stage done.

```json
{
  "schema_version": "1.0",
  "section_id": "crdb-exec-summary-1.2",
  "governing_thought": "The single takeaway conclusion the reader should leave with (Minto top)",
  "narrative_scqa": {
    "situation": "Shared baseline reality",
    "complication": "Tension, blocker, or institutional friction",
    "question": "The governing question this section answers",
    "answer": "The proposed direction (should echo governing_thought)"
  },
  "governing_thought_components": ["the distinct parts governing_thought breaks into"],
  "argument_units": [
    {
      "unit_id": "arg-01",
      "order": 1,
      "paragraph_job": "diagnose",
      "claim": "Central assertion of this unit",
      "grounds": "Concrete evidence, benchmark, or cited parameter",
      "warrant": "Connective reasoning: why do these grounds compel this claim?",
      "application_to_design": "How this finding dictates the deliverable's design",
      "supports": "must exactly match one entry in governing_thought_components",
      "provenance": "recovered | repaired | new — revision mode only"
    }
  ],
  "approval": {"status": "pending", "approved_by": "", "approved_at": ""}
}
```

`paragraph_job` is one of `define`, `diagnose`, `compare`, `conclude` — the
same enum `STYLE_PACK_TH.md` rule 6 uses. `governing_thought_components` is
the mechanical MECE check: every `argument_units[].supports` value must match
one entry, and every entry must be supported by at least one unit.
`argument_gate.py validate` enforces both directions.

`provenance` appears only in revision mode, when the contract names a
`prior_draft`. It records whether a unit was recovered from that draft unchanged,
repaired because the draft argued it incompletely, or built new because the
writing plan required it and the draft skipped it. The gate script does not check
it; the Stage 2 gate and the Stage 5 reviewer read it, and `warrant_trace.py` on a
`recovered` unit is what catches a rewrite dropping approved substance.

`approval.status` must be `approved` before any draft in the same directory
may be written or revised — enforced by the `PreToolUse` hook on
`Write|Edit`, not by this script. The script checks structure only; approval
is a human decision made at the Stage 2 gate.

