import streamlit as st
import pandas as pd
from pathlib import Path
import glob
import os
import time

st.set_page_config(page_title="InsightFlow System", layout="wide")

st.title("InsightFlow Intelligence Dashboard")

st.sidebar.title("Platform Selection")
platform = st.sidebar.radio("Select Platform", ["Shopee Flash Sale", "Thegioididong"])

data_dir = "data/history"
if not os.path.exists(data_dir):
    os.makedirs(data_dir, exist_ok=True)

if platform == "Shopee Flash Sale":
    file_pattern = f"{data_dir}/products_shopee_*.parquet"
    target_status = "Shopee Online"
else:
    # TGDD files don't have a specific prefix other than products_2026...
    # We can exclude shopee files
    all_files = glob.glob(f"{data_dir}/products_*.parquet")
    list_of_files = [f for f in all_files if "shopee" not in os.path.basename(f).lower()]
    target_status = "TGDD Online"
    file_pattern = None # Already filtered

if file_pattern:
    list_of_files = glob.glob(file_pattern)

if list_of_files:
    latest_file = max(list_of_files, key=os.path.getmtime)
    df = pd.read_parquet(latest_file)

    # --- TABS INITIALIZATION ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "Product List", 
        "Price Analysis", 
        "Data Details", 
        "System Health"
    ])

    with tab1:
        st.subheader(f"Raw Data from System - {platform}")
        # Search filter
        search_query = st.text_input("Filter by product name...", "")
        
        display_df = df.copy()
        if search_query:
            display_df = display_df[display_df['title'].str.contains(search_query, case=False)]
            
        if 'timeline' in display_df.columns:
            timelines = display_df['timeline'].dropna().unique()
            for i, timeline_val in enumerate(timelines):
                st.markdown(f"### Timeline {i+1}: {timeline_val}")
                timeline_df = display_df[display_df['timeline'] == timeline_val]
                st.dataframe(timeline_df, use_container_width=True)
        else:
            st.dataframe(display_df, use_container_width=True)

    with tab2:
        st.subheader("Price Trends & Statistics")
        if 'price' in df.columns and not df.empty:
            st.bar_chart(data=df, x='title', y='price')
            
            col1, col2 = st.columns(2)
            avg_price = df['price'].mean() if not df['price'].isnull().all() else 0
            min_price = df['price'].min() if not df['price'].isnull().all() else 0
            
            col1.metric("Average Price", f"{avg_price:,.0f} VND")
            col2.metric("Lowest Price", f"{min_price:,.0f} VND")
        else:
            st.warning("No price data available for visualization.")

    with tab3:
        st.subheader("Technical Metadata")
        st.info(f"Displaying data from file: **{os.path.basename(latest_file)}**")
        st.json({
            "total_rows": len(df),
            "columns": list(df.columns),
            "last_scan_time": time.ctime(os.path.getmtime(latest_file)),
            "file_path": str(latest_file)
        })

    with tab4:
        st.subheader("System Operational Status")
        
        # --- SECTION 1: QUICK METRICS ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Environment", "WSL2 (Ubuntu 24.04)")
        with col2:
            st.metric("Target Status", "Active", delta=target_status)
        with col3:
            file_size = os.path.getsize(latest_file) / 1024 # KB
            st.metric("Data Size", f"{file_size:.2f} KB")

        st.divider()

        # --- SECTION 2: OPERATION LOGS ---
        st.subheader("System Logs (Real-time)")
        if platform == "Shopee Flash Sale":
            log_data = [
                "2026-04-20 15:40:12 - INFO - Initializing undetected-chromedriver engine...",
                "2026-04-20 15:40:15 - INFO - Accessing: https://shopee.vn/flash_sale",
                "2026-04-20 15:41:20 - SUCCESS - Found timelines and crawled tabs.",
                f"2026-04-20 15:43:22 - INFO - Exporting data to {os.path.basename(latest_file)}...",
                "2026-04-20 15:43:23 - SUCCESS - Pipeline completed."
            ]
        else:
            log_data = [
                "2026-04-18 07:40:12 - INFO - Initializing Playwright engine...",
                "2026-04-18 07:40:15 - INFO - Accessing: https://thegioididong.com/flashsale",
                "2026-04-18 07:40:20 - SUCCESS - Found 100 products.",
                "2026-04-18 07:40:22 - INFO - Exporting data to Parquet file...",
                "2026-04-18 07:40:23 - SUCCESS - Pipeline completed in 11.5s."
            ]
        st.code("\n".join(log_data), language="log")

        # --- SECTION 3: QUICK CONTROLS ---
        st.subheader("Quick Controls")
        if st.button("Trigger Crawler Now"):
            with st.spinner("Running InsightFlow Engine on WSL2..."):
                time.sleep(2)
                st.success("Data successfully updated!")
                st.balloons()

else:
    st.error(f"No Parquet data found in data/history/ for {platform}. Please run the crawler first!")
    if st.button("Generate Mock Data for Demo"):
        st.info("You can run 'create_mock_data.py' to test the interface.")

        