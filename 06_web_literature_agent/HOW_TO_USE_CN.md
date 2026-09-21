# Personal AI Research Agents 文献检索 Agent 中文使用说明

作者：Steven Yuandong Yue  
Title：AI Research Tool Builder

## 1. 这个工具是做什么的

这是 Personal AI Research Agents / Personal AI Research Agents 项目的第一版网络文献检索 Agent。

它的目标不是替代 Web of Science、Google Scholar 或专业数据库，而是帮助团队快速做第一轮文献筛选：

- 输入关键词和年份范围
- 从多个公开学术数据源检索论文
- 合并和去重结果
- 显示 DOI、论文链接、PDF 链接、引用数等信息
- 给每篇论文一个 AI 相关性评分
- 对当前选中的论文进行 AI 问答
- 导出 Excel、BibTeX、Markdown 结果

当前默认关键词是：

```text
PEM catalyst HEO
```

## 2. 如何启动

在 PowerShell 运行：

```powershell
D:\Projects_New Energy\Personal_AI_Research_Agents\06_web_literature_agent\start_literature_agent.bat
```

然后打开浏览器：

```text
http://localhost:8501
```

如果页面没有刷新，按：

```text
Ctrl + F5
```

## 3. 基本使用流程

1. 在左侧输入关键词，例如：

```text
PEM catalyst HEO
HER catalyst
OER catalyst
high entropy oxide catalyst
PEM water electrolysis catalyst
```

2. 选择发表年份范围。

3. 选择检索来源。第一版建议先用：

```text
Crossref
arXiv
```

4. 点击：

```text
开始检索 / Search literature
```

5. 查看结果表格。

6. 选择一篇论文，在“论文详情”里查看摘要、DOI、URL、PDF。

7. 在“当前论文问答”里问当前论文相关问题。

8. 最后导出 Excel、BibTeX 或 Markdown。

## 4. 当前已经支持的功能

### 4.1 最近 10 次搜索历史

页面左侧会显示最近 10 次搜索记录，包括关键词、年份、来源和筛选条件。点击 载入历史 / Load history 可以快速恢复之前的检索条件。搜索历史只保存在本机 SQLite 文件中，不会上传到 GitHub。

### 4.2 多来源检索

目前代码里支持这些来源：

- OpenAlex
- Crossref
- arXiv
- Semantic Scholar
- Google Scholar via SerpAPI

注意：支持不等于每次都稳定可用。不同来源有不同 API 限制。

### 4.3 结果表格

结果表格会显示：

- 序号
- 标题
- AI 相关性评分
- AI 相关性原因
- 数据源原始相关性
- 年份
- 期刊或来源
- 引用数
- 类型
- 是否开放获取
- 数据源
- DOI
- URL
- PDF 链接

### 4.4 可点击链接

表格里的：

- URL
- PDF

已经变成可点击链接。

### 4.5 AI Relevance Score

`AI 相关性(0-10)` 是本工具自己计算的相关性评分。

它不是数据库官方评分，也不是影响因子。

目前评分逻辑主要参考：

- 关键词是否出现在标题中
- 关键词是否出现在摘要中
- 是否有 PDF
- 是否有 DOI
- 年份是否较新
- 引用数情况

分数解释：

```text
0-3   相关性弱
4-6   有一定相关性
7-8   比较相关
9-10  高度相关
```

### 4.6 当前论文问答

可以选择一篇论文，然后问：

- 这篇论文主要讲什么？
- 和 PEM catalyst / HEO 有什么关系？
- 有哪些可以提取的数据字段？
- 是否值得优先阅读？

注意：当前问答只基于检索到的标题、摘要、DOI、期刊等信息。第一版还没有真正下载并阅读 PDF 全文。

### 4.7 AI 总结

AI 总结默认使用 Qwen Plus / DashScope。

需要在本地 `.env` 中配置：

```env
LIT_AGENT_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LIT_AGENT_MODEL=qwen-plus
LIT_AGENT_API_KEY=你的 DashScope key
```

不要把 `.env` 或真实 API key 上传到 GitHub。

### 4.8 导出

支持导出：

- Excel：适合项目筛选、分享、继续整理
- BibTeX：适合 Zotero、Mendeley、LaTeX 引用
- Markdown：适合写报告、GitHub notes、会议记录

## 5. 当前不好用或不稳定的地方

### 5.1 OpenAlex 有时会 503

OpenAlex 偶尔会出现：

```text
503 Server Error
```

这通常是 OpenAlex 服务器临时不可用，不是本工具代码错误。

处理方式：

- 暂时取消 OpenAlex
- 保留 Crossref 和 arXiv
- 过一会儿再试 OpenAlex

### 5.2 Semantic Scholar 有时会 429

Semantic Scholar 可能出现：

```text
429 Client Error
```

意思是访问被限流。

处理方式：

- 暂时取消 Semantic Scholar
- 后续配置 Semantic Scholar API key
- 降低检索频率

### 5.3 Google Scholar 不能直接爬

Google Scholar 没有官方开放 API。

第一版不会直接爬 Google Scholar 页面，因为这样容易被封，也有合规风险。

现在只预留了合规第三方接口：

```text
Google Scholar (SerpAPI)
```

如果要用，需要配置：

```env
SERPAPI_API_KEY=你的 SerpAPI key
```

