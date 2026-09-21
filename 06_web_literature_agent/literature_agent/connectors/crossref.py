from __future__ import annotations

import os
from typing import Any

import requests

from literature_agent.models import PaperResult, SearchQuery


CROSSREF_URL = "https://api.crossref.org/works"


def _first_date_part(item: dict[str, Any]) -> int | None:
    for key in ("published-print", "published-online", "published", "created"):
        parts = ((item.get(key) or {}).get("date-parts") or [])
        if parts and parts[0]:
            return parts[0][0]
    return None


def search_crossref(query: SearchQuery) -> list[PaperResult]:
    filters = []
    if query.year_from:
        filters.append(f"from-pub-date:{query.year_from}-01-01")
    if query.year_to:
        filters.append(f"until-pub-date:{query.year_to}-12-31")
    if query.review_only:
        filters.append("type:journal-article")

    params: dict[str, Any] = {
        "query": query.keywords,
        "rows": min(max(query.max_results, 1), 100),
        "sort": "relevance",
        "order": "desc",
        "select": "title,author,published-print,published-online,published,created,DOI,container-title,is-referenced-by-count,URL,type,abstract,link",
    }
    if filters:
        params["filter"] = ",".join(filters)

    mailto = os.getenv("CROSSREF_MAILTO")
    if mailto:
        params["mailto"] = mailto

    headers = {"User-Agent": "PersonalLiteratureAgent/0.1"}
    if mailto:
        headers["User-Agent"] = f"PersonalLiteratureAgent/0.1 (mailto:{mailto})"

    response = requests.get(CROSSREF_URL, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    items = response.json().get("message", {}).get("items", [])

    results: list[PaperResult] = []
    for item in items:
        links = item.get("link") or []
        pdf_url = next((link.get("URL") for link in links if "pdf" in (link.get("content-type") or "")), None)
        if query.open_access_only and not pdf_url:
            continue

        authors = []
        for author in item.get("author") or []:
            name = " ".join(p for p in [author.get("given"), author.get("family")] if p).strip()
            if name:
                authors.append(name)

        results.append(
            PaperResult(
                title=(item.get("title") or [""])[0],
                authors=authors,
                year=_first_date_part(item),
                doi=item.get("DOI"),
                abstract=item.get("abstract"),
                venue=(item.get("container-title") or [None])[0],
                citation_count=item.get("is-referenced-by-count"),
                url=item.get("URL"),
                pdf_url=pdf_url,
                source="Crossref",
                paper_type=item.get("type"),
                open_access=bool(pdf_url),
            )
        )
    return results




