# International News AI Agent Workflow

**An AI Agent workflow for research based on international news media reporting—from source collection and evidence analysis to reports and traceable Word appendices.**

一个以**国际新闻媒体报道为主要数据来源**的 **AI Agent 研究工作流**，覆盖检索、证据整理、分析报告撰写和 Word 素材文档生成。研究主题、检索范围和写作要求由使用者在运行时提供。智库材料可作为可选补充，并与新闻报道分别标注。

```mermaid
flowchart LR
    A[Search / 收集来源] --> B[Organize / 整理证据]
    B --> C[Report / 撰写报告]
    C --> D[Present / 生成文档]
    C -- 补充证据 --> B
```

## AI Agent roles and data sources

The coordinator routes tasks through four specialist roles: Search, Organize, Report, and Present. One AI Agent can perform these roles sequentially; compatible hosts may delegate independent tasks to multiple agents. This repository defines skills, handoff contracts, and deterministic utilities. It does not implement a standalone multi-agent runtime or model API orchestration service.

Primary source data is international news media reporting, selected through the configurable regional publisher catalog. Optional think-tank material is a separately identified supplementary source type. Publisher domains are query filters, not API endpoints or licensed news feeds. The bundled case uses explicitly fictional articles and does not contain real reporting.

## Real retrieval with Tavily

The package includes an executable **Tavily Search API client** and the complete retrieve → review → save handoff. **Every user must provide their own Tavily API key and quota. No author's credentials are included.**

- Start with [START-HERE.md](START-HERE.md) for an AI-ready prompt.
- Follow the full [usage guide](docs/QUICKSTART.md) for setup, query planning, retrieval, screening, writing, and Word export.
- Read the [tool inventory](docs/TOOLS.md) to distinguish the included API client from capabilities supplied by the host AI.

The key is read from TAVILY_API_KEY, or entered privately by the user with --prompt-key. The .env.example file is a blank template and is not automatically loaded. Do not paste keys into an AI conversation, command argument, or tracked file.

## Capabilities

- Separate collection, evidence analysis, drafting, and presentation roles.
- Preserve source URLs and distinguish quotations, paraphrases, and analytical claims.
- Resume work from saved artifacts and record incomplete evidence explicitly.
- Generate Word documents with source hyperlinks and highlighted cited paragraphs.
- Validate input structure and citation mappings with local tools and CI.

## Quick start

Requires Python 3.9+ and Node.js 20+.

```bash
npm ci
npm test
npm run demo
python3 scripts/workflow.py validate examples/demo
python3 scripts/check_package.py
```

The demo models a fictional port scheduling pilot with six fabricated source articles and an analytical report. It writes a validated Word document to a temporary directory. It does not perform live research or require an API key.

## Run a task

```bash
python3 scripts/workflow.py init runs/demo \
  --topic '自定义研究议题' --keywords '关键词一,关键词二' \
  --start 2030-01-01 --end 2030-01-31
```

The dates above are illustrative. Replace them with the desired research period. Open this repository in an agent environment with file and web tools, then ask:

> Read skills/media-workflow/SKILL.md and execute the task in runs/demo/request.json. Record evidence gaps and produce a draft report and a source appendix.

The AI prepares and reviews queries, then runs:

```bash
python3 scripts/tavily_search.py plan runs/demo
# AI edits queries.json, localizes queries, and sets reviewed: true.
python3 scripts/tavily_search.py search runs/demo --dry-run
# Real retrieval requires the user's own TAVILY_API_KEY in the environment.
python3 scripts/tavily_search.py search runs/demo --max-calls 16
# AI reviews candidates.json and writes screening.json for every candidate.
python3 scripts/tavily_search.py save runs/demo
```

Read the usage guide before executing a real search: it consumes the user's own API quota. Subsequent AI stages organize evidence, draft the report, and produce articles.json for the Word renderer. The scripts implement retrieval and deterministic file operations; semantic work and optional subagent delegation use the host AI environment.

## Project map

| Path | Purpose |
|---|---|
| [WORKFLOW.md](WORKFLOW.md) | Stage contracts, quality gates, and recovery |
| [START-HERE.md](START-HERE.md) | Copyable instructions for another AI Agent |
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | Complete end-to-end usage guide |
| [docs/TOOLS.md](docs/TOOLS.md) | Actual API and tool inventory |
| [scripts/tavily_search.py](scripts/tavily_search.py) | Tavily planning, retrieval, caching, screening handoff, and source saving |
| [skills/media-workflow](skills/media-workflow/SKILL.md) | Coordinator instructions |
| [skills/](skills/) | Four stage-specific skills |
| [config/sources.json](config/sources.json) | Editable regional publisher and language catalog |
| [Writing style](skills/media-report/references/writing-style.md) | Analytical structure, attribution, and quotation rules |
| [scripts/](scripts/) | Initialization, validation, and demo utilities |
| [examples/demo](examples/demo/) | Synthetic input and citation example |
| [docs/RELEASE-CHECKLIST.md](docs/RELEASE-CHECKLIST.md) | Publication checks and limitations |

Keep this repository intact so relative skill links remain valid. Actual assignments and output belong in the Git-ignored runs/ directory. Document generation does not grant permission to redistribute source content. No open-source license has been selected.

## 中文说明

项目保留八组媒体与地区检索配置，以及帽段、总领句、分论点、叙事归纳和脚注等文风要求。研究对象由实际任务输入，不预置固定对象。虚构案例使用完整情节与模拟报道展示写法；其中的虚构媒体与真实检索目录分开，避免把构造观点归给现实媒体。

真实检索使用随包提供的 Tavily Search 客户端。**其他使用者必须配置自己的 TAVILY_API_KEY**；项目不提供任何可用密钥。完整流程与命令见中文使用指南，其他 AI 可从 START-HERE.md 直接开始。
