import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# --- CONFIG & DATA LOADING ---
st.set_page_config(page_title="Bible Tracker 2026", layout="wide")
FILENAME = 'bible_reading_plan.csv'


@st.cache_data
def load_data():
    df = pd.read_csv(FILENAME)
    # Ensure Date is treated as a string for consistent matching
    df['Date'] = df['Date'].astype(str)
    return df


def calculate_streak(df):
    """Calculates the current consecutive days of 'Read' status."""
    # Create a copy to avoid SettingWithCopy warnings
    temp_df = df.copy()
    temp_df['Date_DT'] = pd.to_datetime(temp_df['Date']).dt.date

    # Get only completed days, sorted descending (most recent first)
    completed_days = temp_df[temp_df['Status'] == 'Read'].sort_values('Date_DT', ascending=False)

    if completed_days.empty:
        return 0

    today = datetime.now().date()
    last_read_date = completed_days.iloc[0]['Date_DT']

    # If the last read was before yesterday, the streak is dead
    if last_read_date < (today - timedelta(days=1)):
        return 0

    streak = 0
    current_check_date = last_read_date

    # Iterate through completed days to find the contiguous chain
    for _, row in completed_days.iterrows():
        if row['Date_DT'] == current_check_date:
            streak += 1
            current_check_date -= timedelta(days=1)
        else:
            # We found a gap in the dates
            break

    return streak


# Load the data
df = load_data()
today_str = datetime.now().strftime('%Y-%m-%d')

# --- HEADER SECTION ---
st.title("📖 Personal Bible Reading Tracker")
st.markdown("---")

# --- CALCULATE METRICS ---
completed = len(df[df['Status'] == 'Read'])
total = len(df)
remaining = total - completed
progress_pct = (completed / total) * 100
current_streak = calculate_streak(df)

# --- FEATURE: METRICS DASHBOARD ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Completed Days", f"{completed}")
col2.metric("Remaining", f"{remaining}")
col3.metric("Total Progress", f"{progress_pct:.1f}%")
col4.metric("🔥 Current Streak", f"{current_streak} Days")

st.progress(progress_pct / 100)

# --- READING STATUS TABS ---
st.subheader("🗓️ Reading Status")
tab1, tab2 = st.tabs(["Today's Assignment", "Missed Readings"])

with tab1:
    today_row = df[df['Date'] == today_str]
    if not today_row.empty:
        passage = today_row.iloc[0]['Passage']
        status = today_row.iloc[0]['Status']

        st.info(f"**Today's Reading:** {passage}")
        if status == 'Read':
            st.success("You've already finished today's reading!")
        else:
            if st.button("Mark Today as Finished"):
                df.loc[df['Date'] == today_str, 'Status'] = 'Read'
                df.to_csv(FILENAME, index=False)
                st.cache_data.clear()
                st.rerun()
    else:
        st.warning("No reading found for today. (Check if your CSV is set for 2026 dates)")

with tab2:
    # Find Pending entries in the past
    missed_readings = df[(df['Date'] < today_str) & (df['Status'] == 'Pending')]

    if not missed_readings.empty:
        st.warning(f"You have {len(missed_readings)} missed sessions.")
        edited_df = st.data_editor(missed_readings[['Day', 'Date', 'Passage', 'Status']],
                                   disabled=["Day", "Date", "Passage"],
                                   key="missed_editor",
                                   hide_index=True)

        if st.button("Save Catch-up Changes"):
            # Update original df with changes from the editor
            for index, row in edited_df.iterrows():
                actual_idx = df[df['Day'] == row['Day']].index
                df.loc[actual_idx, 'Status'] = row['Status']

            df.to_csv(FILENAME, index=False)
            st.cache_data.clear()
            st.rerun()
    else:
        st.success("You are fully caught up!")

# --- FULL DATA VIEW ---
with st.expander("View Full 365-Day Plan"):
    st.dataframe(df, use_container_width=True, hide_index=True)