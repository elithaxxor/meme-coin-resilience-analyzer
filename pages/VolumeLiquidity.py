import streamlit as st
import pandas as pd
import requests
from config import COINGECKO_API_KEY
from utils.ui import mobile_container, mobile_spacer

with mobile_container():
    st.title("Volume & Liquidity Analytics")
    st.write("Spot meme coins with unusual volume or liquidity spikes.")
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

    data = fetch_top_volume_meme_coins()
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df[["name", "symbol", "current_price", "market_cap", "total_volume"]])
        st.line_chart(df.set_index("name")["total_volume"])
    else:
        st.warning("No data found or API limit reached.")
