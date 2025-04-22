import streamlit as st
import pandas as pd
import os
from datetime import datetime
from main import fetch_coin_history, fetch_large_cap_coins, fetch_live_meme_coins
from utils.coin_utils import get_coin_choices
from utils.ui import mobile_container, mobile_spacer

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
PORTFOLIO_CSV = os.path.join(DATA_DIR, 'portfolios.csv')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def load_portfolios():
    if os.path.exists(PORTFOLIO_CSV):
        return pd.read_csv(PORTFOLIO_CSV)
    else:
        return pd.DataFrame(columns=["portfolio", "asset", "type", "amount", "added_on"])

def save_portfolios(df):
    df.to_csv(PORTFOLIO_CSV, index=False)

def main():
    with mobile_container():
        st.title("Custom Portfolio Tracker")
        st.markdown("""
        Create, manage, and analyze your own portfolios of meme coins and large caps. Save and load portfolios as CSV for easy management.
        """)
        mobile_spacer(8)

        df = load_portfolios()
        portfolios = df['portfolio'].unique().tolist() if not df.empty else []
        selected_portfolio = st.selectbox("Select Portfolio", portfolios + ["Create New"], index=0)

        if selected_portfolio == "Create New":
            new_name = st.text_input("New Portfolio Name")
            if st.button("Create Portfolio") and new_name:
                if new_name not in portfolios:
                    df = pd.concat([df, pd.DataFrame([[new_name, '', '', 0, datetime.now()]], columns=df.columns)])
                    save_portfolios(df)
                    st.experimental_rerun()
                else:
                    st.warning("Portfolio with this name already exists.")
            st.stop()

        st.subheader(f"Manage Portfolio: {selected_portfolio}")
        coin_choices = get_coin_choices()
        add_asset = st.selectbox(
            "Add Asset (autocomplete)",
            options=list(coin_choices.keys()),
            format_func=lambda x: coin_choices[x],
            help="Start typing to search for supported coins."
        )
        amount = st.number_input("Amount Held", min_value=0.0, format="%f")
        if st.button("Add Asset") and add_asset:
            df = pd.concat([df, pd.DataFrame([[selected_portfolio, add_asset, "coin", amount, datetime.now()]], columns=df.columns)])
            save_portfolios(df)
            st.experimental_rerun()

        port_df = df[df['portfolio'] == selected_portfolio & (df['asset'] != '')]
        if not port_df.empty:
            st.dataframe(port_df[['asset', 'amount', 'added_on']])
            remove_asset = st.selectbox("Remove Asset", port_df['asset'].tolist())
            if st.button("Remove Selected Asset"):
                df = df[~((df['portfolio'] == selected_portfolio) & (df['asset'] == remove_asset))]
                save_portfolios(df)
                st.experimental_rerun()

            # Portfolio analytics
            st.subheader("Portfolio Performance & Risk Metrics")
            # Fetch historical price data for each asset
            hist_data = {}
            for asset in port_df['asset']:
                hist = fetch_coin_history(asset, days=90)
                if hist is not None:
                    hist_data[asset] = hist.set_index("date")["price"]
            if hist_data:
                prices_df = pd.DataFrame(hist_data)
                st.line_chart(prices_df)
                st.write("Historical Returns:")
                returns = prices_df.pct_change().dropna()
                st.dataframe(returns.describe().T)
                st.write("Portfolio Value (equal-weighted):")
                port_val = prices_df.mean(axis=1)
                st.line_chart(port_val)
                st.write("Download Portfolio CSV:")
                st.download_button("Download CSV", port_df.to_csv(index=False), f"{selected_portfolio}_portfolio.csv", "text/csv")
                st.write("Upload Portfolio CSV:")
                uploaded = st.file_uploader("Upload Portfolio CSV", type=["csv"])
                if uploaded:
                    new_df = pd.read_csv(uploaded)
                    new_df['portfolio'] = selected_portfolio
                    df = df[df['portfolio'] != selected_portfolio]
                    df = pd.concat([df, new_df])
                    save_portfolios(df)
                    st.success("Portfolio imported!")
                    st.experimental_rerun()
        else:
            st.info("No assets in this portfolio yet.")

if __name__ == "__main__":
    main()
