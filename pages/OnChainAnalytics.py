import streamlit as st
import requests
import pandas as pd
import os
from utils.ui import mobile_container, mobile_spacer

st.title("On-Chain Analytics: Holders, Transactions, & Whale Movements")
st.markdown("""
Analyze on-chain activity for meme coins and large caps. View holder distribution, transaction activity, and recent whale movements. Powered by Etherscan and public APIs.
""")

with mobile_container():
    st.title("On-Chain Analytics: Holders, Transactions, & Whale Movements")
    st.markdown("""
    Analyze on-chain activity for meme coins and large caps. View holder distribution, transaction activity, and recent whale movements. Powered by Etherscan and public APIs.
    """)
    mobile_spacer(8)
    ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY") or st.secrets.get("ETHERSCAN_API_KEY", "")

    @st.cache_data(show_spinner=False)
    def get_token_holders(token_address):
        if not ETHERSCAN_API_KEY:
            return pd.DataFrame()
        url = f"https://api.etherscan.io/api?module=token&action=tokenholderlist&contractaddress={token_address}&apikey={ETHERSCAN_API_KEY}"
        r = requests.get(url)
        if r.status_code == 200 and r.json().get('result'):
            df = pd.DataFrame(r.json()['result'])
            return df
        return pd.DataFrame()

    @st.cache_data(show_spinner=False)
    def get_token_transfers(token_address):
        if not ETHERSCAN_API_KEY:
            return pd.DataFrame()
        url = f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={token_address}&page=1&offset=100&sort=desc&apikey={ETHERSCAN_API_KEY}"
        r = requests.get(url)
        if r.status_code == 200 and r.json().get('result'):
            df = pd.DataFrame(r.json()['result'])
            return df
        return pd.DataFrame()

    # Demo: User selects a coin (for now, hardcoded or select from fetched live coins)
    from main import fetch_live_meme_coins
    meme_coins = fetch_live_meme_coins()
    coin_options = [(c['name'], c['address']) for c in meme_coins if c.get('address')]

    if coin_options:
        coin_name, token_address = st.selectbox("Select Meme Coin (ETH)", coin_options)
        if token_address:
            st.subheader(f"Holder Distribution for {coin_name}")
            holders_df = get_token_holders(token_address)
            if not holders_df.empty:
                st.dataframe(holders_df.head(20))
                st.bar_chart(holders_df['balance'].astype(float).head(20))
            else:
                st.info("No holder data available (API or contract may not support public holder lists).")

            st.subheader(f"Recent Transactions for {coin_name}")
            transfers_df = get_token_transfers(token_address)
            if not transfers_df.empty:
                st.dataframe(transfers_df[['from', 'to', 'value', 'hash', 'timeStamp']].head(20))
            else:
                st.info("No transfer data available.")

            st.subheader(f"Whale Movements (Top 5 Holders)")
            if not holders_df.empty:
                top_holders = holders_df.head(5)
                st.write(top_holders[['address', 'balance']])
                whale_transfers = transfers_df[transfers_df['from'].isin(top_holders['address']) | transfers_df['to'].isin(top_holders['address'])]
                st.write(whale_transfers[['from', 'to', 'value', 'hash', 'timeStamp']].head(10))
    else:
        st.info("No meme coins with contract addresses found.")

    st.caption("Note: On-chain analytics currently supports Ethereum tokens only. For Solana/BSC/Polygon, integration with Solscan/BscScan/Polygonscan APIs is planned.")
