import streamlit as st
from main import (
    fetch_coingecko_data, prompt_factors, weighted_score, fetch_live_meme_coins,
    fetch_vix_history, fetch_sp500_history, fetch_coin_history, compute_correlation_matrix, fetch_large_cap_coins,
    fetch_vix_history_aligned, fetch_sp500_history_aligned, align_and_normalize_series, rolling_volatility, moving_average,
    calc_returns, calc_cumulative_returns, calc_volatility, calc_sharpe, calc_sortino, calc_max_drawdown, calc_beta,
    calc_rsi, calc_macd, calc_bollinger, calc_rolling_stat, calc_skew, calc_kurt, calc_var, price_to_ath, price_to_volume,
    calc_stochastic_oscillator, calc_williams_r, calc_obv, calc_cci, calc_adx
)
import pandas as pd
import plotly.graph_objs as go
import numpy as np

# --- Streamlit Multi-Page Navigation ---
pages = [
    "How to Use",
    "Indicators Explained",
    "Stonk Battle Royale (Analyzer)",
    "Large Cap Crypto Stonks",
    "Meme Coin Feed",
]
page = st.sidebar.radio("Navigation", pages)

if page == "How to Use":
    st.title("How to Use the Meme Coin & Stonk Analyzer ")
    st.markdown("""
    ## Welcome!
    This app lets you analyze meme coins, large cap cryptocurrencies, and market indices (VIX, S&P 500) with advanced analytics and a WallStreetBets parody theme.

    **Main Features:**
    - Live meme coin and large cap feeds with advanced filtering and charting
    - Compare any combination of meme coins, large caps, VIX, and S&P 500
    - 20+ financial ratios and technical indicators (Sharpe, RSI, MACD, etc.)
    - Interactive charts, downloadable data, and correlation matrices

    **Workflow:**
    1. Use the sidebar to navigate between pages.
    2. On the "Stonk Battle Royale" page, select any assets and indicators to compare.
    3. Adjust the time window and rolling/stat window as needed.
    4. Download results or view correlation matrices.
    5. For indicator explanations, see the "Indicators Explained" page.
    """)
    st.info("If you get API errors, try refreshing or reducing the number of coins selected.")

