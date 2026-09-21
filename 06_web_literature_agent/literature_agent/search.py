from __future__ import annotations

from collections.abc import Callable
from difflib import SequenceMatcher

from literature_agent.connectors.arxiv_source import search_arxiv
from literature_agent.connectors.crossref import search_crossref
from literature_agent.connectors.google_scholar_serpapi import search_google_scholar_serpapi
from literature_agent.connectors.openalex import search_openalex
from literature_agent.connectors.semantic_scholar import search_semantic_scholar
from literature_agent.journal_metrics import annotate_with_metrics, filter_by_metrics, load_journal_metrics
from literature_agent.models import PaperResult, SearchQuery


CONNECTORS: dict[str, Callable[[SearchQuery], list[PaperResult]]] = {
    "OpenAlex": search_openalex,
    "Semantic Scholar": search_semantic_scholar,
    "Crossref": search_crossref,
    "arXiv": search_arxiv,
    "Google Scholar (SerpAPI)": search_google_scholar_serpapi,
}


def _title_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def deduplicate(results: list[PaperResult]) -> list[PaperResult]:
    merged: list[PaperResult] = []
    doi_index: dict[str, PaperResult] = {}

    for paper in results:
        doi = paper.normalized_doi
        if doi and doi in doi_index:
            _merge_into(doi_index[doi], paper)
            continue

        title_match = next(
            (
                existing
                for existing in merged
                if _title_similarity(existing.normalized_title, paper.normalized_title) >= 0.94
            ),
            None,
        )
        if title_match:
            _merge_into(title_match, paper)
            if doi:
                doi_index[doi] = title_match
            continue

        merged.append(paper)
        if doi:
            doi_index[doi] = paper

    return merged


def _merge_into(target: PaperResult, source: PaperResult) -> None:
    if source.source not in target.source.split(" + "):
        target.source = f"{target.source} + {source.source}" if target.source else source.source
    target.authors = target.authors or source.authors
    target.year = target.year or source.year
    target.doi = target.doi or source.doi
    target.abstract = target.abstract or source.abstract
    target.venue = target.venue or source.venue
    target.citation_count = max(
        [value for value in [target.citation_count, source.citation_count] if value is not None],
        default=None,
    )
    target.url = target.url or source.url
    target.pdf_url = target.pdf_url or source.pdf_url
    target.paper_type = target.paper_type or source.paper_type
    target.open_access = target.open_access if target.open_access is not None else source.open_access
    target.relevance_score = target.relevance_score or source.relevance_score
    target.extra.update(source.extra)



def _keyword_terms(text: str) -> list[str]:
    terms: list[str] = []
    for raw in text.replace(",", " ").replace(";", " ").split():
        term = "".join(ch.lower() for ch in raw if ch.isalnum() or ch in {"-", "+"})
        if len(term) >= 2 and term not in terms:
            terms.append(term)
    return terms


def add_ai_relevance_scores(results: list[PaperResult], query: SearchQuery) -> list[PaperResult]:
    terms = _keyword_terms(query.keywords)
    if not terms:
        for paper in results:
            paper.extra["ai_relevance_score"] = None
            paper.extra["ai_relevance_reason"] = "No keyword terms."
        return results

    max_citations = max((paper.citation_count or 0 for paper in results), default=0) or 1
    max_year = max((paper.year or 0 for paper in results), default=0) or 1

    for paper in results:
        title = (paper.title or "").lower()
        abstract = (paper.abstract or "").lower()
        venue = (paper.venue or "").lower()
        paper_type = (paper.paper_type or "").lower()
        source = (paper.source or "").lower()

        title_hits = sum(1 for term in terms if term in title)
        abstract_hits = sum(1 for term in terms if term in abstract)
        venue_hits = sum(1 for term in terms if term in venue or term in paper_type or term in source)

        title_score = title_hits / len(terms)
        abstract_score = abstract_hits / len(terms)
        venue_score = venue_hits / len(terms)
        citation_score = min((paper.citation_count or 0) / max_citations, 1.0)
        recency_score = (paper.year or 0) / max_year if paper.year else 0.0
        pdf_score = 1.0 if paper.pdf_url else 0.0
        doi_score = 1.0 if paper.doi else 0.0

        score = (
            title_score * 45
            + abstract_score * 25
            + venue_score * 8
            + citation_score * 8
            + recency_score * 6
            + pdf_score * 5
            + doi_score * 3
        )
        score = max(0.0, min(100.0, score)) / 10

        reasons = []
        if title_hits:
            reasons.append(f"{title_hits}/{len(terms)} keyword(s) in title")
        if abstract_hits:
            reasons.append(f"{abstract_hits}/{len(terms)} keyword(s) in abstract")
        if paper.pdf_url:
            reasons.append("PDF available")
        if paper.citation_count:
            reasons.append(f"{paper.citation_count} citation(s)")
        if paper.year:
            reasons.append(f"year {paper.year}")

        paper.extra["ai_relevance_score"] = round(score, 1)
        paper.extra["ai_relevance_reason"] = "; ".join(reasons) if reasons else "Weak keyword match"

    return results

def rank_results(results: list[PaperResult]) -> list[PaperResult]:
    def score(paper: PaperResult) -> tuple[int, int, int, int]:
        citations = paper.citation_count or 0
        year = paper.year or 0
        has_abstract = 1 if paper.abstract else 0
        has_pdf = 1 if paper.pdf_url else 0
        return (has_pdf, has_abstract, citations, year)

    return sorted(results, key=score, reverse=True)


def search_literature(
    query: SearchQuery,
    journal_metrics_csv: str | None = None,
    min_impact_factor: float | None = None,
    require_wos_or_jcr: bool = False,
) -> tuple[list[PaperResult], dict[str, str]]:
    all_results: list[PaperResult] = []
    errors: dict[str, str] = {}

    for source_name in query.sources:
        connector = CONNECTORS.get(source_name)
        if not connector:
            continue
        try:
            all_results.extend(connector(query))
        except Exception as exc:  # noqa: BLE001 - UI should show source-specific failures.
            errors[source_name] = str(exc)

    ranked = rank_results(deduplicate(all_results))
    ranked = add_ai_relevance_scores(ranked, query)
    try:
        metrics = load_journal_metrics(journal_metrics_csv)
        ranked = annotate_with_metrics(ranked, metrics)
        ranked = filter_by_metrics(ranked, min_impact_factor, require_wos_or_jcr)
    except Exception as exc:  # noqa: BLE001
        errors["Journal metrics"] = str(exc)

    return ranked[: query.max_results], errors






