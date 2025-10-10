import os
import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta

# ---------- Configuration ----------
st.set_page_config(page_title="Carrier Sales Dashboard", layout="wide")

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "change-me")
HEADERS = {"X-API-Key": API_KEY}

# ---------- Helper ----------
def fetch(endpoint, params=None):
    """Helper to call API and handle errors gracefully."""
    try:
        res = requests.get(f"{API_URL}{endpoint}", headers=HEADERS, params=params)
        if res.status_code == 200:
            return res.json()
        else:
            st.error(f"Error {res.status_code}: {res.text}")
            return None
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None



# ---------- Dashboard ----------
st.title("📊 Carrier Sales Representative Metrics Dashboard")
st.caption("Data visualization of call analytics from the Metrics API")

days = st.slider("Days for time-series metrics", 7, 90, 14)

col1, col2, col3 = st.columns(3)

# Total duration
duration_data = fetch("/metrics/total_duration")
if duration_data:
    total_seconds = duration_data["total_duration_seconds"]
    
    # Dynamically choose the most appropriate time unit
    if total_seconds < 60:
        display_value = f"{total_seconds:.0f} sec"
    elif total_seconds < 3600:
        display_value = f"{total_seconds / 60:.1f} min"
    elif total_seconds < 86400:
        display_value = f"{total_seconds / 3600:.1f} hr"
    else:
        display_value = f"{total_seconds / 86400:.1f} days"

    col1.metric("Total Time Saved (call duration)", display_value)

# Total sales volume
sales_data = fetch("/metrics/total_sales_volume")
if sales_data:
    col2.metric("Total Sales Volume ($)", f"{sales_data['total_sales_volume']:.2f}")

# Satisfaction distribution
satisfaction = fetch("/metrics/satisfaction")
if satisfaction:
    df_sat = pd.DataFrame(satisfaction)
    col3.metric("Most Frequent Sentiment", df_sat.loc[df_sat["percentage"].idxmax(), "sentiment"].capitalize())

st.divider()

# ---------- Charts ----------
st.subheader(f"📈 Trends over the last {days} days")

col1, col2 = st.columns(2)

# Duration evolution
duration_evo = fetch("/metrics/duration_evolution", {"days": days})
if duration_evo:
    df = pd.DataFrame(duration_evo)
    df["day"] = pd.to_datetime(df["day"])
    with col1:
        st.line_chart(df.set_index("day")["total_duration_s"], height=250, use_container_width=True)
        st.caption("Total call duration per day")

# Sales evolution
sales_evo = fetch("/metrics/sales_evolution", {"days": days})
if sales_evo:
    df = pd.DataFrame(sales_evo)
    df["day"] = pd.to_datetime(df["day"])
    with col2:
        st.line_chart(df.set_index("day")["sales_volume"], height=250, use_container_width=True)
        st.caption("Sales volume per day")

st.divider()

# ---------- Discount trend ----------
discount_evo = fetch("/metrics/discount_evolution", {"days": days})
if discount_evo:
    df = pd.DataFrame(discount_evo)
    df["day"] = pd.to_datetime(df["day"])
    st.subheader("💰 Average Discount Rate Evolution")
    st.line_chart(df.set_index("day")["avg_discount_rate"], height=250, use_container_width=True)

st.divider()

# ---------- Satisfaction & Success ----------
st.subheader("🙂 Sentiment and Success Distributions")

# --- Sentiment section ---
st.markdown("#### Sentiment Distribution")
col1, col2 = st.columns([1, 2])

if satisfaction:
    df_sat = pd.DataFrame(satisfaction)
    with col1:
        st.dataframe(df_sat, hide_index=True, use_container_width=True)
    with col2:
        st.bar_chart(
            df_sat.set_index("sentiment")["percentage"],
            use_container_width=True,
            height=250,
        )

st.divider()

# --- Success section ---
st.markdown("#### Success Rate Distribution")
col1, col2 = st.columns([1, 2])

success = fetch("/metrics/success")
if success:
    df_succ = pd.DataFrame(success)
    with col1:
        st.dataframe(df_succ, hide_index=True, use_container_width=True)
    with col2:
        st.bar_chart(
            df_succ.set_index("outcome")["percentage"],
            use_container_width=True,
            height=250,
        )
