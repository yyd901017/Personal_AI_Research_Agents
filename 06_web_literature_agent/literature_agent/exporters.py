from __future__ import annotations

from io import BytesIO

import pandas as pd

from literature_agent.models import PaperResult


def to_dataframe(papers: list[PaperResult]) -> pd.DataFrame:
    return pd.DataFrame([paper.to_row() for paper in papers])


def to_excel_bytes(papers: list[PaperResult]) -> bytes:
    output = BytesIO()
    df = to_dataframe(papers)
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="literature_results")
        worksheet = writer.sheets["literature_results"]
        for column_cells in worksheet.columns:
            header = column_cells[0].value or ""
            width = min(max(len(str(header)) + 2, 12), 60)
            worksheet.column_dimensions[column_cells[0].column_letter].width = width
    return output.getvalue()


def _bibtex_key(paper: PaperResult, index: int) -> str:
    first_author = "paper"
    if paper.authors:
        first_author = "".join(ch for ch in paper.authors[0].split()[-1].lower() if ch.isalnum())
    year = paper.year or "nd"
    return f"{first_author}{year}_{index}"


def to_bibtex(papers: list[PaperResult]) -> str:
    entries: list[str] = []
    for index, paper in enumerate(papers, start=1):
        entry_type = "article" if paper.doi or paper.venue != "arXiv" else "misc"
        fields = {
            "title": paper.title,
            "author": " and ".join(paper.authors),
            "year": paper.year,
            "journal": paper.venue,
            "doi": paper.doi,
            "url": paper.url,
        }
        body = []
        for key, value in fields.items():
            if value:
                body.append(f"  {key} = {{{value}}}")
        entries.append(f"@{entry_type}{{{_bibtex_key(paper, index)},\n" + ",\n".join(body) + "\n}")
    return "\n\n".join(entries)


def to_markdown_report(papers: list[PaperResult], query_text: str) -> str:
    lines = [f"# Literature Search Report", "", f"Query: `{query_text}`", ""]
    for index, paper in enumerate(papers, start=1):
        lines.append(f"## {index}. {paper.title}")
        lines.append("")
        meta = [
            f"Year: {paper.year or 'N/A'}",
            f"Venue: {paper.venue or 'N/A'}",
            f"Citations: {paper.citation_count if paper.citation_count is not None else 'N/A'}",
            f"Source: {paper.source}",
        ]
        lines.append(" | ".join(meta))
        if paper.doi:
            lines.append(f"DOI: {paper.doi}")
        if paper.url:
            lines.append(f"URL: {paper.url}")
        if paper.abstract:
            lines.append("")
            lines.append(paper.abstract[:1200])
        lines.append("")
    return "\n".join(lines)



