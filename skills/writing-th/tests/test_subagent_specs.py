#!/usr/bin/env python3
"""Tests verifying canonical subagent specifications across Antigravity and Claude Code runtimes."""

import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
PROMPTS_FILE = SKILL_DIR / "references" / "subagent-prompts.md"
CLAUDE_AGENTS_DIR = SKILL_DIR.parents[1] / ".claude" / "agents"


class TestSubagentSpecs(unittest.TestCase):
    def setUp(self):
        self.assertTrue(PROMPTS_FILE.exists(), f"Missing {PROMPTS_FILE}")
        self.prompts_text = PROMPTS_FILE.read_text(encoding="utf-8")

    def test_all_three_subagents_defined(self):
        expected_agents = ["th-argument-mapper", "th-verbalizer", "th-editorial-reviewer"]
        for agent in expected_agents:
            self.assertIn(agent, self.prompts_text, f"Subagent {agent} missing from canonical prompts")

    def test_model_tier_assignments(self):
        # Stage 1: Mapper requires Pro / high reasoning
        self.assertIn('th-argument-mapper', self.prompts_text)
        self.assertIn('Model: "pro"', self.prompts_text)

        # Stage 3: Verbalizer requires Flash or Pro
        self.assertIn('th-verbalizer', self.prompts_text)
        self.assertIn('Model: "flash"', self.prompts_text)

        # Stage 5: Reviewer requires Pro / independent
        self.assertIn('th-editorial-reviewer', self.prompts_text)

    def test_claude_agents_sync_if_present(self):
        if not CLAUDE_AGENTS_DIR.exists():
            return
        
        expected_files = [
            "th-argument-mapper.md",
            "th-verbalizer.md",
            "th-editorial-reviewer.md",
        ]
        for fname in expected_files:
            claude_file = CLAUDE_AGENTS_DIR / fname
            if claude_file.exists():
                text = claude_file.read_text(encoding="utf-8")
                self.assertIn("You are", text)
                self.assertTrue(len(text) > 200, f"{fname} is suspiciously short")

    def test_references_and_schemas_accessible(self):
        schemas = SKILL_DIR / "references" / "artifact-schemas.md"
        prose_kernel = SKILL_DIR / "references" / "prose-kernel.md"
        rubric = SKILL_DIR / "references" / "editorial-rubric.md"

        self.assertTrue(schemas.exists(), f"Missing {schemas}")
        self.assertTrue(prose_kernel.exists(), f"Missing {prose_kernel}")
        self.assertTrue(rubric.exists(), f"Missing {rubric}")


if __name__ == "__main__":
    unittest.main()
