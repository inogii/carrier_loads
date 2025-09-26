
import os
import csv
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query, Header, Depends
from fastapi.middleware.cors import CORSMiddleware

DATA_PATH = os.environ.get("LOADS_PATH", "data/loads.csv")
API_KEY = os.environ.get("API_KEY", "dev-secret")

app = FastAPI(title="Carrier Loads API", version="0.3.1", description="Searchable loads API with optional filters and sane defaults")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _norm_id(x: str) -> str:
    return (x or "").strip().upper()

def load_data(path: str) -> Dict[str, Dict[str, Any]]:
    cache: Dict[str, Dict[str, Any]] = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Trim whitespace
            for k, v in list(row.items()):
                if isinstance(v, str):
                    row[k] = v.strip()
            # numeric coercion
            try:
                row["loadboard_rate"] = float(row["loadboard_rate"]) if row.get("loadboard_rate") else None
            except Exception:
                row["loadboard_rate"] = None
            try:
                row["weight"] = float(row["weight"]) if row.get("weight") else None
            except Exception:
                row["weight"] = None
            try:
                row["num_of_pieces"] = int(row["num_of_pieces"]) if row.get("num_of_pieces") else None
            except Exception:
                row["num_of_pieces"] = None
            try:
                row["miles"] = int(row["miles"]) if row.get("miles") else None
            except Exception:
                row["miles"] = None
            # normalize id key to uppercase
            row_id = _norm_id(row["load_id"])
            row["load_id"] = row_id
            cache[row_id] = row
    return cache

CACHE = load_data(DATA_PATH)

def require_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key" )):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

@app.get("/health")
def health():
    return {"status": "ok", "records": len(CACHE), "source": DATA_PATH}

# List all loads (with pagination & sorting), no filters
@app.get("/loads", dependencies=[Depends(require_api_key)])
def list_loads(
    sort_by: Optional[str] = Query("pickup_datetime", description="pickup_datetime|delivery_datetime|miles|loadboard_rate"),
    order: Optional[str] = Query("asc", description="asc|desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
):
    results: List[Dict[str, Any]] = list(CACHE.values())
    valid_sort = {"pickup_datetime", "delivery_datetime", "miles", "loadboard_rate"}
    key = sort_by if sort_by in valid_sort else "pickup_datetime"
    reverse = (order.lower() == "desc")
    results.sort(key=lambda r: (r.get(key) is None, r.get(key)), reverse=reverse)
    start = (page - 1) * page_size
    end = start + page_size
    return {"count": len(results), "page": page, "page_size": page_size, "results": results[start:end]}

# SEARCH BEFORE DYNAMIC ROUTE to avoid shadowing by /loads/{load_id}
@app.get("/loads/search", dependencies=[Depends(require_api_key)])
@app.get("/loads/search/", dependencies=[Depends(require_api_key)])
def search_loads(
    origin: Optional[str] = Query(None, description="Text match within origin"),
    destination: Optional[str] = Query(None, description="Text match within destination"),
    equipment_type: Optional[str] = Query(None, description="Exact match on equipment_type"),
    max_weight: Optional[float] = Query(None, description="Filter out loads with weight > max_weight"),
    sort_by: Optional[str] = Query("pickup_datetime", description="Field to sort by: pickup_datetime|delivery_datetime|miles|loadboard_rate"),
    order: Optional[str] = Query("asc", description="Sort order: asc|desc"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
):
    """
    Returns loads filtered by the optional parameters. If no filters are provided,
    returns all loads (paginated). Supports sorting and pagination.
    """
    results: List[Dict[str, Any]] = []
    for load in CACHE.values():
        if origin and origin.lower() not in load.get("origin", "").lower():
            continue
        if destination and destination.lower() not in load.get("destination", "").lower():
            continue
        if equipment_type and equipment_type.lower() != load.get("equipment_type", "").lower():
            continue
        if max_weight is not None and load.get("weight") is not None and load["weight"] > max_weight:
            continue
        results.append(load)
    
    valid_sort = {"pickup_datetime", "delivery_datetime", "miles", "loadboard_rate"}
    key = sort_by if sort_by in valid_sort else "pickup_datetime"
    reverse = (order.lower() == "desc")
    results.sort(key=lambda r: (r.get(key) is None, r.get(key)), reverse=reverse)
    
    start = (page - 1) * page_size
    end = start + page_size
    page_items = results[start:end]
    
    return {"count": len(results), "page": page, "page_size": page_size, "results": page_items}

# Dynamic route defined LAST
@app.get("/loads/{load_id}", dependencies=[Depends(require_api_key)])
def get_load(load_id: str):
    norm = _norm_id(load_id)
    load = CACHE.get(norm)
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    return load
