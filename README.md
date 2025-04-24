# Meme Coin Resilience Analyzer

A modern, educational, and AI-powered analytics platform for meme coins and large caps. Analyze, visualize, and simulate risk, correlation, sentiment, and more—now with explainable AI and forecasting tools!

---

## 🚀 Features

- **AI-Powered Coin Screener**: Get coin suggestions tailored to your risk appetite, sentiment, and correlation preferences. Includes explainable AI (SHAP) for transparency.
- **Forecasting (Coming Soon)**: Price and volatility forecasts using ARIMA, Prophet, and LSTM models.
- **Correlation Tools**: Pairwise and rolling correlations, heatmaps, clustering, and diversification scores.
- **Advanced Charts**: Candlestick, scatter, radar/spider, and price-vs-volume charts.
- **Backtesting**: SMA crossover and RSI strategies with interactive parameter tuning.
- **Portfolio Tracker**: Build, manage, and analyze custom portfolios with CSV import/export.
- **Watchlists**: Multi-asset tracking for price, volume, and news.
- **Whale Alerts**: Track large wallet transactions (API integration-ready).
- **Sentiment Analysis**: Social and market sentiment, with leaderboard and trending coins.
- **Trending & Volume/Liquidity**: Discover hot coins and analyze trading activity.
- **Derivatives Calculator**: Options pricing (Black-Scholes, Binomial, Monte Carlo) and Kelly criterion.
- **Education & Tooltips**: Every tool includes inline help, tips, and links to the Education section.
- **Accessibility & Mobile-First**: Colorblind-friendly, responsive, ARIA-compliant, and touch-friendly.

---

## 🧑‍💻 Quickstart

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # If forecasting/AI tools are used:
   pip install scikit-learn shap prophet statsmodels tensorflow
   ```
2. **Run the app**:
   ```bash
   streamlit run app.py
   # Or run any page directly:
   streamlit run pages/CoinScreener.py
   ```
3. **Open in your browser**: [http://localhost:8501](http://localhost:8501)

---

## 🛠️ Architecture
- Modular Streamlit pages in `/pages`
- Shared utilities in `/utils`
- Data caching for fast, consistent experience
- Easily extensible for new analytics, AI models, or data sources

---

## 📚 Education & Help
- Each page features inline tooltips and banners
- See the Education section for deep dives on analytics, risk, and crypto basics
- Contact: [Your GitHub/Discord/Email here]

---

## ⚠️ Disclaimer
All analytics and suggestions are for educational purposes only. Do your own research (DYOR) before investing in any digital asset.

## API Keys
- CoinGecko (required for live data)
- Alpha Vantage (optional for advanced analytics)
- Etherscan (optional for holder analysis)
- LunarCrush/Twitter (optional for sentiment)

## License
MIT
