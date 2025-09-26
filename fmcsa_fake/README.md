
# FMCSA Facade (Demo)

A tiny FastAPI service that validates carrier eligibility from a local FMCSA CSV snapshot.

## Features
- `GET /carriers/{mc}` → returns normalized eligibility info
- API key check via `X-API-Key` (default `dev-secret`)
- CSV path configurable via `FMCSA_CACHE_PATH`

## Run locally (Python)

```bash
cd fmcsa_facade
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export API_KEY=dev-secret
uvicorn app:app --reload --port 8000
```

## Docker

```bash
cd fmcsa_facade
docker build -t fmcsa-facade:latest .
docker run -p 8000:8000 -e API_KEY=dev-secret fmcsa-facade:latest
```

## Example requests

```bash
# Health
curl -s http://localhost:8000/health

# Check by path
curl -s -H "X-API-Key: dev-secret" http://localhost:8000/carriers/123456 | jq

# Check by POST
curl -s -X POST -H "Content-Type: application/json" -H "X-API-Key: dev-secret" \
  -d '{"mc":"222333"}' http://localhost:8000/carriers/check | jq

```

## Eligibility logic
Eligible if:
- `status == active`
- `insurance_ok == true`
- `authority_ok == true`

The response contains:
```json
{
  "eligible": true,
  "reason": "Eligible",
  "mc": "123456",
  "dot": "987654",
  "carrier_name": "Alpha Logistics LLC",
  "status": "active",
  "insurance_ok": true,
  "authority_ok": true
}
```

## Notes
- Replace the CSV with a larger snapshot as needed (keep same headers).
- In production, set a strong `API_KEY` and run behind HTTPS (e.g., Fly.io/Cloud Run + Let's Encrypt).
