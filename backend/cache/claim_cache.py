"""
SQLite-based claim deduplication cache.
Key: SHA256 hash of normalized claim text.
TTL: 24 hours (configurable in config.py).

Why SQLite: zero dependencies, sufficient for hackathon scale,
persistent across backend restarts.
"""
import hashlib
import json
import sqlite3
import asyncio
from datetime import datetime, timedelta
from backend.config import CACHE_DB_PATH, CACHE_TTL_HOURS

_db: sqlite3.Connection = None

async def init_cache():
    global _db
    _db = sqlite3.connect(CACHE_DB_PATH, check_same_thread=False)
    _db.execute("""
        CREATE TABLE IF NOT EXISTS claim_verdicts (
            claim_hash  TEXT PRIMARY KEY,
            claim_text  TEXT,
            verdict     TEXT,
            created_at  TEXT
        )
    """)
    _db.execute("CREATE INDEX IF NOT EXISTS idx_created ON claim_verdicts(created_at)")
    _db.commit()

def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())

def _hash_claim(text: str) -> str:
    return hashlib.sha256(_normalize(text).encode()).hexdigest()

async def get_cached_verdict(claim_text: str) -> dict | None:
    if _db is None:
        return None
    h = _hash_claim(claim_text)
    cutoff = (datetime.utcnow() - timedelta(hours=CACHE_TTL_HOURS)).isoformat()
    row = _db.execute(
        "SELECT verdict FROM claim_verdicts WHERE claim_hash=? AND created_at>?",
        (h, cutoff)
    ).fetchone()
    if row:
        return json.loads(row[0])
    return None

async def cache_verdict(claim_text: str, verdict: dict):
    if _db is None:
        return
    h = _hash_claim(claim_text)
    _db.execute(
        "INSERT OR REPLACE INTO claim_verdicts VALUES (?, ?, ?, ?)",
        (h, claim_text[:500], json.dumps(verdict), datetime.utcnow().isoformat())
    )
    _db.commit()
