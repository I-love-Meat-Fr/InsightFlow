import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Shopee Flash Sale", page_icon="🛍️", layout="wide")

st.title("🛍️ Shopee Flash Sale Analytics")
st.markdown("This dashboard displays data automatically extracted from the latest Shopee Flash Sale crawl.")

data_file = "shopee_auto_extracted.json"

if not os.path.exists(data_file):
    st.error(f"Could not find `{data_file}`. Please run the `insightflow shopee-crawl` command first to generate data.")
else:
    # Load data
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    if not data:
        st.warning("The data file is empty. The crawler might have been blocked or found no items.")
    else:
        df = pd.DataFrame(data)
        
        # --- TOP LEVEL METRICS ---
        st.subheader("Flash Sale Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Products", len(df))
        with col2:
            avg_discount = df['discount_percent'].mean() if 'discount_percent' in df else 0
            st.metric("Average Discount", f"{avg_discount:.1f}%")
        with col3:
            avg_price = df['price'].mean() if 'price' in df else 0
            st.metric("Average Price", f"{avg_price:,.0f} VND")
            
        st.divider()
        
        # --- VISUALIZATIONS ---
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Price vs Discount Distribution")
            if 'price' in df and 'discount_percent' in df:
                st.scatter_chart(data=df, x='price', y='discount_percent', color='#ff5722')
            else:
                st.info("Insufficient data for chart.")
                
        with col_chart2:
            st.subheader("🔥 Top 5 Biggest Discounts")
            if 'discount_percent' in df:
                top_discounts = df.nlargest(5, 'discount_percent')[['title', 'discount_percent', 'price', 'original_price']]
                # Format prices for display
                top_discounts['price'] = top_discounts['price'].apply(lambda x: f"{x:,.0f} ₫")
                top_discounts['original_price'] = top_discounts['original_price'].apply(lambda x: f"{x:,.0f} ₫")
                st.dataframe(top_discounts, use_container_width=True, hide_index=True)
                
        st.divider()
        
        # --- RAW DATA BROWSER ---
        st.subheader("Browse All Products")
        search_query = st.text_input("🔍 Search products by name...", "")
        
        display_df = df.copy()
        
        # Clean up URL to make it clickable in Streamlit if possible
        if 'url' in display_df:
            # Streamlit dataframes can show URLs natively if configured, 
            # but standard display is also fine.
            pass
            
        if search_query:
            display_df = display_df[display_df['title'].str.contains(search_query, case=False, na=False)]
            
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "url": st.column_config.LinkColumn("Product Link"),
                "price": st.column_config.NumberColumn("Sale Price (VND)", format="%d ₫"),
                "original_price": st.column_config.NumberColumn("Original Price (VND)", format="%d ₫"),
                "discount_percent": st.column_config.NumberColumn("Discount", format="%d %%"),
            }
        )
