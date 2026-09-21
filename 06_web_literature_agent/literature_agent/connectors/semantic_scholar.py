from __future__ import annotations

import os
from typing import Any

import requests

from literature_agent.models import PaperResult, SearchQuery


SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


def _year_filter(query: SearchQuery) -> str | None:
    if query.year_from and query.year_to:
        return f"{query.year_from}-{query.year_to}"
    if query.year_from:
        return f"{query.year_from}-"
    if query.year_to:
        return f"-{query.year_to}"
    return None


def search_semantic_scholar(query: SearchQuery) -> list[PaperResult]:
    params: dict[str, Any] = {
        "query": query.keywords,
        "limit": min(max(query.max_results, 1), 100),
        "fields": (
            "title,authors,year,abstract,venue,citationCount,url,"
            "openAccessPdf,externalIds,publicationTypes"
        ),
    }
    year_filter = _year_filter(query)
    if year_filter:
        params["year"] = year_filter

    headers = {"User-Agent": "PersonalLiteratureAgent/0.1"}
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    response = requests.get(SEMANTIC_SCHOLAR_URL, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    results: list[PaperResult] = []
    for item in data.get("data", []):
        external_ids = item.get("externalIds") or {}
        oa_pdf = item.get("openAccessPdf") or {}
        publication_types = item.get("publicationTypes") or []
        if query.review_only and not any("review" in p.lower() for p in publication_types):
            continue
        if query.open_access_only and not oa_pdf.get("url"):
            continue

        results.append(
            PaperResult(
                title=item.get("title") or "",
                authors=[a.get("name") for a in item.get("authors", []) if a.get("name")],
                year=item.get("year"),
                doi=external_ids.get("DOI"),
                abstract=item.get("abstract"),
                venue=item.get("venue"),
                citation_count=item.get("citationCount"),
                url=item.get("url"),
                pdf_url=oa_pdf.get("url"),
                source="Semantic Scholar",
                paper_type="; ".join(publication_types) if publication_types else None,
                open_access=bool(oa_pdf.get("url")),
                extra={"paper_id": item.get("paperId"), "external_ids": external_ids},
            )
        )
    return results




