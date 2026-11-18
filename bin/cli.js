#!/usr/bin/env node

const { spawnSync } = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs');

const pkgPath = path.resolve(__dirname, '..', 'package.json');
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));

const rootDir = path.resolve(__dirname, '..');
const scriptsDir = path.resolve(rootDir, '.agents', 'skills', 'lead-approach', 'scripts');
const profileJsonPath = path.resolve(rootDir, '.agents', 'skills', 'lead-approach', 'config', 'profile.json');

const args = process.argv.slice(2);
const command = args[0];
const subArgs = args.slice(1);

function getPythonBinary() {
  const candidates = ['python3', 'python'];
  for (const bin of candidates) {
    const res = spawnSync(bin, ['--version'], { encoding: 'utf8' });
    if (!res.error && res.status === 0) {
      return bin;
    }
  }
  return null;
}

function runScript(scriptName, extraArgs) {
  const pyBin = getPythonBinary();
  if (!pyBin) {
    console.error('\x1b[31m[Error]\x1b[0m Python 3 is required but was not found on your system PATH.');
    process.exit(1);
  }
  const scriptPath = path.join(scriptsDir, scriptName);
  const result = spawnSync(pyBin, [scriptPath, ...extraArgs], {
    stdio: 'inherit',
    cwd: process.cwd()
  });
  if (result.error) {
    console.error('\x1b[31m[Error]\x1b[0m', result.error.message);
    process.exit(1);
  }
  process.exit(result.status ?? 0);
}

function showHelp() {
  console.log(`
\x1b[1;34mlead-approach\x1b[0m v${pkg.version}
Universal Outbound & Cold Approach Engine (No-Call Methodology)

\x1b[1mUsage:\x1b[0m
  lead-approach <command> [options]
  leadapp <command> [options]

\x1b[1mCommands:\x1b[0m
  \x1b[32minstall\x1b[0m   Install the skill into your AI agents (Antigravity, Claude Code, Codex)
  \x1b[32msetup\x1b[0m     Configure business profile, offer, tone, links, and brand manual
  \x1b[32mlist\x1b[0m      Process lead list (PDF, TXT, CSV, MD, JSON) and build outreach roadmap
  \x1b[32mrecon\x1b[0m     Run technical performance & mobile audit on a lead website URL
  \x1b[32mreport\x1b[0m    Compile executive A4 PDF dossier according to saved brand manual
  \x1b[32mstatus\x1b[0m    Display the current campaign profile and brand configuration

\x1b[1mGlobal Options:\x1b[0m
  -v, --version   Display version
  -h, --help      Display this help guide

\x1b[1mExamples:\x1b[0m
  npx lead-approach install --all
  lead-approach setup --interactive
  lead-approach list leads.pdf --output roadmap.md
  lead-approach recon https://example.com
  lead-approach report --sample --output demo.pdf
`);
}

function showStatus() {
  if (!fs.existsSync(profileJsonPath)) {
    console.log('\x1b[33mNo profile configured yet. Run:\x1b[0m lead-approach setup --interactive');
    return;
  }
  try {
    const profile = JSON.parse(fs.readFileSync(profileJsonPath, 'utf8'));
    console.log('\x1b[1;34m=== Active Outbound Profile ===\x1b[0m');
    console.log(`Company:   ${profile.company_name || 'N/A'}`);
    console.log(`Service:   ${profile.service_offered || 'N/A'}`);
    console.log(`Tone:      ${profile.tone_of_voice || 'N/A'}`);
    console.log(`Channels:  ${(profile.channels || []).join(', ') || 'N/A'}`);
    console.log(`Website:   ${profile.website_en || profile.website_pt || 'N/A'}`);
    console.log(`Brand:     Primary: ${profile.brand_primary || 'default'} | Font: ${profile.brand_font || 'default'}`);
  } catch (err) {
    console.error('Failed to read profile.json:', err.message);
  }
}

function runInstall(installArgs) {
  const installShPath = path.resolve(rootDir, 'install.sh');
  const finalArgs = [...installArgs];
  const isNpx = __dirname.includes('_npx') || __dirname.includes('.npm');
  if (isNpx && !finalArgs.includes('--copy') && !finalArgs.includes('-c') && !finalArgs.includes('--help') && !finalArgs.includes('-h')) {
    finalArgs.push('--copy');
  }
  const result = spawnSync('bash', [installShPath, ...finalArgs], {
    stdio: 'inherit',
    cwd: process.cwd()
  });
  if (result.error) {
    console.error('\x1b[31m[Error running install.sh]\x1b[0m', result.error.message);
    process.exit(1);
  }
  process.exit(result.status ?? 0);
}

if (!command || command === '--help' || command === '-h') {
  showHelp();
  process.exit(0);
}

if (command === '--version' || command === '-v') {
  console.log(`lead-approach v${pkg.version}`);
  process.exit(0);
}

switch (command) {
  case 'install':
    runInstall(subArgs);
    break;
  case 'setup':
    runScript('setup_profile.py', subArgs);
    break;
  case 'list':
    runScript('process_list.py', subArgs);
    break;
  case 'recon':
    runScript('recon_lead.py', subArgs);
    break;
  case 'report':
    runScript('compile_report.py', subArgs);
    break;
  case 'status':
  case 'info':
    showStatus();
    break;
  default:
    console.error(`\x1b[31mUnknown command:\x1b[0m ${command}`);
    showHelp();
    process.exit(1);
}
