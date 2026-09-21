from __future__ import annotations

from datetime import date
from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from literature_agent.exporters import to_bibtex, to_dataframe, to_excel_bytes, to_markdown_report
from literature_agent.history import load_recent_searches, save_search_history
from literature_agent.models import SearchQuery
from literature_agent.search import CONNECTORS, add_ai_relevance_scores, search_literature
from literature_agent.summarizer import ai_available, answer_paper_question, summarize_papers


load_dotenv()

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_METRICS_CSV = PROJECT_DIR / "data" / "journal_metrics_template.csv"

COLUMN_LABELS = {
    "no": "序号 / No.",
    "title": "标题 / Title",
    "year": "年份 / Year",
    "venue": "期刊或来源 / Venue",
    "impact_factor": "影响因子 / IF",
    "indexed_in": "收录 / Indexed In",
    "jcr_quartile": "JCR 分区 / Quartile",
    "citation_count": "引用数 / Citations",
    "relevance_score": "相关性 / Relevance",
    "ai_relevance_score": "AI 相关性(0-10) / AI Relevance",
    "ai_relevance_reason": "AI 相关性原因 / AI Reason",
    "paper_type": "类型 / Type",
    "open_access": "开放获取 / OA",
    "source": "数据源 / Source",
    "doi": "DOI",
    "url": "链接 / URL",
    "pdf_url": "PDF 链接 / PDF",
}

st.set_page_config(
    page_title="Literature Search Agent | 文献检索助手",
    page_icon="CE",
    layout="wide",
)

st.title("文献检索 Agent")
st.caption("Network Literature Search Assistant | 网络文献检索助手")
st.markdown("**Author / 作者:** Steven Yuandong Yue  |  **Title:** AI Research Tool Builder")

DEFAULT_KEYWORDS = "PEM catalyst HEO"
DEFAULT_SOURCES = ["OpenAlex", "Crossref", "arXiv"]
DEFAULT_SUMMARY_GOAL = "筛选对氢能源材料、AI 数据提取和催化剂发现最有价值的论文。"
SUMMARY_QUICK_GOALS = [
    "总结这些论文中最值得优先阅读的 5 篇，并说明原因。",
    "筛选对氢能源材料、AI 数据提取和催化剂发现最有价值的论文。",
    "总结这些论文和 PEM catalyst / HEO / 氢能源催化剂的关系。",
    "按研究方向把这些论文分类，并指出每类代表论文。",
    "提取这些论文中可能有用的数据字段，例如材料体系、催化剂、性能指标、实验条件。",
    "从商业研发角度判断哪些论文最适合 Personal AI Research Agents 后续跟进。",
]

