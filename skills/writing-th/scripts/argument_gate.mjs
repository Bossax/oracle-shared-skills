#!/usr/bin/env node
import fs from 'node:fs';

const PARAGRAPH_JOBS = new Set(['define', 'diagnose', 'compare', 'conclude']);
const UNIT_REQUIRED = [
  'unit_id', 'order', 'paragraph_job', 'claim',
  'grounds', 'warrant', 'application_to_design',
  'verbalization_payload', 'supports'
];
const PAYLOAD_REQUIRED = ['claim', 'mechanism', 'consequence'];

function validateArgumentMap(filePath) {
  if (!fs.existsSync(filePath)) {
    console.error(`File not found: ${filePath}`);
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const errors = [];
  const advisories = [];

  if (!data.schema_version) {
    errors.push('Missing top-level schema_version');
  }

  if (!Array.isArray(data.argument_units) || data.argument_units.length === 0) {
    errors.push('argument_units must be a non-empty array');
    console.error(`FAILED: ${errors.join(', ')}`);
    process.exit(1);
  }

  const seenIds = new Set();
  const seenOrders = new Set();

  data.argument_units.forEach((unit, idx) => {
    const tag = `Unit[${idx}]`;

    // Check required unit fields
    for (const field of UNIT_REQUIRED) {
      if (unit[field] === undefined || unit[field] === null || unit[field] === '') {
        errors.push(`${tag} missing required field '${field}'`);
      }
    }

    if (unit.unit_id) {
      if (seenIds.has(unit.unit_id)) {
        errors.push(`Duplicate unit_id '${unit.unit_id}' at ${tag}`);
      }
      seenIds.add(unit.unit_id);
    }

    if (unit.order !== undefined) {
      if (seenOrders.has(unit.order)) {
        errors.push(`Duplicate order '${unit.order}' at ${tag}`);
      }
      seenOrders.add(unit.order);
    }

    if (unit.paragraph_job && !PARAGRAPH_JOBS.has(unit.paragraph_job)) {
      errors.push(`${tag} invalid paragraph_job '${unit.paragraph_job}'. Must be one of: ${Array.from(PARAGRAPH_JOBS).join(', ')}`);
    }

    // Check verbalization_payload
    const payload = unit.verbalization_payload;
    if (payload && typeof payload === 'object') {
      for (const pfield of PAYLOAD_REQUIRED) {
        if (!payload[pfield] || typeof payload[pfield] !== 'string') {
          errors.push(`${tag}.verbalization_payload missing string '${pfield}'`);
        }
      }
    }
  });

  if (errors.length > 0) {
    console.error(`FAILED: Found ${errors.length} error(s) in ${filePath}:`);
    for (const err of errors) {
      console.error(`  - ${err}`);
    }
    process.exit(1);
  }

  console.log(`PASSED: ${filePath} is structurally valid (${data.argument_units.length} argument units).`);
  process.exit(0);
}

const command = process.argv[2];
const target = process.argv[3];

if (command === 'validate' && target) {
  validateArgumentMap(target);
} else {
  console.log('Usage: node argument_gate.mjs validate <argument-map.json>');
  process.exit(1);
}
