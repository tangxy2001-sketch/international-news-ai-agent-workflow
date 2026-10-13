# 接口与工具清单

本版本包含实际使用流程所需的 Tavily Search 接入，不再只是检索指令。检索调用已整理为 Python 工具，统一处理日期、候选文件、缓存和密钥保护。

| 工具 | 用途 | 包内实现 / 外部要求 |
|---|---|---|
| Tavily Search API | 国际新闻检索，返回摘要与可取得的原文 | scripts/tavily_search.py；使用者提供自己的 TAVILY_API_KEY |
| Python 3 标准库 | HTTP、JSON、元数据保存、URL 去重、日期和脚注校验 | 无需额外 Python 依赖 |
| Node.js 与 docx | 生成含超链接与黄色高亮的 Word 文档 | npm ci 安装锁定依赖 |
| 宿主 AI 的文件与命令工具 | 读取素材、执行脚本、维护状态 | 使用者所用 AI 环境提供 |
| 宿主 AI 的语言能力 | 查询本地化、语义筛选、论点组织、写作和翻译 | 本项目提供五个技能与交接规范 |
| 宿主浏览器或人工剪藏 | 对照来源、补全合法取得的正文 | 可选；保存至任务目录 Clippings/，匹配 source URL |
| 宿主子 Agent 功能 | 按篇并行精读或翻译 | 可选；不支持时串行执行 |

## Tavily 请求

客户端固定调用 `POST https://api.tavily.com/search`，通过 Authorization Bearer 请求头传入当前用户的密钥。默认 advanced、每查询最多 5 条、请求 raw_content 和 usage，按查询计划使用 news 或 general 及域名约束。API 日期范围略放宽，返回后按用户实际起止日筛选。

参考：[Tavily 官方 Search 文档](https://docs.tavily.com/documentation/api-reference/endpoint/search)。各参数与费用以服务商当前文档及账户设置为准。请求失败不会输出请求头或服务端错误正文；日志只保存结果、用量与脱敏状态。401、403、429、额度错误停止本轮新增请求；重新执行只重试缺失结果。

## 凭据与运行边界

用户必须使用自己的 API 密钥，环境变量名是 TAVILY_API_KEY。也可由用户在终端用 --prompt-key 隐藏输入。代码不会读取私人凭据文件，不会自动加载 .env，不接受命令行明文密钥参数。示例环境文件为空，不包含可用凭据。

完整步骤见 [QUICKSTART.md](QUICKSTART.md)。CLI 的 --dry-run、测试与 Word 示例无需密钥。测试使用模拟 HTTP 响应，验证请求结构和文件交接；没有使用作者的密钥进行在线调用，不代表已验证任何个人账户、额度或实时搜索质量。

本项目不包含 Tavily Extract/Crawl 接口、独立模型 API 服务或自动创建 Agent 的运行时；这些不是本工作流的必需组件。保留实际使用的 Search 接口与宿主能力边界，不把未实现的工具列作已交付功能。
