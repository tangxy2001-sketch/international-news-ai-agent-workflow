# Project instructions

Read START-HERE.md, docs/QUICKSTART.md, and WORKFLOW.md, then load the skill for the requested stage. This is a generic media research toolkit; task-specific requirements belong in an ignored runs/ directory.

Never add real assignments, unpublished documents, client names, credentials, personal paths, or third-party article bodies to examples or documentation. Use clearly synthetic examples. Do not infer that successful structural checks establish factual accuracy.

After changes run npm test, npm run demo, and python3 scripts/check_package.py. Only package tracked, reviewed files. Keep upstream private material outside this repository.

Use scripts/tavily_search.py for Tavily retrieval. Users must supply their own TAVILY_API_KEY privately. Never inspect secret files, echo environment values, or include keys in prompts. Tests mock HTTP and must not require real credentials. Keep API/tool boundaries and docs synchronized with implementation.
