import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from main import compute_correlation_matrix, fetch_coin_history, fetch_live_meme_coins, fetch_large_cap_coins
from utils.ui import mobile_container, mobile_spacer
from functools import lru_cache

@st.cache_data(ttl=600)
def get_coin_choices():
    # Combine meme coins and large caps for autocomplete dropdown
    meme_coins = fetch_live_meme_coins(50)
    large_caps = fetch_large_cap_coins(20)
    choices = {c['id']: f"{c['name']} ({c['symbol'].upper()})" for c in meme_coins + large_caps}
    return choices

@st.cache_data(ttl=600)
def get_price_history(asset_id, days=90):
    return fetch_coin_history(asset_id, days=days)

with mobile_container():
    st.title("Correlation & Diversification Tools")
    st.markdown("""
    Explore asset correlations and build diversified portfolios. Visualize rolling correlations and risk heatmaps.
    """)
    st.caption("ℹ️ Correlation insights and clustering explanations are in the Education page. Tooltips are available throughout.")
    mobile_spacer(8)

    # --- Asset Selection with Autocomplete ---
    coin_choices = get_coin_choices()
    selected_assets = st.multiselect(
        "Select assets (autocomplete)",
        options=list(coin_choices.keys()),
        format_func=lambda x: coin_choices[x],
        help="Start typing to search for supported coins."
    )
    window_sizes = st.multiselect("Rolling Windows (days)", [7, 14, 30, 60, 90], default=[30], help="Choose one or more rolling window sizes for correlation analysis.")
    mobile_spacer(4)
    st.info("You can select multiple assets and overlay different rolling windows for comparison.")

    # --- Error Handling and Data Fetch ---
    data = {}
    missing_assets = []
    if selected_assets:
        with st.spinner("Fetching price history..."):
            try:
                for asset in selected_assets:
                    hist = get_price_history(asset, days=90)
                    if hist is not None and not hist.empty:
                        data[coin_choices[asset]] = hist.set_index("date")["price"]
                    else:
                        missing_assets.append(asset)
            except Exception as e:
                st.error(f"Error fetching correlation data: {e}")
        if missing_assets:
            st.warning(f"No data found for: {', '.join([coin_choices[a] for a in missing_assets])}")

    # --- Main Analytics ---
    if data:
        df = pd.DataFrame(data)
        st.subheader("Correlation Matrix")
        corr = df.corr()
        st.dataframe(corr)
        st.write("Download Correlation Matrix:")
        st.download_button("Download CSV", corr.to_csv(), "correlation_matrix.csv", "text/csv")

        # --- Correlation Heatmap ---
        st.subheader("Correlation Heatmap")
        fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu", zmin=-1, zmax=1)
        st.plotly_chart(fig, use_container_width=True)

        # --- Rolling Correlation: Pairwise ---
        if len(data) >= 2:
            st.subheader("Pairwise Rolling Correlation")
            asset1 = st.selectbox("Asset 1", list(data.keys()), key="asset1")
            asset2 = st.selectbox("Asset 2", list(data.keys()), key="asset2")
            if asset1 != asset2:
                for w in window_sizes:
                    rolling_corr = df[asset1].rolling(w).corr(df[asset2])
                    st.line_chart(rolling_corr.rename(f"{asset1} vs {asset2} ({w}d)"))

        # --- Rolling Correlation Heatmap (Averaged) ---
        st.subheader("Rolling Correlation Heatmap (Averaged)")
        for w in window_sizes:
            rolling_corr = df.rolling(w).corr().dropna()
            avg_rolling = rolling_corr.groupby(level=0).mean()
            fig = px.imshow(avg_rolling, color_continuous_scale="RdBu", zmin=-1, zmax=1, title=f"Window: {w} days")
            st.plotly_chart(fig, use_container_width=True)

        # --- Diversification Score ---
        st.subheader("Diversification Score")
        div_score = 1 - corr.abs().mean().mean()
        st.metric("Diversification Score (0-1, higher=better)", f"{div_score:.2f}")
        # Historical Diversification Score
        st.subheader("Historical Diversification Score")
        hist_score = 1 - df.rolling(window_sizes[0]).corr().abs().mean(axis=1)
        st.line_chart(hist_score)

        # --- Advanced Analytics: Clustering ---
        st.subheader("Asset Clustering (Correlation Dendrogram)")
        try:
            import scipy.cluster.hierarchy as sch
            import scipy.spatial.distance as ssd
            dist = 1 - corr.abs()
            linkage = sch.linkage(ssd.squareform(dist), method='average')
            import matplotlib.pyplot as plt
            import io
            fig2, ax = plt.subplots(figsize=(8, 3))
            sch.dendrogram(linkage, labels=list(data.keys()), ax=ax)
            buf = io.BytesIO()
            fig2.savefig(buf, format="png")
            st.image(buf.getvalue(), caption="Hierarchical clustering dendrogram", use_column_width=True)
            plt.close(fig2)
        except Exception as e:
            st.info(f"Clustering not available: {e}")

        # --- Export Visualizations ---
        st.subheader("Export Visualizations")
        st.download_button("Download Correlation Heatmap (PNG)", fig.to_image(format="png"), "correlation_heatmap.png")

        # --- Education & Tooltips ---
        st.markdown("""
        **What is correlation?**
        Correlation measures how closely two assets move together. A value near 1 means they move together, -1 means they move oppositely, and 0 means no relationship.
        
        **Diversification Score:**
        A higher score means assets are less correlated and your portfolio is more diversified.
        
        [Learn more in the Education section.](#)
        """)
    else:
        st.info("Select assets above to begin analysis. Example: DOGE, SHIB, PEPE, WBTC, ETH.")

    st.markdown("<style>.stDataFrame th, .stDataFrame td { font-size: 1.1em; } .stCaption { color: #6c757d; } </style>", unsafe_allow_html=True)
    st.markdown('<a href="#top">Back to Top</a>', unsafe_allow_html=True)