### 5.4 Web of Science 不是免费公开 API

Web of Science 属于 Clarivate，需要机构或个人授权。

第一版不能直接完整检索 Web of Science。

可以先通过授权账号导出数据，再导入本项目后续版本处理。

### 5.5 影响因子不能自动获取

影响因子 IF 是 JCR / Clarivate 的期刊级指标，不是普通论文 API 自动返回的字段。

如果没有上传 JCR/WoS 期刊指标 CSV，勾选“最低影响因子”会导致没有结果。

正确做法是上传类似这样的 CSV：

```csv
venue,impact_factor,indexed_in,jcr_quartile,metric_year,source
Nature Energy,49.7,Web of Science,JCR Q1,2025,JCR
Advanced Energy Materials,24.4,Web of Science,JCR Q1,2025,JCR
Electrochemistry Communications,5.4,Web of Science,JCR Q2,2025,JCR
```

没有这张表时，不建议开启：

- Minimum impact factor
- Require Web of Science / JCR validated journal

### 5.6 检索来源还不完善

第一版主要接入公开元数据 API。

当前还没有完整接入：

- Scopus
- Web of Science API
- PubMed
- IEEE Xplore
- ScienceDirect
- ACS / RSC / Springer / Wiley 出版社全文 API
- 公司内部文献库

### 5.7 还没有全文阅读能力

当前版本主要使用 metadata 和 abstract。

还没有实现：

- 自动下载 open-access PDF
- 解析 PDF 全文
- 从全文中抽取实验条件
- 从图表中抽取数据
- 多篇论文 RAG 问答

### 5.8 AI Relevance Score 只是第一版评分

当前 AI Relevance Score 是本地规则评分，不是真正的大模型逐篇深度评审。

它适合快速排序，但不能作为最终科研判断。

后续可以升级为：

- Qwen Plus 对每篇论文打分
- 按 Personal AI Research Agents 的技术路线定制评分
- 加入材料体系、实验指标、是否有数据表等维度

## 6. 推荐当前使用方式

第一版建议这样用：

1. 不勾影响因子。
2. 不勾 Web of Science / JCR。
3. 数据源先选 Crossref + arXiv。
4. 关键词使用英文。
5. 先看 AI Relevance Score。
6. 再打开 URL / PDF 人工确认。
7. 最后导出 Excel 发给团队筛选。

## 7. 下一版可以做什么

建议 v0.2 做这些功能：

- PDF 自动下载和全文解析
- 保存搜索历史
- 将搜索结果同步到 Personal AI Research Agents 数据平台 Excel
- 按材料体系自动分类，例如 PEM、HER、OER、HEO、HEA
- Qwen Plus 深度打分
- 文献 RAG 问答
- Web of Science / JCR 导出文件导入
- 团队共享部署版本

## 8. 安全提醒

不要上传：

- `.env`
- API key
- 数据库密码
- 未获授权的 PDF 全文
- 需要保密的公司材料

当前 GitHub 上传的是代码、模板和说明，不包含真实 key。

## 9. a collaborator 如何使用这个工具

如果 a collaborator 想使用这个 Literature Agent，有两种方式。

### 方式一：本地运行

适合第一版内部测试。

前提：需要先给 a collaborator GitHub private repo 访问权限。

GitHub repo：

```text
YOUR_PERSONAL_REPOSITORY_URL
```

a collaborator 可以选择下载 ZIP，或者用 git clone：

```bash
git clone YOUR_PERSONAL_REPOSITORY_URL.git
```

进入 Agent 文件夹：

```bash
cd Personal_AI_Research_Agents/06_web_literature_agent
```

创建虚拟环境并安装依赖：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

启动网页：

```bash
streamlit run app.py
```

然后打开：

```text
http://localhost:8501
```

如果是在 Windows，也可以使用项目里的启动脚本：

```powershell
start_literature_agent.bat
```

### AI 总结和当前论文问答是否必须配置 key

不是必须。

不配置 API key 时，仍然可以使用：

- 关键词检索
- 年份筛选
- 结果表格
- URL / PDF 链接
- AI Relevance Score
- Excel / BibTeX / Markdown 导出

如果要使用：

- AI 总结
- 当前论文问答

则需要配置 Qwen Plus / DashScope key。

在 `06_web_literature_agent` 里复制：

```text
.env.example
```

改名为：

```text
.env
```

填写：

```env
LIT_AGENT_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LIT_AGENT_MODEL=qwen-plus
LIT_AGENT_API_KEY=a collaborator 自己的 DashScope key
```

注意：不要把 `.env` 或真实 API key 上传到 GitHub。

### 方式二：未来部署成网页

如果希望 a collaborator 不安装 Python、不下载代码，只通过浏览器使用，可以后续部署到云端，例如：

- Streamlit Cloud
- Hugging Face Spaces
- Render
- 阿里云
- 公司服务器

部署后，a collaborator 只需要打开一个网址，例如：

```text
https://personal-literature-agent.streamlit.app
```

但是部署前需要先处理：

- API key 安全
- 是否需要登录权限
- GitHub private repo 权限
- Google Scholar / Web of Science 授权问题
- IF/JCR 数据来源

当前第一版建议：先通过 GitHub private repo 分享代码和图文使用手册，本地运行测试；功能稳定后再考虑云端部署。