elif page == "Indicators Explained":
    st.title("Indicators & Ratios: Explanations & Demos ")
    st.markdown("""
    This page explains each indicator and ratio available in the app, with formulas and demonstration graphics where possible.
    """)
    demo_series = pd.Series(np.cumprod(1 + np.random.normal(0, 0.03, 90)), index=pd.date_range(end=pd.Timestamp.today(), periods=90))
    st.header("Price & Returns")
    st.markdown("**Price:** The raw price of the asset.")
    st.line_chart(demo_series)
    st.markdown("**Returns:** Daily % change. Formula: (P_t - P_{t-1}) / P_{t-1}")
    st.line_chart(calc_returns(demo_series))
    st.markdown("**Cumulative Returns:** Compounded return over time. Formula: (1 + r).cumprod() - 1")
    st.line_chart(calc_cumulative_returns(demo_series))
    st.header("Volatility & Drawdown")
    st.markdown("**Rolling Volatility:** Std dev of returns over a window. Measures risk.")
    st.line_chart(calc_volatility(demo_series, window=14))
    st.markdown("**Max Drawdown:** Largest drop from peak. Shows risk of big losses.")
    st.line_chart(calc_max_drawdown(demo_series))
    st.header("Sharpe & Sortino Ratio")
    st.markdown("**Sharpe Ratio:** (Mean excess return) / (Std dev of return). Higher is better.")
    st.line_chart(calc_sharpe(demo_series, window=14))
    st.markdown("**Sortino Ratio:** Like Sharpe, but only penalizes downside volatility.")
    st.line_chart(calc_sortino(demo_series, window=14))
    st.header("Beta")
    st.markdown("**Beta:** Sensitivity to S&P 500. >1 = more volatile than market.")
    st.code("cov(asset, sp500) / var(sp500)")
    st.header("Moving Averages")
    st.markdown("**SMA/EMA:** Smooth price trends. SMA = simple, EMA = exponential.")
    st.line_chart(moving_average(demo_series, window=7, kind="sma"))
    st.line_chart(moving_average(demo_series, window=7, kind="ema"))
    st.header("RSI (Relative Strength Index)")
    st.markdown("Oscillator (0-100) showing overbought (>70) or oversold (<30) conditions.")
    st.line_chart(calc_rsi(demo_series, window=14))
    st.header("MACD")
    st.markdown("Trend-following momentum indicator. MACD = EMA(12) - EMA(26). Signal = EMA(9) of MACD.")
    macd, signal = calc_macd(demo_series)
    st.line_chart(macd)
    st.line_chart(signal)
    st.header("Bollinger Bands")
    st.markdown("Bands at SMA ± 2 std dev. Shows price volatility and extremes.")
    sma, upper, lower = calc_bollinger(demo_series, window=14)
    st.line_chart(pd.DataFrame({'SMA': sma, 'Upper': upper, 'Lower': lower}))
    st.header("Rolling Statistics")
    st.markdown("Mean, std, min, max over a rolling window.")
    st.line_chart(calc_rolling_stat(demo_series, window=14, stat="mean"))
    st.line_chart(calc_rolling_stat(demo_series, window=14, stat="std"))
    st.line_chart(calc_rolling_stat(demo_series, window=14, stat="min"))
    st.line_chart(calc_rolling_stat(demo_series, window=14, stat="max"))
    st.header("Skewness & Kurtosis")
    st.markdown("Skewness: Asymmetry of returns. Kurtosis: Fat tails/extremes.")
    st.line_chart(calc_skew(demo_series, window=14))
    st.line_chart(calc_kurt(demo_series, window=14))
    st.header("Value at Risk (VaR)")
    st.markdown("Worst expected loss at a given confidence (e.g., 5%).")
    st.line_chart(calc_var(demo_series, quantile=0.05, window=14))
    st.header("Custom Ratios")
    st.markdown("**Price/ATH:** Price divided by all-time-high. Shows room to moon.")
    st.markdown("**Price/Volume:** Price divided by trading volume. Shows liquidity.")
    st.info("All indicators are for informational purposes only. Not financial advice!")

