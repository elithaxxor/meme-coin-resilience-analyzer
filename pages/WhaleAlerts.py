import streamlit as st
from utils.coin_utils import get_coin_choices
from utils.ui import mobile_container, mobile_spacer

with mobile_container():
    st.title("Whale Alerts")
    st.markdown("""
    Track large transactions and whale activity for your favorite meme coins and large caps.
    """)
    st.caption("ℹ️ Whale alerts help you spot major market moves. Learn more in the Education section.")
    mobile_spacer(8)
    coin_choices = get_coin_choices()
    selected_asset = st.selectbox(
        "Select asset for whale alerts (autocomplete)",
        options=list(coin_choices.keys()),
        format_func=lambda x: coin_choices[x],
        help="Start typing to search for supported coins."
    )
    try:
        if selected_asset:
            st.success(f"Showing whale alerts for: {coin_choices[selected_asset]}")
            st.info("This module will track large wallet transactions and alert on major moves. (API integration coming soon)")
        else:
            st.info("Select an asset to view whale alerts.")
        st.markdown("<style>.stDataFrame th, .stDataFrame td { font-size: 1.1em; } .stCaption { color: #6c757d; } </style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading whale alerts: {e}")
        st.info("Please check your internet connection, API keys, or try again later. If the issue persists, contact support.")
    st.markdown('<a href="#top">Back to Top</a>', unsafe_allow_html=True)
