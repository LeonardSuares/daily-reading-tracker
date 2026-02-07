import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIG ---
CANONICAL_FILE = 'bible_canonical_progress.csv'
SESSION_FILE = 'last_session.csv'


def load_canonical_data():
    """Loads progress data or initializes a new Bible structure."""
    if os.path.exists(CANONICAL_FILE) and os.path.getsize(CANONICAL_FILE) > 0:
        df = pd.read_csv(CANONICAL_FILE)
        # Ensure the Last_Updated column exists in older files
        if 'Last_Updated' not in df.columns:
            df['Last_Updated'] = "Never"
        return df

    # Initialize full Bible structure
    data = {
        'Book': [
            'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy',
            'Joshua', 'Judges', 'Ruth', '1 Samuel', '2 Samuel',
            '1 Kings', '2 Kings', '1 Chronicles', '2 Chronicles', 'Ezra',
            'Nehemiah', 'Esther', 'Job', 'Psalms', 'Proverbs',
            'Ecclesiastes', 'Song of Solomon', 'Isaiah', 'Jeremiah', 'Lamentations',
            'Ezekiel', 'Daniel', 'Hosea', 'Joel', 'Amos',
            'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk',
            'Zephaniah', 'Haggai', 'Zechariah', 'Malachi', 'Matthew',
            'Mark', 'Luke', 'John', 'Acts', 'Romans',
            '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians', 'Philippians',
            'Colossians', '1 Thessalonians', '2 Thessalonians', '1 Timothy', '2 Timothy',
            'Titus', 'Philemon', 'Hebrews', 'James', '1 Peter',
            '2 Peter', '1 John', '2 John', '3 John', 'Jude', 'Revelation'
        ],
        'Total_Chapters': [
            50, 40, 27, 36, 34, 24, 21, 4, 31, 24,
            22, 25, 29, 36, 10, 13, 10, 42, 150, 31,
            12, 8, 66, 52, 5, 48, 12, 14, 3, 9,
            1, 4, 7, 3, 3, 3, 2, 14, 4, 28,
            16, 24, 21, 28, 16, 16, 13, 6, 6, 4,
            4, 5, 3, 6, 4, 3, 1, 13, 5, 5,
            3, 5, 1, 1, 1, 22
        ],
        'Chapters_Read': [0] * 66,
        'Last_Updated': ["Never"] * 66
    }
    df = pd.DataFrame(data)
    df.to_csv(CANONICAL_FILE, index=False)
    return df


def get_last_session():
    """Retrieves the last book and chapter modified from disk."""
    if os.path.exists(SESSION_FILE):
        return pd.read_csv(SESSION_FILE).iloc[0].to_dict()
    return {'Book': 'Genesis', 'Chapter': 0}


def save_session(book, chapter):
    """Saves current state to disk to persist across app restarts."""
    pd.DataFrame([{'Book': book, 'Chapter': chapter}]).to_csv(SESSION_FILE, index=False)


# --- APP START ---
st.set_page_config(page_title="Bible Tracker", layout="wide")
st.title("📚 Bible Progress Tracker")

df_canon = load_canonical_data()
last_session_data = get_last_session()

# Initialize Session State for the active book if not already set
if 'active_book' not in st.session_state:
    st.session_state.active_book = last_session_data['Book']

# --- OVERALL PROGRESS METRICS ---
total_chapters_bible = df_canon['Total_Chapters'].sum()
read_chapters_bible = df_canon['Chapters_Read'].sum()
overall_pct = (read_chapters_bible / total_chapters_bible) * 100

m_col1, m_col2 = st.columns(2)
m_col1.metric("Overall Completion", f"{overall_pct:.1f}%")
m_col2.metric("Chapters Read", f"{read_chapters_bible} / {total_chapters_bible}")
st.progress(overall_pct / 100)

st.markdown("---")

# --- INTERACTIVE UPDATE SECTION ---
col1, col2 = st.columns([1, 2])

with col1:
    book_list = list(df_canon['Book'].unique())
    try:
        # Find index of current active book to keep the selectbox stable
        default_index = book_list.index(st.session_state.active_book)
    except ValueError:
        default_index = 0

    selected_book = st.selectbox(
        "Choose a Book",
        book_list,
        index=default_index,
        key="book_picker"
    )

    # Sync internal state with widget selection
    st.session_state.active_book = selected_book

with col2:
    book_row = df_canon[df_canon['Book'] == selected_book].iloc[0]
    current_chapters = int(book_row['Chapters_Read'])
    total_chapters = int(book_row['Total_Chapters'])

    # Set slider start value: use session file value ONLY if the book matches
    # Otherwise, use the actual read count from the main dataframe
    if selected_book == last_session_data['Book']:
        slider_start = last_session_data['Chapter']
    else:
        slider_start = current_chapters

    new_val = st.slider(f"Progress for {selected_book}", 0, total_chapters, slider_start)

    if st.button(f"Save Progress for {selected_book}", type="primary"):
        # 1. Update Main Dataframe
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        df_canon.loc[df_canon['Book'] == selected_book, 'Chapters_Read'] = new_val
        df_canon.loc[df_canon['Book'] == selected_book, 'Last_Updated'] = timestamp
        df_canon.to_csv(CANONICAL_FILE, index=False)

        # 2. Update Persistence File
        save_session(selected_book, new_val)

        # 3. Success Feedback & Refresh
        st.success(f"Successfully updated {selected_book} to {new_val} chapters!")
        st.rerun()

# --- DATA SUMMARY TABLE ---
st.markdown("---")
st.subheader("Detailed Progress")

# Add percentage column for the table view
df_canon['Completion %'] = (df_canon['Chapters_Read'] / df_canon['Total_Chapters'] * 100).round(1)

# We removed the 'df_sorted' line to keep your original Bible order!
st.dataframe(
    df_canon[['Book', 'Chapters_Read', 'Total_Chapters', 'Completion %', 'Last_Updated']],
    hide_index=True,
    use_container_width=True
)