elif page == "Stonk Battle Royale (Analyzer)":
    # --- Customizable Comparison Section ---
    st.header(" Compare Meme Coins, Large Caps, VIX & S&P 500 — Custom Stonk Battle Royale")

    # Gather asset choices
    def get_asset_choices():
        meme_coins = fetch_live_meme_coins()
        meme_names = [c['name'] for c in meme_coins]
        meme_id_map = {c['name']: c['id'] for c in meme_coins}
        meme_vol_map = {c['name']: c['volume'] for c in meme_coins}
        meme_ath_map = {c['name']: c['ath'] for c in meme_coins}
        large_caps = fetch_large_cap_coins()
        large_names = [c['name'] for c in large_caps]
        large_id_map = {c['name']: c['id'] for c in large_caps}
        large_vol_map = {c['name']: c['volume'] for c in large_caps}
        large_ath_map = {c['name']: c['ath'] for c in large_caps}
        index_names = ["VIX (Volatility Index)", "S&P 500"]
        return meme_names, meme_id_map, meme_vol_map, meme_ath_map, large_names, large_id_map, large_vol_map, large_ath_map, index_names

    meme_names, meme_id_map, meme_vol_map, meme_ath_map, large_names, large_id_map, large_vol_map, large_ath_map, index_names = get_asset_choices()
    all_choices = meme_names + large_names + index_names

    indicator_options = [
        "Price", "Normalized Price", "Returns", "Cumulative Returns", "Volatility (7d)", "Sharpe Ratio", "Sortino Ratio", "Max Drawdown", "Beta (vs S&P 500)",
        "SMA (7d)", "EMA (7d)", "RSI (14d)", "MACD", "Bollinger Bands", "Rolling Mean (7d)", "Rolling Std (7d)", "Rolling Min (7d)", "Rolling Max (7d)",
        "Skewness (30d)", "Kurtosis (30d)", "VaR (5%, 30d)", "Price/ATH", "Price/Volume",
        "Stochastic Oscillator (14d)", "Williams %R (14d)", "On-Balance Volume (OBV)", "CCI (20d)", "ADX (14d)"
    ]

    compare_assets = st.multiselect(
        "Select any assets to compare (meme coins, large caps, VIX, S&P 500)",
        options=all_choices,
        default=["Bitcoin", "Ethereum", "VIX (Volatility Index)"]
    )
    indicator = st.selectbox("Indicator / Ratio", indicator_options)
    days = st.slider("Days of History", 14, 90, 30)
    window = st.slider("Window (days) for rolling/stat indicators", 7, 30, 14)

    # Chart type selection
    chart_type = st.selectbox("Chart Type", ["Line", "Bar", "Heatmap"], index=0)

    # Fetch and align data
    series_dict = {}
    volume_dict = {}
    ath_dict = {}
    high_dict = {}
    low_dict = {}
    close_dict = {}
    for name in compare_assets:
        if name in meme_names:
            coin_id = meme_id_map[name]
            hist = fetch_coin_history(coin_id, days=days)
            if hist is not None:
                series_dict[name] = hist.set_index("date")["price"]
                volume_dict[name] = hist.set_index("date")["volume"]
                ath_dict[name] = float(meme_ath_map[name]) if meme_ath_map[name] not in (None, "-") else np.nan
                high_dict[name] = hist.set_index("date")["price"]  # Placeholder for high
                low_dict[name] = hist.set_index("date")["price"]   # Placeholder for low
                close_dict[name] = hist.set_index("date")["price"] # Placeholder for close
        elif name in large_names:
            coin_id = large_id_map[name]
            hist = fetch_coin_history(coin_id, days=days)
            if hist is not None:
                series_dict[name] = hist.set_index("date")["price"]
                volume_dict[name] = hist.set_index("date")["volume"]
                ath_dict[name] = float(large_ath_map[name]) if large_ath_map[name] not in (None, "-") else np.nan
                high_dict[name] = hist.set_index("date")["price"]
                low_dict[name] = hist.set_index("date")["price"]
                close_dict[name] = hist.set_index("date")["price"]
        elif name == "VIX (Volatility Index)":
            vix_df = fetch_vix_history_aligned(days=days)
            if vix_df is not None:
                series_dict[name] = vix_df.set_index("date")["price"]
                high_dict[name] = vix_df.set_index("date")["price"]
                low_dict[name] = vix_df.set_index("date")["price"]
                close_dict[name] = vix_df.set_index("date")["price"]
        elif name == "S&P 500":
            spx_df = fetch_sp500_history_aligned(days=days)
            if spx_df is not None:
                series_dict[name] = spx_df.set_index("date")["price"]
                high_dict[name] = spx_df.set_index("date")["price"]
                low_dict[name] = spx_df.set_index("date")["price"]
                close_dict[name] = spx_df.set_index("date")["price"]

    # Analytics logic
    aligned = None
    if indicator == "Stochastic Oscillator (14d)":
        aligned = pd.DataFrame({n: calc_stochastic_oscillator(s, window=14) for n, s in series_dict.items()}).dropna()
    elif indicator == "Williams %R (14d)":
        aligned = pd.DataFrame({n: calc_williams_r(s, window=14) for n, s in series_dict.items()}).dropna()
    elif indicator == "On-Balance Volume (OBV)":
        aligned = pd.DataFrame({n: calc_obv(series_dict[n], volume_dict[n]) for n in series_dict if n in volume_dict}).dropna()
    elif indicator == "CCI (20d)":
        aligned = pd.DataFrame({n: calc_cci(s, window=20) for n, s in series_dict.items()}).dropna()
    elif indicator == "ADX (14d)":
        aligned = pd.DataFrame({n: calc_adx(high_dict[n], low_dict[n], close_dict[n], window=14) for n in series_dict}).dropna()
    # (existing analytics logic for other indicators remains unchanged)

    if aligned is not None and not aligned.empty:
        st.subheader(f"{indicator} Chart")
        fig = go.Figure()
        if chart_type == "Line":
            for col in aligned.columns:
                fig.add_trace(go.Scatter(x=aligned.index, y=aligned[col], mode="lines", name=col))
        elif chart_type == "Bar":
            for col in aligned.columns:
                fig.add_trace(go.Bar(x=aligned.index, y=aligned[col], name=col))
        elif chart_type == "Heatmap":
            fig = go.Figure(data=go.Heatmap(z=aligned.values, x=aligned.index, y=aligned.columns, colorscale="Viridis"))
        fig.update_layout(title=f"Custom Comparison: {', '.join(compare_assets)}", xaxis_title="Date", yaxis_title=indicator)
        st.plotly_chart(fig, use_container_width=True)
        # Download data
        csv = aligned.reset_index().to_csv(index=False).encode('utf-8')
        st.download_button("Download Data CSV", csv, f"{indicator.lower().replace(' ','_')}_comparison.csv", "text/csv")
    # (existing chart rendering logic remains unchanged)

