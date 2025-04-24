import streamlit as st
from utils.ui import mobile_container, mobile_spacer

with mobile_container():
    try:
        st.title("New Meme Coin Listings & Early Discovery")
        st.markdown("""
        Stay ahead with the latest meme coin launches and new token listings. Data is aggregated from CoinGecko, CoinMarketCap, and DEXs.\n
        **Tip:** Use the table sorter and search to find the newest coins. Listings update frequently.\n
        [Learn more about how listings are sourced and what to watch for in new tokens on the Education page.](/Education)
        """)
        mobile_spacer(8)
    except Exception as e:
        st.error(f"Error loading new listings: {e}")
        st.info("Please check your internet connection, data sources, or try again later. If the issue persists, contact support.")
