---
name: study
description: '[core] v1.0.0 | Human-in-the-Loop (HITL) Iterative Study & Extraction. Orchestrates micro-query extraction, saves verbatim runs, synthesizes results, and freezes for human judgment.'
trigger: /study
argument-hint: "<notebook_id> <prompt_file> [--source-ids <ids>]"
metadata:
  origin: oracle-shared-skills
  installer: project
---

# /study — Human-in-the-Loop Study & Ground-Truthing

## 📜 Philosophical Guidance & Objectives of Iterations

Iterative study is an exploratory process designed to map reality and ground design choices, not to generate a single-turn answer. The workflow MUST follow a progressive zoom-in rhythm:

1. **Iteration 1: High-Level Discovery (Mapping the Landscape)**
   * **Objective**: Broad conceptual grounding. Map the vocabulary, identify key document sources, define major structural boundaries, and understand the general architecture or rules. Do NOT dive into granular details or specific parameters yet.
2. **Iteration 2+: Query Refinement (Zooming In on Gaps & Details)**
   * **Objective**: Zoom in on specific details, formulas, variables, or operational gaps identified during Iteration 1. Run highly focused single-question micro-queries bound to specific source documents to retrieve exact facts.
3. **Iteration Final: Decoupled Local Harmonization (Anchoring the Decisions)**
   * **Objective**: Stitch the compiled facts into local project logs or target assets. Keep the synthesis and transformation local in the repository where structure is controlled. Do not ask the AI/NotebookLM to design the final system or change code directly.

---

## 🛡️ Core Protocol Locks (Strictly Mandatory)

1. **[Lock] Decision & Integration Gate (State-Changing)**:
   Once the raw findings are compiled from NotebookLM, the agent MUST stop, present the synthesized decision points/recommendations, and explicitly ask for the human's judgment. The agent MUST NOT call any file-write, replacement, or code execution tools to modify the workspace until the human grants approval in a subsequent turn.

2. **[Lock] Decision Log Freeze (Anti-Ledger Mutation)**:
   The agent **MUST NOT** directly write findings to project ledgers or code templates. All findings and options must be written to a local draft log or target workspace file first, and final ledger updates can only be executed when the user invokes the `/seal` skill.

---

## 🔄 The HITL Study Cycle (Sensing → Forge → Harvest → Rhythm)

### Step 1: Preflight Alignment (Sensing)
1. Read the user's research prompt or study objective.
2. Verify active NotebookLM credentials:
   ```bash
   nlm login --check
   ```
3. List the source documents registered in the notebook:
   ```bash
   nlm list sources <notebook_id>
   ```
4. Define the micro-query prompt structure for the current iteration objective. The agent is authorized to iteratively execute read-only queries (using `nlm query`) and compile facts in memory or temporary run folders during the exploration phase without waiting for turn-by-turn approval. All queries to NotebookLM executed during the study session MUST comply with the protocol gates defined in `notebooklm-rules` (`.agents/skills/notebooklm-rules/SKILL.md`).

### Step 2: Query Execution & Verbatim Audit (Forge)
1. Execute the query using the nlm CLI according to the parameter rules in `notebooklm-rules` (`.agents/skills/notebooklm-rules/SKILL.md`).
2. Ensure the raw JSON response is saved verbatim inside `notebooklm_runs/`.

### Step 3: Local Harmonization & Synthesis Draft (Harvest)
1. Read the raw JSONs directly, extract citation-rich snippets and conceptual definitions, and perform the cognitive synthesis using the local project context.
2. Draft the human-readable Study Synthesis Log markdown file in the designated workspace inbox.
3. Present this draft to the human to solicit their judgment.
4. **[Exploratory Iteration Loop]**: The human's feedback steers the next research path (pointing out gaps, introducing project-specific parameters, or requesting specific details). The agent MUST translate this organic direction into refined parameters for the next iteration:
   * **Adjust Query Scoping**: If the feedback redirects focus to other documents or sections, resolve the correct source UUIDs and update the targeted source IDs.
   * **Zoom-In Prompting**: If the feedback highlights missing granular details, narrow the next prompt to target only those specific elements.
   * **Harmonize Constraints**: If the feedback introduces specific project constraints, incorporate these boundaries directly into the local synthesis recommendations.
   * Loop back to **Step 1** to run the next iteration pass, appending the new findings and citations to the draft Study Synthesis Log before re-submitting to the human.

### Step 4: Decision Log Freeze (Rhythm)
1. Write the final approved decisions and recommendations to the target project log or workspace asset.
2. Move the finalized Study Synthesis Log to the designated repository memory folder as a permanent record of the iterative trace.
