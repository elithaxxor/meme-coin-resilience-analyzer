import streamlit as st
from main import fetch_live_meme_coins, fetch_large_cap_coins, fetch_coin_history

@st.cache_data(ttl=600)
def get_coin_choices():
    """
    Returns a dict of {coin_id: 'Name (SYMBOL)'} for meme coins and large caps.
    Used for asset selection dropdowns across the app.
    """
    meme_coins = fetch_live_meme_coins(50)
    large_caps = fetch_large_cap_coins(20)
    choices = {c['id']: f"{c['name']} ({c['symbol'].upper()})" for c in meme_coins + large_caps}
    return choices

@st.cache_data(ttl=600)
def get_price_history(asset_id, days=90):
    """
    Fetches and caches price history for a given asset.
    Returns a DataFrame or None.
    """
    return fetch_coin_history(asset_id, days=days)
