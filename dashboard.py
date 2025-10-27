import streamlit as st
import pandas as pd
from utils import read_from_sheet
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="Tax Consulting SA Brand Tracker", page_icon="📊", layout="wide")

st.title("📊 Tax Consulting South Africa Brand Mention Dashboard")
st.markdown("Track visibility on ChatGPT and Google SGE. Data from 'Tax_Tracker' Sheet.")

# Sidebar for tab selection
sheet_tab = st.sidebar.selectbox("Select Sheet Tab:", ["ChatGPT", "SGE", "Summaries"])

# Load data
@st.cache_data(ttl=300)  # Cache for 5 min
def load_data(tab):
    return read_from_sheet(tab)

df = load_data(sheet_tab)

if df.empty:
    st.error(f"No data found in '{sheet_tab}' tab. Run the bots first!")
else:
    # Metrics (if applicable)
    if 'Mention' in df.columns:
        mention_rate = (df['Mention'] == 'Yes').mean() * 100
        avg_score = df['Visibility Score'].mean() if 'Visibility Score' in df.columns else 0
        st.sidebar.metric("Mention Rate (%)", f"{mention_rate:.1f}")
        st.sidebar.metric("Avg Visibility Score", f"{avg_score:.1f}")

    # Display table
    st.subheader(f"Data from '{sheet_tab}' Tab")
    st.dataframe(df, use_container_width=True, height=400)

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        if 'Mention' in df.columns:
            st.subheader("Mention Distribution")
            mention_counts = df['Mention'].value_counts()
            st.bar_chart(mention_counts)

    with col2:
        if 'Visibility Score' in df.columns:
            st.subheader("Visibility Scores Over Time")
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            df_sorted = df.sort_values('Timestamp')
            st.line_chart(df_sorted.set_index('Timestamp')['Visibility Score'])

    # Filter by date
    if 'Timestamp' in df.columns:
        st.subheader("Filter by Date")
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        min_date, max_date = df['Timestamp'].min(), df['Timestamp'].max()
        date_range = st.date_input("Select Date Range", [min_date.date(), max_date.date()])
        filtered_df = df[(df['Timestamp'].dt.date >= date_range[0]) & (df['Timestamp'].dt.date <= date_range[1])]
        st.dataframe(filtered_df)

    # Download CSV
    csv = df.to_csv(index=False)
    st.download_button("Download Data as CSV", csv, f"{sheet_tab}_data.csv", "text/csv")

# Footer
st.markdown("---")
st.markdown("Run bots daily for fresh data. Built with Streamlit.")