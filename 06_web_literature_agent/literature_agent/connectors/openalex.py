from __future__ import annotations

import os
from typing import Any

import requests

from literature_agent.models import PaperResult, SearchQuery


OPENALEX_URL = "https://api.openalex.org/works"


def _abstract_from_inverted_index(index: dict[str, list[int]] | None) -> str | None:
    if not index:
        return None
    positions: list[tuple[int, str]] = []
    for word, word_positions in index.items():
        for position in word_positions:
            positions.append((position, word))
    return " ".join(word for _, word in sorted(positions))


def _authors(authorships: list[dict[str, Any]]) -> list[str]:
    names: list[str] = []
    for item in authorships or []:
        author = item.get("author") or {}
        name = author.get("display_name")
        if name:
            names.append(name)
    return names


def search_openalex(query: SearchQuery) -> list[PaperResult]:
    filters = []
    if query.year_from:
        filters.append(f"from_publication_date:{query.year_from}-01-01")
    if query.year_to:
        filters.append(f"to_publication_date:{query.year_to}-12-31")
    if query.open_access_only:
        filters.append("is_oa:true")
    if query.review_only:
        filters.append("type:review")

    params: dict[str, Any] = {
        "search": query.keywords,
        "per-page": min(max(query.max_results, 1), 200),
        "sort": "relevance_score:desc",
        "select": (
            "id,doi,title,display_name,publication_year,authorships,"
            "primary_location,locations,open_access,cited_by_count,type,"
            "abstract_inverted_index,relevance_score"
        ),
    }

    if filters:
        params["filter"] = ",".join(filters)

    api_key = os.getenv("OPENALEX_API_KEY")
    if api_key:
        params["api_key"] = api_key

    mailto = os.getenv("OPENALEX_MAILTO")
    if mailto:
        params["mailto"] = mailto

    headers = {"User-Agent": "PersonalLiteratureAgent/0.1"}
    if mailto:
        headers["User-Agent"] = f"PersonalLiteratureAgent/0.1 (mailto:{mailto})"

    response = requests.get(OPENALEX_URL, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    results: list[PaperResult] = []
    for item in data.get("results", []):
        primary = item.get("primary_location") or {}
        source = primary.get("source") or {}
        open_access = item.get("open_access") or {}
        best_oa = open_access.get("oa_url")
        landing_url = primary.get("landing_page_url") or item.get("doi") or item.get("id")
        pdf_url = primary.get("pdf_url") or best_oa

        results.append(
            PaperResult(
                title=item.get("title") or item.get("display_name") or "",
                authors=_authors(item.get("authorships") or []),
                year=item.get("publication_year"),
                doi=item.get("doi"),
                abstract=_abstract_from_inverted_index(item.get("abstract_inverted_index")),
                venue=source.get("display_name"),
                citation_count=item.get("cited_by_count"),
                url=landing_url,
                pdf_url=pdf_url,
                source="OpenAlex",
                paper_type=item.get("type"),
                open_access=open_access.get("is_oa"),
                relevance_score=item.get("relevance_score"),
                extra={"openalex_id": item.get("id")},
            )
        )
    return results




