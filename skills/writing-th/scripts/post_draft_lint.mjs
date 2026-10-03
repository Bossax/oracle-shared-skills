#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

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

// Trigger on markdown writes inside ψ/writing/
if (normalized.includes('/ψ/writing/') && normalized.endsWith('.md')) {
  const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
  const linterScript = path.join(__dirname, 'lint_thai_writing.mjs');
  const lexiconPath = path.join(projectDir, 'ψ/memory/style/LEXICON_TH.json');

  if (fs.existsSync(lexiconPath) && fs.existsSync(targetPath)) {
    try {
      const output = execFileSync(process.execPath, [linterScript, targetPath, lexiconPath, '--scope', 'report'], {
        encoding: 'utf8'
      });
      console.log(`[writing-th lint] ${output.trim()}`);
    } catch (err) {
      console.warn(`[writing-th lint warning] Lexicon/style issues found in ${path.basename(targetPath)}:\n${err.stderr || err.stdout}`);
    }
  }
}

process.exit(0);
