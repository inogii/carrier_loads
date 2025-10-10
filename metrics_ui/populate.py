import requests
import random
from datetime import datetime, timedelta

API_URL = "https://metrics-api-cold-grass-4301.fly.dev/calls"
API_KEY = "change-me"
HEADERS = {"X-API-Key": API_KEY}

# Define some fake reference data
MC_NUMBERS = [f"MC{1000 + i}" for i in range(10)]
SENTIMENTS = ["happy", "neutral", "upset", "n/a"]
OUTCOMES = ["successful", "unsuccessful", "n/a"]

def random_call():
    """Generate a single fake call record."""
    original_price = round(random.uniform(800, 2500), 2)
    had_discount = random.choice([True, False])
    discount_rate = round(random.uniform(5, 25), 2) if had_discount else 0
    agreed_price = round(original_price * (1 - discount_rate / 100), 2)
    duration = random.randint(60, 1200)
    timestamp = datetime.utcnow() - timedelta(days=random.randint(0, 30))
    sentiment = random.choices(SENTIMENTS, weights=[0.4, 0.4, 0.15, 0.05])[0]
    outcome = random.choices(OUTCOMES, weights=[0.7, 0.25, 0.05])[0]
    return {
        "mc_number": random.choice(MC_NUMBERS),
        "original_price": original_price,
        "agreed_price": agreed_price,
        "had_discount": had_discount,
        "discount_rate": discount_rate,
        "sentiment": sentiment,
        "outcome": outcome,
        "duration": duration,
        "timestamp": timestamp.isoformat(),
    }

def populate(n=100):
    """Send n fake call events to the API."""
    success, errors = 0, 0
    for _ in range(n):
        data = random_call()
        r = requests.post(API_URL, json=data, headers=HEADERS)
        if r.status_code == 200:
            success += 1
        else:
            errors += 1
            print(f"❌ Failed: {r.status_code} -> {r.text}")
    print(f"✅ Inserted {success} calls ({errors} errors)")

if __name__ == "__main__":
    populate(300)

