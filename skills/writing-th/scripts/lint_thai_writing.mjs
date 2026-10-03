#!/usr/bin/env node
import fs from 'node:fs';

const [,, targetFile, lexiconFile, ...rawArgs] = process.argv;
if (!targetFile || !lexiconFile) {
  console.error('Usage: node lint_thai_writing.mjs <target.md> <LEXICON_TH.json> [--scope report|article|all]');
  process.exit(1);
}

if (!fs.existsSync(targetFile)) {
  console.error(`Target file not found: ${targetFile}`);
  process.exit(1);
}

if (!fs.existsSync(lexiconFile)) {
  console.error(`Lexicon file not found: ${lexiconFile}`);
  process.exit(1);
}

const scope = rawArgs.includes('--scope') ? rawArgs[rawArgs.indexOf('--scope') + 1] : 'all';
const content = fs.readFileSync(targetFile, 'utf8');
const lexicon = JSON.parse(fs.readFileSync(lexiconFile, 'utf8'));

// Native V8 ICU Thai word segmentation (Zero external dependencies)
const segmenter = new Intl.Segmenter('th', { granularity: 'word' });
const tokens = new Set(Array.from(segmenter.segment(content)).map(s => s.segment));

const violations = [];

// 1. Banned words check from LEXICON_TH.json
for (const entry of lexicon.banned_words || []) {
  if (entry.scope && entry.scope !== 'all' && scope !== 'all' && entry.scope !== scope) {
    continue;
  }
  if (tokens.has(entry.term) || content.includes(entry.term)) {
    violations.push({
      type: 'banned_word',
      term: entry.term,
      suggestion: entry.replace_with || 'rephrase',
      reason: entry.reason || 'Prohibited term / AI filler'
    });
  }
}

// 2. Anti-AI Pattern 1: Staging instead of stating (Negation-first contrast)
const negatedContrastRegex = /ไม่ได้[^\n]{1,35}แต่/g;
let match;
while ((match = negatedContrastRegex.exec(content)) !== null) {
  violations.push({
    type: 'anti_ai_pattern',
    term: match[0],
    suggestion: 'State what it is directly rather than what it is not',
    reason: 'Negation-first contrast (ไม่ได้...แต่)'
  });
}

// 3. Anti-AI Pattern 4: Formatting by rule (Colons in Thai headings)
const colonInHeadingRegex = /^#{1,6}\s+[^:\n]+[:：]/gm;
while ((match = colonInHeadingRegex.exec(content)) !== null) {
  violations.push({
    type: 'formatting_rule',
    term: match[0].trim(),
    suggestion: 'Remove colon from Thai heading',
    reason: 'Colons in Thai headings are unnatural calques'
  });
}

// Output report
if (violations.length > 0) {
  console.error(`FAILED: Found ${violations.length} style/lexicon violation(s) in ${targetFile}:`);
  for (const v of violations) {
    console.error(`  - [${v.type}] "${v.term}" -> ${v.suggestion} (${v.reason})`);
  }
  process.exit(1);
}

console.log(`PASSED: ${targetFile} is 100% compliant with Thai lexicon and style rules.`);
process.exit(0);
