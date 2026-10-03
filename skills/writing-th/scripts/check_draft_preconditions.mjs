#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

// Parse tool input from stdin (Claude Code PreToolUse Hook) or command-line args
let targetPath = process.argv[2] || '';
try {
  const stdinData = fs.readFileSync(0, 'utf8');
  if (stdinData && stdinData.trim()) {
    const parsed = JSON.parse(stdinData);
    targetPath = parsed?.tool_input?.file_path || parsed?.tool_input?.path || targetPath;
  }
} catch (e) {
  // Stdin not present or not JSON, fallback to argv
}

if (!targetPath) {
  process.exit(0);
}

const normalized = targetPath.replace(/\\/g, '/');

// 1. Memory & Ledger Protection Gate
if (normalized.includes('/ψ/memory/ledgers/')) {
  console.error('DENIED: Direct write to project ledgers is protected. Project ledgers can be modified only if the seal skill is explicitly invoked.');
  process.exit(1);
}

if (normalized.includes('/ψ/memory/style/') || normalized.includes('/ψ/memory/resonance/')) {
  console.error('DENIED: Style memory (ψ/memory/style/, ψ/memory/resonance/) is managed via style-capture. Direct edits during drafting are blocked.');
  process.exit(1);
}

// 2. Structured Drafting Lane Gate: ψ/writing/<chapter_id>/draft*.md
const match = normalized.match(/\/ψ\/writing\/([^/]+)\/draft.*\.md$/);
if (match) {
  const chapterDir = path.dirname(targetPath);
  const planPath = path.join(chapterDir, 'drafting-plan.md');

  if (!fs.existsSync(planPath)) {
    console.error(`DENIED: Structured chapter drafting requires an approved drafting-plan.md in ${chapterDir}`);
    process.exit(1);
  }

  const planContent = fs.readFileSync(planPath, 'utf8');
  const isApproved = planContent.includes('สถานะการอนุมัติ: approved') ||
                     planContent.includes('สถานะการอนุมัติ (Approval Status): approved') ||
                     planContent.includes('Approval Status: approved') ||
                     planContent.includes('status: approved');

  if (!isApproved) {
    console.error(`DENIED: drafting-plan.md in ${chapterDir} is not yet approved. Human review must approve the plan before verbalization begins.`);
    process.exit(1);
  }
}

// Fast Tactical Lane (standalone notes, translations, quick polish) passes immediately
process.exit(0);
