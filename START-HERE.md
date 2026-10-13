# AI Agent entry point

将下面的指令交给能读写文件、运行命令的 AI Agent，并替换任务目录：

> 请阅读 AGENTS.md、docs/QUICKSTART.md 和 skills/media-workflow/SKILL.md。任务目录为 runs/my-topic，按照 request.json 与可选 outline.md 完成 Tavily 检索、候选筛选保存、证据整理、报告撰写和 Word 素材呈现。先检查已有进度，复用成功结果。用户将通过运行环境配置自己的 TAVILY_API_KEY；不要读取、打印、请求粘贴或写入用户的密钥。缺少密钥时提示用户自行配置，仍可完成查询计划。不得把模板查询误当作已完成本地化，不得把检索成功误当作证据核验完成。记录未解决的覆盖与来源缺口，按已授权范围继续推进。

## 必须理解的交接顺序

1. 初始化任务；读取媒体配置与研究要求。
2. 生成 queries.json，由 AI 本地化并检查，然后设 reviewed: true。
3. 调用 scripts/tavily_search.py search；失败或预算耗尽时保留已取得材料。
4. AI 阅读 candidates.json，为全部候选生成 screening.json。
5. 调用 save，将通过筛选的报道保存为 Markdown。
6. 精读并产出论点整理与 evidence-map.json。
7. 依据文风要求撰写报告、核对脚注与原文。
8. 按脚注组织 articles.json，运行 DOCX 生成与检查。
9. 更新 pipeline-status.md，交付报告、素材文档和核验结果。

Tavily 密钥属于使用者本人；Node/docx 用于文档输出；Python 标准库用于接口与文件操作。翻译与语义判断由宿主 AI 完成。真实检索会使用个人 API 额度；项目自带 demo 与测试均不调用真实 API。
