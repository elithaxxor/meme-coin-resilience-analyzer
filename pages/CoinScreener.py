import streamlit as st
import pandas as pd
import numpy as np
from utils.coin_utils import get_coin_choices, get_price_history
from utils.ui import mobile_container, mobile_spacer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
import shap

@st.cache_data(ttl=600)
def get_demo_features():
    # This would be replaced by actual API calls and feature engineering
    np.random.seed(42)
    coins = get_coin_choices()
    n = len(coins)
    df = pd.DataFrame({
        'symbol': list(coins.keys()),
        'name': list(coins.values()),
        'volatility': np.random.uniform(0.05, 0.8, n),
        'avg_volume': np.random.uniform(1e5, 1e8, n),
        'sentiment': np.random.uniform(-1, 1, n),
        'correlation_btc': np.random.uniform(-1, 1, n),
        'recent_return': np.random.uniform(-0.5, 2.0, n)
    })
    return df

def score_coins(df, risk_level):
    # Simple scoring logic for demo; replace with ML model in production
    weights = {
        'Low':   {'volatility': -2, 'sentiment': 2, 'correlation_btc': -1, 'recent_return': 1},
        'Medium':{'volatility': -1, 'sentiment': 2, 'correlation_btc': -0.5, 'recent_return': 1.5},
        'High':  {'volatility': 1, 'sentiment': 2, 'correlation_btc': 0.5, 'recent_return': 2}
    }[risk_level]
    scaler = MinMaxScaler()
    features = ['volatility', 'sentiment', 'correlation_btc', 'recent_return']
    df_scaled = pd.DataFrame(scaler.fit_transform(df[features]), columns=features)
    score = sum(df_scaled[f] * w for f, w in weights.items())
    return score

def explain_scores(df, score):
    # Use SHAP for simple explainability (demo)
    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    y = (score > np.median(score)).astype(int)  # Fix: use np.median for correct threshold
    clf.fit(df, y)
    explainer = shap.Explainer(clf, df)
    shap_values = explainer(df)
    return shap_values

with mobile_container():
    st.title("AI-Powered Coin Screener")
    st.markdown("""
    Discover meme coins tailored to your risk appetite, using AI to blend risk, sentiment, and correlation factors. All suggestions are for educational purposes only.
    """)
    st.caption("ℹ️ Screener uses demo data for now. In production, it will use live sentiment, volume, and price feeds.")
    mobile_spacer(8)
    try:
        risk = st.selectbox("Select Risk Appetite", ["Low", "Medium", "High"], help="Low = stable, High = moonshot.")
        filter_sentiment = st.slider("Minimum Sentiment", -1.0, 1.0, -0.2, step=0.05, help="Filter for coins with at least this sentiment score.")
        filter_corr = st.slider("Max Correlation to BTC", -1.0, 1.0, 0.8, step=0.05, help="Screen out coins that move too closely with BTC.")
        df = get_demo_features()
        df = df[df['sentiment'] >= filter_sentiment]
        df = df[df['correlation_btc'] <= filter_corr]
        features = ['volatility', 'sentiment', 'correlation_btc', 'recent_return']
        score = score_coins(df, risk)
        df['AI Score'] = score
        top = df.sort_values("AI Score", ascending=False).head(10)
        st.subheader("Top Coin Suggestions")
        st.dataframe(top[["name", "symbol", "AI Score", "volatility", "sentiment", "correlation_btc", "recent_return"]], use_container_width=True, hide_index=True)
        st.caption("Scores are relative and for educational/demo purposes only.")
        # Explainability (SHAP summary)
        st.subheader("Why these coins?")
        st.markdown("Feature importances are shown for the top-ranked coin.")
        try:
            shap_values = explain_scores(top[features], top["AI Score"])
            shap.plots.bar(shap_values[0], show=False)
            st.pyplot(shap.plots.bar(shap_values[0], show=False))
        except Exception as e:
            st.info(f"Explainability demo not available: {e}")
    except Exception as e:
        st.error(f"An error occurred in the Coin Screener: {e}")
        st.info("Please check your internet connection, data sources, or try again later. If the issue persists, contact support.")
    st.markdown("<style>.stDataFrame th, .stDataFrame td { font-size: 1.1em; } .stCaption { color: #6c757d; } </style>", unsafe_allow_html=True)
    st.markdown('<a href="#top">Back to Top</a>', unsafe_allow_html=True)
