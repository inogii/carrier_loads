import os
import psycopg2
from fastapi import FastAPI, HTTPException, Header, Depends, Query
from pydantic import BaseModel, Field, condecimal
from typing import Optional
from datetime import datetime

# ---------- Configuration ----------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/dbname")
API_KEY = os.getenv("API_KEY", "change-me")

app = FastAPI(title="Metrics API (psycopg2)", version="0.3.0")


# ---------- Helpers ----------
def require_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """Dependency that enforces a valid API key for all protected endpoints."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


def get_conn():
    """Open a PostgreSQL connection using psycopg2."""
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB connection failed: {e}")


# ---------- Models ----------
class CallEvent(BaseModel):
    """Schema representing a single call record."""
    mc_number: str
    original_price: condecimal(max_digits=12, decimal_places=2) = Field(ge=0)
    agreed_price: Optional[condecimal(max_digits=12, decimal_places=2)] = Field(default=None, ge=0)
    had_discount: bool = False
    discount_rate: condecimal(max_digits=5, decimal_places=2) = Field(default=0, ge=0, le=100)
    sentiment: str = Field(pattern="^(happy|neutral|upset|n/a)$")
    outcome: str = Field(pattern="^(successful|unsuccessful|n/a)$")
    duration: int = Field(ge=0)
    timestamp: datetime


# ---------- Endpoints ----------
@app.get("/health")
def health():
    """Check service health and connectivity."""
    return {"status": "ok"}


@app.post("/calls", dependencies=[Depends(require_api_key)])
def insert_call(event: CallEvent):
    """Insert a new call record into the database."""
    q = """
        INSERT INTO calls (
            mc_number, original_price, agreed_price, had_discount, discount_rate,
            sentiment, outcome, duration, timestamp
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING call_id;
    """
    vals = (
        event.mc_number, event.original_price, event.agreed_price, event.had_discount,
        event.discount_rate, event.sentiment, event.outcome, event.duration, event.timestamp
    )
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(q, vals)
        call_id = cur.fetchone()[0]
        conn.commit()
    return {"ok": True, "call_id": call_id}


@app.get("/metrics/total_duration", dependencies=[Depends(require_api_key)])
def total_duration():
    """Return the total call duration (in seconds) across all records."""
    q = "SELECT COALESCE(SUM(duration),0) FROM calls;"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(q)
        total = cur.fetchone()[0]
    return {"total_duration_seconds": total}


@app.get("/metrics/duration_evolution", dependencies=[Depends(require_api_key)])
def duration_evolution(days: int = Query(7, ge=1, le=90)):
    """Show the evolution of total call duration over the past X days."""
    q = """
        SELECT DATE_TRUNC('day', timestamp)::date AS day, SUM(duration) AS total_duration_s
        FROM calls
        WHERE timestamp >= NOW() - INTERVAL '%s days'
        GROUP BY 1 ORDER BY 1;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(q, (days,))
        rows = cur.fetchall()
    return [{"day": r[0].isoformat(), "total_duration_s": r[1]} for r in rows]


@app.get("/metrics/total_sales_volume", dependencies=[Depends(require_api_key)])
def total_sales_volume():
    """Return the total sales volume (sum of agreed prices from successful calls)."""
    q = "SELECT COALESCE(SUM(agreed_price),0) FROM calls WHERE outcome='successful';"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(q)
        total = cur.fetchone()[0]
    return {"total_sales_volume": float(total)}


@app.get("/metrics/sales_evolution", dependencies=[Depends(require_api_key)])
def sales_evolution(days: int = Query(7, ge=1, le=90)):
    """Display aggregated daily sales volumes for the past X days."""
    q = """
        SELECT DATE_TRUNC('day', timestamp)::date AS day, COALESCE(SUM(agreed_price),0) AS daily_sales
        FROM calls
        WHERE outcome='successful' AND timestamp >= NOW() - INTERVAL '%s days'
        GROUP BY 1 ORDER BY 1;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(q, (days,))
        rows = cur.fetchall()
    return [{"day": r[0].isoformat(), "sales_volume": float(r[1])} for r in rows]


@app.get("/metrics/discount_evolution", dependencies=[Depends(require_api_key)])
def discount_evolution(days: int = Query(7, ge=1, le=90)):
    """Track the evolution of average discount rate per day for the past X days."""
    q = """
        SELECT DATE_TRUNC('day', timestamp)::date AS day, ROUND(AVG(discount_rate), 2)
        FROM calls
        WHERE timestamp >= NOW() - INTERVAL '%s days'
        GROUP BY 1 ORDER BY 1;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(q, (days,))
        rows = cur.fetchall()
    return [{"day": r[0].isoformat(), "avg_discount_rate": float(r[1]) if r[1] else 0} for r in rows]


@app.get("/metrics/satisfaction", dependencies=[Depends(require_api_key)])
def satisfaction():
    """Return the percentage distribution of call sentiment categories."""
    q = """
        SELECT sentiment, ROUND(100.0 * COUNT(*) / NULLIF((SELECT COUNT(*) FROM calls),0), 2)
        FROM calls GROUP BY sentiment ORDER BY 1;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(q)
        rows = cur.fetchall()
    return [{"sentiment": r[0], "percentage": float(r[1])} for r in rows]


@app.get("/metrics/success", dependencies=[Depends(require_api_key)])
def success():
    """Return the percentage distribution of call outcomes (success vs failure)."""
    q = """
        SELECT outcome, ROUND(100.0 * COUNT(*) / NULLIF((SELECT COUNT(*) FROM calls),0), 2)
        FROM calls GROUP BY outcome ORDER BY 1;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(q)
        rows = cur.fetchall()
    return [{"outcome": r[0], "percentage": float(r[1])} for r in rows]
