from __future__ import annotations

from pathlib import Path

import pandas as pd

from literature_agent.models import PaperResult


def normalize_venue(value: str | None) -> str:
    return " ".join((value or "").lower().replace("&", "and").split())


def load_journal_metrics(csv_path: str | Path | None) -> dict[str, dict]:
    if not csv_path:
        return {}
    path = Path(csv_path)
    if not path.exists():
        return {}

    df = pd.read_csv(path)
    required = {"venue", "impact_factor"}
    if not required.issubset(set(df.columns)):
        raise ValueError("Journal metrics CSV must include at least: venue, impact_factor")

    metrics: dict[str, dict] = {}
    for _, row in df.iterrows():
        venue = normalize_venue(str(row.get("venue", "")))
        if not venue:
            continue
        metrics[venue] = {
            "impact_factor": _to_float(row.get("impact_factor")),
            "indexed_in": row.get("indexed_in"),
            "jcr_quartile": row.get("jcr_quartile"),
            "metric_year": row.get("metric_year"),
            "source": row.get("source"),
        }
    return metrics


def annotate_with_metrics(papers: list[PaperResult], metrics: dict[str, dict]) -> list[PaperResult]:
    if not metrics:
        return papers
    for paper in papers:
        metric = metrics.get(normalize_venue(paper.venue))
        if metric:
            paper.extra["impact_factor"] = metric.get("impact_factor")
            paper.extra["indexed_in"] = metric.get("indexed_in")
            paper.extra["jcr_quartile"] = metric.get("jcr_quartile")
            paper.extra["metric_year"] = metric.get("metric_year")
            paper.extra["journal_metric_source"] = metric.get("source")
    return papers


def filter_by_metrics(
    papers: list[PaperResult],
    min_impact_factor: float | None = None,
    require_wos_or_jcr: bool = False,
) -> list[PaperResult]:
    filtered: list[PaperResult] = []
    for paper in papers:
        impact_factor = paper.extra.get("impact_factor")
        indexed_in = str(paper.extra.get("indexed_in") or "").lower()
        metric_source = str(paper.extra.get("journal_metric_source") or "").lower()

        if min_impact_factor is not None:
            if impact_factor is None or impact_factor < min_impact_factor:
                continue

        if require_wos_or_jcr:
            if "web of science" not in indexed_in and "wos" not in indexed_in and "jcr" not in metric_source:
                continue

        filtered.append(paper)
    return filtered


def _to_float(value) -> float | None:
    try:
        if pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


