import streamlit as st
import pandas as pd
import requests
from config import COINGECKO_API_KEY, SUPPORTED_CHAINS

st.title("Trending Meme Coins (Multi-Chain)")
st.write("Live trending meme coins across Ethereum, Solana, BSC, Polygon, and more.")

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
    st.dataframe(df[["name", "symbol", "market_cap_rank", "score"]])
else:
    st.warning("No trending coins found or API limit reached.")