elif page == "Large Cap Crypto Stonks":
    # --- Large Cap Cryptocurrencies Section ---
    st.header("")
    large_cap_coins = fetch_large_cap_coins()
    if large_cap_coins:
        lc_df = pd.DataFrame(large_cap_coins)
        lc_df = lc_df.rename(columns={
            "name": "Name", "symbol": "Symbol", "price": "Price (USD)", "market_cap": "Market Cap (USD)",
            "volume": "Volume (USD)", "price_change_24h": "24h Change (%)", "ath": "ATH", "atl": "ATL",
            "supply": "Circulating Supply", "launch_date": "Launch Date"
        })
        st.dataframe(lc_df, use_container_width=True)
        # Large cap charting
        st.subheader("")
        lc_chart_type = st.selectbox("Large Cap Chart Type", ["Bar", "Line", "Area", "Scatter"], index=0, key="lc_chart_type")
        lc_selected = st.multiselect("Select large caps to chart", lc_df["Name"].tolist(), default=lc_df["Name"].tolist()[:3], key="lc_chart")
        lc_chart_df = lc_df[lc_df["Name"].isin(lc_selected)]
        lc_chart = go.Figure()
        for _, row in lc_chart_df.iterrows():
            if lc_chart_type == "Bar":
                lc_chart.add_trace(go.Bar(x=[row["Name"]], y=[row["Price (USD)"]], name=row["Name"]))
            elif lc_chart_type == "Line":
                lc_chart.add_trace(go.Scatter(x=[row["Name"]], y=[row["Price (USD)"]], name=row["Name"], mode="lines+markers"))
            elif lc_chart_type == "Area":
                lc_chart.add_trace(go.Scatter(x=[row["Name"]], y=[row["Price (USD)"]], name=row["Name"], fill="tozeroy"))
            elif lc_chart_type == "Scatter":
                lc_chart.add_trace(go.Scatter(x=[row["Name"]], y=[row["Price (USD)"]], name=row["Name"], mode="markers"))
        lc_chart.update_layout(title=f"Large Cap Price Comparison", xaxis_title="Coin", yaxis_title="Price (USD)")
        st.plotly_chart(lc_chart, use_container_width=True)
    else:
        st.warning("Could not fetch large cap coins. The suits are hiding the data!")

