from __future__ import annotations

import os
import re
from typing import Any

import requests

from literature_agent.models import PaperResult, SearchQuery


SERPAPI_URL = "https://serpapi.com/search.json"


def _extract_year(text: str | None) -> int | None:
    if not text:
        return None
    matches = re.findall(r"\b(19\d{2}|20\d{2})\b", text)
    if not matches:
        return None
    return int(matches[-1])


def _authors(publication_info: dict[str, Any]) -> list[str]:
    authors = publication_info.get("authors") or []
    names = [item.get("name") for item in authors if item.get("name")]
    if names:
        return names
    summary = publication_info.get("summary") or ""
    if " - " in summary:
        return [part.strip() for part in summary.split(" - ")[0].split(",") if part.strip()]
    return []


def search_google_scholar_serpapi(query: SearchQuery) -> list[PaperResult]:
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Google Scholar 需要合规第三方 API key。请在本地 .env 设置 SERPAPI_API_KEY。"
        )

    params: dict[str, Any] = {
        "engine": "google_scholar",
        "q": query.keywords,
        "api_key": api_key,
        "num": min(max(query.max_results, 1), 20),
    }
    if query.year_from:
        params["as_ylo"] = query.year_from
    if query.year_to:
        params["as_yhi"] = query.year_to

    response = requests.get(SERPAPI_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    results: list[PaperResult] = []
    for item in data.get("organic_results", []):
        publication_info = item.get("publication_info") or {}
        resources = item.get("resources") or []
        inline_links = item.get("inline_links") or {}
        cited_by = inline_links.get("cited_by") or {}
        year = _extract_year(publication_info.get("summary") or item.get("snippet"))
        if query.year_from and year and year < query.year_from:
            continue
        if query.year_to and year and year > query.year_to:
            continue
        pdf_url = next((r.get("link") for r in resources if "pdf" in (r.get("title") or "").lower()), None)
        if query.open_access_only and not pdf_url:
            continue
        if query.review_only and "review" not in (item.get("title") or "").lower() and "review" not in (item.get("snippet") or "").lower():
            continue

        results.append(
            PaperResult(
                title=item.get("title") or "",
                authors=_authors(publication_info),
                year=year,
                abstract=item.get("snippet"),
                venue=publication_info.get("summary"),
                citation_count=cited_by.get("total"),
                url=item.get("link"),
                pdf_url=pdf_url,
                source="Google Scholar (SerpAPI)",
                open_access=bool(pdf_url),
                extra={"result_id": item.get("result_id"), "cited_by_link": cited_by.get("link")},
            )
        )
    return results



