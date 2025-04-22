import streamlit as st
import pandas as pd
import requests
from config import COINGECKO_API_KEY

st.title("Holder & Distribution Analysis")
st.write("Analyze token holder concentration and whale activity (ETH-based tokens only).")

address = st.text_input("Enter Token Contract Address (Ethereum)")
if address:
    # Example: Use Etherscan API for holder distribution (requires public API key)
    ETHERSCAN_API_KEY = st.secrets["ETHERSCAN_API_KEY"] if "ETHERSCAN_API_KEY" in st.secrets else ""
    if ETHERSCAN_API_KEY:
        url = f"https://api.etherscan.io/api"
        params = {
            "module": "token",
            "action": "tokenholderlist",
            "contractaddress": address,
            "apikey": ETHERSCAN_API_KEY
        }
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            holders = data.get("result", [])
            if holders:
                df = pd.DataFrame(holders)
                st.dataframe(df)
                st.bar_chart(df["balance"].astype(float))
            else:
                st.warning("No holder data found.")
        else:
            st.error("Failed to fetch data from Etherscan.")
    else:
        st.info("Add your ETHERSCAN_API_KEY to Streamlit secrets for live holder analysis.")
else:
    st.info("Enter a contract address above to analyze holders.")
