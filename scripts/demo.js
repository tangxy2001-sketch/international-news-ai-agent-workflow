const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const output = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'media-demo-')), '素材呈现.docx');
execFileSync(process.execPath, [path.join(root, 'skills/media-present/scripts/generate.js'), path.join(root, 'examples/demo/articles.json'), output], {stdio:'inherit'});
execFileSync('python3', [path.join(root, 'scripts/check_docx.py'), output], {stdio:'inherit'});
