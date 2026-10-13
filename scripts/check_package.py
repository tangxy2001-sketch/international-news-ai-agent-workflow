#!/usr/bin/env python3
"""Check public package files without printing potentially sensitive content."""
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[1]
if (root / '.git').exists():
    paths = [root / p for p in subprocess.check_output(['git','ls-files','-z'], cwd=root, text=True).split('\0') if p]
else:
    paths = [p for p in root.rglob('*') if p.is_file() and not any(x in p.parts for x in ['node_modules','__pycache__','dist'])]
errors = []
for path in paths:
    relative = path.relative_to(root)
    if any(x in relative.parts for x in ['runs','node_modules','.git']) or path.name in ['SECRET.md','.env']:
        errors.append(str(relative) + ': excluded artifact')
    text = path.read_text(encoding='utf-8')
    patterns = [r'gh[pousr]_[A-Za-z0-9]{20,}', r'tvly-[A-Za-z0-9_-]{15,}', r'/Users/' + r'[^/\s]+/', r'/home/' + r'[^/\s]+/']
    if any(re.search(pattern,text) for pattern in patterns):
        errors.append(str(relative) + ': possible credential or private path')
    if chr(0xfffd) in text:
        errors.append(str(relative) + ': damaged encoding')
    if relative.parts[0] == 'examples':
        for url in re.findall(r'https?://[^\s"<>]+', text):
            if not url.startswith('https://example.com/'):
                errors.append(str(relative) + ': non-example URL')
assert not errors, '\n'.join(errors)
print('Package checks passed: {} files. Contextual review is still required.'.format(len(paths)))
