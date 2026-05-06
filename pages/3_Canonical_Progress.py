import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# --- 1. CONFIG (Defined at the top to avoid NameErrors) ---
CANONICAL_FILE = 'bible_canonical_progress.csv'

# --- 2. INITIALIZATION LOGIC ---
def initialize_rsv2ce_csv():
    """Creates the CSV file with the 73 books of the Ignatius RSV-2CE Bible."""
    rsv2ce_data = [
        {"Book": "Genesis", "Total_Chapters": 50}, {"Book": "Exodus", "Total_Chapters": 40},
        {"Book": "Leviticus", "Total_Chapters": 27}, {"Book": "Numbers", "Total_Chapters": 36},
        {"Book": "Deuteronomy", "Total_Chapters": 34}, {"Book": "Joshua", "Total_Chapters": 24},
        {"Book": "Judges", "Total_Chapters": 21}, {"Book": "Ruth", "Total_Chapters": 4},
        {"Book": "1 Samuel", "Total_Chapters": 31}, {"Book": "2 Samuel", "Total_Chapters": 24},
        {"Book": "1 Kings", "Total_Chapters": 22}, {"Book": "2 Kings", "Total_Chapters": 25},
        {"Book": "1 Chronicles", "Total_Chapters": 29}, {"Book": "2 Chronicles", "Total_Chapters": 36},
        {"Book": "Ezra", "Total_Chapters": 10}, {"Book": "Nehemiah", "Total_Chapters": 13},
        {"Book": "Tobit", "Total_Chapters": 14}, {"Book": "Judith", "Total_Chapters": 16},
        {"Book": "Esther", "Total_Chapters": 10}, {"Book": "1 Maccabees", "Total_Chapters": 16},
        {"Book": "2 Maccabees", "Total_Chapters": 15}, {"Book": "Job", "Total_Chapters": 42},
        {"Book": "Psalms", "Total_Chapters": 150}, {"Book": "Proverbs", "Total_Chapters": 31},
        {"Book": "Ecclesiastes", "Total_Chapters": 12}, {"Book": "Song of Solomon", "Total_Chapters": 8},
        {"Book": "Wisdom", "Total_Chapters": 19}, {"Book": "Sirach", "Total_Chapters": 51},
        {"Book": "Isaiah", "Total_Chapters": 66}, {"Book": "Jeremiah", "Total_Chapters": 52},
        {"Book": "Lamentations", "Total_Chapters": 5}, {"Book": "Baruch", "Total_Chapters": 6},
        {"Book": "Ezekiel", "Total_Chapters": 48}, {"Book": "Daniel", "Total_Chapters": 14},
        {"Book": "Hosea", "Total_Chapters": 14}, {"Book": "Joel", "Total_Chapters": 3},
        {"Book": "Amos", "Total_Chapters": 9}, {"Book": "Obadiah", "Total_Chapters": 1},
        {"Book": "Jonah", "Total_Chapters": 4}, {"Book": "Micah", "Total_Chapters": 7},
        {"Book": "Nahum", "Total_Chapters": 3}, {"Book": "Habakkuk", "Total_Chapters": 3},
        {"Book": "Zephaniah", "Total_Chapters": 3}, {"Book": "Haggai", "Total_Chapters": 2},
        {"Book": "Zechariah", "Total_Chapters": 14}, {"Book": "Malachi", "Total_Chapters": 4},
        {"Book": "Matthew", "Total_Chapters": 28}, {"Book": "Mark", "Total_Chapters": 16},
        {"Book": "Luke", "Total_Chapters": 24}, {"Book": "John", "Total_Chapters": 21},
        {"Book": "Acts", "Total_Chapters": 28}, {"Book": "Romans", "Total_Chapters": 16},
        {"Book": "1 Corinthians", "Total_Chapters": 16}, {"Book": "2 Corinthians", "Total_Chapters": 13},
        {"Book": "Galatians", "Total_Chapters": 6}, {"Book": "Ephesians", "Total_Chapters": 6},
        {"Book": "Philippians", "Total_Chapters": 4}, {"Book": "Colossians", "Total_Chapters": 4},
        {"Book": "1 Thessalonians", "Total_Chapters": 5}, {"Book": "2 Thessalonians", "Total_Chapters": 3},
        {"Book": "1 Timothy", "Total_Chapters": 6}, {"Book": "2 Timothy", "Total_Chapters": 4},
        {"Book": "Titus", "Total_Chapters": 3}, {"Book": "Philemon", "Total_Chapters": 1},
        {"Book": "Hebrews", "Total_Chapters": 13}, {"Book": "James", "Total_Chapters": 5},
        {"Book": "1 Peter", "Total_Chapters": 5}, {"Book": "2 Peter", "Total_Chapters": 3},
        {"Book": "1 John", "Total_Chapters": 5}, {"Book": "2 John", "Total_Chapters": 1},
        {"Book": "3 John", "Total_Chapters": 1}, {"Book": "Jude", "Total_Chapters": 1},
        {"Book": "Revelation", "Total_Chapters": 22}
    ]
    df = pd.DataFrame(rsv2ce_data)
    df['Chapters_Read'] = 0
    df['Last_Updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    df.to_csv(CANONICAL_FILE, index=False)
    st.success("CSV initialized with RSV-2CE Books!")

# --- 3. TRIGGER INITIALIZATION ---
# Uncomment the line below to reset your data to the 73-book RSV-2CE version
# initialize_rsv2ce_csv()
# --- 3. TRIGGER INITIALIZATION (SAFE VERSION) ---
if not os.path.exists(CANONICAL_FILE):
    initialize_rsv2ce_csv()

# --- 4. SESSION STATE ---
if 'celebrate' not in st.session_state:
    st.session_state.celebrate = False

if 'active_book' not in st.session_state:
    st.session_state.active_book = 'Genesis'

@st.cache_data
def load_canonical_data():
    """Loads the bible progress data and ensures the Pct column exists."""
    if os.path.exists(CANONICAL_FILE):
        df = pd.read_csv(CANONICAL_FILE)
        df['Pct'] = (df['Chapters_Read'] / df['Total_Chapters'] * 100).round(1)
        return df
    return pd.DataFrame()

# --- 5. APP START ---
st.set_page_config(page_title="Canonical Progress", layout="wide")

# Check if we should celebrate a book completion
if st.session_state.celebrate:
    st.balloons()
    st.session_state.celebrate = False

st.title("📚 Canonical Progress Dashboard")

df_canon = load_canonical_data()

if not df_canon.empty:
    # --- ANALYTICS ---
    total_ch = df_canon['Total_Chapters'].sum()
    read_ch = df_canon['Chapters_Read'].sum()
    overall_pct = (read_ch / total_ch) * 100

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Bible Completion", f"{overall_pct:.1f}%")
    m2.metric("Chapters Read", f"{read_ch:,} / {total_ch:,}")
    m3.metric("Books Finished", len(df_canon[df_canon['Chapters_Read'] == df_canon['Total_Chapters']]))
    st.progress(overall_pct / 100)

    # --- VISUAL CHART ---
    st.subheader("🗺️ Scripture Completion Map (Relative Scale)")
    df_visual = df_canon.copy()
    df_visual['Pending_Chapters'] = df_visual['Total_Chapters'] - df_visual['Chapters_Read']
    df_long = df_visual.melt(
        id_vars=['Book'],
        value_vars=['Chapters_Read', 'Pending_Chapters'],
        var_name='Chapter_Status',
        value_name='Chapter_Count'
    )
    df_long['Chapter_Status'] = df_long['Chapter_Status'].replace({'Chapters_Read': 'Completed', 'Pending_Chapters': 'Pending'})

    fig_map = px.bar(
        df_long, x='Book', y='Chapter_Count', color='Chapter_Status',
        color_discrete_map={'Completed': '#28a745', 'Pending': '#e0e0e0'},
        template="plotly_white", height=450
    )
    fig_map.update_layout(xaxis_tickangle=-45, yaxis_title="Total Chapters")
    st.plotly_chart(fig_map, use_container_width=True)

    st.divider()

    # --- UPDATE SECTION ---
    c1, c2 = st.columns([1, 2])
    with c1:
        book_options = list(df_canon['Book'].unique())
        try:
            current_index = book_options.index(st.session_state.active_book)
        except ValueError:
            current_index = 0

        selected_book = st.selectbox("Select Book to Update", book_options, index=current_index)
        st.session_state.active_book = selected_book
        book_row = df_canon[df_canon['Book'] == selected_book].iloc[0]

    with c2:
        total_book_ch = int(book_row['Total_Chapters'])
        current_book_ch = int(book_row['Chapters_Read'])
        new_val = st.slider(f"Current Progress for {selected_book}", 0, total_book_ch, current_book_ch)

        if st.button(f"Save {selected_book} Progress", type="primary", use_container_width=True):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            df_canon.loc[df_canon['Book'] == selected_book, 'Chapters_Read'] = new_val
            df_canon.loc[df_canon['Book'] == selected_book, 'Last_Updated'] = timestamp
            df_canon.to_csv(CANONICAL_FILE, index=False)

            if new_val == total_book_ch and current_book_ch < total_book_ch:
                st.session_state.celebrate = True

            st.cache_data.clear()
            st.rerun()

    # --- AUDIT TABLE ---
    st.divider()
    with st.expander("📂 View Detailed Canonical Audit."):
        st.dataframe(
            df_canon[['Book', 'Chapters_Read', 'Total_Chapters', 'Pct', 'Last_Updated']],
            column_config={"Pct": st.column_config.ProgressColumn("Progress", format="%.1f%%", min_value=0, max_value=100)},
            use_container_width=True, hide_index=True
        )
else:
    st.error(f"⚠️ {CANONICAL_FILE} not found. Please ensure it is in the project root.")