for key, value in {
    "keywords_input": DEFAULT_KEYWORDS,
    "year_range_input": (2020, date.today().year),
    "max_results_input": 25,
    "sources_input": DEFAULT_SOURCES,
    "open_access_input": False,
    "review_only_input": False,
    "use_min_if_input": False,
    "min_if_input": 5.0,
    "require_wos_input": False,
    "summary_goal_input": DEFAULT_SUMMARY_GOAL,
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

with st.sidebar:
    st.header("最近搜索 / Recent Searches")
    recent_searches = load_recent_searches(10)
    if recent_searches:
        labels = [
            f"{item['created_at']} | {item['keywords']} | {item['year_from']}-{item['year_to']}"
            for item in recent_searches
        ]
        selected_history_label = st.selectbox("选择历史 / Select history", labels, key="history_select")
        if st.button("载入历史 / Load history", use_container_width=True):
            selected_history = recent_searches[labels.index(selected_history_label)]
            st.session_state.keywords_input = selected_history["keywords"]
            st.session_state.year_range_input = (selected_history["year_from"], selected_history["year_to"])
            st.session_state.max_results_input = selected_history["max_results"]
            st.session_state.sources_input = [s for s in selected_history["sources"] if s in CONNECTORS]
            st.session_state.open_access_input = selected_history["open_access_only"]
            st.session_state.review_only_input = selected_history["review_only"]
            st.session_state.use_min_if_input = selected_history["min_impact_factor"] is not None
            st.session_state.min_if_input = float(selected_history["min_impact_factor"] or 5.0)
            st.session_state.require_wos_input = selected_history["require_wos_or_jcr"]
            st.rerun()
    else:
        st.caption("暂无历史 / No history yet")
    st.header("检索条件 / Search")
    keywords = st.text_area(
        "关键词 / Keywords",
        value=st.session_state.keywords_input,
        key="keywords_input",
        height=100,
        help="可以输入英文关键词，也可以输入多个短语。",
    )

    current_year = date.today().year
    year_from, year_to = st.slider(
        "发表年份 / Publication year",
        min_value=1990,
        max_value=current_year,
        value=st.session_state.year_range_input,
        key="year_range_input",
    )

    max_results = st.slider("最大结果数 / Max results", min_value=5, max_value=100, value=st.session_state.max_results_input, step=5, key="max_results_input")
    sources = st.multiselect(
        "检索来源 / Search sources",
        options=list(CONNECTORS.keys()),
        default=st.session_state.sources_input,
        key="sources_input",
        help="Google Scholar 需要配置合规第三方 API key 后才能使用。",
    )

    st.header("质量筛选 / Quality Filters")
    open_access_only = st.checkbox("只看开放获取 / Open access only", value=st.session_state.open_access_input, key="open_access_input")
    review_only = st.checkbox("只看综述论文 / Review papers only", value=st.session_state.review_only_input, key="review_only_input")
    use_min_if = st.checkbox("设置最低影响因子 / Minimum impact factor", value=st.session_state.use_min_if_input, key="use_min_if_input")
    min_impact_factor = None
    if use_min_if:
        min_impact_factor = st.number_input("IF >=", min_value=0.0, value=st.session_state.min_if_input, step=0.5, key="min_if_input")

    require_wos_or_jcr = st.checkbox("要求 Web of Science / JCR 验证期刊", value=st.session_state.require_wos_input, key="require_wos_input")
    metrics_upload = st.file_uploader(
        "上传 JCR/WoS 期刊指标 CSV",
        type=["csv"],
        help="CSV 列名：venue, impact_factor, indexed_in, jcr_quartile, metric_year, source",
    )

    st.header("平台要求 / Requested Platforms")
    wants_google_scholar = st.checkbox("需要 Google Scholar 论文", value=False)
    if wants_google_scholar:
        st.caption(
            "Google Scholar 没有官方开放 API。本工具不会直接爬 Google Scholar；后续可通过 SerpAPI 或机构授权导出接入。"
        )

    language = st.selectbox("AI 总结语言 / AI summary language", ["Chinese", "English"], index=0)
    run_search = st.button("开始检索 / Search literature", type="primary", use_container_width=True)

st.info(
    "说明：本工具使用公开学术元数据 API。IF 和 Web of Science/JCR 筛选需要上传来自授权来源的期刊指标 CSV。"
)

if "papers" not in st.session_state:
    st.session_state.papers = []
if "query_text" not in st.session_state:
    st.session_state.query_text = ""
if "paper_chat_messages" not in st.session_state:
    st.session_state.paper_chat_messages = []
if "paper_chat_title" not in st.session_state:
    st.session_state.paper_chat_title = None



def _format_ai_score(value) -> str:
    try:
        if value is None or pd.isna(value):
            return "N/A"
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return "N/A"

def _metrics_csv_path(uploaded_file) -> str | None:
    if uploaded_file is None:
        if DEFAULT_METRICS_CSV.exists():
            return str(DEFAULT_METRICS_CSV)
        return None
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    tmp.write(uploaded_file.getvalue())
    tmp.close()
    return tmp.name


if run_search:
    if not keywords.strip():
        st.warning("请输入关键词 / Please enter keywords.")
    elif not sources:
        st.warning("请至少选择一个检索来源 / Please select at least one source.")
    else:
        metrics_csv = _metrics_csv_path(metrics_upload)
        if (min_impact_factor is not None or require_wos_or_jcr) and metrics_upload is None:
            st.info(
                "IF / Web of Science 筛选需要上传已填好的 JCR/WoS 指标 CSV。默认模板只有表头，不包含真实 IF 数据。"
            )

        query = SearchQuery(
            keywords=keywords.strip(),
            year_from=year_from,
            year_to=year_to,
            max_results=max_results,
            open_access_only=open_access_only,
            review_only=review_only,
            sources=sources,
        )
        with st.spinner("正在检索学术数据库 / Searching scholarly sources..."):
            papers, errors = search_literature(
                query,
                journal_metrics_csv=metrics_csv,
                min_impact_factor=min_impact_factor,
                require_wos_or_jcr=require_wos_or_jcr,
            )
        st.session_state.papers = papers
        st.session_state.query_text = keywords.strip()
        st.session_state.errors = errors
        save_search_history(
            keywords=keywords.strip(),
            year_from=year_from,
            year_to=year_to,
            max_results=max_results,
            sources=sources,
            open_access_only=open_access_only,
            review_only=review_only,
            min_impact_factor=min_impact_factor,
            require_wos_or_jcr=require_wos_or_jcr,
        )
papers = st.session_state.papers
errors = st.session_state.get("errors", {})

if errors:
    with st.expander("来源提示 / Source warnings", expanded=True):
        for source, message in errors.items():
            st.warning(f"{source}: {message}")


if papers:
    # Ensure AI relevance scores exist for old session results too.
    if any(paper.extra.get("ai_relevance_score") is None for paper in papers):
        fallback_query = SearchQuery(keywords=st.session_state.query_text or keywords)
        papers = add_ai_relevance_scores(papers, fallback_query)
        st.session_state.papers = papers
    df = to_dataframe(papers)
    df.insert(0, "no", range(1, len(df) + 1))
    if "relevance_score" not in df.columns:
        df["relevance_score"] = None
    df["relevance_score"] = pd.to_numeric(df["relevance_score"], errors="coerce").round(3).fillna("N/A")
    if "ai_relevance_score" not in df.columns:
        df["ai_relevance_score"] = "N/A"
    df["ai_relevance_score"] = df["ai_relevance_score"].apply(_format_ai_score)
    if "ai_relevance_reason" not in df.columns:
        df["ai_relevance_reason"] = "N/A"

    metric_cols = st.columns(5)
    metric_cols[0].metric("结果 / Results", len(df))
    metric_cols[1].metric("有 DOI / With DOI", int(df["doi"].notna().sum()))
    metric_cols[2].metric("有 PDF / With PDF", int(df["pdf_url"].notna().sum()))
    metric_cols[3].metric("有 IF / With IF", int(df["impact_factor"].notna().sum()) if "impact_factor" in df.columns else 0)
    metric_cols[4].metric("来源数 / Sources", len(set(" + ".join(df["source"].dropna()).split(" + "))))

    st.subheader("检索结果 / Results")
    display_columns = [
        "no",
        "title",
        "ai_relevance_score",
        "ai_relevance_reason",
        "relevance_score",
        "year",
        "venue",
        "impact_factor",
        "indexed_in",
        "jcr_quartile",
        "citation_count",
        "paper_type",
        "open_access",
        "source",
        "doi",
        "url",
        "pdf_url",
    ]
    display_df = df[[col for col in display_columns if col in df.columns]].rename(columns=COLUMN_LABELS)
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "链接 / URL": st.column_config.LinkColumn("链接 / URL", display_text="Open"),
            "PDF 链接 / PDF": st.column_config.LinkColumn("PDF 链接 / PDF", display_text="Open PDF"),
        },
    )

    st.subheader("论文详情 / Paper Details")
    paper_options = {f"{index}. {paper.title}": paper for index, paper in enumerate(papers, start=1)}
    selected_label = st.selectbox("选择论文 / Select a paper", list(paper_options.keys()))
    selected = paper_options[selected_label]
    st.markdown(f"**标题 / Title:** {selected.title}")
    st.markdown(f"**作者 / Authors:** {', '.join(selected.authors) if selected.authors else 'N/A'}")
    st.markdown(f"**年份 / 期刊来源:** {selected.year or 'N/A'} / {selected.venue or 'N/A'}")
    st.markdown(f"**影响因子 / IF:** {selected.extra.get('impact_factor') or 'N/A'}")
    st.markdown(f"**AI 相关性(0-10) / AI Relevance:** {_format_ai_score(selected.extra.get('ai_relevance_score'))}")
    st.markdown(f"**相关性原因 / Reason:** {selected.extra.get('ai_relevance_reason') or 'N/A'}")
    st.markdown(f"**收录 / Indexed In:** {selected.extra.get('indexed_in') or 'N/A'}")
    st.markdown(f"**JCR 分区 / Quartile:** {selected.extra.get('jcr_quartile') or 'N/A'}")
    st.markdown(f"**DOI:** {selected.doi or 'N/A'}")
    st.markdown(f"**链接 / URL:** [Open]({selected.url})" if selected.url else "**链接 / URL:** N/A")
    st.markdown(f"**PDF:** [Open PDF]({selected.pdf_url})" if selected.pdf_url else "**PDF:** N/A")
    st.write(selected.abstract or "暂无摘要 / No abstract available.")

    st.subheader("AI 总结 / AI Summary")
    summary_quick_goal = st.selectbox(
        "快速总结目标 / Quick summary goal",
        SUMMARY_QUICK_GOALS,
        index=0,
    )
    if st.button("使用快速总结目标 / Use quick summary goal"):
        st.session_state.summary_goal_input = summary_quick_goal
        st.rerun()
    summary_goal = st.text_input(
        "总结目标 / Summary goal",
        key="summary_goal_input",
    )
    if st.button("生成 AI 总结 / Generate AI summary"):
        if not ai_available():
            st.info(
                "AI 总结尚未配置。默认使用 Qwen Plus，请在本地 .env 设置 LIT_AGENT_API_KEY，或设置系统环境变量 DASHSCOPE_API_KEY。"
            )
        else:
            with st.spinner("正在生成总结 / Generating summary..."):
                st.markdown(summarize_papers(papers, summary_goal, language=language))

    st.subheader("当前论文问答 / Ask Current Paper")
    st.caption("基于当前选中论文的标题、期刊、DOI、摘要等信息回答；还没有下载全文。")

    if st.session_state.paper_chat_title != selected.title:
        st.session_state.paper_chat_title = selected.title
        st.session_state.paper_chat_messages = []

    example_question = st.selectbox(
        "快速问题 / Quick question",
        [
            "这篇论文主要研究什么？",
            "这篇论文和 PEM catalyst / HEO 有什么关系？",
            "这篇论文有哪些可提取的数据字段？",
            "这篇论文是否值得优先阅读？为什么？",
        ],
    )
    ask_example = st.button("询问快速问题 / Ask quick question")
    typed_question = st.chat_input("问当前论文 / Ask about the selected paper")
    question = typed_question or (example_question if ask_example else "")

    for message in st.session_state.paper_chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if question:
        if not st.session_state.paper_chat_messages or st.session_state.paper_chat_messages[-1].get("content") != question:
            st.session_state.paper_chat_messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant"):
                with st.spinner("正在回答 / Answering..."):
                    answer = answer_paper_question(selected, question, language=language)
                st.markdown(answer)
            st.session_state.paper_chat_messages.append({"role": "assistant", "content": answer})
    st.subheader("导出 / Export")
    export_cols = st.columns(3)
    export_cols[0].download_button(
        "下载 Excel / Download Excel",
        data=to_excel_bytes(papers),
        file_name="literature_search_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    export_cols[1].download_button(
        "下载 BibTeX / Download BibTeX",
        data=to_bibtex(papers),
        file_name="literature_search_results.bib",
        mime="text/plain",
        use_container_width=True,
    )
    export_cols[2].download_button(
        "下载 Markdown / Download Markdown",
        data=to_markdown_report(papers, st.session_state.query_text),
        file_name="literature_search_report.md",
        mime="text/markdown",
        use_container_width=True,
    )
else:
    st.info("请输入检索条件，然后点击开始检索 / Enter search conditions and click Search literature.")




























