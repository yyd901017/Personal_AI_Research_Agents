from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote_plus

import requests


@dataclass
class PaperClue:
    clue_type: str
    value: str
    source_url: str | None = None
    year: int | None = None
    doi: str | None = None
    venue: str | None = None
    url: str | None = None
    verified: bool = False


@dataclass
class ParseResult:
    url: str | None = None
    fetched: bool = False
    fetch_error: str | None = None
    clues: list[PaperClue] = field(default_factory=list)


DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
TITLE_PATTERNS = [
    re.compile(r"(?:论文题目|题目|标题|Title|Paper)[:：]\s*([^\n\r]{12,220})", re.IGNORECASE),
    re.compile(r"[《\"]([^《》\"\n\r]{12,220})[》\"]"),
]


def build_search_links(keywords: str) -> list[dict[str, str]]:
    encoded = quote_plus(keywords.strip())
    return [
        {
            "入口 / Entry": "搜狗微信文章搜索 / Sogou WeChat Articles",
            "说明 / Notes": "常用公众号文章搜索入口，可能出现验证码或访问限制。",
            "链接 / Link": f"https://weixin.sogou.com/weixin?type=2&query={encoded}",
        },
        {
            "入口 / Entry": "Bing 限定微信公众号 / Bing site:mp.weixin.qq.com",
            "说明 / Notes": "用 Bing 搜索已被索引的公众号文章。",
            "链接 / Link": f"https://www.bing.com/search?q=site%3Amp.weixin.qq.com%2Fs+{encoded}",
        },
        {
            "入口 / Entry": "Google 限定微信公众号 / Google site:mp.weixin.qq.com",
            "说明 / Notes": "需要能访问 Google；适合补充搜索。",
            "链接 / Link": f"https://www.google.com/search?q=site%3Amp.weixin.qq.com%2Fs+{encoded}",
        },
    ]


def fetch_wechat_text(url: str) -> tuple[str, str | None]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        return "", str(exc)
    text = response.text
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip(), None


def extract_dois(text: str) -> list[str]:
    seen: list[str] = []
    for match in DOI_RE.findall(text or ""):
        doi = match.rstrip(".,;，。；)）]").strip()
        if doi and doi.lower() not in [item.lower() for item in seen]:
            seen.append(doi)
    return seen


def extract_title_candidates(text: str) -> list[str]:
    candidates: list[str] = []
    for pattern in TITLE_PATTERNS:
        for match in pattern.findall(text or ""):
            title = re.sub(r"\s+", " ", match).strip(" ：:，,。.")
            if 12 <= len(title) <= 220 and title not in candidates:
                candidates.append(title)
    return candidates[:10]


def verify_crossref(query_text: str, max_results: int = 2) -> list[PaperClue]:
    params = {
        "query": query_text,
        "rows": max_results,
        "select": "title,DOI,container-title,published,published-online,published-print,URL",
    }
    headers = {"User-Agent": "PersonalWeChatResearchAgent/0.1"}
    try:
        response = requests.get("https://api.crossref.org/works", params=params, headers=headers, timeout=20)
        response.raise_for_status()
    except Exception:
        return []

    clues: list[PaperClue] = []
    for item in response.json().get("message", {}).get("items", []):
        title = (item.get("title") or [""])[0]
        venue = (item.get("container-title") or [None])[0]
        year = _year_from_crossref(item)
        doi = item.get("DOI")
        url = item.get("URL") or (f"https://doi.org/{doi}" if doi else None)
        if title:
            clues.append(
                PaperClue(
                    clue_type="Crossref verified paper",
                    value=title,
                    year=year,
                    doi=doi,
                    venue=venue,
                    url=url,
                    verified=True,
                )
            )
    return clues


def parse_article(url: str | None = None, pasted_text: str | None = None) -> ParseResult:
    result = ParseResult(url=url)
    parts: list[str] = []
    if pasted_text:
        parts.append(pasted_text)
    if url:
        fetched_text, error = fetch_wechat_text(url)
        result.fetch_error = error
        result.fetched = bool(fetched_text and not error)
        if fetched_text:
            parts.append(fetched_text)

    combined = "\n".join(parts)
    doi_candidates = extract_dois(combined)
    title_candidates = extract_title_candidates(combined)

    for doi in doi_candidates:
        result.clues.append(PaperClue("DOI candidate", doi, source_url=url, doi=doi, url=f"https://doi.org/{doi}"))
    for title in title_candidates:
        result.clues.append(PaperClue("Title candidate", title, source_url=url))

    seen = set()
    for query in [*doi_candidates[:5], *title_candidates[:5]]:
        for clue in verify_crossref(query):
            key = (clue.doi or clue.value).lower()
            if key not in seen:
                clue.source_url = url
                result.clues.append(clue)
                seen.add(key)
    return result


def clues_to_rows(clues: list[PaperClue]) -> list[dict[str, Any]]:
    return [
        {
            "type": clue.clue_type,
            "value": clue.value,
            "verified": clue.verified,
            "year": clue.year,
            "doi": clue.doi,
            "venue": clue.venue,
            "source_url": clue.source_url,
            "url": clue.url,
        }
        for clue in clues
    ]


def _year_from_crossref(item: dict[str, Any]) -> int | None:
    for key in ("published", "published-online", "published-print"):
        parts = ((item.get(key) or {}).get("date-parts") or [])
        if parts and parts[0]:
            return parts[0][0]
    return None


