import streamlit as st
import pandas as pd
import requests
import os
from utils.ui import mobile_container, mobile_spacer

LUNARCRUSH_API_KEY = os.environ.get("LUNARCRUSH_API_KEY") or st.secrets.get("LUNARCRUSH_API_KEY", "")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY") or st.secrets.get("NEWS_API_KEY", "")

@st.cache_data(show_spinner=False)
def get_lunarcrush_sentiment(symbol):
    if not LUNARCRUSH_API_KEY:
        return None
    url = f"https://api.lunarcrush.com/v2?data=assets&key={LUNARCRUSH_API_KEY}&symbol={symbol}"  # symbol = e.g. DOGE
    r = requests.get(url)
    if r.status_code == 200 and r.json().get('data'):
        return r.json()['data'][0]
    return None

@st.cache_data(show_spinner=False)
def get_news(query):
    if not NEWS_API_KEY:
        return []
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&language=en&sortBy=publishedAt&pageSize=10"
    r = requests.get(url)
    if r.status_code == 200 and r.json().get('articles'):
        return r.json()['articles']
    return []

from main import fetch_live_meme_coins
meme_coins = fetch_live_meme_coins()
coin_options = [c['symbol'] for c in meme_coins if c.get('symbol')]

with mobile_container():
    st.title("Sentiment & News Integration")
    st.markdown("""
    Track real-time sentiment and news for meme coins and large caps. View Twitter, Reddit, and Telegram scores, plus latest headlines and social buzz.\n
    **Note:** For full functionality, add API keys for LunarCrush, Twitter, or NewsAPI to your Streamlit secrets.
    """)
    mobile_spacer(8)

    selected_symbol = st.selectbox("Select Coin Symbol", coin_options)

    if selected_symbol:
        try:
            st.subheader(f"Sentiment for {selected_symbol}")
            sentiment = get_lunarcrush_sentiment(selected_symbol)
            if sentiment:
                st.write({k: v for k, v in sentiment.items() if k in ['alt_rank', 'galaxy_score', 'social_score', 'social_volume', 'price', 'volatility']})
            else:
                st.info("No sentiment data available (API key required or coin not tracked).")

            st.subheader(f"Latest News for {selected_symbol}")
            news_items = get_news(selected_symbol)
            if news_items:
                for article in news_items:
                    st.markdown(f"**[{article['title']}]({article['url']})**  ")
                    st.caption(f"{article['source']['name']} | {article['publishedAt']}")
                    st.write(article['description'])
            else:
                st.info("No news found or API key missing.")
        except Exception as e:
            st.error(f"Error loading sentiment news: {e}")
            st.info("Please check your internet connection, news sources, or try again later. If the issue persists, contact support.")

    st.caption("For Telegram/Reddit integration, add your API keys and see docs for setup.")
