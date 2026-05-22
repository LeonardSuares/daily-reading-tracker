import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Daily Reading Tracker", layout="wide", page_icon="📖")

# --- 2. UNIFIED DATA SOURCES ---
FILENAME = 'bible_reading_plan.csv'
WEEKLY_FILE = 'user_progress.csv'


def sync_weekly_progress(daily_df):
    """Marks weeks complete in user_progress.csv if all 7 corresponding days are read."""
    if os.path.exists(WEEKLY_FILE):
        weekly_df = pd.read_csv(WEEKLY_FILE)
        daily_df['Day_Group'] = (daily_df['Day'] - 1) // 7 + 1
        for week_num in weekly_df['Week']:
            days_in_week = daily_df[daily_df['Day_Group'] == week_num]
            status = not days_in_week.empty and (days_in_week['Status'] == 'Read').all()
            weekly_df.loc[weekly_df['Week'] == week_num, 'Completed'] = status
        weekly_df.to_csv(WEEKLY_FILE, index=False)


@st.cache_data
def load_data():
    if os.path.exists(FILENAME):
        data = pd.read_csv(FILENAME)
        data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%Y-%m-%d')
        return data
    return pd.DataFrame()


def load_actual_weekly_progress():
    """Calculates completion metrics directly from the user progress table."""
    if os.path.exists(WEEKLY_FILE):
        w_df = pd.read_csv(WEEKLY_FILE)
        completed_weeks = w_df['Completed'].sum()
        total_weeks = len(w_df)
        pct = (completed_weeks / total_weeks * 100) if total_weeks > 0 else 0
        return completed_weeks, total_weeks, pct
    return 0, 52, 0


def calculate_streak(daily_df):
    temp_df = daily_df.copy()
    temp_df['Date_DT'] = pd.to_datetime(temp_df['Date']).dt.date
    completed = set(temp_df[temp_df['Status'] == 'Read']['Date_DT'])
    if not completed: return 0
    today, streak = datetime.now().date(), 0
    curr = today if today in completed else today - timedelta(days=1)
    while curr in completed:
        streak += 1
        curr -= timedelta(days=1)
    return streak


# --- UI EXECUTION ---
df = load_data()
completed_weeks, total_weeks, actual_pct = load_actual_weekly_progress()
today_str = datetime.now().strftime('%Y-%m-%d')

if df.empty:
    st.error(f"⚠️ {FILENAME} not found.")
else:
    st.title("📖 Daily Scripture Tracker")

    # --- 3. TOP KPI ROW (COMPARISON METRICS) ---
    completed_days_count = len(df[df['Status'] == 'Read'])
    current_streak = calculate_streak(df)

    start_date = pd.to_datetime(df['Date'].min())
    days_passed = (datetime.now() - start_date).days + 1
    total_days = len(df)

    # Expected schedule calculation
    proposed_pct = (days_passed / total_days) * 100 if total_days > 0 else 0
    expected_weeks_passed = days_passed / 7

    # Directly subtract proposed schedule metrics from your live values
    streak_delta = completed_days_count - days_passed
    pace_diff = completed_weeks - expected_weeks_passed

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Real-Time Progress", f"{actual_pct:.1f}%")
    m2.metric("Current Streak", f"{current_streak} Days", delta=f"{streak_delta} Days vs Plan",
              delta_color="normal" if streak_delta >= 0 else "inverse")
    m3.metric("Proposed Target", f"{proposed_pct:.1f}%")
    m4.metric("Pace vs. Proposal", f"{completed_weeks}/{int(expected_weeks_passed)} Wks",
              delta=f"{pace_diff:.1f} Weeks Ahead" if pace_diff >= 0 else f"{pace_diff:.1f} Weeks Behind",
              delta_color="normal" if pace_diff >= 0 else "inverse")

    st.write(
        f"**Overall Progress:** You have completed **{completed_weeks}** out of **{total_weeks}** scheduled study weeks.")
    st.progress(actual_pct / 100)
    st.divider()

    # --- 4. ACTION TABS ---
    tab1, tab2, tab3 = st.tabs(["🎯 Today's Task", "⚠️ Catch-up", "📊 Full Schedule"])

    with tab1:
        st.subheader(f"Status for {datetime.now().strftime('%A, %b %d')}")
        today_row = df[df['Date'] == today_str]

        if not today_row.empty:
            passage = today_row.iloc[0]['Passage']
            status = today_row.iloc[0]['Status']

            if status == 'Read':
                st.success(
                    f"### ✅ All caught up with today's assigned reading block! \n Keep working through your custom plan.")
            else:
                st.info(f"### 📖 Today's Target Reading: **{passage}**")
                if st.button("Mark Assignment as Complete", use_container_width=True):
                    df.loc[df['Date'] == today_str, 'Status'] = 'Read'
                    df.to_csv(FILENAME, index=False)
                    sync_weekly_progress(df)
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.warning("No template assignment found for today's calendar date.")

    with tab2:
        missed = df[(df['Date'] < today_str) & (df['Status'] == 'Pending')]
        if not missed.empty:
            st.warning(f"Attention: {len(missed)} daily milestones require catch-up verification.")
            edited_df = st.data_editor(missed[['Day', 'Date', 'Passage', 'Status']], hide_index=True,
                                       disabled=['Day', 'Date', 'Passage'], use_container_width=True)
            if st.button("Update Catch-up Progress"):
                for _, row in edited_df.iterrows():
                    df.loc[df['Day'] == row['Day'], 'Status'] = row['Status']
                df.to_csv(FILENAME, index=False)
                sync_weekly_progress(df)
                st.cache_data.clear()
                st.rerun()
        else:
            st.success("Perfect alignment! Your reading track matches your 2026 milestones exactly.")

    with tab3:
        st.subheader("2026 Master Reading Plan Matrix")
        st.dataframe(df[['Day', 'Date', 'Passage', 'Status']], use_container_width=True, hide_index=True)