import streamlit as st

st.set_page_config(page_title="EEG + BRFSS Explorer", layout="wide")

st.title("📊 EEG + BRFSS Data Explorer")
st.markdown("""
Welcome to the **EEG + BRFSS App**, where we explore public health and brain activity data side by side.

This interactive tool lets you:
- 🧠 View EEG summary statistics and visualizations
- 🧍‍♀️ Analyze BRFSS behavioral risk data
- 🔄 Compare and explore shared features across both datasets

Use the sidebar to navigate through each section.
""")

st.info("📌 Use the sidebar to choose EEG, BRFSS, or other pages.")
