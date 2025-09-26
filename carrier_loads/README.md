
# Carrier Loads API (Demo)

A simple FastAPI service exposing available freight loads from a CSV snapshot.

## Features
- `GET /loads/{load_id}` → fetch a specific load
- `GET /loads/search?origin=&destination=&equipment_type=&max_weight=` → search loads
- API key check via `X-API-Key` (default `dev-secret`)
- CSV path configurable via `LOADS_PATH`

## Run locally

```bash
cd carrier_loads
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

## Docker

```bash
cd carrier_loads
docker build -t carrier-loads:latest .
docker run -p 8000:8000 -e API_KEY=dev-secret carrier-loads:latest
```

## Example requests

```bash
# Health
curl -s http://localhost:8000/health

# Get a load
curl -s -H "X-API-Key: dev-secret" http://localhost:8000/loads/L001 | jq

# Search loads by origin/destination
curl -s -H "X-API-Key: dev-secret" "http://localhost:8000/loads/search?origin=Chicago&destination=Dallas" | jq
```

## Sample CSV schema

```
load_id,origin,destination,pickup_datetime,delivery_datetime,equipment_type,loadboard_rate,notes,weight,commodity_type,num_of_pieces,miles,dimensions
```
