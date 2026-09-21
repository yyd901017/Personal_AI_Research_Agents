from __future__ import annotations

import arxiv

from literature_agent.models import PaperResult, SearchQuery


def search_arxiv(query: SearchQuery) -> list[PaperResult]:
    search = arxiv.Search(
        query=query.keywords,
        max_results=min(max(query.max_results, 1), 100),
        sort_by=arxiv.SortCriterion.Relevance,
    )
    client = arxiv.Client(page_size=min(max(query.max_results, 1), 100), delay_seconds=3)

    results: list[PaperResult] = []
    for item in client.results(search):
        year = item.published.year if item.published else None
        if query.year_from and year and year < query.year_from:
            continue
        if query.year_to and year and year > query.year_to:
            continue
        if query.review_only and "review" not in (item.summary or "").lower() and "review" not in item.title.lower():
            continue

        results.append(
            PaperResult(
                title=item.title,
                authors=[a.name for a in item.authors],
                year=year,
                doi=item.doi,
                abstract=item.summary,
                venue="arXiv",
                citation_count=None,
                url=item.entry_id,
                pdf_url=item.pdf_url,
                source="arXiv",
                paper_type="preprint",
                open_access=True,
                extra={"arxiv_id": item.get_short_id(), "categories": item.categories},
            )
        )
    return results



