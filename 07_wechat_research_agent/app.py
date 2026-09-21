from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from wechat_research_agent.core import build_search_links, clues_to_rows, parse_article


load_dotenv()

PROJECT_DIR = Path(__file__).resolve().parent
LOGO_PATH = PROJECT_DIR.parent / "04_images" / "image001.png"

st.set_page_config(
    page_title="WeChat Research Agent | 公众号科研线索助手",
    page_icon="CE",
    layout="wide",
)

if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), width=430)
st.title("微信公众号科研线索 Agent")
st.caption("WeChat Research Lead Assistant | 公众号科研线索助手")
st.markdown("**Author / 作者:** Steven Yuandong Yue  |  **Title:** AI Research Tool Builder")

def _to_excel_bytes(df: pd.DataFrame) -> bytes:
    from io import BytesIO

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="wechat_research_clues")
    return output.getvalue()

st.info(
    "这个 Agent 专门处理微信公众号文章：先生成公众号搜索入口，再从文章链接或正文中提取论文 DOI / 标题线索，并用 Crossref 做正式论文验证。"
)

st.subheader("1. 公众号搜索入口 / WeChat Search Launcher")
search_keywords = st.text_input("搜索关键词 / Search keywords", value="PEM catalyst HEO")
if search_keywords.strip():
    search_df = pd.DataFrame(build_search_links(search_keywords))
    st.dataframe(
        search_df,
        use_container_width=True,
        hide_index=True,
        column_config={"链接 / Link": st.column_config.LinkColumn("链接 / Link", display_text="Open Search")},
    )
else:
    st.warning("请输入关键词 / Please enter keywords.")

st.caption("找到公众号文章后，把文章链接或正文复制到下面。链接不一定能自动读取，正文粘贴更稳定。")

st.subheader("2. 公众号文章解析 / WeChat Article Parser")
article_url = st.text_input("公众号文章链接 / WeChat article URL", placeholder="https://mp.weixin.qq.com/s/...")
article_text = st.text_area("公众号文章正文 / Pasted article text", height=220, placeholder="如果链接读取失败，把公众号文章正文复制到这里。")

if st.button("提取论文线索 / Extract Paper Clues", type="primary"):
    if not article_url.strip() and not article_text.strip():
        st.warning("请粘贴公众号链接或文章正文 / Please paste a URL or article text.")
    else:
        with st.spinner("正在提取和验证 / Extracting and verifying..."):
            result = parse_article(article_url.strip() or None, article_text.strip() or None)

        if result.fetch_error:
            st.warning(f"链接自动读取失败，请使用正文粘贴方式。错误：{result.fetch_error}")
        elif article_url.strip():
            st.success("链接已读取 / URL fetched")

        rows = clues_to_rows(result.clues)
        if rows:
            result_df = pd.DataFrame(rows)
            st.dataframe(
                result_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "source_url": st.column_config.LinkColumn("source_url", display_text="Open Source"),
                    "url": st.column_config.LinkColumn("url", display_text="Open Paper"),
                },
            )

            st.download_button(
                "下载 Excel / Download Excel",
                data=_to_excel_bytes(result_df),
                file_name="wechat_research_clues.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.info("没有识别到 DOI 或明显论文标题。建议粘贴更多正文，或手动复制论文标题。")

st.subheader("3. 当前限制 / Limitations")
st.markdown(
    """
- 不直接批量爬微信公众号。
- 微信链接可能限制自动访问，正文粘贴更稳定。
- 公众号文章只是科研线索来源，不是正式论文数据库。
- Crossref 验证结果需要人工复核。
- Web of Science、Google Scholar、影响因子仍需要授权来源或手动导入。
"""
)






