import streamlit as st
import pandas as pd
import requests
from config import COINGECKO_API_KEY, SUPPORTED_CHAINS
from utils.coin_utils import get_coin_choices
from utils.ui import mobile_container, mobile_spacer

with mobile_container():
    st.title("Trending Coins")
    st.markdown("""
    Discover which meme coins and large caps are trending now, based on price, volume, and social activity.
    """)
    st.caption("ℹ️ Trending scores reflect real-time social and trading activity. Use the [Education page](/Education) for more on how to interpret these metrics.")
    mobile_spacer(8)
    coin_choices = get_coin_choices()
    selected_assets = st.multiselect(
        "Select assets to compare (autocomplete)",
        options=list(coin_choices.keys()),
        format_func=lambda x: coin_choices[x],
        help="Start typing to search for supported coins."
    )
    if selected_assets:
        st.success(f"Trending comparison for: {', '.join([coin_choices[a] for a in selected_assets])}")
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

        try:
            trending_coins = fetch_trending_coins()
            if trending_coins:
                df = pd.DataFrame(trending_coins)
                st.dataframe(df[["name", "symbol", "market_cap_rank", "score"]], use_container_width=True, hide_index=True)
                st.bar_chart(df.set_index("name")["score"], use_container_width=True)
                st.caption("Trending scores reflect real-time social and trading activity. Use the [Education page](/Education) for more on how to interpret these metrics.")
            else:
                st.warning("No trending coins found or API limit reached.")
        except Exception as e:
            st.error(f"Error loading trending data: {e}")
    else:
        st.info("Select assets above to compare trends.")
    st.markdown("<style>.stDataFrame th, .stDataFrame td { font-size: 1.1em; padding: 0.5em; } .stCaption { color: #6c757d; font-size: 0.95em; } </style>", unsafe_allow_html=True)
    st.markdown('<a href="#top">Back to Top</a>', unsafe_allow_html=True)
