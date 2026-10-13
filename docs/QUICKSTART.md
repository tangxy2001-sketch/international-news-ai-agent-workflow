# 使用流程：给使用者和执行任务的 AI

项目提供可执行的 Tavily Search 客户端，以及真实的“检索—筛选保存—精读整理—报告—素材呈现”交接流程。数据以国际新闻媒体报道为主，智库分析作为单独标注的补充。案例、事件和引语全部虚构；实际研究对象由使用者填写。

## 1. 准备环境与自己的 API 密钥

需要 Python 3.9+、Node.js 20+，以及能够读写本地文件、运行命令的 AI Agent。在项目根目录执行：

```bash
npm ci
npm test
npm run demo
```

Python 检索脚本只用标准库；Node 的 `docx` 依赖由 npm 安装。以上演示和测试不联网检索、不需要密钥。

真实检索需要使用者在 [Tavily](https://app.tavily.com/) 获取**自己的 API 密钥和额度**。项目不提供作者的密钥、账户或订阅。两种配置方式：

- 推荐让运行环境的密钥管理功能注入 `TAVILY_API_KEY`，随后 AI 可以运行检索脚本，但不得读取或打印变量值。
- 也可由使用者在自己的交互式终端执行下文的 `--prompt-key` 命令，密钥输入不回显，只在该进程内使用。不要让 AI 在对话中索要密钥，不把密钥写进命令参数或提交到 Git。

`.env.example` 展示变量名；脚本**不会自动加载 .env**，复制文件本身不等于配置完成。使用环境注入或隐藏输入即可。

## 2. 初始化真实任务

在终端执行，替换议题、关键词和日期；以下参数仅为格式示意：

```bash
python3 scripts/workflow.py init runs/my-topic \
  --topic '用户指定的研究议题' --keywords '关键词一,关键词二' \
  --start 2031-04-01 --end 2031-04-30
python3 scripts/tavily_search.py plan runs/my-topic
```

默认为八个来源分组。需要限定范围时，在 init 后追加如 `--regions '英国,欧洲大陆'`。已有目录不覆盖。编辑 request.json 可调整任务规格；已有输出时改任务须重新核对下游版本。

如有提纲、篇幅、重点问题或风格要求，写入 runs/my-topic/outline.md。需要自己的媒体清单时编辑 config/sources.json；媒体目录是查询配置，不是现成的数据订阅。

## 3. 由 AI 编写查询计划

请 AI 阅读 skills/media-workflow/SKILL.md、request.json 和查询模板 queries.json：

- 根据议题与各组语言改写查询，每组先准备 1—2 条。
- 模板中的 query 只是原始议题拼接，language_hint 只是提示；程序不会自动翻译。
- 配置 domains（仅域名，不含协议）；新闻用 topic: news，智库可用 general。
- 完成范围与语言检查后，将 queries.json 的 reviewed 设为 true。这表示 AI 已完成计划检查，不是要求用户再次确认。
- 缺口补搜只增加必要查询；新查询改变请求指纹，旧成功查询可复用。

用以下命令检查实际请求计划，不联网也不读取密钥：

```bash
python3 scripts/tavily_search.py search runs/my-topic --dry-run --max-calls 16
```

## 4. 调用 Tavily 并保存候选结果

环境已经注入自己的密钥时：

```bash
python3 scripts/tavily_search.py search runs/my-topic --max-calls 16
```

需要手动输入自己的密钥时，由用户在终端执行：

```bash
python3 scripts/tavily_search.py search runs/my-topic --max-calls 16 --prompt-key
```

脚本向固定的 Tavily Search 地址发送请求，读取返回的正文或摘要。默认 advanced、每查询最多 5 条结果，记录实际 usage；收费和限额以个人账户及服务商政策为准。`--max-calls` 限制本次新增 API 请求次数，不是累计费用上限。

输出 candidates.json、search-log.json、search-log.md 和 .search-cache/。同一请求复用成功缓存；失败请求在下次命令中重试，脚本不会自动循环消耗额度。401、403、429 和额度错误停止本次新增请求，但保留缓存。错误或预算未完成时返回非零退出码，已取得结果仍可审阅；中断后可再次执行同一命令。

按实际发布日期校验用户指定的包含首尾日区间；未知日期不能直接接受。URL 去掉常见跟踪参数后去重，保留影响文章身份的其他参数。结果中的 raw_content 也可能不完整，因此 content_quality 初始为 partial，由 AI 回查后判断。

## 5. AI 逐篇筛选并正式保存

AI 阅读 candidates.json，为每个候选生成一个 screening.json 条目；不得缺项、重复或使用虚构候选 ID。示例：

```json
[
  {
    "id": "替换为候选结果中的真实ID",
    "decision": "accept",
    "reason": "与研究对象有实质关系，包含可归因的分析观点，日期已核实。",
    "content_reviewed": true,
    "content_quality": "full"
  }
]
```

`decision` 为 accept、reject 或 needs_review。筛选包括：实质相关性、观点价值、日期范围、正文质量，以及同源转载去重。词频和观点信号仅辅助判断，不能代替语义精读。正文不足、日期未知时用 needs_review；仅摘要可保存为 partial，但不能当成全文引用。

若从原页面核实了缺失日期，可在 candidates.json 更新 published，并在筛选理由中记录核验依据；不要改任务指纹或猜测日期。摘要无法直接标为 full；补齐正文应另存合法取得的 Clippings/ 文件，保留同一 source URL 与来源说明。

```bash
python3 scripts/tavily_search.py save runs/my-topic
```

接受的报道保存到 原始素材/<分组>/<候选ID>.md，包含可解析的 frontmatter。重复执行不覆盖已保存文章；若需替换正文，保留版本并由 AI 同步证据索引。脚本不会把完成请求等同于完成检索阶段，协调 Agent 仍需检查未解决的筛选项和覆盖缺口。

## 6. AI 精读整理、撰写与引用核验

执行 skills/media-organize/SKILL.md：逐篇提取独特信息、直接引语、间接转述和限制条件，按论点组织，输出 素材整理（按论点）.md 与 evidence-map.json。依据提纲构建框架；默认争取每个分论点至少 3 个独立来源，不足标注或补搜。不能以同一通讯稿的转载增加独立证据数量。

执行 skills/media-report/SKILL.md 和文风规范：输出 报告初稿.md 与 review.md。保留帽段、论点标题、总领句和分论点；每个判断回到对应来源。专家直引与转述分开，保留日期、数字和不确定性。新增引用先回到整理阶段，不绕过证据映射。

## 7. AI 翻译素材并生成 Word

执行 skills/media-present/SKILL.md：按脚注 URL 优先寻找合法取得的 Clippings/，再找原始素材；只有核实同一报道才可替换。翻译或整理成 articles.json，并标记报告实际引用的段落。能够分配任务的宿主可分批翻译，主 Agent 统一合并；不能并发时顺序完成相同流程。

```bash
python3 scripts/workflow.py validate runs/my-topic
node skills/media-present/scripts/generate.js runs/my-topic/articles.json runs/my-topic/素材呈现.docx
python3 scripts/check_docx.py runs/my-topic/素材呈现.docx
```

已有 Word 输出不会覆盖，改用新的版本文件名。完成后核对数量、来源匹配、翻译完整性、引用高亮和证据缺口，更新 pipeline-status.md。结构检查不能代替原文核验。

## 8. 给其他 AI 的启动指令

使用 [START-HERE.md](../START-HERE.md) 中的提示词。检索脚本处理 API 和文件，AI 负责查询语言、语义筛选、精读、写作与翻译。宿主提供 AI 模型能力，本项目不另行实现模型 API 服务。

实际任务、缓存和素材应保存在 runs/，该目录默认不提交。公开项目和示例不可加入真实任务材料、凭据或来源使用权限不允许再分发的全文。
