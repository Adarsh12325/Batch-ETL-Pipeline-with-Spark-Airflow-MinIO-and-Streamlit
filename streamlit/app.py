import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# -----------------------------------
# Page Configuration
# -----------------------------------
st.set_page_config(
    page_title="Ecommerce Analytics Dashboard",
    layout="wide"
)

st.title("📊 Ecommerce Analytics Dashboard")
st.markdown("Gold Layer → PostgreSQL → Streamlit")

# -----------------------------------
# Database Connection
# -----------------------------------
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "airflow")
POSTGRES_USER = os.getenv("POSTGRES_USER", "airflow")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "airflow")


@st.cache_data
def load_data():
    try:
        db_url = f"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}/{os.environ['POSTGRES_DB']}"
        engine = create_engine(db_url)

        query = "SELECT * FROM daily_metrics ORDER BY event_date;"
        df = pd.read_sql(query, engine)
        engine.dispose()
        return df

    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return pd.DataFrame()


df = load_data()

if df.empty:
    st.warning("⚠ No data found in daily_metrics table.")
    st.stop()

# Convert date column
df["event_date"] = pd.to_datetime(df["event_date"])

# -----------------------------------
# KPI Section
# -----------------------------------
col1, col2, col3 = st.columns(3)

col1.metric(
    "📦 Total Events",
    f"{df['total_events'].sum():,}"
)

col2.metric(
    "👥 Avg Daily Active Users",
    f"{int(df['daily_active_users'].mean()):,}"
)

col3.metric(
    "📈 Total Days Recorded",
    f"{df['event_date'].nunique():,}"
)

st.divider()

# -----------------------------------
# Events Trend Chart
# -----------------------------------
st.subheader("📈 Daily Events Trend")
events_chart = px.line(
    df,
    x="event_date",
    y="total_events",
    markers=True
)
st.plotly_chart(events_chart, use_container_width=True)

# -----------------------------------
# Active Users Chart
# -----------------------------------
st.subheader("👥 Daily Active Users")

users_chart = px.bar(
    df,
    x="event_date",
    y="daily_active_users"
)

st.plotly_chart(users_chart, use_container_width=True)

st.divider()

st.success("✅ Dashboard successfully connected to PostgreSQL")
