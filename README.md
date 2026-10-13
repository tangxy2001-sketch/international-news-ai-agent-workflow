# Media Research Workflow

**A reusable agent workflow for collecting sources, organizing evidence, drafting reports, and producing a traceable Word appendix.**

一个通用媒体研究工具包：用四个阶段把来源资料转化为可核查的报告与文档。研究主题、检索范围和写作要求由使用者在运行时提供。

```mermaid
flowchart LR
    A[Search / 收集来源] --> B[Organize / 整理证据]
    B --> C[Report / 撰写报告]
    C --> D[Present / 生成文档]
    C -- 补充证据 --> B
```

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

The agent performs research and semantic review. The CLI initializes files, checks citation mappings, and formats documents; it is not an autonomous model service. Use a search provider supported by the host environment. If that provider needs credentials, configure them through its environment or secret manager, never in task messages or tracked files.

## Project map

| Path | Purpose |
|---|---|
| [WORKFLOW.md](WORKFLOW.md) | Stage contracts, quality gates, and recovery |
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
