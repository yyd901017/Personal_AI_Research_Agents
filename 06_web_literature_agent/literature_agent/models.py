from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SearchQuery:
    keywords: str
    year_from: int | None = None
    year_to: int | None = None
    max_results: int = 25
    open_access_only: bool = False
    review_only: bool = False
    sources: list[str] = field(default_factory=list)


@dataclass
class PaperResult:
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    doi: str | None = None
    abstract: str | None = None
    venue: str | None = None
    citation_count: int | None = None
    url: str | None = None
    pdf_url: str | None = None
    source: str = ""
    paper_type: str | None = None
    open_access: bool | None = None
    relevance_score: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def normalized_doi(self) -> str:
        return (self.doi or "").lower().replace("https://doi.org/", "").strip()

    @property
    def normalized_title(self) -> str:
        return " ".join((self.title or "").lower().split())

    def to_row(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "authors": "; ".join(self.authors),
            "year": self.year,
            "doi": self.doi,
            "venue": self.venue,
            "citation_count": self.citation_count,
            "paper_type": self.paper_type,
            "open_access": self.open_access,
            "url": self.url,
            "pdf_url": self.pdf_url,
            "source": self.source,
            "abstract": self.abstract,
            "relevance_score": self.relevance_score,
            "ai_relevance_score": self.extra.get("ai_relevance_score"),
            "ai_relevance_reason": self.extra.get("ai_relevance_reason"),
        }





