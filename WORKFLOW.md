# AI Agent workflow contract

## Execution model

An AI Agent coordinator manages four roles. One agent may perform all roles sequentially; independent collection or translation tasks may be delegated when the host supports it and the task permits it. The coordinator alone writes shared indexes and final outputs.

Primary research data comes from international news media reporting; optional think-tank analysis is labeled separately. Retrieval is supplied by the host environment, not by a bundled API client. See [tool boundaries](docs/TOOLS.md).

## Task specification

Initialize a directory with scripts/workflow.py. request.json contains the topic, keywords, date interval, and source groups. Default source groups and publisher domains are defined in config/sources.json; select groups with --regions or customize the catalog for the task. Date endpoints are inclusive. Optional outline and style instructions are supplied by the user and remain in the run directory.

## Stage handoffs

| Stage | Inputs | Outputs | Quality gate |
|---|---|---|---|
| Search | Task specification, permitted source scope | 原始素材/, search-log.md | Verifiable URL, date, relevance, access quality, duplicate check |
| Organize | Collected material, optional outline | 素材整理（按论点）.md, evidence-map.json | Claims linked to source passages; gaps and conflicting evidence recorded |
| Report | Evidence map, organized material, writing requirements | 报告初稿.md, review.md | Every cited claim traceable; quotations and uncertainty preserved |
| Present | Draft, source materials, evidence map | articles.json, 素材呈现.docx | Citation IDs and URLs match; cited passages highlighted; document validates |

## Data contracts

Source metadata: title, source, publisher, published, created, source_group, content_quality (`full` or `partial`). Unknown dates are null. Source text and summaries must be clearly distinguished.

evidence-map.json: `{ "claims": [{ "id": "C1", "text": "Claim", "sources": ["https://example.com/source"], "limitations": [] }] }`. Independent evidence is counted by original reporting, not the number of syndicated copies. Support thresholds are task-specific; never add citations just to hit a target.

Report footnotes follow `[^1]: https://example.com/source`. Use one number per URL and reuse that number for repeated citations. First appearances are numbered consecutively.

articles.json follows [the synthetic example](examples/demo/articles.json). Each item has a positive consecutive footnote, media_cn, title_cn, url, and paragraphs with text and a Boolean highlight. At least one genuinely cited passage must be highlighted. The renderer refuses truncated translations and existing output paths.

## State and recovery

Update pipeline-status.md after each stage: status (pending, running, needs_input, completed, failed), inputs, output paths, checks, and remaining gaps. Verify files before resuming; do not trust a status label alone. When sources or the outline change, invalidate affected downstream stages.

Retry transient provider errors only within the task's budget and provider limits. Record partial results. Missing evidence or unverifiable citations remain gaps, not completed work.

## Review and interaction

Reuse the user's existing task authorization. Show meaningful findings and proposed outline changes. Ask only when essential input is missing or a material decision cannot be inferred. Keep confirmed structure unless evidence requires revision, and record the reason.

Structural validation cannot establish factual correctness, translation quality, or whether a source supports a claim. The agent must review those points against the original material and record findings in review.md.

## Default editorial format

Use the analytical report style in [writing-style.md](skills/media-report/references/writing-style.md) unless the user supplies another format. The [fictional case](examples/demo/README.md) demonstrates the format and reasoning with fabricated events and sources, distinct from the real publisher catalog.
