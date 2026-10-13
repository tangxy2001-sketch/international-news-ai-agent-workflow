# Tool and interface boundaries

## Retrieval

This package contains the Search role's instructions and source-domain configuration. It does not ship a working search API client, HTTP retrieval script, browser automation module, crawler, provider SDK, or API subscription.

The AI Agent must obtain international news media reporting through tools supplied by its host environment or an API integration installed separately. The source catalog limits or guides searches; it does not provide direct data access. Optional think-tank material should be identified as supplemental analysis.

Before a real task, check whether the host exposes a usable search tool, whether that tool supports date/domain filters, and whether source passages can be retrieved with sufficient context. If retrieval is unavailable, import permitted material and start at Organize, or report the missing capability. Never claim to have searched because a query plan was generated.

`.env.example` contains an empty `SEARCH_API_KEY` placeholder only. No project script reads this variable or automatically loads an .env file. Credentials and provider-specific configuration belong in the host's environment or secret manager; no real credentials are distributed here.

## Executable utilities

- scripts/workflow.py: initialize task directories and check report-footnote mappings.
- skills/media-present/scripts/generate.js: validate article JSON and render a Word appendix.
- scripts/check_docx.py: check ZIP/XML structure, source hyperlinks, and highlights.
- scripts/check_package.py: inspect tracked package files for common publication leaks.
- scripts/demo.js: render and check the bundled fictional case without network retrieval.

These utilities do not call a language model, perform live news searches, or establish factual accuracy. The host AI Agent performs semantic analysis and source review.
