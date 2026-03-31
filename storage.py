from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'data' / 'analysis_history.db'


CREATE_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sender TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    risk_score INTEGER NOT NULL,
    risk_level TEXT NOT NULL,
    ml_probability REAL NOT NULL,
    report_json TEXT NOT NULL
);
'''



def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn



def init_db() -> None:
    with get_connection() as conn:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()



def save_analysis(report: dict[str, Any]) -> int:
    init_db()
    with get_connection() as conn:
        cursor = conn.execute(
            '''
            INSERT INTO analyses (sender, subject, body, risk_score, risk_level, ml_probability, report_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                report['sender'],
                report['subject'],
                report['body'],
                report['risk_score'],
                report['risk_level'],
                report['ml_probability'],
                report['report_json'],
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)



def fetch_history(limit: int = 50) -> list[sqlite3.Row]:
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            'SELECT id, created_at, sender, subject, risk_score, risk_level FROM analyses ORDER BY id DESC LIMIT ?',
            (limit,),
        ).fetchall()
    return rows



def fetch_analysis(analysis_id: int) -> sqlite3.Row | None:
    init_db()
    with get_connection() as conn:
        row = conn.execute('SELECT * FROM analyses WHERE id = ?', (analysis_id,)).fetchone()
    return row