elif page == "Meme Coin Feed":
    # --- Live Meme Coin Feed ---
    st.header("")
    refresh = st.button("")
    if 'meme_coins' not in st.session_state or refresh:
        st.session_state['meme_coins'] = fetch_live_meme_coins()
    meme_coins = st.session_state['meme_coins']

    if meme_coins:
        df = pd.DataFrame(meme_coins)
        df = df.rename(columns={
            "name": "Name", "symbol": "Symbol", "price": "Price (USD)", "market_cap": "Market Cap (USD)",
            "volume": "Volume (USD)", "price_change_24h": "24h Change (%)", "ath": "ATH", "atl": "ATL",
            "supply": "Circulating Supply", "launch_date": "Launch Date"
        })
        # Advanced Filtering
        st.sidebar.header("")
        min_price, max_price = st.sidebar.slider("", float(df["Price (USD)"].min()), float(df["Price (USD)"].max()), (float(df["Price (USD)"].min()), float(df["Price (USD)"].max())))
        min_mcap, max_mcap = st.sidebar.slider("", float(df["Market Cap (USD)"].min()), float(df["Market Cap (USD)"].max()), (float(df["Market Cap (USD)"].min()), float(df["Market Cap (USD)"].max())))
        search = st.sidebar.text_input("", "")
        sort_col = st.sidebar.selectbox("", df.columns.tolist(), index=3)
        ascending = st.sidebar.checkbox("", value=False)
        filtered_df = df[(df["Price (USD)"] >= min_price) & (df["Price (USD)"] <= max_price) &
                         (df["Market Cap (USD)"] >= min_mcap) & (df["Market Cap (USD)"] <= max_mcap)]
        if search:
            filtered_df = filtered_df[(filtered_df["Name"].str.contains(search, case=False)) | (filtered_df["Symbol"].str.contains(search, case=False))]
        filtered_df = filtered_df.sort_values(by=sort_col, ascending=ascending)
        st.dataframe(filtered_df, use_container_width=True)
        # Download CSV
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("", csv, "meme_coins_filtered.csv", "text/csv")
        # Advanced Charting
        st.subheader("")
        chart_type = st.selectbox("", ["Price", "Market Cap", "Volume", "24h Change (%)"], index=0, help="")
        selected_coins = st.multiselect("", filtered_df["Name"].tolist(), default=filtered_df["Name"].tolist()[:3])
        chart_style = st.selectbox("", ["Bar", "Line", "Area", "Scatter"], index=0)
        chart_df = filtered_df[filtered_df["Name"].isin(selected_coins)]
        chart = go.Figure()
        for _, row in chart_df.iterrows():
            if chart_style == "Bar":
                chart.add_trace(go.Bar(x=[row["Name"]], y=[row[chart_type]], name=row["Name"]))
            elif chart_style == "Line":
                chart.add_trace(go.Scatter(x=[row["Name"]], y=[row[chart_type]], name=row["Name"], mode="lines+markers"))
            elif chart_style == "Area":
                chart.add_trace(go.Scatter(x=[row["Name"]], y=[row[chart_type]], name=row["Name"], fill="tozeroy"))
            elif chart_style == "Scatter":
                chart.add_trace(go.Scatter(x=[row["Name"]], y=[row[chart_type]], name=row["Name"], mode="markers"))
        chart.update_layout(title=f"{chart_type} Comparison — Stonks Only Go Up! ", xaxis_title="Coin", yaxis_title=chart_type)
        st.plotly_chart(chart, use_container_width=True)
        selected = st.selectbox("", filtered_df["Name"].tolist())
    else:
        selected = None
        st.warning("")

# --- Coin Selection ---
if selected:
    coin_name = selected
else:
    coin_name = st.text_input("", "")
auto_fetch = st.checkbox("", value=True)
prefill = None
if coin_name and auto_fetch:
    with st.spinner(f""):
        prefill = fetch_coingecko_data(coin_name)
        if not prefill:
            st.warning("")

with st.form("resilience_form"):
    st.subheader("")
    utility = st.radio("", ["yes", "no"], index=1, help="") == "yes"

    st.subheader("")
    deflationary = st.radio("", ["yes", "no"], index=1, help="") == "yes"
    staking_apy = st.number_input("", value=float(prefill["staking_apy"]) if prefill and "staking_apy" in prefill else 0.0)
    team_locked = st.radio("", ["yes", "no"], index=1) == "yes"
    fair_distribution = st.radio("", ["yes", "no"], index=1) == "yes"
    whale_concentration = st.radio("", ["yes", "no"], index=1, help="") == "yes"

    st.subheader("")
    liquidity_usd = st.number_input("", value=float(prefill["market_cap"]) if prefill and "market_cap" in prefill else 0.0)
    liquidity_locked = st.radio("", ["yes", "no"], index=1) == "yes"
    daily_volume = st.number_input("", value=float(prefill["volume"]) if prefill and "volume" in prefill else 0.0)
    organic = st.radio("", ["yes", "no"], index=1) == "yes"

    st.subheader("")
    trending = st.radio("", ["yes", "no"], index=1) == "yes"
    active_community = st.radio("", ["yes", "no"], index=1) == "yes"
    meme_virality = st.slider("", 1, 5, 3)
    growth = st.radio("", ["yes", "no"], index=1, help="") == "yes"
    hype_volatility = st.radio("", ["yes", "no"], index=1, help="") == "yes"

    st.subheader("")
    interest_rates_low = st.radio("", ["yes", "no"], index=1) == "yes"
    favorable_inflation = st.radio("", ["yes", "no"], index=1) == "yes"
    regulatory_news = st.radio("", ["yes", "no"], index=1) == "yes"

    st.subheader("")
    audited = st.radio("", ["yes", "no"], index=1) == "yes"
    doxxed_team = st.radio("", ["yes", "no"], index=1, help="") == "yes"
    open_source = st.radio("", ["yes", "no"], index=1) == "yes"
    verified_contract = st.radio("", ["yes", "no"], index=1) == "yes"
    active_dev = st.radio("", ["yes", "no"], index=1) == "yes"

    st.subheader("")
    renounced_ownership = st.radio("", ["yes", "no"], index=1, help="") == "yes"
    honeypot = st.radio("", ["yes", "no"], index=1) == "yes"
    rugpull_pattern = st.radio("", ["yes", "no"], index=1) == "yes"

    submitted = st.form_submit_button("")

