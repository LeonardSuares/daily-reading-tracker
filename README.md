# 📈 Daily Reading Tracker

**Live Application:** [View on Streamlit Cloud](https://daily-reading-tracker-fzdldtbjb6ybskw6rjdhdm.streamlit.app/)

## 📖 Project Overview
The **2026 Scripture Command Center** is a high-resolution operational dashboard built to transform personal habits into quantifiable data. This project synthesizes **Python, Pandas, and Plotly** to provide a three-tier tracking system—daily, weekly, and canonical—to maintain an active engagement loop with 365-day spiritual discipline goals.

---

## 🚀 Key Features

* **Dynamic KPI Dashboard:** Real-time calculation of current streaks, annual completion percentages, and daily velocity (chapters/day).
* **Predictive Forecasting:** A custom **Velocity Engine** that applies historical reading behavior to project a "Projected Finish Date".
* **Weekly Burndown Analytics:** Interactive Plotly visualizations comparing **Ideal vs. Actual** pace with dynamic time-based targets.
* **Canonical Heatmapping:** A relative-scale bar chart identifying volume-based progress across all 66 books, highlighting reading gaps by actual volume (total chapters).
* **Relational Data Sync:** Automated logic that propagates daily progress into weekly milestones to ensure cross-module data integrity.
* **Stateful Persistence:** Implementation of **Streamlit Session State** to maintain user context (e.g., active book selection) across app reruns.

---

## 🛠️ Technical Highlights

### 📈 Analytics & Modeling
* **Gaps and Islands Logic:** Developed a custom algorithm to calculate contiguous reading chains, ensuring streak accuracy.
* **Vectorized Processing:** Optimized data calculations using Pandas `.cumsum()` and `.melt()` for instantaneous UI response times.

### 🔄 State Management
* **Selection Persistence:** Engineered a "Persistence Engine" to solve the "Genesis Revert" issue, ensuring user selection remains stable during data writes.
* **Daily Timestamps:** Automated record-keeping that logs activity timestamps on a per-interaction basis.

### 🎨 Advanced Visualization
* **Event-Driven UX:** Integrated celebratory firecracker animations using `streamlit-extras` to provide visual reinforcement for habit completion.
* **Relative Scale Mapping:** Designed a scripture map that scales by volume, providing a true representation of workload (e.g., Psalms vs. Obadiah).

---

## 📂 Project Structure
```text
Daily-Reading-Tracker/
├── Home.py                       # Executive Dashboard & Predictive KPIs
├── bible_reading_plan.csv         # Master Daily Source-of-Truth
├── user_progress.csv              # Weekly Analytics Database
├── last_session.csv               # Session Persistence Metadata
├── requirements.txt               # Dependencies (Pandas, Plotly, Streamlit-Extras)
└── pages/                         # Specialized Analytical Modules
    ├── 1_Daily_Tracker.py         # Logging & Catch-up Engine
    ├── 2_Weekly_Tracker.py        # Burndown & Pace Analysis
    └── 3_Canonical_Progress.py    # Volume-Based Heatmap
