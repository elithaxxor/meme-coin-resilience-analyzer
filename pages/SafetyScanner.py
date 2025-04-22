import streamlit as st
import requests
st.title("Smart Contract Safety & Scam Detection")
st.write("Analyze smart contract safety using TokenSniffer (public endpoint demo).")

address = st.text_input("Enter Token Contract Address (Ethereum)")
if address:
    url = f"https://tokensniffer.com/api/v2/token/{address}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        st.json(data)
        score = data.get("score", None)
        if score is not None:
            st.metric("TokenSniffer Safety Score", score)
    else:
        st.warning("Could not fetch TokenSniffer data. Token may not be indexed or API limit reached.")
else:
    st.info("Enter a contract address above to scan for safety.")
