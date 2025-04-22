import streamlit as st
import pandas as pd
import requests
from config import COINGECKO_API_KEY, SUPPORTED_CHAINS

st.title("Multi-Chain Meme Coin Analytics")
st.write("Compare meme coins across Ethereum, Solana, BSC, Polygon, and more. Data from CoinGecko.")

@st.cache_data(ttl=120)
def fetch_top_meme_coins(chain):
    url = f"https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "category": "meme-token",
        "order": "market_cap_desc",
        "per_page": 25,
        "page": 1,
        "sparkline": False,
        "x_cg_pro_api_key": COINGECKO_API_KEY,
    }
    if chain:
        params["platform"] = chain
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        return resp.json()
    return []

chain = st.selectbox("Select Chain", SUPPORTED_CHAINS)
coins = fetch_top_meme_coins(chain)

if coins:
    df = pd.DataFrame(coins)
    st.dataframe(df[["name", "symbol", "current_price", "market_cap", "total_volume"]])
else:
    st.warning("No meme coins found for this chain or API limit reached.")
