import streamlit as st
import pandas as pd
from main import fetch_coin_history, calc_returns, moving_average, calc_rsi
from utils.ui import mobile_container, mobile_spacer

with mobile_container():
    st.title("Backtesting & Strategy Simulation")
    st.markdown("""
    Simulate simple trading strategies (moving average crossovers, RSI thresholds) on meme coins and large caps. Analyze historical returns, drawdowns, and win rates.
    """)
    mobile_spacer(8)

    strategy = st.selectbox("Select Strategy", ["SMA Crossover", "RSI Overbought/Oversold"])
    asset = st.text_input("Coin Name (as in app)")
    days = st.slider("Backtest Days", 30, 365, 90)

    if asset:
        hist = fetch_coin_history(asset, days=days)
        if hist is not None:
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
            st.warning("No price history found for this asset.")
    else:
        st.info("Enter a coin name to begin.")
