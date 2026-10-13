---
name: media-present
description: Render a report source appendix as a Word document, preserving source links and highlighting passages actually cited.
---

# Present the source appendix

Input: 报告初稿.md, organized evidence, and permitted source text. Output: articles.json and 素材呈现.docx.

1. Parse report footnotes in numeric order. Match each URL to verified source material: prefer legally obtained complete Clippings/ files, then 原始素材/. Preserve quality labels. Similar titles are candidates, not proof of a match.
2. Translate material if requested and permitted, preserving paragraph meaning, uncertainty, dates, units, and attribution. Label excerpts as excerpts. Do not present missing or truncated text as a complete translation.
3. Highlight passages actually quoted or paraphrased by the report. Do not highlight unrelated content merely because it appears in the evidence notes.
4. Produce one JSON object per footnote using [the example](../../examples/demo/articles.json). Serialize with a standard JSON library; do not change source punctuation to repair JSON syntax.
5. From the repository root run:

```bash
npm ci
python3 scripts/workflow.py validate runs/demo
node skills/media-present/scripts/generate.js runs/demo/articles.json runs/demo/素材呈现.docx
python3 scripts/check_docx.py runs/demo/素材呈现.docx
```

Use the actual run directory. Existing output paths are rejected; archive the old version or choose a new path. The renderer uses blue headings, clickable source URLs, and yellow highlights. Confirm source count and semantic correspondence, then record completion and limitations in pipeline-status.md.
