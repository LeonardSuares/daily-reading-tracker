import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# 1. INITIALIZE GLOBAL VARIABLES
today_str = datetime.now().strftime('%Y-%m-%d')
FILENAME = 'bible_reading_plan.csv'

# 2. SYNC LOGIC (Define function BEFORE it is called)
def sync_weekly_progress(daily_df):
    """Updates weekly CSV if 7-day chunks are complete."""
    # Note: Adjust pathing based on your folder structure
    WEEKLY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_progress.csv')
    if os.path.exists(WEEKLY_FILE):
        weekly_df = pd.read_csv(WEEKLY_FILE)
        daily_df['Day_Group'] = (daily_df['Day'] - 1) // 7 + 1
        for week_num in weekly_df['Week']:
            days_in_week = daily_df[daily_df['Day_Group'] == week_num]
            if not days_in_week.empty and (days_in_week['Status'] == 'Read').all():
                weekly_df.loc[weekly_df['Week'] == week_num, 'Completed'] = True
        weekly_df.to_csv(WEEKLY_FILE, index=False)

@st.cache_data
def load_data():
    try:
        data = pd.read_csv(FILENAME)
        data['Date'] = data['Date'].astype(str)
        return data
    except FileNotFoundError:
        return pd.DataFrame()

def calculate_streak(df):
    temp_df = df.copy()
    temp_df['Date_DT'] = pd.to_datetime(temp_df['Date']).dt.date
    completed_days = temp_df[temp_df['Status'] == 'Read'].sort_values('Date_DT', ascending=False)
    if completed_days.empty: return 0
    today = datetime.now().date()
    last_read_date = completed_days.iloc[0]['Date_DT']
    if last_read_date < (today - timedelta(days=1)): return 0
    streak = 0
    curr = last_read_date
    for _, row in completed_days.iterrows():
        if row['Date_DT'] == curr:
            streak += 1
            curr -= timedelta(days=1)
        else: break
    return streak

# 3. UI EXECUTION
df = load_data()

if df.empty:
    st.error(f"⚠️ {FILENAME} not found. Please ensure the data file is in the root directory.")
else:
    st.title("📖 Daily Bible Reading Tracker")
    st.markdown("---")

    # Metrics
    completed = len(df[df['Status'] == 'Read'])
    total = len(df)
    progress_pct = (completed / total) * 100
    current_streak = calculate_streak(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Completed Days", completed)
    col2.metric("Remaining", total - completed)
    col3.metric("Total Progress", f"{progress_pct:.1f}%")
    col4.metric("🔥 Current Streak", f"{current_streak} Days")
    st.progress(progress_pct / 100)

    # Tabs (Defined inside the 'if' to ensure safety)
    tab1, tab2 = st.tabs(["Today's Assignment", "Missed Readings"])

    with tab1:
        today_row = df[df['Date'] == today_str]
        if not today_row.empty:
            passage = today_row.iloc[0]['Passage']
            if today_row.iloc[0]['Status'] == 'Read':
                st.success(f"✅ Finished: {passage}")
            else:
                st.info(f"📖 **Today:** {passage}")
                if st.button("Mark Today as Finished", key="daily_btn"):
                    df.loc[df['Date'] == today_str, 'Status'] = 'Read'
                    df.to_csv(FILENAME, index=False)
                    sync_weekly_progress(df) # Syncs to weekly file
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.warning("No assignment found for today. Check your CSV dates.")

    with tab2:
        missed = df[(df['Date'] < today_str) & (df['Status'] == 'Pending')]
        if not missed.empty:
            st.warning(f"You have {len(missed)} missed readings.")
            edited = st.data_editor(missed[['Day', 'Date', 'Passage', 'Status']],
                                    disabled=["Day", "Date", "Passage"], hide_index=True)
            if st.button("Save Catch-up Changes"):
                for idx, row in edited.iterrows():
                    df.loc[df['Day'] == row['Day'], 'Status'] = row['Status']
                df.to_csv(FILENAME, index=False)
                sync_weekly_progress(df)
                st.cache_data.clear()
                st.rerun()
        else:
            st.success("You're all caught up!")

    with st.expander("View Full 365-Day Plan"):
        st.dataframe(df, use_container_width=True, hide_index=True)