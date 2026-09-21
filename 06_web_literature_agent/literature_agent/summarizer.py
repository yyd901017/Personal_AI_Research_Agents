from __future__ import annotations

import os

from openai import AuthenticationError, OpenAI, OpenAIError

from literature_agent.models import PaperResult


DEFAULT_QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_QWEN_MODEL = "qwen-plus"


def _api_key() -> str | None:
    return os.getenv("LIT_AGENT_API_KEY") or os.getenv("DASHSCOPE_API_KEY")


def ai_available() -> bool:
    return bool(_api_key())


def summarize_papers(papers: list[PaperResult], user_goal: str, language: str = "Chinese") -> str:
    api_key = _api_key()
    if not api_key:
        return (
            "AI 总结尚未配置。请在本项目的 .env 文件中设置 DashScope / Qwen key。\n\n"
            "推荐配置：\n"
            "LIT_AGENT_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1\n"
            "LIT_AGENT_MODEL=qwen-plus\n"
            "LIT_AGENT_API_KEY=你的 DashScope key\n\n"
            "也可以使用系统环境变量 DASHSCOPE_API_KEY。"
        )

    base_url = os.getenv("LIT_AGENT_BASE_URL") or DEFAULT_QWEN_BASE_URL
    model = os.getenv("LIT_AGENT_MODEL") or DEFAULT_QWEN_MODEL
    client = OpenAI(api_key=api_key, base_url=base_url)

    compact = []
    for index, paper in enumerate(papers[:20], start=1):
        compact.append(
            {
                "rank": index,
                "title": paper.title,
                "year": paper.year,
                "venue": paper.venue,
                "citations": paper.citation_count,
                "doi": paper.doi,
                "abstract": (paper.abstract or "")[:1500],
            }
        )

    prompt = (
        f"You are a scientific literature analyst. Answer in {language}. "
        "Use only the supplied paper metadata. Do not invent claims. "
        "Return: key themes, top papers, why they matter, data fields worth extracting, and gaps.\n\n"
        f"User goal: {user_goal}\n\n"
        f"Papers: {compact}"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You help researchers screen scholarly literature with traceable evidence."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
    except AuthenticationError:
        return (
            "AI 总结失败：当前 Qwen / DashScope API key 无效或已过期。\n\n"
            "请检查本项目 .env 的 LIT_AGENT_API_KEY，或系统环境变量 DASHSCOPE_API_KEY。不要把真实 key 上传到 GitHub。"
        )
    except OpenAIError as exc:
        return f"AI 总结失败：{exc}"
    except Exception as exc:  # noqa: BLE001
        return f"AI 总结失败：{exc}"

    return response.choices[0].message.content or ""


def answer_paper_question(paper: PaperResult, question: str, language: str = "Chinese") -> str:
    api_key = _api_key()
    if not api_key:
        return (
            "AI 问答尚未配置。请在本项目的 .env 文件中设置 LIT_AGENT_API_KEY，"
            "或设置系统环境变量 DASHSCOPE_API_KEY。"
        )

    base_url = os.getenv("LIT_AGENT_BASE_URL") or DEFAULT_QWEN_BASE_URL
    model = os.getenv("LIT_AGENT_MODEL") or DEFAULT_QWEN_MODEL
    client = OpenAI(api_key=api_key, base_url=base_url)

    paper_context = {
        "title": paper.title,
        "authors": paper.authors,
        "year": paper.year,
        "venue": paper.venue,
        "doi": paper.doi,
        "citation_count": paper.citation_count,
        "paper_type": paper.paper_type,
        "open_access": paper.open_access,
        "url": paper.url,
        "pdf_url": paper.pdf_url,
        "abstract": paper.abstract,
        "impact_factor": paper.extra.get("impact_factor"),
        "indexed_in": paper.extra.get("indexed_in"),
        "jcr_quartile": paper.extra.get("jcr_quartile"),
    }

    prompt = (
        f"Answer in {language}. You are helping screen one scholarly paper. "
        "Use only the metadata and abstract supplied below. If the question requires full text, say that the current app has not downloaded/read the full paper yet. "
        "Be concise, practical, and traceable.\n\n"
        f"Paper metadata and abstract: {paper_context}\n\n"
        f"User question: {question}"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You answer questions about a selected scholarly paper using only supplied metadata and abstract."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
    except AuthenticationError:
        return "AI 问答失败：当前 Qwen / DashScope API key 无效或已过期。"
    except OpenAIError as exc:
        return f"AI 问答失败：{exc}"
    except Exception as exc:  # noqa: BLE001
        return f"AI 问答失败：{exc}"

    return response.choices[0].message.content or ""


