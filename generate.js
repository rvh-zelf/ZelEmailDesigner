#!/usr/bin/env node
/**
 * generate.js - MJML email compiler skill
 *
 * Usage:
 *   node generate.js <config.json> <output.html>
 *   echo '{"template":"...","variables":{...},"output":"out.html"}' | node generate.js
 *
 * Config JSON shape:
 * {
 *   "template": "/path/to/template.mjml",
 *   "variables": { "recipient_name": "Jane", ... },
 *   "output": "/path/to/output.html"
 * }
 */

'use strict';

const fs = require('fs');
const path = require('path');
const mjml = require('mjml');

const SKILL_DIR = __dirname;

function resolveTemplate(templatePath) {
  if (path.isAbsolute(templatePath)) return templatePath;
  const fromSkill = path.join(SKILL_DIR, templatePath);
  if (fs.existsSync(fromSkill)) return fromSkill;
  const fromCwd = path.resolve(process.cwd(), templatePath);
  if (fs.existsSync(fromCwd)) return fromCwd;
  throw new Error('Template not found: ' + templatePath);
}

function substituteVariables(mjmlSource, variables) {
  if (!variables) return mjmlSource;
  let result = mjmlSource;
  for (const [key, value] of Object.entries(variables)) {
    const regex = new RegExp('\\{\\{' + key + '\\}\\}', 'g');
    result = result.replace(regex, value != null ? String(value) : '');
  }
  return result;
}

function checkSize(html) {
  const bytes = Buffer.byteLength(html, 'utf8');
  const kb = (bytes / 1024).toFixed(1);
  if (bytes > 102 * 1024) {
    process.stderr.write('WARNING: compiled HTML is ' + kb + 'KB - exceeds Gmail 102KB clip threshold!\n');
  } else {
    process.stderr.write('HTML size: ' + kb + 'KB (under 102KB limit OK)\n');
  }
}

async function compileEmail(config) {
  const templatePath = resolveTemplate(config.template);
  const rawMjml = fs.readFileSync(templatePath, 'utf8');
  const processedMjml = substituteVariables(rawMjml, config.variables || {});

  const result = await mjml(processedMjml, {
    filePath: templatePath,
    validationLevel: 'soft',
    minify: false,
  });

  if (result.errors && result.errors.length > 0) {
    const warnings = result.errors.map(function(e) {
      return '  [' + e.tagName + '] ' + e.message;
    }).join('\n');
    process.stderr.write('MJML warnings:\n' + warnings + '\n');
  }

  return result.html;
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return Buffer.concat(chunks).toString('utf8');
}

async function main() {
  let config;

  if (process.argv[2]) {
    const configPath = path.resolve(process.cwd(), process.argv[2]);
    config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    if (process.argv[3]) config.output = process.argv[3];
  } else {
    const stdin = await readStdin();
    config = JSON.parse(stdin);
  }

  if (!config.template) {
    process.stderr.write('Error: config.template is required\n');
    process.exit(1);
  }

  const html = await compileEmail(config);
  checkSize(html);

  if (config.output) {
    const outPath = path.resolve(process.cwd(), config.output);
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, html, 'utf8');
    process.stderr.write('Output written to: ' + outPath + '\n');
  } else {
    process.stdout.write(html);
  }
}

main().catch(function(err) {
  process.stderr.write('Fatal error: ' + err.message + '\n');
  process.exit(1);
});
