import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIG ---
FILENAME = 'bible_reading_plan.csv'

# --- DATA UTILITIES ---
def load_and_calculate_stats():
    """Loads the main CSV and calculates real-time KPIs."""
    if not os.path.exists(FILENAME):
        return None

    df = pd.read_csv(FILENAME)

    # 1. Progress Metrics
    completed = len(df[df['Status'] == 'Read'])
    total = len(df)
    progress_pct = (completed / total) * 100

    # 2. Velocity & Projection Logic
    days_elapsed = (datetime.now().date() - datetime(2026, 1, 1).date()).days + 1
    # Ensure we don't divide by zero if today is Jan 1st
    velocity = completed / max(days_elapsed, 1)

    if velocity > 0:
        days_to_finish = total / velocity
        projected_finish = datetime(2026, 1, 1) + timedelta(days=days_to_finish)
        finish_date_str = projected_finish.strftime("%b %d, %Y")
    else:
        finish_date_str = "TBD"

    # 3. Streak Calculation Logic
    temp_df = df.copy()
    temp_df['Date_DT'] = pd.to_datetime(temp_df['Date']).dt.date
    completed_days = set(temp_df[temp_df['Status'] == 'Read']['Date_DT'])

    streak = 0
    if completed_days:
        today = datetime.now().date()
        curr = today
        if curr not in completed_days:
            curr -= timedelta(days=1)

        while curr in completed_days:
            streak += 1
            curr -= timedelta(days=1)

    # CRITICAL FIX: All keys used in the UI must be returned here
    return {
        "completed": completed,
        "total": total,
        "pct": progress_pct,
        "streak": streak,
        "remaining": total - completed,
        "velocity": velocity,
        "finish_date": finish_date_str
    }

# --- PAGE SETUP ---
st.set_page_config(
    page_title="2026 Reading Tracker",
    page_icon="📖",
    layout="wide"
)

stats = load_and_calculate_stats()

# --- HERO SECTION ---
st.title("🛡️ The 2026 Scripture Command Center")
st.markdown("""
    **Stay focused. Maintain the streak. Finish the year.**
    *Dynamic operational intelligence for your 365-day spiritual discipline plan.*
""")

st.divider()

if stats:
    # --- KPI SNAPSHOT ---
    col1, col2, col3, col4 = st.columns(4)

    # 1. The Streak
    col1.metric("Current Streak", f"{stats['streak']} Days", "🔥")

    # 2. Annual Progress & Velocity
    col2.metric("Annual Progress", f"{stats['pct']:.1f}%", f"{stats['velocity']:.2f} days/day")

    # 3. Projected Finish
    # Target for today (March 6) is roughly 17.8% of the year
    col3.metric("Projected Finish", stats['finish_date'],
                delta="Ahead" if stats['pct'] >= 17.8 else "Behind")

    # 4. Days Remaining
    col4.metric("Days Remaining", stats['remaining'], help="Days left to complete the 365-day plan")

    st.divider()

    # --- VISUAL PROGRESS GAUGE ---
    left_co, cent_co, last_co = st.columns([1, 2, 1])

    with cent_co:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=stats['pct'],
            title={'text': "2026 Completion Journey"},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "#1f77b4"},
                'steps': [
                    {'range': [0, stats['pct']], 'color': "rgba(31, 119, 180, 0.1)"},
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': (datetime.now().timetuple().tm_yday / 365) * 100
                }
            }
        ))
        fig_gauge.update_layout(height=350, margin=dict(t=50, b=0))
        st.plotly_chart(fig_gauge, use_container_width=True)
else:
    st.error(f"⚠️ {FILENAME} not found. Please ensure it is in the root directory.")

st.divider()

# --- NAVIGATION GUIDE ---
st.subheader("🧭 Strategic Navigation")
c1, c2 = st.columns(2)

with c1:
    st.info("### 📅 Daily Tracker\nLog daily chapters and track consistency.")

with c2:
    st.success("### 📈 Weekly Analytics\nView your burndown rate and pace adjustments.")