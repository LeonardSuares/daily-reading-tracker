import streamlit as st
import pandas as pd
import os

# --- CONFIG ---
CANONICAL_FILE = 'bible_canonical_progress.csv'
SESSION_FILE = 'last_session.csv'  # NEW: Tracks the last book/chapter viewed

def load_canonical_data():
    # Check if file exists AND is not empty (size > 0 bytes)
    if os.path.exists(CANONICAL_FILE) and os.path.getsize(CANONICAL_FILE) > 0:
        try:
            return pd.read_csv(CANONICAL_FILE)
        except pd.errors.EmptyDataError:
            # This is a fallback in case getsize failed us
            st.warning("Found an empty file. Re-initializing...")
            pass

    # If we are here, the file is either missing or empty
    # Let's initialize the full Bible structure (all 66 books)
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
        'Chapters_Read': [0] * 66
    }
    df = pd.DataFrame(data)
    df.to_csv(CANONICAL_FILE, index=False)
    return df

def get_last_session():
    """Retrieves the last book and chapter modified."""
    if os.path.exists(SESSION_FILE):
        return pd.read_csv(SESSION_FILE).iloc[0].to_dict()
    # Default to Genesis if no session exists
    return {'Book': 'Genesis', 'Chapter': 0}

def save_session(book, chapter):
    """Saves the current book and chapter to persist on restart."""
    pd.DataFrame([{'Book': book, 'Chapter': chapter}]).to_csv(SESSION_FILE, index=False)

st.title("📚 Bible Progress")
df_canon = load_canonical_data()
last_session = get_last_session() # Load the 'Memory'

# --- OVERALL PROGRESS ---
total_chapters_bible = df_canon['Total_Chapters'].sum()
read_chapters_bible = df_canon['Chapters_Read'].sum()
overall_pct = (read_chapters_bible / total_chapters_bible) * 100

st.metric("Total Bible Completion", f"{overall_pct:.1f}%", f"{read_chapters_bible}/{total_chapters_bible} Chapters")
st.progress(overall_pct / 100)

st.markdown("---")

# --- INTERACTIVE CHECKLIST ---

# Initialize session state if it doesn't exist
if 'active_book' not in st.session_state:
    st.session_state.active_book = last_session['Book']

col1, col2 = st.columns([1, 2])

with col1:
    book_list = list(df_canon['Book'].unique())
    try:
        # We find the index based on what is CURRENTLY in session_state
        default_index = book_list.index(st.session_state.active_book)
    except ValueError:
        default_index = 0

    # Every time this changes, it updates st.session_state.active_book
    selected_book = st.selectbox(
        "Select a Book to Update",
        book_list,
        index=default_index,
        key="book_selector"  # Adding a key helps Streamlit track this specific widget
    )

    # Update our state tracker
    st.session_state.active_book = selected_book

with col2:
    book_data = df_canon[df_canon['Book'] == selected_book].iloc[0]
    current_read = int(book_data['Chapters_Read'])
    total_chaps = int(book_data['Total_Chapters'])

    # Logic: Only use the session file's chapter if it matches the currently viewed book
    if selected_book == last_session['Book']:
        start_val = last_session['Chapter']
    else:
        start_val = current_read

    new_read_count = st.slider(f"Chapters finished in {selected_book}", 0, total_chaps, start_val)

    if st.button(f"Update {selected_book}"):
        df_canon.loc[df_canon['Book'] == selected_book, 'Chapters_Read'] = new_read_count
        df_canon.to_csv(CANONICAL_FILE, index=False)

        # Update the file so it survives a full app restart/refresh
        save_session(selected_book, new_read_count)

        # Update the session state so it survives navigation
        st.session_state.active_book = selected_book

        st.success(f"Updated {selected_book}: {new_read_count}/{total_chaps}")
        st.rerun()

# --- VISUAL SUMMARY ---
st.subheader("Progress by Book")
df_canon['Pct'] = (df_canon['Chapters_Read'] / df_canon['Total_Chapters']) * 100
st.dataframe(df_canon[['Book', 'Chapters_Read', 'Total_Chapters', 'Pct']],
             hide_index=True, use_container_width=True)