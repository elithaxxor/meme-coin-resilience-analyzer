import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from main import fetch_coin_history
from utils.ui import mobile_container, mobile_spacer

with mobile_container():
    st.title("Advanced Chart Types")
    st.markdown("""
    Explore advanced charting: candlestick, scatter, radar/spider charts, and multi-axis plots for deep technical analysis.
    """)
    mobile_spacer(8)
    asset = st.text_input("Coin Name (as in app)")
    days = st.slider("Days of History", 30, 365, 90)
    chart_type = st.selectbox("Chart Type", ["Candlestick", "Scatter", "Radar/Spider", "Price vs Volume"])

    if asset:
        hist = fetch_coin_history(asset, days=days)
        if hist is not None:
            df = hist.set_index("date")
            if chart_type == "Candlestick":
                # For demo, use price as open/high/low/close
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['price'], high=df['price'], low=df['price'], close=df['price'])])
                st.plotly_chart(fig, use_container_width=True)
            elif chart_type == "Scatter":
                fig = go.Figure(data=go.Scatter(x=df.index, y=df['price'], mode='markers'))
                st.plotly_chart(fig, use_container_width=True)
            elif chart_type == "Radar/Spider":
                stats = [df['price'].max(), df['price'].min(), df['price'].mean(), df['price'].std()]
                categories = ['Max', 'Min', 'Mean', 'Std']
                fig = go.Figure(data=go.Scatterpolar(r=stats, theta=categories, fill='toself'))
                st.plotly_chart(fig, use_container_width=True)
            elif chart_type == "Price vs Volume" and 'volume' in df:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['price'], name='Price', yaxis='y1'))
                fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='Volume', yaxis='y2', opacity=0.3))
                fig.update_layout(yaxis2=dict(overlaying='y', side='right', title='Volume'), yaxis=dict(title='Price'))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No price history found for this asset.")
    else:
        st.info("Enter a coin name to begin.")
