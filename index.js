const path = require('node:path');
const fs = require('node:fs');

const rootDir = __dirname;
const skillDir = path.resolve(rootDir, '.agents', 'skills', 'lead-approach');
const scriptsDir = path.resolve(skillDir, 'scripts');
const templatesDir = path.resolve(skillDir, 'templates');
const configDir = path.resolve(skillDir, 'config');
const profileJsonPath = path.resolve(configDir, 'profile.json');

function getProfile() {
  if (fs.existsSync(profileJsonPath)) {
    return JSON.parse(fs.readFileSync(profileJsonPath, 'utf8'));
  }
  return null;
}

module.exports = {
  rootDir,
  skillDir,
  scriptsDir,
  templatesDir,
  configDir,
  profileJsonPath,
  getProfile
};
