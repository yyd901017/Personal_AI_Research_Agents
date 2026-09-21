# Personal AI Research Agents WeChat Research Agent

A separate Streamlit agent for finding and extracting research leads from WeChat public-account articles.

Author: Steven Yuandong Yue  
Title: AI Research Tool Builder

## User Guides

Markdown guides:

- 中文图文使用手册: [`USER_GUIDE_WITH_SCREENSHOTS_CN.md`](USER_GUIDE_WITH_SCREENSHOTS_CN.md)
- 中文说明: [`HOW_TO_USE_CN.md`](HOW_TO_USE_CN.md)

HTML guides, easier to open locally with screenshots rendered:

- 中文 HTML 使用说明: [`docs/html/HOW_TO_USE_CN.html`](docs/html/HOW_TO_USE_CN.html)
- English HTML guide: [`docs/html/HOW_TO_USE_EN.html`](docs/html/HOW_TO_USE_EN.html)
- 中文图文 HTML 使用手册: [`docs/html/USER_GUIDE_WITH_SCREENSHOTS_CN.html`](docs/html/USER_GUIDE_WITH_SCREENSHOTS_CN.html)

## Difference From Literature Agent

- `06_web_literature_agent`: searches scholarly metadata APIs such as Crossref, arXiv, OpenAlex, Semantic Scholar.
- `07_wechat_research_agent`: focuses on WeChat public-account articles as research leads.

This agent does not bulk-scrape WeChat or connect directly to a personal WeChat account.

## Features

- Generate external WeChat article search links.
- Search launcher includes Sogou WeChat, Bing site search, and Google site search.
- Parse WeChat article URL when accessible.
- Accept pasted WeChat article text when URL access is restricted.
- Extract DOI candidates and title candidates.
- Verify candidates through Crossref.
- Export extracted clues to Excel.

## Quick Start

```powershell
cd "D:\Projects_New Energy\Personal_AI_Research_Agents\07_wechat_research_agent"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py --server.port 8502
```

Or run:

```powershell
D:\Projects_New Energy\Personal_AI_Research_Agents\07_wechat_research_agent\start_wechat_research_agent.bat
```

Open:

```text
http://localhost:8502
```

## Notes

The attached ChatGPT-on-WeChat / WordPress article describes a different future direction: connecting an official WeChat public account to an AI bot service. That would be a deployment/integration project requiring WeChat public-account admin credentials, server configuration, token/aes key setup, and API key security.

This first version is safer and simpler: it helps users search public WeChat article pages and extract paper clues manually or semi-automatically.




