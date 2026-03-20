"""
All SQLite tables. Run init_db() on startup.
Using SQLite for hackathon — zero setup, file-based, persistent.
"""

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS claims (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_text      TEXT NOT NULL,
    claim_hash      TEXT UNIQUE,
    original_lang   TEXT DEFAULT 'en',
    translated_text TEXT,
    verdict         TEXT,            -- TRUE | FALSE | MISLEADING | UNCERTAIN
    risk_level      TEXT,            -- CRITICAL | HIGH | MEDIUM | LOW
    p_true          REAL,            -- 0.0 to 1.0 — Bayesian probability claim is TRUE
    confidence      REAL,            -- overall system confidence
    correction      TEXT,            -- REAL correction text from Agent 4 (Gemini)
    explanation     TEXT,
    sources         TEXT,            -- JSON array of {name, url, snippet}
    claim_type      TEXT,            -- health_myth | drug_interaction | disease_claim
    bias_flags      TEXT,            -- JSON array of bias/inequality flags from Agent 5
    page_url        TEXT,
    page_title      TEXT,
    from_cache      INTEGER DEFAULT 0,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS trends (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    topic       TEXT,
    risk_level  TEXT,
    count       INTEGER DEFAULT 1,
    region_lang TEXT,
    date        TEXT DEFAULT (date('now')),
    UNIQUE(topic, risk_level, date)
);

CREATE TABLE IF NOT EXISTS language_stats (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    lang_code   TEXT UNIQUE,
    lang_name   TEXT,
    claim_count INTEGER DEFAULT 0,
    critical_count INTEGER DEFAULT 0,
    last_seen   TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS agent_performance (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id        INTEGER REFERENCES claims(id),
    agent_name      TEXT,
    p_true_contrib  REAL,
    latency_ms      INTEGER,
    error           TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_claims_hash     ON claims(claim_hash);
CREATE INDEX IF NOT EXISTS idx_claims_lang     ON claims(original_lang);
CREATE INDEX IF NOT EXISTS idx_claims_risk     ON claims(risk_level);
CREATE INDEX IF NOT EXISTS idx_claims_created  ON claims(created_at);
CREATE INDEX IF NOT EXISTS idx_trends_date     ON trends(date);
"""
