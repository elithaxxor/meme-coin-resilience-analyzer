# Meme Coin Resilience Analyzer

A powerful, modular Streamlit app for analyzing meme coins, large caps, and market indices with advanced analytics, technical indicators, and multi-chain support.

## Features
- Live trending meme coin dashboard (multi-chain, powered by CoinGecko)
- Multi-chain analytics: Ethereum, Solana, BSC, Polygon, and more
- Volume & liquidity analytics with charts
- Holder & distribution analysis (Etherscan integration)
- Smart contract safety & scam detection (TokenSniffer integration)
- Community & social sentiment analytics (LunarCrush/Twitter/Reddit-ready)
- Whale & insider activity alerts (stub for whale tracking APIs)
- New listings & early discovery (DEXTools/Birdeye/CoinGecko-ready)
- Automated price alerts & watchlists (local CSV-backed)
- Educational content and community leaderboard
- 20+ technical indicators: Sharpe, RSI, MACD, Bollinger Bands, Stochastic, ADX, CCI, OBV, and more
- Customizable comparison of meme coins, large caps, VIX, and S&P 500
- Advanced charting: line, bar, heatmap, area, and more
- Rolling correlation, downloadable CSVs, and more

## Quickstart
1. Install requirements: `pip install -r requirements.txt`
2. Add your API keys to `config.py` (CoinGecko, Alpha Vantage, etc.)
3. (Optional) Add Etherscan, LunarCrush, or other API keys to Streamlit secrets for advanced features
4. Run the app: `streamlit run app.py`

## Example Screenshots
- Trending meme coins dashboard
- Technical indicator comparison
- Safety scanner & holder analysis

## API Keys
- CoinGecko (required for live data)
- Alpha Vantage (optional for advanced analytics)
- Etherscan (optional for holder analysis)
- LunarCrush/Twitter (optional for sentiment)

## License
MIT
