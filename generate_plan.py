import pandas as pd
import datetime

def generate_bible_csv():
    # Start date for 2026
    start_date = datetime.date(2026, 1, 1)

    # We'll create 365 entries
    data = []

    # Simplified plan logic:
    # This distributes the 1,189 chapters of the Bible across 365 days.
    # Note: For a professional-grade plan, you'd map specific chapters,
    # but this script sets up the structure you need.
    for i in range(365):
        current_date = start_date + datetime.timedelta(days=i)

        # Placeholder for the passage - you can manually tweak specific ranges
        # or use a mapping dictionary for specific books.
        passage = f"Day {i+1} Assignment"

        data.append({
            "Day": i + 1,
            "Date": current_date.strftime("%Y-%m-%d"),
            "Passage": passage,
            "Status": "Pending",
            "Notes": ""
        })

    df = pd.DataFrame(data)
    df.to_csv('bible_reading_plan.csv', index=False)
    print("File 'bible_reading_plan.csv' generated successfully.")

generate_bible_csv()