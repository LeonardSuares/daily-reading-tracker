import pandas as pd
import datetime


def generate_bible_csv():
    # 1. THE DATA SOURCE (Ignatius RSV-2CE)
    bible_data = {
        "Genesis": 50, "Exodus": 40, "Leviticus": 27, "Numbers": 36, "Deuteronomy": 34,
        "Joshua": 24, "Judges": 21, "Ruth": 4, "1 Samuel": 31, "2 Samuel": 24,
        "1 Kings": 22, "2 Kings": 25, "1 Chronicles": 29, "2 Chronicles": 36,
        "Ezra": 10, "Nehemiah": 13, "Tobit": 14, "Judith": 16, "Esther": 10,
        "1 Maccabees": 16, "2 Maccabees": 15, "Job": 42, "Psalms": 150, "Proverbs": 31,
        "Ecclesiastes": 12, "Song of Solomon": 8, "Wisdom": 19, "Sirach": 51,
        "Isaiah": 66, "Jeremiah": 52, "Lamentations": 5, "Baruch": 6, "Ezekiel": 48,
        "Daniel": 14, "Hosea": 14, "Joel": 3, "Amos": 9, "Obadiah": 1, "Jonah": 4,
        "Micah": 7, "Nahum": 3, "Habakkuk": 3, "Zephaniah": 3, "Haggai": 2,
        "Zechariah": 14, "Malachi": 4, "Matthew": 28, "Mark": 16, "Luke": 24,
        "John": 21, "Acts": 28, "Romans": 16, "1 Corinthians": 16, "2 Corinthians": 13,
        "Galatians": 6, "Ephesians": 6, "Philippians": 4, "Colossians": 4,
        "1 Thessalonians": 5, "2 Thessalonians": 3, "1 Timothy": 6, "2 Timothy": 4,
        "Titus": 3, "Philemon": 1, "Hebrews": 13, "James": 5, "1 Peter": 5,
        "2 Peter": 3, "1 John": 5, "2 John": 1, "3 John": 1, "Jude": 1, "Revelation": 22
    }

    # 2. Create a flat list of every single chapter in order
    all_chapters = []
    for book, chapters in bible_data.items():
        for c in range(1, chapters + 1):
            all_chapters.append(f"{book} {c}")

    # 3. Distribute chapters across 365 days
    # Total chapters (1329) / 365 days ≈ 3.64 chapters per day
    total_chapters = len(all_chapters)
    start_date = datetime.date(2026, 1, 1)
    data = []

    current_ch_idx = 0
    for day_idx in range(365):
        # Calculate how many chapters to read today to stay on pace
        target_ch_idx = int((day_idx + 1) * total_chapters / 365)
        days_chapters = all_chapters[current_ch_idx:target_ch_idx]

        # Format the passage (e.g., "Genesis 1-4")
        if not days_chapters:
            passage = "Reflect/Catch-up"
        elif len(days_chapters) == 1:
            passage = days_chapters[0]
        else:
            book_start = " ".join(days_chapters[0].split()[:-1])
            ch_start = days_chapters[0].split()[-1]
            book_end = " ".join(days_chapters[-1].split()[:-1])
            ch_end = days_chapters[-1].split()[-1]

            if book_start == book_end:
                passage = f"{book_start} {ch_start}-{ch_end}"
            else:
                passage = f"{days_chapters[0]} - {days_chapters[-1]}"

        current_date = start_date + datetime.timedelta(days=day_idx)
        data.append({
            "Day": day_idx + 1,
            "Date": current_date.strftime("%Y-%m-%d"),
            "Passage": passage,
            "Status": "Pending",
            "Notes": ""
        })
        current_ch_idx = target_ch_idx

    # 4. Save the file
    df = pd.DataFrame(data)
    df.to_csv('bible_reading_plan.csv', index=False)
    print("Success! bible_reading_plan.csv now contains the full RSV-2CE schedule.")


if __name__ == "__main__":
    generate_bible_csv()