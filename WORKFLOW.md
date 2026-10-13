# AI Agent workflow contract

## Execution model

An AI Agent coordinator manages four roles. One agent may perform all roles sequentially; independent collection or translation tasks may be delegated when the host supports it and the task permits it. The coordinator alone writes shared indexes and final outputs.

Primary research data comes from international news media reporting; optional think-tank analysis is labeled separately. Retrieval uses the bundled Tavily Search client with the current user's own API key. The host supplies the AI model, file access, and command execution. See [tool boundaries](docs/TOOLS.md).

## Task specification

Initialize a directory with scripts/workflow.py. request.json contains the topic, keywords, date interval, and source groups. Default source groups and publisher domains are defined in config/sources.json; select groups with --regions or customize the catalog for the task. Date endpoints are inclusive. Optional outline and style instructions are supplied by the user and remain in the run directory.

## Stage handoffs

| Stage | Inputs | Outputs | Quality gate |
|---|---|---|---|
| Search | Task specification, queries.json, user-owned TAVILY_API_KEY | candidates.json, screening.json, 原始素材/, search-log.json / .md | Verifiable URL, date, relevance, access quality, duplicate check |
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

## Executable Search handoff

Read [QUICKSTART.md](docs/QUICKSTART.md). Run `tavily_search.py plan`, have the AI localize and review queries.json, then run `search`. The AI reviews every candidate and writes screening.json before `save`. No semantic pass/fail decision is inferred by the API client. Candidate raw content starts as partial until reviewed; summary-only content cannot be labeled full.

Successful requests are cached by the request and task interval; changing the plan creates new request IDs. max-calls bounds new requests per invocation. Failed requests are not cached as successes. Rerun after fixing credentials/limits or allowing more calls. The client does not auto-retry in a loop; record and investigate repeated failures. Mark Search complete only after assessing per-query failures, region coverage, screening outcomes, and remaining source gaps.

A user can import legally obtained files into Clippings/ when the API lacks sufficient text. Keep source URLs and completeness labels. Later stages must prioritize verified full source material, not silently upgrade snippets to full articles.
