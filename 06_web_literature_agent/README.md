# Personal AI Research Agents Literature Agent

Network literature search agent for Personal AI Research Agents research scouting.

## What It Does

- Search public scholarly metadata APIs by keyword and year range.
- Combine results from OpenAlex, Semantic Scholar, Crossref, and arXiv.
- Deduplicate results by DOI and similar titles.
- Rank papers by PDF availability, abstract availability, citations, and year.
- Export search results to Excel, BibTeX, and Markdown.
- Optionally generate an AI summary if an API key is configured locally.

## User Guides

- Chinese guide with screenshots: [`USER_GUIDE_WITH_SCREENSHOTS_CN.md`](USER_GUIDE_WITH_SCREENSHOTS_CN.md)
- Chinese guide: [`HOW_TO_USE_CN.md`](HOW_TO_USE_CN.md)
- English guide: [`HOW_TO_USE.md`](HOW_TO_USE.md)

## Quick Start

```powershell
cd "D:\Projects_New Energy\Personal_AI_Research_Agents\06_web_literature_agent"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit.

## Optional API Configuration

Copy `.env.example` to `.env` and fill only local values.

Do not commit `.env`.

For Qwen Plus via DashScope OpenAI-compatible API:

```env
LIT_AGENT_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LIT_AGENT_MODEL=qwen-plus
LIT_AGENT_API_KEY=your-local-dashscope-key
```

OpenAlex, Semantic Scholar, and Crossref can work without keys in many cases, but API keys or contact emails improve reliability and rate limits.

## Suggested First Test

Keywords:

```text
hydrogen evolution reaction machine learning catalyst
```

Year range:

```text
2020-2026
```

Sources:

```text
OpenAlex, Semantic Scholar
```

## Product Notes

- This is an MVP for literature discovery, not a replacement for expert review.
- Always verify important papers from the publisher, DOI page, or official PDF.
- Do not scrape Google Scholar directly in this version.
- Next possible modules: saved search history, team accounts, PDF full-text extraction, RAG over downloaded open-access papers, and MCP server integration.


## Impact Factor, Web of Science, and Google Scholar

- Impact Factor is a journal-level metric from Journal Citation Reports / Clarivate. Public metadata APIs usually do not return official IF values.
- To filter by IF, export or prepare an authorized JCR/WoS journal metrics CSV and upload it in the app.
- CSV columns: `venue, impact_factor, indexed_in, jcr_quartile, metric_year, source`.
- Template: `data/journal_metrics_template.csv`.
- Web of Science direct search requires a licensed Clarivate API. This MVP supports WoS/JCR filtering through an uploaded authorized metrics file.
- Google Scholar has no official public API. This app does not scrape Google Scholar directly. If needed, configure a compliant provider such as SerpAPI with `SERPAPI_API_KEY` and select `Google Scholar (SerpAPI)` as a source.





