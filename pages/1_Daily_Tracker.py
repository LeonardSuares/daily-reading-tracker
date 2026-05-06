import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Daily Reading Tracker", layout="wide", page_icon="📖")

# --- 2. DATA SOURCES & SYNC ---
FILENAME = 'bible_reading_plan.csv'
WEEKLY_FILE = 'user_progress.csv'
CANONICAL_FILE = 'bible_canonical_progress.csv'


def sync_weekly_progress(daily_df):
    if os.path.exists(WEEKLY_FILE):
        weekly_df = pd.read_csv(WEEKLY_FILE)
        daily_df['Day_Group'] = (daily_df['Day'] - 1) // 7 + 1
        for week_num in weekly_df['Week']:
            days_in_week = daily_df[daily_df['Day_Group'] == week_num]
            status = not days_in_week.empty and (days_in_week['Status'] == 'Read').all()
            weekly_df.loc[weekly_df['Week'] == week_num, 'Completed'] = status
        weekly_df.to_csv(WEEKLY_FILE, index=False)


def load_data():
    if os.path.exists(FILENAME):
        data = pd.read_csv(FILENAME)
        data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%Y-%m-%d')
        return data
    return pd.DataFrame()


def get_realtime_chapter():
    """Finds the next chapter to read from canonical data."""
    if os.path.exists(CANONICAL_FILE):
        df_canon = pd.read_csv(CANONICAL_FILE)
        unfinished = df_canon[df_canon['Chapters_Read'] < df_canon['Total_Chapters']]
        if not unfinished.empty:
            book = unfinished.iloc[0]
            return f"{book['Book']} {int(book['Chapters_Read']) + 1}"
    return "Plan Completed!"


def load_canonical_stats():
    if os.path.exists(CANONICAL_FILE):
        df = pd.read_csv(CANONICAL_FILE)
        read_ch, total_ch = df['Chapters_Read'].sum(), df['Total_Chapters'].sum()
        return read_ch, total_ch, (read_ch / total_ch * 100)
    return 0, 1328, 0


def calculate_streak(df):
    temp_df = df.copy()
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
read_ch, total_ch, canon_pct = load_canonical_stats()
current_reading = get_realtime_chapter()
today_str = datetime.now().strftime('%Y-%m-%d')

if df.empty:
    st.error(f"⚠️ {FILENAME} not found.")
else:
    st.title("📖 Daily Scripture Tracker")

    # --- 3. TOP KPI ROW ---
    completed_days_count = len(df[df['Status'] == 'Read'])
    current_streak = calculate_streak(df)

    start_date = pd.to_datetime(df['Date'].min())
    days_passed = (datetime.now() - start_date).days + 1
    total_days = (pd.to_datetime(df['Date'].max()) - start_date).days + 1
    proposed_pct = (days_passed / total_days) * 100

    streak_delta = completed_days_count - days_passed
    pace_diff = canon_pct - proposed_pct

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Real-Time Status", f"{canon_pct:.1f}%")
    m2.metric("Current Streak", f"{current_streak} Days", delta=f"{streak_delta} vs Plan",
              delta_color="normal" if streak_delta >= 0 else "inverse")
    m3.metric("Proposed Progress", f"{proposed_pct:.1f}%")
    m4.metric("Pace vs. Proposal", f"{pace_diff:.1f}%", delta=f"{pace_diff:.1f}%",
              delta_color="normal" if pace_diff >= 0 else "inverse")

    st.write(f"**Overall Completion:** {read_ch} of {total_ch} Chapters")
    st.progress(canon_pct / 100)
    st.divider()

    # --- 4. ACTION TABS ---
    tab1, tab2, tab3 = st.tabs(["🎯 Today's Task", "⚠️ Catch-up", "📊 Full Schedule"])

    with tab1:
        # Cleaned up: Only one status area
        st.subheader(f"Status for {datetime.now().strftime('%A, %b %d')}")

        today_row = df[df['Date'] == today_str]
        if not today_row.empty:
            passage = today_row.iloc[0]['Passage']
            status = today_row.iloc[0]['Status']

            if status == 'Read':
                # Consolidate: Tell them they are done AND show the real-time chapter in one ribbon
                st.success(f"### ✅ All caught up! \n **Next up in your Canonical Plan:** {current_reading}")
            else:
                st.info(f"### 📖 Today's Assignment: **{passage}**")
                st.write(f"*Your overall Canonical Progress is currently at:* **{current_reading}**")
                if st.button("Mark Assignment as Complete", use_container_width=True):
                    df.loc[df['Date'] == today_str, 'Status'] = 'Read'
                    df.to_csv(FILENAME, index=False)
                    sync_weekly_progress(df)
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.warning("No assignment found for today.")

    with tab2:
        missed = df[(df['Date'] < today_str) & (df['Status'] == 'Pending')]
        if not missed.empty:
            st.warning(f"Attention: {len(missed)} readings require catch-up.")
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
            st.success("Perfect! You are fully caught up with the plan.")

    with tab3:
        st.subheader("2026 Master Reading Plan")
        st.dataframe(df[['Day', 'Date', 'Passage', 'Status']], use_container_width=True, hide_index=True)