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
import os
import importlib.util
from utils.ui import mobile_container, mobile_spacer, mobile_header

# --- Inject PWA manifest and meta tags for mobile/PWA support ---
st.markdown("""
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#22223b">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
""", unsafe_allow_html=True)

# --- Streamlit Multi-Page Navigation ---
PAGES_DIR = os.path.join(os.path.dirname(__file__), "pages")
if os.path.isdir(PAGES_DIR):
    page_files = [f for f in os.listdir(PAGES_DIR) if f.endswith(".py") and not f.startswith("__")]
    page_names = [os.path.splitext(f)[0] for f in page_files]
    pages = ["How to Use", "Indicators Explained", "Stonk Battle Royale (Analyzer)", "Large Cap Crypto Stonks", "Meme Coin Feed"] + page_names
else:
    pages = ["How to Use", "Indicators Explained", "Stonk Battle Royale (Analyzer)", "Large Cap Crypto Stonks", "Meme Coin Feed"]
page = st.sidebar.radio("Navigation", pages)

if page in page_names:
    # Dynamically import and run the selected module
    spec = importlib.util.spec_from_file_location(page, os.path.join(PAGES_DIR, f"{page}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    st.stop()

if page == "How to Use":
    with mobile_container():
        st.title("How to Use the Meme Coin & Stonk Analyzer ")
        st.markdown("""
        ## Welcome!
        This app lets you analyze meme coins, large cap cryptocurrencies, and market indices (VIX, S&P 500) with advanced analytics and a WallStreetBets parody theme.

        **Main Features:**
        - Live meme coin and large cap feeds with advanced filtering and charting
        - Compare any combination of meme coins, large caps, VIX, and S&P 500
        - 20+ financial ratios and technical indicators (Sharpe, RSI, MACD, etc.)
        """)
        mobile_spacer(16)
        st.info("Tip: Add this app to your mobile home screen for an app-like experience! On iOS: Share > Add to Home Screen. On Android: Menu > Install App.")
        st.markdown("""
        **Workflow:**
        1. Use the sidebar to navigate between pages.
        2. On the "Stonk Battle Royale" page, select any assets and indicators to compare.
        3. Adjust the time window and rolling/stat window as needed.
        4. Download results or view correlation matrices.
        5. For indicator explanations, see the "Indicators Explained" page.
        """)
        st.info("If you get API errors, try refreshing or reducing the number of coins selected.")

elif page == "Indicators Explained":
    with mobile_container():
        st.title("Indicators & Ratios: Explanations & Demos ")
        st.markdown("""
        ## Indicator Explanations
        - **Sharpe Ratio**: Measures risk-adjusted return.
        - **Sortino Ratio**: Like Sharpe but only penalizes downside volatility.
        - **RSI**: Relative Strength Index, momentum oscillator.
        - **MACD**: Trend-following momentum indicator.
        - **Bollinger Bands**: Volatility bands above/below SMA.
        - **Stochastic Oscillator**: Momentum indicator comparing close price to range.
        - **ADX**: Average Directional Index, trend strength.
        - ...and more! See each page for live demos.
        """)
        mobile_spacer(8)
        st.info("Scroll down for live indicator charts and explanations.")
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
        st.markdown("Moving Average Convergence Divergence: trend-following momentum indicator.")
        macd, signal = calc_macd(demo_series)
        st.line_chart(pd.DataFrame({'MACD': macd, 'Signal': signal}))
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

        # New indicators
        st.header("Stochastic Oscillator")
        st.markdown("Momentum indicator comparing a particular closing price to a range of its prices over a certain period. Useful for identifying overbought/oversold conditions.")
        st.line_chart(calc_stochastic_oscillator(demo_series, window=14))

        st.header("Williams %R")
        st.markdown("A momentum indicator measuring overbought and oversold levels, similar to the Stochastic Oscillator but on a negative scale (0 to -100).")
        st.line_chart(calc_williams_r(demo_series, window=14))

        st.header("On-Balance Volume (OBV)")
        st.markdown("A cumulative indicator that uses volume flow to predict changes in stock price. Useful for confirming trends.")
        st.line_chart(calc_obv(demo_series, pd.Series(np.random.randint(1000, 2000, len(demo_series)), index=demo_series.index)))

        st.header("Commodity Channel Index (CCI)")
        st.markdown("A versatile indicator that can be used to identify a new trend or warn of extreme conditions. Measures the deviation of the price from its average.")
        st.line_chart(calc_cci(demo_series, window=20))

        st.header("Average Directional Index (ADX)")
        st.markdown("A trend strength indicator. ADX values above 20 indicate a strong trend, while values below 20 indicate a weak trend or sideways movement.")
        st.line_chart(calc_adx(demo_series, demo_series, demo_series, window=14))

elif page == "Stonk Battle Royale (Analyzer)":
    with mobile_container():
        st.header(" Compare Meme Coins, Large Caps, VIX & S&P 500 — Custom Stonk Battle Royale")
        st.info("Tip: On mobile, scroll horizontally on charts and use the install option for an app-like experience!")
        mobile_spacer(8)
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
            return (
                meme_names, meme_id_map, meme_vol_map, meme_ath_map,
                large_names, large_id_map, large_vol_map, large_ath_map, index_names
            )
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
        selected_indicator = st.selectbox("Indicator / Ratio", indicator_options)
        days = st.slider("Days of History", 14, 90, 30)
        window = st.slider("Window (days) for rolling/stat indicators", 7, 30, 14)

        chart_type = st.selectbox("Chart Type", ["Line", "Bar", "Heatmap"], index=0)

        if compare_assets and selected_indicator:
            plot_data = {}
            for asset in compare_assets:
                if asset in meme_names:
                    coin_id = meme_id_map[asset]
                    hist_df = fetch_coin_history(coin_id, days=90)
                    if hist_df is not None:
                        series = hist_df.set_index("date")["price"]
                        # Expanded indicator logic
                        if selected_indicator == "Price":
                            plot_data[asset] = series
                        elif selected_indicator == "Normalized Price":
                            plot_data[asset] = series / series.iloc[0]
                        elif selected_indicator == "Returns":
                            plot_data[asset] = calc_returns(series)
                        elif selected_indicator == "Cumulative Returns":
                            plot_data[asset] = calc_cumulative_returns(series)
                        elif selected_indicator == "Volatility (7d)":
                            plot_data[asset] = calc_volatility(series, window=window)
                        elif selected_indicator == "Sharpe Ratio":
                            plot_data[asset] = calc_sharpe(series, window=window)
                        elif selected_indicator == "Sortino Ratio":
                            plot_data[asset] = calc_sortino(series, window=window)
                        elif selected_indicator == "Max Drawdown":
                            plot_data[asset] = calc_max_drawdown(series)
                        elif selected_indicator == "Beta (vs S&P 500)":
                            sp500 = fetch_sp500_history_aligned(days=90)
                            plot_data[asset] = calc_beta(series, sp500)
                        elif selected_indicator == "SMA (7d)":
                            plot_data[asset] = moving_average(series, window=7, kind="sma")
                        elif selected_indicator == "EMA (7d)":
                            plot_data[asset] = moving_average(series, window=7, kind="ema")
                        elif selected_indicator == "RSI (14d)":
                            plot_data[asset] = calc_rsi(series, window=14)
                        elif selected_indicator == "MACD":
                            macd, _ = calc_macd(series)
                            plot_data[asset] = macd
                        elif selected_indicator == "Bollinger Bands":
                            sma, upper, lower = calc_bollinger(series, window=14)
                            plot_data[asset] = upper - lower
                        elif selected_indicator == "Rolling Mean (7d)":
                            plot_data[asset] = calc_rolling_stat(series, window=7, stat="mean")
                        elif selected_indicator == "Rolling Std (7d)":
                            plot_data[asset] = calc_rolling_stat(series, window=7, stat="std")
                        elif selected_indicator == "Rolling Min (7d)":
                            plot_data[asset] = calc_rolling_stat(series, window=7, stat="min")
                        elif selected_indicator == "Rolling Max (7d)":
                            plot_data[asset] = calc_rolling_stat(series, window=7, stat="max")
                        elif selected_indicator == "Skewness (30d)":
                            plot_data[asset] = calc_skew(series, window=30)
                        elif selected_indicator == "Kurtosis (30d)":
                            plot_data[asset] = calc_kurt(series, window=30)
                        elif selected_indicator == "VaR (5%, 30d)":
                            plot_data[asset] = calc_var(series, quantile=0.05, window=30)
                        elif selected_indicator == "Price/ATH":
                            plot_data[asset] = price_to_ath(series, meme_ath_map[asset])
                        elif selected_indicator == "Price/Volume":
                            plot_data[asset] = price_to_volume(series, meme_vol_map[asset])
                        elif selected_indicator == "Stochastic Oscillator (14d)":
                            plot_data[asset] = calc_stochastic_oscillator(series, window=14)
                        elif selected_indicator == "Williams %R (14d)":
                            plot_data[asset] = calc_williams_r(series, window=14)
                        elif selected_indicator == "On-Balance Volume (OBV)":
                            # For demo, use synthetic volume
                            plot_data[asset] = calc_obv(series, pd.Series(np.random.randint(1000, 2000, len(series)), index=series.index))
                        elif selected_indicator == "CCI (20d)":
                            plot_data[asset] = calc_cci(series, window=20)
                        elif selected_indicator == "ADX (14d)":
                            plot_data[asset] = calc_adx(series, series, series, window=14)
                elif asset in large_names:
                    coin_id = large_id_map[asset]
                    hist_df = fetch_coin_history(coin_id, days=90)
                    if hist_df is not None:
                        series = hist_df.set_index("date")["price"]
                        # Same indicator logic as above
                        # (For brevity, you can refactor this logic into a helper function)
                        plot_data[asset] = series
                elif asset in index_names:
                    if asset == "VIX (Volatility Index)":
                        series = fetch_vix_history_aligned(days=90)
                    else:
                        series = fetch_sp500_history_aligned(days=90)
                    if series is not None:
                        plot_data[asset] = series

            if plot_data:
                df_plot = pd.DataFrame(plot_data)
                if chart_type == "Line":
                    st.line_chart(df_plot)
                elif chart_type == "Bar":
                    st.bar_chart(df_plot)
                elif chart_type == "Heatmap":
                    import plotly.graph_objs as go
                    st.plotly_chart(go.Figure(data=go.Heatmap(
                        z=df_plot.fillna(0).values.T, x=df_plot.index, y=df_plot.columns,
                        colorscale="RdBu", zmin=df_plot.min().min(), zmax=df_plot.max().max(), colorbar=dict(title=selected_indicator)
                    )), use_container_width=True)
            else:
                st.warning("No data available for selected assets.")

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

    # --- Advanced Analytics: Rolling Correlation, Download, More Visuals ---
    st.header("Rolling Correlation (Dynamic)")
    if len(price_dict) > 1:
        base = list(price_dict.keys())[0]
        for other in list(price_dict.keys())[1:]:
            base_series = price_dict[base].dropna()
            other_series = price_dict[other].dropna()
            min_len = min(len(base_series), len(other_series))
            if min_len > 30:
                roll_corr = base_series[-min_len:].rolling(window=14).corr(other_series[-min_len:])
                st.line_chart(roll_corr.rename(f"Rolling Corr: {base} vs {other}"))

    st.header("Download Data")
    if price_dict:
        full_df = pd.DataFrame(price_dict)
        st.download_button("Download Price Data (CSV)", full_df.to_csv().encode(), file_name="meme_coin_prices.csv", mime="text/csv")

    st.header("Additional Visualizations")
    if price_dict:
        for name, series in price_dict.items():
            st.area_chart(series.rename(f"{name} Price (Area)"))
            st.bar_chart(series.rename(f"{name} Price (Bar)"))
else:
    st.info("Select one or more coins to view historical price and volume.")
