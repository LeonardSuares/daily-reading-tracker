import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIG ---
FILENAME = 'bible_reading_plan.csv'
CANONICAL_FILE = 'bible_canonical_progress.csv'


# --- DATA UTILITIES ---
def load_and_calculate_stats():
    """Loads CSVs and calculates real-time KPIs vs Proposed Plan."""
    if not os.path.exists(FILENAME) or not os.path.exists(CANONICAL_FILE):
        return None

    # Load Daily Data for Streak and Calendar Logic
    df_daily = pd.read_csv(FILENAME)
    # Load Canonical Data for "Real-Time" Progress
    df_canon = pd.read_csv(CANONICAL_FILE)

    # 1. Real-Time Progress Metrics (from Canonical Page)
    read_ch = df_canon['Chapters_Read'].sum()
    total_ch = df_canon['Total_Chapters'].sum()
    progress_pct = (read_ch / total_ch) * 100

    # 2. Proposed Plan Logic (Calendar-based)
    start_date = pd.to_datetime(df_daily['Date']).min().date()
    end_date = pd.to_datetime(df_daily['Date']).max().date()

    today = datetime.now().date()
    total_days_in_plan = (end_date - start_date).days + 1
    days_elapsed = (today - start_date).days + 1

    # Calculate what % you SHOULD be at today
    proposed_pct = (days_elapsed / total_days_in_plan) * 100

    # 3. Velocity & Projection Logic
    velocity = progress_pct / max(days_elapsed, 1)  # % progress per day

    if velocity > 0:
        total_days_needed = 100 / velocity
        projected_finish = start_date + timedelta(days=total_days_needed)
        finish_date_str = projected_finish.strftime("%b %d, %Y")
    else:
        finish_date_str = "TBD"

    # 4. Streak Calculation Logic
    temp_df = df_daily.copy()
    temp_df['Date_DT'] = pd.to_datetime(temp_df['Date']).dt.date
    completed_days = set(temp_df[temp_df['Status'] == 'Read']['Date_DT'])

    streak = 0
    if completed_days:
        curr = today
        if curr not in completed_days:
            curr -= timedelta(days=1)
        while curr in completed_days:
            streak += 1
            curr -= timedelta(days=1)

    return {
        "read_chapters": read_ch,
        "total_chapters": total_ch,
        "pct": progress_pct,
        "proposed_pct": proposed_pct,
        "streak": streak,
        "velocity": velocity,
        "finish_date": finish_date_str,
        "pace_diff": progress_pct - proposed_pct
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
st.markdown(f"""
    **Stay focused. Maintain the streak. Finish the year.**
    *Currently synced with your **Canonical Progress** and the **Proposed Plan**.*
""")

st.divider()

if stats:
    # --- KPI SNAPSHOT ---
    col1, col2, col3, col4 = st.columns(4)

    # 1. The Streak
    col1.metric("Current Streak", f"{stats['streak']} Days", "🔥")

    # 2. Real-Time Status (The "Canadian" Progress)
    col2.metric("Real-Time Status", f"{stats['pct']:.1f}%",
                delta=f"{stats['pace_diff']:.1f}% vs Plan")

    # 3. Projected Finish
    # Delta shows if you are finishing before or after Dec 31
    is_ahead = stats['pace_diff'] >= 0
    col3.metric("Projected Finish", stats['finish_date'],
                delta="Ahead of Schedule" if is_ahead else "Behind Schedule",
                delta_color="normal" if is_ahead else "inverse")

    # 4. Chapters Remaining
    remaining_ch = stats['total_chapters'] - stats['read_chapters']
    col4.metric("Chapters Left", f"{remaining_ch:,}", help="Total chapters remaining in the RSV-2CE Bible")

    st.divider()

    # --- VISUAL PROGRESS GAUGE ---
    left_co, cent_co, last_co = st.columns([1, 2, 1])

    with cent_co:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=stats['pct'],
            title={'text': "2026 Journey: Actual vs. Proposed"},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "#1f77b4"},
                'steps': [
                    {'range': [0, stats['proposed_pct']], 'color': "rgba(0, 0, 0, 0.1)"},
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': stats['proposed_pct']
                }
            }
        ))
        fig_gauge.update_layout(height=350, margin=dict(t=50, b=0))
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.caption(
            f"The red line indicates where you should be today ({stats['proposed_pct']:.1f}%) according to the Proposed Plan.")

else:
    st.error(
        "⚠️ Data files not found. Please ensure both bible_reading_plan.csv and bible_canonical_progress.csv exist.")

st.divider()

# --- NAVIGATION GUIDE ---
st.subheader("🧭 Strategic Navigation")
c1, c2, c3 = st.columns(3)

with c1:
    st.info("### 📅 Daily Tracker\nLog daily chapters and view real-time assignments.")
with c2:
    st.success("### 📈 Weekly Analytics\nView your burndown rate and pace adjustments.")
with c3:
    st.warning("### 📚 Canonical Progress\nUpdate your book-by-book chapter completion.")