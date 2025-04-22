import streamlit as st
from utils.ui import mobile_container, mobile_spacer

with mobile_container():
    st.title("New Listings & Early Discovery")
    st.write("New meme coin listing alerts coming soon! (Integrate DEXTools, Birdeye, or CoinGecko new listings APIs)")
    st.info("This module will aggregate and alert on newly listed meme coins across multiple chains.")
    mobile_spacer(8)
