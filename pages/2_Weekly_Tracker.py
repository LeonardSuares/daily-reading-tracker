import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
from pathlib import Path

# 1. ROBUST PATHING
# Pathlib is the modern standard for Senior Developers
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / 'bible_reading_plan.csv'  # Keeping your CSV preference
PROGRESS_FILE = BASE_DIR / 'user_progress.csv'
START_DATE = datetime.date(2026, 1, 1)


@st.cache_data
def load_weekly_data():
    if not DATA_FILE.exists():
        st.error(f"Master plan not found at {DATA_FILE}")
        return pd.DataFrame()

    if PROGRESS_FILE.exists():
        # Load existing progress
        df_progress = pd.read_csv(PROGRESS_FILE)
        # Handle case-sensitivity if necessary
        if 'Passage' not in df_progress.columns and 'Reading Range' in df_progress.columns:
            df_progress = df_progress.rename(columns={'Reading Range': 'Passage'})
        return df_progress

    # INITIALIZATION LOGIC
    # If progress file doesn't exist, we create it from the daily plan
    daily_df = pd.read_csv(DATA_FILE)

    # 1. Create the Week index
    daily_df['Week'] = (daily_df['Day'] - 1) // 7 + 1

    # 2. Group by week and aggregate the Passage column
    # This creates a string like "Genesis 1-7" for each week
    weekly_df = daily_df.groupby('Week').agg({
        'Passage': lambda x: f"{x.iloc[0].split()[0]} {x.iloc[0].split()[-1]}-{x.iloc[-1].split()[-1]}",
        'Status': lambda x: (x == 'Read').all()  # Auto-check if all 7 days are 'Read'
    }).reset_index()

    weekly_df = weekly_df.rename(columns={'Status': 'Completed'})
    weekly_df.to_csv(PROGRESS_FILE, index=False)
    return weekly_df


# --- UI INITIALIZATION ---
st.title("📊 Weekly Burndown Analytics")
df = load_weekly_data()

if not df.empty:
    # 2. TEMPORAL LOGIC
    today = datetime.date.today()
    day_of_year = (today - START_DATE).days + 1
    current_week = max(0, (day_of_year // 7) + 1)

    # 3. METRIC CALCULATION
    total_weeks = 52
    completed_weeks = df['Completed'].sum()
    pace_status = "On Track" if completed_weeks >= current_week - 1 else "Behind"

    m1, m2, m3 = st.columns(3)
    m1.metric("Current Week", f"Week {current_week}", f"Day {day_of_year}")
    m2.metric("Completion", f"{completed_weeks}/{total_weeks}", f"{int((completed_weeks / 52) * 100)}%")
    m3.metric("Pace Analysis", pace_status,
              delta=int(completed_weeks - (current_week - 1)),
              delta_color="normal" if pace_status == "On Track" else "inverse")

    st.divider()

    # --- ANALYTICS: PROJECTED VS. ACTUAL ---
    st.subheader("📉 Strategy: Projected Target vs. Actual Pace")

    # 1. Generate the time-based target
    weeks = list(range(1, 53))
    # Vectorized cumulative sum for actual progress
    actual_series = df.sort_values('Week')['Completed'].astype(int).cumsum().tolist()
    actual_series += [actual_series[-1]] * (52 - len(actual_series))

    # 2. Calculate the 'Required' point based on today's date
    today = datetime.date.today()
    days_into_year = (today - START_DATE).days + 1
    target_week = min(52, max(0, (days_into_year // 7) + 1))

    fig = go.Figure()

    # --- TRACE 1: IDEAL PACE LINE ---
    fig.add_trace(go.Scatter(
        x=weeks, y=weeks,
        mode='lines', name='Ideal Annual Pace',
        line=dict(color='rgba(150, 150, 150, 0.3)', dash='dash')
    ))

    # --- TRACE 2: ACTUAL PROGRESS (WITH FILL) ---
    fig.add_trace(go.Scatter(
        x=weeks, y=actual_series,
        mode='lines+markers', name='Actual Progress',
        fill='tozeroy', fillcolor='rgba(0, 123, 255, 0.1)',
        line=dict(color='#007BFF', width=3)
    ))

    # --- TRACE 3: CURRENT PROJECTED TARGET (Vertical Marker) ---
    fig.add_vline(
        x=target_week,
        line_width=2,
        line_dash="dot",
        line_color="red",
        annotation_text=f"Today: Week {target_week}",
        annotation_position="top left"
    )

    # Highlight the 'Target' point on the Ideal Line
    fig.add_trace(go.Scatter(
        x=[target_week], y=[target_week],
        mode='markers',
        name='Projected Requirement',
        marker=dict(color='red', size=12, symbol='star')
    ))

    fig.update_layout(
        hovermode="x unified",
        xaxis=dict(title="Week Number", dtick=4),
        yaxis=dict(title="Weeks Completed", range=[0, 52]),
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 5. INTERACTIVE CHECKLIST
    st.divider()
    st.subheader("Weekly Milestone Checklist")

    # Use a data editor for mass-updates - much faster than a form with 52 checkboxes
    edited_df = st.data_editor(
        df[['Week', 'Passage', 'Completed']],
        key="weekly_editor",
        hide_index=True,
        disabled=['Week', 'Passage'],
        use_container_width=True
    )

    if st.button("Save Weekly Progress", use_container_width=True):
        edited_df.to_csv(PROGRESS_FILE, index=False)
        st.cache_data.clear()
        st.success("Milestones updated and synced with Daily Tracker.")
        st.rerun()