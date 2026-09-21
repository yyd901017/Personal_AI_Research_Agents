from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "search_history.sqlite"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            keywords TEXT NOT NULL,
            year_from INTEGER,
            year_to INTEGER,
            max_results INTEGER,
            sources_json TEXT,
            open_access_only INTEGER,
            review_only INTEGER,
            min_impact_factor REAL,
            require_wos_or_jcr INTEGER
        )
        """
    )
    return conn


def save_search_history(
    *,
    keywords: str,
    year_from: int | None,
    year_to: int | None,
    max_results: int,
    sources: list[str],
    open_access_only: bool,
    review_only: bool,
    min_impact_factor: float | None,
    require_wos_or_jcr: bool,
) -> None:
    conn = _connect()
    with conn:
        conn.execute(
            """
            INSERT INTO search_history (
                created_at, keywords, year_from, year_to, max_results, sources_json,
                open_access_only, review_only, min_impact_factor, require_wos_or_jcr
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                keywords,
                year_from,
                year_to,
                max_results,
                json.dumps(sources, ensure_ascii=False),
                int(open_access_only),
                int(review_only),
                min_impact_factor,
                int(require_wos_or_jcr),
            ),
        )
    conn.close()


def load_recent_searches(limit: int = 10) -> list[dict[str, Any]]:
    conn = _connect()
    rows = conn.execute(
        """
        SELECT id, created_at, keywords, year_from, year_to, max_results, sources_json,
               open_access_only, review_only, min_impact_factor, require_wos_or_jcr
        FROM search_history
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()

    history: list[dict[str, Any]] = []
    for row in rows:
        history.append(
            {
                "id": row[0],
                "created_at": row[1],
                "keywords": row[2],
                "year_from": row[3],
                "year_to": row[4],
                "max_results": row[5],
                "sources": json.loads(row[6] or "[]"),
                "open_access_only": bool(row[7]),
                "review_only": bool(row[8]),
                "min_impact_factor": row[9],
                "require_wos_or_jcr": bool(row[10]),
            }
        )
    return history


