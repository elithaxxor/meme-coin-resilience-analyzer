import streamlit as st
import pandas as pd
import requests
from config import COINGECKO_API_KEY, SUPPORTED_CHAINS
from utils.ui import mobile_container, mobile_spacer

with mobile_container():
    st.title("Trending Meme Coins & Market Movers")
    st.markdown("""
    Discover the hottest meme coins and top movers in the market. Data is refreshed frequently from major APIs.\n
    **Tip:** Tap column headers to sort, and scroll horizontally for more info. Charts and tables are interactive on mobile and desktop.
    """)
    mobile_spacer(8)

    @st.cache_data(ttl=60)
    def fetch_trending_coins(chain=None):
        # Use CoinGecko trending endpoint as a base example
        url = f"https://api.coingecko.com/api/v3/search/trending"
        headers = {"x-cg-pro-api-key": COINGECKO_API_KEY}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            coins = data.get("coins", [])
            # Optionally filter by chain if needed
            return [c["item"] for c in coins]
        return []

    chain = st.selectbox("Select Chain", ["all"] + SUPPORTED_CHAINS)
    trending_coins = fetch_trending_coins(chain if chain != "all" else None)

    if trending_coins:
        df = pd.DataFrame(trending_coins)
        st.dataframe(df[["name", "symbol", "market_cap_rank", "score"]], use_container_width=True, hide_index=True)
        st.bar_chart(df.set_index("name")["score"], use_container_width=True)
        st.caption("Trending scores reflect real-time social and trading activity. Use the [Education page](/Education) for more on how to interpret these metrics.")
        st.markdown("""
        <style>
        .stDataFrame th, .stDataFrame td { font-size: 1.1em; padding: 0.5em; }
        .stCaption { color: #6c757d; font-size: 0.95em; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.warning("No trending coins found or API limit reached.")
