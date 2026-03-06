import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# --- CONFIG ---
CANONICAL_FILE = 'bible_canonical_progress.csv'

# 1. INITIALIZE SESSION STATE (Persistence & Celebration)
# Ensuring the app remembers your last selected book after saving
if 'celebrate' not in st.session_state:
    st.session_state.celebrate = False

if 'active_book' not in st.session_state:
    st.session_state.active_book = 'Genesis'


@st.cache_data
def load_canonical_data():
    """Loads the bible progress data and ensures the Pct column exists."""
    if os.path.exists(CANONICAL_FILE):
        df = pd.read_csv(CANONICAL_FILE)
        # Calculate completion percentage for the metrics and audit table
        df['Pct'] = (df['Chapters_Read'] / df['Total_Chapters'] * 100).round(1)
        return df
    return pd.DataFrame()


# --- APP START ---
st.set_page_config(page_title="Canonical Progress", layout="wide")
st.title("📚 Canonical Progress Dashboard")

df_canon = load_canonical_data()

if not df_canon.empty:
    # 2. OVERALL ANALYTICS
    total_ch = df_canon['Total_Chapters'].sum()
    read_ch = df_canon['Chapters_Read'].sum()
    overall_pct = (read_ch / total_ch) * 100

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Bible Completion", f"{overall_pct:.1f}%")
    m2.metric("Chapters Read", f"{read_ch:,} / {total_ch:,}")
    m3.metric("Books Finished", len(df_canon[df_canon['Chapters_Read'] == df_canon['Total_Chapters']]))
    st.progress(overall_pct / 100)

    # 3. THE VISUAL PROGRESS CHART (Relative Sizing)
    # This chart shows book size (volume) rather than a 100% stacked view
    st.subheader("🗺️ Scripture Completion Map (Relative Scale)")

    df_visual = df_canon.copy()
    df_visual['Pending_Chapters'] = df_visual['Total_Chapters'] - df_visual['Chapters_Read']

    # Melt data to "Long" format for Plotly stacking
    df_long = df_visual.melt(
        id_vars=['Book'],
        value_vars=['Chapters_Read', 'Pending_Chapters'],
        var_name='Chapter_Status',
        value_name='Chapter_Count'
    )
    df_long['Chapter_Status'] = df_long['Chapter_Status'].replace({
        'Chapters_Read': 'Completed',
        'Pending_Chapters': 'Pending'
    })

    fig_map = px.bar(
        df_long, x='Book', y='Chapter_Count', color='Chapter_Status',
        color_discrete_map={'Completed': '#28a745', 'Pending': '#e0e0e0'},
        template="plotly_white",
        height=450
    )
    fig_map.update_layout(
        xaxis_tickangle=-45,
        yaxis_title="Total Chapters",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.divider()

    # 4. PERSISTENT INTERACTIVE UPDATE SECTION
    c1, c2 = st.columns([1, 2])

    with c1:
        book_options = list(df_canon['Book'].unique())
        try:
            # Prevents the selector from jumping back to Genesis after a save
            current_index = book_options.index(st.session_state.active_book)
        except ValueError:
            current_index = 0

        selected_book = st.selectbox(
            "Select Book to Update",
            book_options,
            index=current_index
        )
        st.session_state.active_book = selected_book
        book_row = df_canon[df_canon['Book'] == selected_book].iloc[0]

    with c2:
        total_book_ch = int(book_row['Total_Chapters'])
        current_book_ch = int(book_row['Chapters_Read'])

        new_val = st.slider(f"Current Progress for {selected_book}", 0, total_book_ch, current_book_ch)

        if st.button(f"Save {selected_book} Progress", type="primary", use_container_width=True):
            # Daily Timestamp: Refreshes whenever progress is logged
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

            df_canon.loc[df_canon['Book'] == selected_book, 'Chapters_Read'] = new_val
            df_canon.loc[df_canon['Book'] == selected_book, 'Last_Updated'] = timestamp

            df_canon.to_csv(CANONICAL_FILE, index=False)

            # Milestone check for celebratory effects
            if new_val == total_book_ch and current_book_ch < total_book_ch:
                st.session_state.celebrate = True

            st.cache_data.clear()
            st.success(f"Log Updated: {selected_book} at {new_val} chapters.")
            st.rerun()

    # 5. DETAILED DATA AUDIT
    st.divider()
    with st.expander("📂 View Detailed Canonical Audit"):
        st.dataframe(
            df_canon[['Book', 'Chapters_Read', 'Total_Chapters', 'Pct', 'Last_Updated']],
            column_config={
                "Pct": st.column_config.ProgressColumn("Progress", format="%.1f%%", min_value=0, max_value=100)
            },
            use_container_width=True, hide_index=True
        )
else:
    st.error(f"⚠️ {CANONICAL_FILE} not found. Please ensure it is in the project root.")