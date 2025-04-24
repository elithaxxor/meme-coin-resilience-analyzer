import streamlit as st
import pandas as pd
import os

st.title("Community Voting & Leaderboards")
st.markdown("""
Vote for your favorite meme coins and see live leaderboards for most hyped, best performing, and most discussed coins!
""")

VOTES_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'votes.csv')

if not os.path.exists(os.path.dirname(VOTES_CSV)):
    os.makedirs(os.path.dirname(VOTES_CSV))

def load_votes():
    if os.path.exists(VOTES_CSV):
        return pd.read_csv(VOTES_CSV)
    else:
        return pd.DataFrame(columns=["coin", "user", "vote", "timestamp"])

def save_votes(df):
    df.to_csv(VOTES_CSV, index=False)

from main import fetch_live_meme_coins

try:
    meme_coins = fetch_live_meme_coins()
    coin_options = [c['name'] for c in meme_coins]
    user = st.text_input("Your Username (for leaderboard)")
    selected_coin = st.selectbox("Vote for a Meme Coin", coin_options)
    if st.button("Vote") and user and selected_coin:
        df = load_votes()
        df = pd.concat([df, pd.DataFrame([[selected_coin, user, 1, pd.Timestamp.now()]], columns=df.columns)])
        save_votes(df)
        st.success("Vote submitted!")
    st.subheader("Live Leaderboard (Most Voted)")
    df = load_votes()
    if not df.empty:
        leaderboard = df.groupby('coin').vote.sum().sort_values(ascending=False).reset_index()
        st.dataframe(leaderboard)
    else:
        st.info("No votes yet.")
except Exception as e:
    st.error(f"Error loading community data: {e}")
    st.info("Please check your internet connection, data sources, or try again later. If the issue persists, contact support.")
st.markdown('<a href="#top">Back to Top</a>', unsafe_allow_html=True)
