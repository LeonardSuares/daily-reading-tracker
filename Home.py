import streamlit as st

st.set_page_config(
    page_title="2026 Reading Tracker",
    page_icon="📖",
    layout="wide"
)

st.title("🛡️ The 2026 Scripture Command Center")
st.markdown("---")

st.markdown("""
### Welcome to your Personal Bible Progress Suite.
Use the sidebar on the left to navigate between your tracking resolutions:

1. **Daily Tracker:** High-resolution monitoring of your 365-day plan.
2. **Weekly Tracker:** Strategic 52-week overview with burndown analytics.

**Stay focused. Maintain the streak. Finish the year.**
""")

# Quick Stats Overview could go here if you wanted to aggregate data from both CSVs