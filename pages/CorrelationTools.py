import streamlit as st
import pandas as pd
from main import compute_correlation_matrix, fetch_coin_history
from utils.ui import mobile_container, mobile_spacer

with mobile_container():
    st.title("Correlation & Diversification Tools")
    st.markdown("""
    Explore asset correlations and build diversified portfolios. Visualize rolling correlations and risk heatmaps.
    """)
    mobile_spacer(8)

    assets = st.text_area("Enter asset names (comma separated)")
    window = st.slider("Rolling Window (days)", 7, 90, 30)

    if assets:
        asset_list = [a.strip() for a in assets.split(",") if a.strip()]
        data = {}
        for asset in asset_list:
            hist = fetch_coin_history(asset, days=90)
            if hist is not None:
                data[asset] = hist.set_index("date")["price"]
        if data:
            df = pd.DataFrame(data)
            st.subheader("Correlation Matrix")
            corr = df.corr()
            st.dataframe(corr)
            st.subheader("Rolling Correlation Heatmap")
            rolling_corr = df.rolling(window).corr().dropna()
            st.line_chart(rolling_corr.groupby(level=0).mean())
            st.write("Download Correlation Matrix:")
            st.download_button("Download CSV", corr.to_csv(), "correlation_matrix.csv", "text/csv")
            st.subheader("Diversification Score")
            div_score = 1 - corr.abs().mean().mean()
            st.metric("Diversification Score (0-1, higher=better)", f"{div_score:.2f}")
        else:
            st.warning("No data found for entered assets.")
    else:
        st.info("Enter asset names to begin.")
