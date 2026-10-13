---
name: media-workflow
description: Coordinate source collection, evidence organization, report drafting, and document presentation for a user-defined media research task.
---

# Coordinate the workflow

Read [WORKFLOW.md](../../WORKFLOW.md) and the executable steps in [QUICKSTART.md](../../docs/QUICKSTART.md). Identify the topic, date range, permitted source scope, desired outputs, and existing material. Ask only for essential missing inputs.

1. Inspect request.json and pipeline-status.md in the run directory.
2. Select the earliest incomplete stage after checking its actual artifacts.
3. Load only the relevant skill: [search](../media-search/SKILL.md), [organize](../media-organize/SKILL.md), [report](../media-report/SKILL.md), or [present](../media-present/SKILL.md).
4. Enforce the stage handoff contract. Record gaps and return to the stage that can resolve them.
5. Deliver the requested artifacts with verification results and remaining limitations.

Independent source tasks may run concurrently when supported and authorized. Merge only validated results. Keep shared reports, indexes, and state updates under one writer.

Tavily Search is implemented in scripts/tavily_search.py. Use only the current user’s own key supplied by their environment; never ask to see its value. Missing credentials block live retrieval, not offline planning. Do not bypass AI screening between candidates.json and source saving. API success is not evidence validation.
