import streamlit as st
import pandas as pd
import os
from utils.coin_utils import get_coin_choices
from utils.ui import mobile_container, mobile_spacer

WATCHLIST_FILE = "watchlist.csv"

if os.path.exists(WATCHLIST_FILE):
    watchlist = pd.read_csv(WATCHLIST_FILE)
else:
    watchlist = pd.DataFrame(columns=["name", "symbol", "target_price"])

with mobile_container():
    st.title("Watchlists")
    st.markdown("""
    Create and manage your custom watchlists of meme coins and large caps. Track price, volume, and news for selected assets.
    """)
    st.caption(" Tip: Use the Education page for guidance on building effective watchlists and setting alerts.")
    mobile_spacer(8)
    try:
        coin_choices = get_coin_choices()
        selected_assets = st.multiselect(
            "Select assets to watch (autocomplete)",
            options=list(coin_choices.keys()),
            format_func=lambda x: coin_choices[x],
            help="Start typing to search for supported coins."
        )
        if selected_assets:
            st.success(f"Assets in your watchlist: {', '.join([coin_choices[a] for a in selected_assets])}")
        else:
            st.info("Select assets above to build your watchlist.")
        st.dataframe(watchlist)

        with st.form("add_coin"):
            name = st.text_input("Coin Name")
            symbol = st.text_input("Symbol")
            target_price = st.number_input("Target Price Alert (USD)", min_value=0.0, value=0.0)
            submitted = st.form_submit_button("Add to Watchlist")
            if submitted and name and symbol and target_price > 0:
                try:
                    watchlist = watchlist._append({"name": name, "symbol": symbol, "target_price": target_price}, ignore_index=True)
                    watchlist.to_csv(WATCHLIST_FILE, index=False)
                    st.success(f"Added {name} to watchlist!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error adding coin to watchlist: {e}")
    except Exception as e:
        st.error(f"Error loading watchlists: {e}")
        st.info("Please check your internet connection, data files, or try again later. If the issue persists, contact support.")

    # Accessibility & colorblind mode
    st.markdown("<style>.stDataFrame th, .stDataFrame td { font-size: 1.1em; } .stCaption { color: #6c757d; } </style>", unsafe_allow_html=True)
    # Back to top button for long pages
    st.markdown('<a href="#top">Back to Top</a>', unsafe_allow_html=True)
