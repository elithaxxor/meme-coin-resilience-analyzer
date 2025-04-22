import streamlit as st
import pandas as pd
import os

st.title("Automated Price Alerts & Watchlists")
st.write("Create and manage your meme coin watchlist. (Local storage demo)")

WATCHLIST_FILE = "watchlist.csv"

if os.path.exists(WATCHLIST_FILE):
    watchlist = pd.read_csv(WATCHLIST_FILE)
else:
    watchlist = pd.DataFrame(columns=["name", "symbol", "target_price"])

st.dataframe(watchlist)

with st.form("add_coin"):
    name = st.text_input("Coin Name")
    symbol = st.text_input("Symbol")
    target_price = st.number_input("Target Price Alert (USD)", min_value=0.0, value=0.0)
    submitted = st.form_submit_button("Add to Watchlist")
    if submitted and name and symbol and target_price > 0:
        watchlist = watchlist._append({"name": name, "symbol": symbol, "target_price": target_price}, ignore_index=True)
        watchlist.to_csv(WATCHLIST_FILE, index=False)
        st.success(f"Added {name} to watchlist!")
        st.experimental_rerun()
