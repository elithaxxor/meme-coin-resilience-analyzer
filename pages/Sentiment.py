import streamlit as st
from utils.coin_utils import get_coin_choices
from utils.ui import mobile_container, mobile_spacer

with mobile_container():
    st.title("Community & Social Sentiment Analytics")
    st.write("Sentiment analysis for meme coins coming soon! (Integrate LunarCrush, Twitter, Reddit, etc.)")
    st.info("This module will aggregate social sentiment and trending mentions across platforms.\n\nTo enable, add your LunarCrush or Twitter API key to config.py or Streamlit secrets.")
    mobile_spacer(8)
    coin_choices = get_coin_choices()
    selected_asset = st.selectbox(
        "Select asset for sentiment analysis (autocomplete)",
        options=list(coin_choices.keys()),
        format_func=lambda x: coin_choices[x],
        help="Start typing to search for supported coins."
    )
    if selected_asset:
        st.success(f"Sentiment for: {coin_choices[selected_asset]}")
    else:
        st.info("Select an asset to view sentiment analysis.")
