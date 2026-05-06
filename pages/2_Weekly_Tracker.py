import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
from pathlib import Path
import os

# --- 1. CONFIGURATION & PATHING ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / 'bible_reading_plan.csv'
PROGRESS_FILE = BASE_DIR / 'user_progress.csv'
START_DATE = datetime.date(2026, 1, 1)


@st.cache_data
def load_weekly_data():
    if not DATA_FILE.exists():
        st.error(f"Master plan not found at {DATA_FILE}")
        return pd.DataFrame()

    # Read the master plan (The 365-day CSV)
    daily_df = pd.read_csv(DATA_FILE)

    # Ensure 'Week' is calculated (7 days per week)
    daily_df['Week'] = (daily_df['Day'] - 1) // 7 + 1

    # --- THE READER-FRIENDLY FORMATTING LOGIC ---
    def clean_weekly_label(group):
        # We only care about the very first day and the very last day of the week
        first_raw = str(group.iloc[0]).strip()
        last_raw = str(group.iloc[-1]).strip()

        # Helper to extract Book and the FIRST chapter number
        # Example: "1 Maccabees 15-18" -> Book: "1 Maccabees", Chapter: "15"
        def parse_entry(entry):
            parts = entry.split()
            if not parts: return "", ""
            book = " ".join(parts[:-1])
            # Split by dash to ignore the end-of-day range (e.g., ignore the '16' in '13-16')
            chapter = parts[-1].split('-')[0]
            return book, chapter

        book_f, chap_f = parse_entry(first_raw)
        book_l, chap_l = parse_entry(last_raw)

        # Scenario 1: The entire week is within the same book (e.g., Job 13 — 37)
        if book_f == book_l:
            return f"{book_f} {chap_f} — {chap_l}"

        # Scenario 2: The week spans across two different books (e.g., Ezra 8 — Tobit 6)
        else:
            return f"{book_f} {chap_f} — {book_l} {chap_l}"

    # Group the daily plan into 52 weekly rows with the clean labels
    weekly_df = daily_df.groupby('Week')['Passage'].apply(clean_weekly_label).reset_index()
    weekly_df['Completed'] = False

    # --- SYNC PROGRESS ---
    # This part keeps your checkmarks safe when the book names update
    if PROGRESS_FILE.exists():
        df_old = pd.read_csv(PROGRESS_FILE)
        if 'Completed' in df_old.columns:
            status_map = dict(zip(df_old['Week'], df_old['Completed']))
            weekly_df['Completed'] = weekly_df['Week'].map(status_map).fillna(False)

    # Save the cleaned-up weekly progress to disk
    weekly_df.to_csv(PROGRESS_FILE, index=False)
    return weekly_df


# --- 2. UI INITIALIZATION ---
st.set_page_config(page_title="Weekly Analytics", layout="wide")
st.title("📊 Weekly Burndown Analytics")

df = load_weekly_data()

if not df.empty:
    # --- METRICS CALCULATIONS ---
    today = datetime.date.today()
    day_of_year = (today - START_DATE).days + 1
    current_week = max(1, (day_of_year // 7) + 1)

    total_weeks = len(df)
    completed_weeks = df['Completed'].sum()
    pace_status = "On Track" if completed_weeks >= current_week - 1 else "Behind"

    m1, m2, m3 = st.columns(3)
    m1.metric("Current Week", f"Week {current_week}", f"Day {day_of_year}")
    m2.metric("Completion", f"{completed_weeks}/{total_weeks}", f"{int((completed_weeks / total_weeks) * 100)}%")
    m3.metric("Pace Analysis", pace_status, delta=int(completed_weeks - (current_week - 1)))

    st.divider()

    # --- BURNDOWN CHART ---
    weeks = list(range(1, total_weeks + 1))

    # 1. ACTUAL PROGRESS: Find your current finish line
    last_completed_week = df[df['Completed'] == True]['Week'].max() if any(df['Completed']) else 0
    cumulative_completed = df.sort_values('Week')['Completed'].astype(int).cumsum().tolist()

    # Mask the line so it stops at your current finish line
    actual_series = [val if i < last_completed_week else None for i, val in enumerate(cumulative_completed)]

    fig = go.Figure()

    # --- TRACE 1: PROPOSED PLAN (Dashed Target Line) ---
    fig.add_trace(go.Scatter(
        x=weeks, y=weeks,
        mode='lines',
        name='Proposed Plan (Target)',
        line=dict(color='rgba(200, 200, 200, 0.5)', dash='dash', width=2),
    ))

    # --- TRACE 2: THE BLUE LINE (Clean Line only) ---
    fig.add_trace(go.Scatter(
        x=weeks, y=actual_series,
        mode='lines',
        name='Your Actual Progress',
        line=dict(color='#007BFF', width=4),
        fill='tozeroy',
        fillcolor='rgba(0, 123, 255, 0.05)',
        connectgaps=False,
    ))

    # --- TRACE 3: CALENDAR MARKER (Red Star at Today's Week) ---
    # This shows where the calendar says you should be
    fig.add_trace(go.Scatter(
        x=[current_week], y=[current_week],
        mode='markers',
        name='Calendar Position',
        marker=dict(size=14, symbol='star', color='#FF4B4B'),
        hovertemplate="Calendar Target: Week %{x}<extra></extra>"
    ))

    # --- TRACE 4: FINISHED MARKER (Checkmark at Finish Line) ---
    # This shows your actual current outperformance
    if last_completed_week > 0:
        fig.add_trace(go.Scatter(
            x=[last_completed_week], y=[last_completed_week],
            mode='markers',
            name='Your Finish Line',
            marker=dict(size=14, symbol='hexagram', color='#28a745'),
            hovertemplate="Finished: Week %{x}<extra></extra>"
        )
        )

    # --- TRACE 5: "TODAY" VERTICAL MARKER ---
    fig.add_vline(
        x=current_week,
        line_width=1,
        line_dash="dot",
        line_color="red",
    )

    # --- ANNOTATION: THE "LEAP AHEAD" LABEL ---
    if last_completed_week > current_week:
        leap = last_completed_week - current_week
        fig.add_annotation(
            x=last_completed_week, y=last_completed_week,
            text=f"🔥 {leap} Weeks Ahead!",
            showarrow=True, arrowhead=2, ax=0, ay=-50,
            bgcolor="#28a745", font=dict(color="white", size=12)
        )

    fig.update_layout(
        title=dict(text="Progress Comparison: Calendar vs. Reading", x=0.5),
        hovermode="closest",
        xaxis=dict(title="Calendar Week Number", range=[1, 53], showgrid=False),
        yaxis=dict(title="Weeks Completed", range=[0, 53]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=50, b=0),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- THE WEEKLY CHECKLIST ---
    st.divider()
    st.subheader("Weekly Milestone Checklist")

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
        st.success("Milestones updated and synced with Progress File.")
        st.rerun()
else:
    st.error("⚠️ Master plan is empty or could not be loaded")