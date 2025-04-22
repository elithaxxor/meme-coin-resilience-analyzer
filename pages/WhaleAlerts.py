import streamlit as st
from utils.coin_utils import get_coin_choices
from utils.ui import mobile_container, mobile_spacer

with mobile_container():
    st.title("Whale Alerts")
    st.markdown("""
    Track large transactions and whale activity for your favorite meme coins and large caps.
    """)
    mobile_spacer(8)
    coin_choices = get_coin_choices()
    selected_asset = st.selectbox(
        "Select asset for whale alerts (autocomplete)",
        options=list(coin_choices.keys()),
        format_func=lambda x: coin_choices[x],
        help="Start typing to search for supported coins."
    )
    if selected_asset:
        st.success(f"Showing whale alerts for: {coin_choices[selected_asset]}")
        st.write("Whale alert functionality coming soon! (Integrate whale tracking APIs or Etherscan logs)")
        st.info("This module will track large wallet transactions and alert on major moves.\n\nTo enable, add a whale tracking API key or use Etherscan logs.")
    else:
        st.info("Select an asset to view whale alerts.")