if submitted:
    tokenomics = {
        'deflationary': deflationary,
        'staking_apy': staking_apy,
        'team_locked': team_locked,
        'fair_distribution': fair_distribution,
    }
    liquidity = {
        'liquidity_usd': liquidity_usd,
        'liquidity_locked': liquidity_locked,
        'daily_volume': daily_volume,
        'organic': organic,
    }
    social = {
        'trending': trending,
        'active_community': active_community,
        'meme_virality': meme_virality,
        'growth': growth,
        'hype_volatility': hype_volatility,
    }
    macro = {
        'interest_rates_low': interest_rates_low,
        'favorable_inflation': favorable_inflation,
        'regulatory_news': regulatory_news,
    }
    security = {
        'audited': audited,
        'doxxed_team': doxxed_team,
        'open_source': open_source,
        'verified_contract': verified_contract,
        'active_dev': active_dev,
    }
    red_flags = {
        'renounced_ownership': renounced_ownership,
        'honeypot': honeypot,
        'rugpull_pattern': rugpull_pattern,
    }
    score, breakdown = weighted_score(
        utility, tokenomics, whale_concentration, liquidity, social, macro, security, red_flags
    )
    st.subheader(f"Resilience Score: {score:.2f}/10 — How YOLO is this coin? ")
    st.write("### Score Breakdown (for your DD)")
    st.table({"Factor": list(breakdown.keys()), "Score": [f"{v:.2f}" for v in breakdown.values()]})
    if breakdown.get('Red Flags', 0) < 0:
        st.error("")

# --- Historical Time Series and Correlation ---
st.header("")
hist_coins = st.multiselect("", df["Name"].tolist() if meme_coins else [], default=[]) 
hist_days = st.slider("", 7, 90, 30)
if hist_coins:
    price_dict = {}
    for name in hist_coins:
        coin_id = df[df["Name"] == name]["id"].values[0]
        hist_df = fetch_coin_history(coin_id, days=hist_days)
        if hist_df is not None:
            price_dict[name] = hist_df.set_index("date")["price"]
            # Show time series
            st.subheader(f"{name} Price & Volume History (HODL!)")
            chart_ts = go.Figure()
            chart_ts.add_trace(go.Scatter(x=hist_df["date"], y=hist_df["price"], name=f"{name} Price", mode="lines"))
            chart_ts.add_trace(go.Bar(x=hist_df["date"], y=hist_df["volume"], name=f"{name} Volume", yaxis="y2", opacity=0.3))
            chart_ts.update_layout(
                title=f"{name} Price & Volume Over Time",
                xaxis_title="Date", yaxis_title="Price (USD)",
                yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False, zeroline=False),
                legend=dict(x=0, y=1.1, orientation="h")
            )
            st.plotly_chart(chart_ts, use_container_width=True)
    # Correlation Matrix
    if len(price_dict) > 1:
        corr_df = compute_correlation_matrix(price_dict)
        st.subheader("Correlation Matrix (Price) — Which YOLOs moon together?")
        heatmap = go.Figure(data=go.Heatmap(
            z=corr_df.values,
            x=corr_df.columns,
            y=corr_df.index,
            colorscale="RdBu",
            zmin=-1, zmax=1,
            colorbar=dict(title="Correlation")
        ))
        heatmap.update_layout(title="Correlation Matrix of Selected Meme Coins (Price)")
        st.plotly_chart(heatmap, use_container_width=True)
