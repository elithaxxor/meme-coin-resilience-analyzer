import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from utils.coin_utils import get_coin_choices, get_price_history
from utils.ui import mobile_container, mobile_spacer

with mobile_container():
    st.title("Advanced Chart Types")
    st.markdown("""
    Explore advanced charting: candlestick, scatter, radar/spider charts, and multi-axis plots for deep technical analysis.
    """)
    st.caption("ℹ️ Use the Education page for chart interpretation tips and best practices.")
    mobile_spacer(8)
    coin_choices = get_coin_choices()
    asset = st.selectbox(
        "Select Asset (autocomplete)",
        options=list(coin_choices.keys()),
        format_func=lambda x: coin_choices[x],
        help="Start typing to search for supported coins."
    )
    days = st.slider("Days of History", 30, 365, 90, help="How many days of historical data to chart.")
    chart_type = st.selectbox("Chart Type", ["Candlestick", "Scatter", "Radar/Spider", "Price vs Volume"], help="Choose the visualization type.")

    if asset:
        with st.spinner("Fetching price history..."):
            try:
                hist = get_price_history(asset, days=days)
                if hist is not None and not hist.empty:
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
                    st.warning(f"No data found for: {coin_choices[asset]}")
            except Exception as e:
                st.error(f"Error fetching price history: {e}")
    else:
        st.info("Select an asset to view charts.")
    st.markdown("<style>.stDataFrame th, .stDataFrame td { font-size: 1.1em; } .stCaption { color: #6c757d; } </style>", unsafe_allow_html=True)
    st.markdown('<a href="#top">Back to Top</a>', unsafe_allow_html=True)
