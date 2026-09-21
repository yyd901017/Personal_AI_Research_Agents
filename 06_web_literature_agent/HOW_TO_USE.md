# How To Use: Personal AI Research Agents Literature Agent

This is the first web version of the Personal AI Research Agents literature search agent.

Author: Steven Yuandong Yue  
Title: AI Research Tool Builder

## 1. Start The App

Open PowerShell and run:

```powershell
D:\Projects_New Energy\Personal_AI_Research_Agents\06_web_literature_agent\start_literature_agent.bat
```

Then open:

```text
http://localhost:8501
```

If the page is already open but looks old, press `Ctrl + F5`.

## 2. Search Literature

The sidebar shows the latest 10 searches. Use Load history to restore previous keywords, year range, sources, and filters. Search history is saved locally in SQLite and is not committed to GitHub.

Use the left sidebar:

- Keywords: default is `PEM catalyst HEO`
- Publication year: choose a year range
- Max results: choose how many papers to show
- Search sources: OpenAlex, Crossref, arXiv, Semantic Scholar, Google Scholar via SerpAPI

Recommended stable sources for first use:

```text
Crossref
arXiv
```

OpenAlex and Semantic Scholar may sometimes return API warnings such as `503` or `429`.

## 3. Quality Filters

- Open access only: show papers likely to have free access or PDF.
- Review papers only: show review-style papers when metadata supports it.
- Minimum impact factor: requires a JCR/WoS metrics CSV.
- Require Web of Science / JCR: requires a JCR/WoS metrics CSV.

Impact Factor is not automatically provided by most public paper APIs. To use IF filters, upload a CSV with this format:

```csv
venue,impact_factor,indexed_in,jcr_quartile,metric_year,source
Nature Energy,49.7,Web of Science,JCR Q1,2025,JCR
Advanced Energy Materials,24.4,Web of Science,JCR Q1,2025,JCR
```

## 4. Read Results

Important columns:

- No.: paper number
- AI Relevance (0-10): local relevance score based on keywords, title, abstract, year, DOI, PDF, and citations
- AI Reason: explanation for the score
- Relevance: original relevance score from source APIs, often blank unless OpenAlex returns it
- URL: clickable paper page
- PDF: clickable PDF link when available

## 5. Ask Current Paper

Select a paper under `Paper Details`, then use `Ask Current Paper` to ask questions such as:

- What is this paper about?
- How is it related to PEM catalyst / HEO?
- What data fields can we extract?
- Is this paper worth reading first?

The answer uses the metadata and abstract currently available. The app does not yet download/read full PDFs.

## 6. AI Summary With Qwen Plus

The AI summary uses Qwen Plus / DashScope by default.

Create a local `.env` file from `.env.example` and set:

```env
LIT_AGENT_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LIT_AGENT_MODEL=qwen-plus
LIT_AGENT_API_KEY=your-local-dashscope-key
```

Do not commit `.env` or any real API key to GitHub.

## 7. Export

After searching, you can export:

- Excel: best for project screening and sharing
- BibTeX: best for citation managers or LaTeX
- Markdown: best for quick reports or GitHub notes

## 8. Notes For Sharing

This is a local MVP. It can be shared through GitHub as code, but others need to install dependencies and run it locally unless it is deployed to a cloud service.

Do not scrape Google Scholar directly. Use compliant third-party APIs or institutional exports.

## 9. How a collaborator Can Use This Tool

There are two practical ways for a collaborator to use this Literature Agent.

### Option 1: Run Locally

This is recommended for the first internal prototype.

First, grant a collaborator access to the private GitHub repository:

```text
YOUR_PERSONAL_REPOSITORY_URL
```

She can either download the ZIP from GitHub or clone the repository:

```bash
git clone YOUR_PERSONAL_REPOSITORY_URL.git
```

Go to the agent folder:

```bash
cd Personal_AI_Research_Agents/06_web_literature_agent
```

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Start the app:

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

On Windows, she can also use the included startup script:

```powershell
start_literature_agent.bat
```

### Is An AI API Key Required?

No. Without an API key, she can still use:

- Keyword search
- Year filtering
- Results table
- URL / PDF links
- AI Relevance Score
- Excel / BibTeX / Markdown export

An API key is only needed for:

- AI summary
- Ask Current Paper

For Qwen Plus / DashScope, copy `.env.example` to `.env` and set:

```env
LIT_AGENT_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LIT_AGENT_MODEL=qwen-plus
LIT_AGENT_API_KEY=a collaborator's local DashScope key
```

Do not commit `.env` or any real API key to GitHub.

### Option 2: Deploy As A Web App Later

If a collaborator should use it without installing Python or downloading code, the app can later be deployed to a cloud service such as:

- Streamlit Cloud
- Hugging Face Spaces
- Render
- Alibaba Cloud
- Internal company server

After deployment, she would only need to open a URL, for example:

```text
https://personal-literature-agent.streamlit.app
```

Before deployment, the team should decide:

- How to protect API keys
- Whether login is required
- Who can access the private GitHub repository
- How to handle Google Scholar / Web of Science licensing
- How to provide JCR / Impact Factor data

For the first version, the recommended approach is to share the private GitHub repository and the Chinese screenshot guide, run locally, collect feedback, and deploy later when the workflow is stable.





