import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Daily Reading Tracker", layout="wide", page_icon="📖")

# 2. Pathing & Sync Logic
FILENAME = 'bible_reading_plan.csv'
# Using os.path.join for robust cross-platform pathing
WEEKLY_FILE = os.path.join('data', 'user_progress.csv')


def sync_weekly_progress(daily_df):
    """Updates weekly progress based on completed 7-day blocks."""
    if os.path.exists(WEEKLY_FILE):
        weekly_df = pd.read_csv(WEEKLY_FILE)
        # Calculate which week each day belongs to
        daily_df['Day_Group'] = (daily_df['Day'] - 1) // 7 + 1

        for week_num in weekly_df['Week']:
            days_in_week = daily_df[daily_df['Day_Group'] == week_num]
            if not days_in_week.empty and (days_in_week['Status'] == 'Read').all():
                weekly_df.loc[weekly_df['Week'] == week_num, 'Completed'] = True

        weekly_df.to_csv(WEEKLY_FILE, index=False)


@st.cache_data
def load_data():
    if os.path.exists(FILENAME):
        data = pd.read_csv(FILENAME)
        data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%Y-%m-%d')
        return data
    return pd.DataFrame()


def calculate_streak(df):
    """Calculates consecutive days read ending yesterday or today."""
    temp_df = df.copy()
    temp_df['Date_DT'] = pd.to_datetime(temp_df['Date']).dt.date
    completed_days = set(temp_df[temp_df['Status'] == 'Read']['Date_DT'])

    if not completed_days: return 0

    today = datetime.now().date()
    streak = 0
    curr = today

    # If not read today, check if streak ended yesterday
    if curr not in completed_days:
        curr -= timedelta(days=1)

    while curr in completed_days:
        streak += 1
        curr -= timedelta(days=1)
    return streak


# --- UI EXECUTION ---
df = load_data()
today_str = datetime.now().strftime('%Y-%m-%d')

if df.empty:
    st.error(f"⚠️ {FILENAME} not found. Please ensure it is in the project root.")
else:
    st.title("📖 Daily Scripture Tracker")

    # 3. TOP KPI ROW
    completed = len(df[df['Status'] == 'Read'])
    total = len(df)
    progress_pct = (completed / total) * 100
    current_streak = calculate_streak(df)

    # Calculate if you are ahead or behind schedule
    days_passed = (datetime.now() - pd.to_datetime(df['Date'].min())).days + 1
    pace_diff = completed - days_passed

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Completed Days", completed)
    m2.metric("Streak", f"{current_streak} Days", "🔥")
    m3.metric("Annual Progress", f"{progress_pct:.1f}%")
    m4.metric("Pace vs. Calendar", f"{pace_diff} Days", delta_color="normal")

    st.progress(progress_pct / 100)
    st.divider()

    # 4. ACTION TABS
    tab1, tab2, tab3 = st.tabs(["🎯 Today's Task", "⚠️ Catch-up", "📊 Full Schedule"])

    with tab1:
        today_row = df[df['Date'] == today_str]
        if not today_row.empty:
            passage = today_row.iloc[0]['Passage']
            status = today_row.iloc[0]['Status']

            st.subheader(f"Assignment for {datetime.now().strftime('%A, %b %d')}")

            if status == 'Read':
                st.success(f"### ✅ Well done! You finished: **{passage}**")
            else:
                st.info(f"### 📖 Reading: **{passage}**")
                if st.button("Mark as Complete", use_container_width=True):
                    df.loc[df['Date'] == today_str, 'Status'] = 'Read'
                    df.to_csv(FILENAME, index=False)
                    sync_weekly_progress(df)
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.warning("No specific assignment found for today's date in the CSV.")

    with tab2:
        missed = df[(df['Date'] < today_str) & (df['Status'] == 'Pending')]
        if not missed.empty:
            st.warning(f"Attention: {len(missed)} readings require catch-up.")
            # Data editor for quick status updates
            edited_df = st.data_editor(
                missed[['Day', 'Date', 'Passage', 'Status']],
                hide_index=True,
                disabled=['Day', 'Date', 'Passage'],
                use_container_width=True
            )
            if st.button("Update Catch-up Progress"):
                # Apply changes back to main df
                for _, row in edited_df.iterrows():
                    df.loc[df['Day'] == row['Day'], 'Status'] = row['Status']
                df.to_csv(FILENAME, index=False)
                sync_weekly_progress(df)
                st.cache_data.clear()
                st.rerun()
        else:
            st.balloons()
            st.success("Perfect Consistency! You are fully caught up with the 2026 plan.")

    with tab3:
        st.subheader("2026 Master Reading Plan")
        # Color coding the status for the big table
        st.dataframe(
            df[['Day', 'Date', 'Passage', 'Status']].style.applymap(
                lambda x: 'color: green' if x == 'Read' else 'color: red', subset=['Status']
            ),
            use_container_width=True,
            hide_index=True
        )