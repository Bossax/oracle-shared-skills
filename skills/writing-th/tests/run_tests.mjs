#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import assert from 'node:assert';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const scriptsDir = path.join(__dirname, '../scripts');
const linterPath = path.join(scriptsDir, 'lint_thai_writing.mjs');
const precheckPath = path.join(scriptsDir, 'check_draft_preconditions.mjs');
const argGatePath = path.join(scriptsDir, 'argument_gate.mjs');

console.log('=== Running writing-th v7.0 Node.js Test Suite ===\n');

// 1. Test Native Intl.Segmenter
console.log('1. Testing native Intl.Segmenter Thai word segmentation...');
const segmenter = new Intl.Segmenter('th', { granularity: 'word' });
const sampleText = 'ประเทศไทยมีความจำเป็นต้องพัฒนาระบบข้อมูล';
const segments = Array.from(segmenter.segment(sampleText)).map(s => s.segment);
assert(segments.length > 3, 'Intl.Segmenter should segment Thai text into multiple tokens');
console.log('   OK: Segmented tokens:', segments.slice(0, 5).join(' | '));

// 2. Test Linter Violations Detection
console.log('\n2. Testing lint_thai_writing.mjs violation detection...');
const tmpDir = path.join(__dirname, 'tmp_test');
fs.mkdirSync(tmpDir, { recursive: true });

const badDocPath = path.join(tmpDir, 'bad_doc.md');
const testLexiconPath = path.join(tmpDir, 'test_lexicon.json');

fs.writeFileSync(badDocPath, '# หัวข้อรายงาน:\n\nไม่ได้ทำเพื่อประโยชน์ส่วนตนแต่ทำเพื่อส่วนรวม และมีนัยสำคัญอย่างยิ่ง');
fs.writeFileSync(testLexiconPath, JSON.stringify({
  banned_words: [
    { term: 'มีนัยสำคัญอย่างยิ่ง', replace_with: 'แสดงผลกระทบชัดเจน', reason: 'filler' }
  ]
}));

let linterFailed = false;
try {
  execFileSync(process.execPath, [linterPath, badDocPath, testLexiconPath], { encoding: 'utf8' });
} catch (e) {
  linterFailed = true;
  assert(e.stderr.includes('Colons in Thai headings') || e.stdout.includes('Colons in Thai headings'), 'Must flag colon in heading');
  assert(e.stderr.includes('ไม่ได้...แต่') || e.stdout.includes('ไม่ได้...แต่'), 'Must flag negated contrast');
  assert(e.stderr.includes('มีนัยสำคัญอย่างยิ่ง') || e.stdout.includes('มีนัยสำคัญอย่างยิ่ง'), 'Must flag banned word');
}
assert(linterFailed, 'Linter should exit with non-zero on violations');
console.log('   OK: Linter successfully caught colon in heading, negated contrast, and banned word.');

// 3. Test Preconditions Hook Gate
console.log('\n3. Testing check_draft_preconditions.mjs...');

// Ledger write denial
let ledgerDenied = false;
try {
  execFileSync(process.execPath, [precheckPath, 'C:/project/ψ/memory/ledgers/test.json'], { encoding: 'utf8' });
} catch (e) {
  ledgerDenied = true;
  assert(e.stderr.includes('DENIED'), 'Must deny ledger write');
}
assert(ledgerDenied, 'Pre-check must deny direct writes to ψ/memory/ledgers/');
console.log('   OK: Denied ledger modification.');

// Style memory denial
let styleDenied = false;
try {
  execFileSync(process.execPath, [precheckPath, 'C:/project/ψ/memory/style/STYLE_PACK_TH.md'], { encoding: 'utf8' });
} catch (e) {
  styleDenied = true;
  assert(e.stderr.includes('DENIED'), 'Must deny style memory write');
}
assert(styleDenied, 'Pre-check must deny direct writes to ψ/memory/style/');
console.log('   OK: Denied style memory modification.');

// Fast Lane allow
try {
  execFileSync(process.execPath, [precheckPath, 'C:/project/ψ/writing/quick_note.md'], { encoding: 'utf8' });
  console.log('   OK: Allowed Fast Lane standalone draft.');
} catch (e) {
  assert.fail('Fast Lane should be allowed immediately');
}

// 4. Test Argument Gate
console.log('\n4. Testing argument_gate.mjs...');
const validMapPath = path.join(tmpDir, 'valid_map.json');
fs.writeFileSync(validMapPath, JSON.stringify({
  schema_version: '1.1',
  argument_units: [
    {
      unit_id: 'unit_1',
      order: 1,
      paragraph_job: 'diagnose',
      claim: 'National climate data requires structural reform',
      grounds: '3.63M people affected',
      warrant: 'Systemic resilience needs baseline',
      application_to_design: 'Build DRD schema',
      verbalization_payload: {
        claim: 'Data needs reform',
        mechanism: 'Floods exceeded thresholds',
        consequence: 'Early warning must upgrade'
      },
      supports: []
    }
  ]
}));

try {
  const out = execFileSync(process.execPath, [argGatePath, 'validate', validMapPath], { encoding: 'utf8' });
  assert(out.includes('PASSED'), 'Argument gate should pass valid map');
  console.log('   OK: Validated argument-map.json.');
} catch (e) {
  assert.fail(`Argument gate failed: ${e.stderr || e.stdout}`);
}

// Cleanup tmp
fs.rmSync(tmpDir, { recursive: true, force: true });

console.log('\n=== ALL TESTS PASSED (100% Zero-Dependency Node.js Engine) ===');
