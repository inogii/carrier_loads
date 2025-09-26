# FMCSA Facade
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default API key for local dev; override in prod
ENV API_KEY=dev-secret
ENV FMCSA_CACHE_PATH=data/fmcsa_cache.csv

EXPOSE 8001

CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001" ]
