import streamlit as st
import pandas as pd
import requests
from config import COINGECKO_API_KEY
from utils.ui import mobile_container, mobile_spacer

with mobile_container():
    st.title("Volume & Liquidity Analytics")
    st.write("Spot meme coins with unusual volume or liquidity spikes.")
    st.markdown("""
    Visualize and compare trading volume and liquidity for meme coins and large caps. Identify thinly traded or high-liquidity assets.
    """)
    st.caption("ℹ️ See Education for tips on interpreting volume and liquidity charts.")
    mobile_spacer(8)
    @st.cache_data(ttl=120)
    def fetch_top_volume_meme_coins():
        url = f"https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "category": "meme-token",
            "order": "volume_desc",
            "per_page": 25,
            "page": 1,
            "sparkline": False,
            "x_cg_pro_api_key": COINGECKO_API_KEY,
        }
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            return resp.json()
        return []

    try:
        data = fetch_top_volume_meme_coins()
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df[["name", "symbol", "current_price", "market_cap", "total_volume"]], use_container_width=True, hide_index=True)
            st.line_chart(df.set_index("name")["total_volume"], use_container_width=True)
            st.caption("Tip: Tap column headers to sort. Scroll horizontally for more data. Charts are interactive on mobile and desktop.")
        else:
            st.warning("No data found or API limit reached.")
            st.caption("If this persists, please try again later or check API status.")
    except Exception as e:
        st.error(f"Error loading volume/liquidity analytics: {e}")
        st.info("Please check your internet connection, data sources, or try again later. If the issue persists, contact support.")
    st.markdown("<style>.stDataFrame th, .stDataFrame td { font-size: 1.1em; } .stCaption { color: #6c757d; } </style>", unsafe_allow_html=True)
    st.markdown('<a href="#top">Back to Top</a>', unsafe_allow_html=True)
