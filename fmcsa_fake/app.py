
import os
import csv
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DATA_PATH = os.environ.get("FMCSA_CACHE_PATH", "data/fmcsa_cache.csv")
API_KEY = os.environ.get("API_KEY", "dev-secret")  # change in prod

app = FastAPI(title="FMCSA Fake", version="0.1.0", description="Demo-ready fake FMCSA eligibility checks")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CheckRequest(BaseModel):
    mc: str

def load_cache(path: str) -> Dict[str, Dict[str, Any]]:
    cache: Dict[str, Dict[str, Any]] = {}
    with open(path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # normalize booleans and keys
            row["mc"] = str(row["mc"]).strip()
            row["dot"] = str(row.get("dot", "")).strip()
            row["carrier_name"] = row.get("carrier_name", "").strip()
            row["status"] = row.get("status", "").strip().lower()
            row["insurance_ok"] = str(row.get("insurance_ok", "")).strip().lower() in ("true","1","yes","y")
            row["authority_ok"] = str(row.get("authority_ok", "")).strip().lower() in ("true","1","yes","y")
            row["reason"] = row.get("reason", "").strip()
            cache[row["mc"]] = row
    return cache

CACHE = load_cache(DATA_PATH)

def require_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")):
    if not API_KEY:
        # If API_KEY is empty, treat as disabled (not recommended)
        return
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

@app.get("/health")
def health():
    return {"status": "ok", "records": len(CACHE)}

def evaluate_eligibility(record: Dict[str, Any]) -> Dict[str, Any]:
    eligible = (record.get("status") == "active") and record.get("insurance_ok") and record.get("authority_ok")
    reason = record.get("reason") or ("Eligible" if eligible else "Not eligible")
    return {
        "eligible": eligible,
        "reason": reason,
        "mc": record.get("mc"),
        "dot": record.get("dot"),
        "carrier_name": record.get("carrier_name"),
        "status": record.get("status"),
        "insurance_ok": record.get("insurance_ok"),
        "authority_ok": record.get("authority_ok"),
    }

@app.get("/carriers/{mc}", dependencies=[Depends(require_api_key)])
def get_carrier(mc: str):
    mc_norm = str(mc).strip()
    rec = CACHE.get(mc_norm)
    if not rec:
        raise HTTPException(status_code=404, detail="MC not found in cache")
    return evaluate_eligibility(rec)
