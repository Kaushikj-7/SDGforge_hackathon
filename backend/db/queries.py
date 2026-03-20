import hashlib
from datetime import datetime, timedelta
import sqlite3
import json
from backend.config import DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_hash TEXT UNIQUE,
            claim_text TEXT,
            original_lang TEXT,
            translated_text TEXT,
            verdict TEXT,
            risk_level TEXT,
            p_true REAL,
            confidence REAL,
            correction TEXT,
            explanation TEXT,
            sources TEXT,
            claim_type TEXT,
            bias_flags TEXT,
            page_url TEXT,
            page_title TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_claim(text: str) -> str:
    return hashlib.sha256(text.lower().strip().encode()).hexdigest()

def get_cached(claim_text: str, ttl_hours: int = 24) -> dict | None:
    # FORCE BYPASS CACHE ALWAYS
    return None

def save_claim(result: dict):
    conn = get_db()
    h = hash_claim(result.get("claim_text", ""))
    
    # Store sources as JSON string
    sources_str = json.dumps(result.get("sources", []))
    bias_flags_str = json.dumps(result.get("bias_flags", []))
    
    try:
        conn.execute('''
            INSERT INTO claims (
                claim_hash, claim_text, original_lang, translated_text,
                verdict, risk_level, p_true, confidence, correction,
                explanation, sources, claim_type, bias_flags,
                page_url, page_title, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            h,
            result.get("claim_text"),
            result.get("original_lang", "en"),
            result.get("translated_text", ""),
            result.get("verdict"),
            result.get("risk_level"),
            result.get("p_true"),
            result.get("confidence"),
            result.get("correction"),
            result.get("explanation"),
            sources_str,
            result.get("claim_type"),
            bias_flags_str,
            result.get("page_url"),
            result.get("page_title"),
            datetime.utcnow().isoformat()
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Already exists
    finally:
        conn.close()

def get_dashboard_stats() -> dict:
    conn = get_db()
    
    # Defaults
    stats = {
        "total_verified": 0,
        "critical_myths": 0,
        "high_risk": 0,
        "medium_risk": 0,
        "low_risk": 0,
        "recent_claims": []
    }
    
    try:
        row = conn.execute("SELECT COUNT(*) as c FROM claims").fetchone()
        stats["total_verified"] = row["c"]
        
        row_c = conn.execute("SELECT COUNT(*) as c FROM claims WHERE risk_level='CRITICAL'").fetchone()
        stats["critical_myths"] = row_c["c"]
        
        row_h = conn.execute("SELECT COUNT(*) as c FROM claims WHERE risk_level='HIGH'").fetchone()
        stats["high_risk"] = row_h["c"]

        row_h = conn.execute("SELECT COUNT(*) as c FROM claims WHERE risk_level='MEDIUM'").fetchone()
        stats["medium_risk"] = row_h["c"]

        row_h = conn.execute("SELECT COUNT(*) as c FROM claims WHERE risk_level='LOW'").fetchone()
        stats["low_risk"] = row_h["c"]

        recent = conn.execute("SELECT * FROM claims ORDER BY created_at DESC LIMIT 10").fetchall()
        for r in recent:
            item = dict(r)
            item["sources"] = json.loads(item["sources"]) if item["sources"] else []
            item["bias_flags"] = json.loads(item["bias_flags"]) if item["bias_flags"] else []
            stats["recent_claims"].append(item)
            
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        conn.close()
        
    return stats
