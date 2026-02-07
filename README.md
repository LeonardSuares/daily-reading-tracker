# 📈 Daily Reading Tracker

**Live Application:** [View on Streamlit Cloud](https://daily-reading-tracker-fzdldtbjb6ybskw6rjdhdm.streamlit.app/)

## 📖 Project Overview
A utility-focused application built to transform personal habits into quantifiable data. This project serves as a comprehensive reading tracker using Python, Pandas, and Streamlit, emphasizing data persistence, logic-based tracking, and specialized data serialization.

Standard reading plans are often passive. This solution provides a two-tier tracking system—daily and weekly—to create an active engagement loop with personal reading goals.

---

## 🛠️ Technical Highlights

### Data Persistence
Managed via a **CRUD-capable CSV backend**, ensuring that all progress is saved locally or in the cloud without the need for a complex SQL setup. This highlights efficient data handling and file I/O operations.

### Logic-Based Streaks
Implemented a **"Gaps and Islands" algorithm** to calculate contiguous reading chains.
* **Automatic Reset:** The streak resets automatically if a 24-hour window is missed.
* **Algorithmic Complexity:** Leverages Pandas indexing to identify islands of activity within a sea of missing entries.

### Dashboarding & Visualization
Integrated **Matplotlib** and **Streamlit** to provide real-time visual feedback:
* **Progress Tracking:** Interactive progress bars for individual books and overall completion.
* **Catch-up Analysis:** Data-driven insights to help users identify how many chapters are needed to return to a specific goal.

---

## 📂 Project Structure
```text
Daily-Reading-Tracker/
├── bible_canonical_progress.csv  # Main database for reading logs
├── last_session.csv              # Session persistence metadata
├── main.py                       # Streamlit application logic
└── requirements.txt               # Dependencies (Pandas, Streamlit, etc.)

```
## 📄 License
This project is licensed under the **MIT License**. This means you are free to use, modify, and distribute the code, provided that the original copyright notice and permission notice are included. See the `LICENSE` file for more details.
