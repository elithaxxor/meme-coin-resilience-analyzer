import streamlit as st
import pandas as pd
from utils.coin_utils import get_coin_choices, get_price_history
from utils.ui import mobile_container, mobile_spacer
from main import calc_returns, moving_average, calc_rsi

with mobile_container():
    st.title("Backtesting & Strategy Simulation")
    st.markdown("""
    Simulate simple trading strategies (moving average crossovers, RSI thresholds) on meme coins and large caps. Analyze historical returns, drawdowns, and win rates.
    """)
    st.caption("ℹ️ See the Education page for strategy explanations and backtesting tips.")
    mobile_spacer(8)
    strategy = st.selectbox("Select Strategy", ["SMA Crossover", "RSI Overbought/Oversold"], help="Choose a backtesting strategy.")
    coin_choices = get_coin_choices()
    asset = st.selectbox(
        "Select Asset (autocomplete)",
        options=list(coin_choices.keys()),
        format_func=lambda x: coin_choices[x],
        help="Start typing to search for supported coins."
    )
    days = st.slider("Backtest Days", 30, 365, 90, help="How many days of historical data to use.")

    if asset:
        with st.spinner("Fetching price history..."):
            try:
                hist = get_price_history(asset, days=days)
                if hist is not None and not hist.empty:
                    price = hist.set_index("date")["price"]
                    st.line_chart(price)
                    if strategy == "SMA Crossover":
                        fast = st.slider("Fast SMA Window", 3, 30, 7)
                        slow = st.slider("Slow SMA Window", 10, 90, 21)
                        sma_fast = moving_average(price, window=fast, kind="sma")
                        sma_slow = moving_average(price, window=slow, kind="sma")
                        signals = (sma_fast > sma_slow).astype(int).diff().fillna(0)
                        st.line_chart(pd.DataFrame({"Price": price, "SMA Fast": sma_fast, "SMA Slow": sma_slow}))
                        st.write("Buy signals:", signals[signals == 1].count())
                        st.write("Sell signals:", signals[signals == -1].count())
                        returns = calc_returns(price)
                        strat_returns = returns * (signals.shift(1).fillna(0) > 0)
                        st.write("Backtested Return:", strat_returns.sum())
                    elif strategy == "RSI Overbought/Oversold":
                        window = st.slider("RSI Window", 7, 30, 14)
                        rsi = calc_rsi(price, window=window)
                        overbought = st.slider("Overbought Threshold", 60, 90, 70)
                        oversold = st.slider("Oversold Threshold", 10, 40, 30)
                        buy_signals = (rsi < oversold).astype(int).diff().fillna(0)
                        sell_signals = (rsi > overbought).astype(int).diff().fillna(0)
                        st.line_chart(pd.DataFrame({"Price": price, "RSI": rsi}))
                        st.write("Buy signals:", buy_signals[buy_signals == 1].count())
                        st.write("Sell signals:", sell_signals[sell_signals == 1].count())
                        returns = calc_returns(price)
                        strat_returns = returns * (buy_signals.shift(1).fillna(0) > 0)
                        st.write("Backtested Return:", strat_returns.sum())
                else:
                    st.warning(f"No data found for: {coin_choices[asset]}")
            except Exception as e:
                st.error(f"Error fetching price history: {e}")
    else:
        st.info("Select an asset to backtest.")
    st.markdown("<style>.stDataFrame th, .stDataFrame td { font-size: 1.1em; } .stCaption { color: #6c757d; } </style>", unsafe_allow_html=True)
    st.markdown('<a href="#top">Back to Top</a>', unsafe_allow_html=True)
