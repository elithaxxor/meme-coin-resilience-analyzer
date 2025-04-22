import sys
from rich.console import Console
from rich.table import Table
from typing import Tuple
import requests
import argparse
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm

console = Console()

def get_input(prompt, cast_type=str, choices=None, default=None):
    while True:
        if default is not None:
            prompt_full = f"{prompt} [{default}]: "
        else:
            prompt_full = prompt
        val = input(prompt_full)
        if val == '' and default is not None:
            val = default
        try:
            val = cast_type(val)
            if choices and val not in choices:
                raise ValueError
            return val
        except Exception:
            console.print(f"[red]Invalid input. Please enter a valid value.[/red]")

def fetch_coingecko_data(coin_name):
    # Search for the coin by name
    search_url = f"https://api.coingecko.com/api/v3/search?query={coin_name}"
    try:
        resp = requests.get(search_url, timeout=10)
        data = resp.json()
        if not data['coins']:
            return None
        coin_id = data['coins'][0]['id']
        # Get coin market data
        coin_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=true&community_data=true&developer_data=false&sparkline=false"
        resp2 = requests.get(coin_url, timeout=10)
        coin_data = resp2.json()
        result = {
            'symbol': coin_data.get('symbol'),
            'price': coin_data['market_data']['current_price'].get('usd'),
            'volume': coin_data['market_data']['total_volume'].get('usd'),
            'market_cap': coin_data['market_data']['market_cap'].get('usd'),
            'liquidity_score': coin_data.get('liquidity_score'),
            'links': coin_data.get('links', {}),
            'community_score': coin_data.get('community_score'),
            'public_interest_score': coin_data.get('public_interest_score'),
            'categories': coin_data.get('categories', []),
            'staking_apy': 0,  # default value
        }
        return result
    except Exception as e:
        console.print(f"[red]Failed to fetch CoinGecko data: {e}[/red]")
        return None

def fetch_vix_history(period="1mo", interval="1d"):
    """Fetch VIX index historical data using yfinance."""
    try:
        vix = yf.download("^VIX", period=period, interval=interval, progress=False)
        return vix
    except Exception as e:
        console.print(f"[red]Failed to fetch VIX data: {e}[/red]")
        return None

def fetch_sp500_history(period="1mo", interval="1d"):
    """Fetch S&P 500 historical data using yfinance."""
    try:
        spx = yf.download("^GSPC", period=period, interval=interval, progress=False)
        return spx
    except Exception as e:
        console.print(f"[red]Failed to fetch S&P 500 data: {e}[/red]")
        return None

def fetch_vix_history_aligned(days=90):
    """Fetch VIX daily close for the last N days, as a DataFrame with 'date' and 'price'."""
    vix_df = fetch_vix_history(period=f"{days}d", interval="1d")
    if vix_df is not None and not vix_df.empty:
        df = vix_df.reset_index()[["Date", "Close"]].rename(columns={"Date": "date", "Close": "price"})
        df["date"] = pd.to_datetime(df["date"])
        return df
    return None

def fetch_sp500_history_aligned(days=90):
    spx_df = fetch_sp500_history(period=f"{days}d", interval="1d")
    if spx_df is not None and not spx_df.empty:
        df = spx_df.reset_index()[["Date", "Close"]].rename(columns={"Date": "date", "Close": "price"})
        df["date"] = pd.to_datetime(df["date"])
        return df
    return None

def fetch_live_meme_coins(per_page=50):
    """
    Fetches a live list of meme coins from CoinGecko with extended stats.
    Returns a list of dicts: [{id, symbol, name, price, market_cap, volume, price_change_24h, image, ath, atl, supply, launch_date}, ...]
    """
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "category": "meme-token",
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "24h"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        coins = []
        for coin in data:
            coins.append({
                "id": coin["id"],
                "symbol": coin["symbol"],
                "name": coin["name"],
                "price": coin["current_price"],
                "market_cap": coin["market_cap"],
                "volume": coin["total_volume"],
                "price_change_24h": coin.get("price_change_percentage_24h", 0),
                "image": coin.get("image", ""),
                "ath": coin.get("ath", None),
                "atl": coin.get("atl", None),
                "supply": coin.get("circulating_supply", None),
                "launch_date": coin.get("atl_date", None)
            })
        return coins
    except Exception as e:
        console.print(f"[red]Failed to fetch meme coin feed: {e}[/red]")
        return []

def fetch_coin_history(coin_id, days=30, vs_currency="usd"): 
    """Fetch historical price and volume for a coin from CoinGecko."""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": days, "interval": "daily"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        prices = data.get("prices", [])
        volumes = data.get("total_volumes", [])
        df = pd.DataFrame({
            "date": [pd.to_datetime(p[0], unit="ms") for p in prices],
            "price": [p[1] for p in prices],
            "volume": [v[1] for v in volumes]
        })
        return df
    except Exception as e:
        console.print(f"[red]Failed to fetch history for {coin_id}: {e}[/red]")
        return None

def fetch_large_cap_coins(limit=15):
    """Fetch top large cap cryptocurrencies from CoinGecko."""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": False
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        coins = []
        for c in data:
            coins.append({
                "id": c["id"],
                "name": c["name"],
                "symbol": c["symbol"].upper(),
                "price": c["current_price"],
                "market_cap": c["market_cap"],
                "volume": c["total_volume"],
                "price_change_24h": c.get("price_change_percentage_24h", 0),
                "ath": c.get("ath", "-"),
                "atl": c.get("atl", "-"),
                "supply": c.get("circulating_supply", "-"),
                "launch_date": c.get("atl_date", "-")
            })
        return coins
    except Exception as e:
        console.print(f"[red]Failed to fetch large cap coins: {e}[/red]")
        return []

def align_and_normalize_series(series_dict):
    """Given {name: pd.Series}, align on date and normalize to 1 at start."""
    df = pd.DataFrame(series_dict)
    df = df.dropna()
    normed = df / df.iloc[0]
    return normed

def rolling_volatility(series, window=7):
    return series.pct_change().rolling(window=window).std() * (window ** 0.5)

def moving_average(series, window=7, kind="sma"):
    if kind == "ema":
        return series.ewm(span=window, adjust=False).mean()
    return series.rolling(window=window).mean()

def compute_correlation_matrix(price_dict):
    """
    Given a dict {name: price_series}, compute the correlation matrix DataFrame.
    """
    df = pd.DataFrame(price_dict)
    return df.corr()

def prompt_factors(coin_name=None, prefill=None):
    if prefill is None:
        prefill = {}
    # Utility / Use Case
    console.print("\n[bold]--- Utility & Use Case ---[/bold]")
    utility = get_input("Does the coin have real utility? (yes/no): ", str, ['yes','no'], default='no') == 'yes'

    # Tokenomics & Fundamentals
    console.print("\n[bold]--- Tokenomics & Fundamentals ---[/bold]")
    tokenomics = {}
    tokenomics['deflationary'] = get_input("Deflationary? (yes/no): ", str, ['yes','no'], default='no') == 'yes'
    tokenomics['staking_apy'] = get_input("Staking APY (%): ", float, default=prefill.get('staking_apy', 0))
    tokenomics['team_locked'] = get_input("Team tokens locked > 1 year? (yes/no): ", str, ['yes','no'], default='no') == 'yes'
    tokenomics['fair_distribution'] = get_input("Fair token distribution? (yes/no): ", str, ['yes','no'], default='no') == 'yes'

    # Token Distribution
    whale_concentration = get_input("High whale concentration? (yes/no): ", str, ['yes','no'], default='no') == 'yes'

    # Liquidity & Trading Volume
    console.print("\n[bold]--- Liquidity & Trading Volume ---[/bold]")
    liquidity = {}
    liquidity['liquidity_usd'] = prefill.get('market_cap') or get_input("Liquidity pool size (USD): ", float, default=0)
    liquidity['liquidity_locked'] = get_input("Liquidity locked > 6 months? (yes/no): ", str, ['yes','no'], default='no') == 'yes'
    liquidity['daily_volume'] = prefill.get('volume') or get_input("24h trading volume (USD): ", float, default=0)
    liquidity['organic'] = get_input("Is liquidity organic (not project incentives)? (yes/no): ", str, ['yes','no'], default='no') == 'yes'

    # Social Sentiment & Community
    console.print("\n[bold]--- Social Sentiment & Community ---[/bold]")
    social = {}
    community_score = prefill.get('community_score')
    trending_default = 'yes' if (community_score is not None and community_score > 5) else 'no'
    social['trending'] = get_input("Trending on X/Twitter? (yes/no): ", str, ['yes','no'], default=trending_default) == 'yes'
    public_interest_score = prefill.get('public_interest_score')
    active_default = 'yes' if (public_interest_score is not None and public_interest_score > 0) else 'no'
    social['active_community'] = get_input("Active Telegram/Discord? (yes/no): ", str, ['yes','no'], default=active_default) == 'yes'
    meme_virality_default = 3
    social['meme_virality'] = get_input("Meme virality (1-5): ", int, [1,2,3,4,5], default=meme_virality_default)
    social['growth'] = get_input("Is the community growing? (yes/no): ", str, ['yes','no'], default='no') == 'yes'
    social['hype_volatility'] = get_input("Is the hype just a spike (not sustained)? (yes/no): ", str, ['yes','no'], default='no') == 'yes'

    # Macroeconomic Tailwinds
    console.print("\n[bold]--- Macroeconomic Tailwinds ---[/bold]")
    macro = {}
    macro['interest_rates_low'] = get_input("Interest rates low? (yes/no): ", str, ['yes','no'], default='no') == 'yes'
    macro['favorable_inflation'] = get_input("Favorable inflation? (yes/no): ", str, ['yes','no'], default='no') == 'yes'
    macro['regulatory_news'] = get_input("Recent positive regulatory news? (yes/no): ", str, ['yes','no'], default='no') == 'yes'

    # Transparency & Security
    console.print("\n[bold]--- Transparency & Security ---[/bold]")
    security = {}
    security['audited'] = get_input("Smart contract audited? (yes/no): ", str, ['yes','no'], default='no') == 'yes'
    security['doxxed_team'] = get_input("Team is doxxed? (yes/no): ", str, ['yes','no'], default='no') == 'yes'
    security['open_source'] = get_input("Open-source code? (yes/no): ", str, ['yes','no'], default='no') == 'yes'
    security['verified_contract'] = get_input("Is contract verified on-chain? (yes/no): ", str, ['yes','no'], default='no') == 'yes'
    security['active_dev'] = get_input("Is there active development (e.g. GitHub)? (yes/no): ", str, ['yes','no'], default='no') == 'yes'

    # Red Flags
    console.print("\n[bold]--- Red Flags ---[/bold]")
    red_flags = {}
    red_flags['renounced_ownership'] = get_input("Renounced contract ownership? (yes/no): ", str, ['yes','no'], default='no') == 'yes'
    red_flags['honeypot'] = get_input("Honeypot risk (can't sell)? (yes/no): ", str, ['yes','no'], default='no') == 'yes'
    red_flags['rugpull_pattern'] = get_input("Rug pull pattern detected? (yes/no): ", str, ['yes','no'], default='no') == 'yes'

    return utility, tokenomics, whale_concentration, liquidity, social, macro, security, red_flags

def weighted_score(utility, tokenomics, whale_concentration, liquidity, social, macro, security, red_flags):
    breakdown = {}
    total = 0
    # Utility (1)
    u_score = 1 if utility else 0
    breakdown['Utility/Use Case'] = u_score
    total += u_score
    # Tokenomics & Fundamentals (1)
    t_score = (
        0.3 * tokenomics['deflationary'] +
        0.2 * (tokenomics['staking_apy'] >= 50) +
        0.3 * tokenomics['team_locked'] +
        0.2 * tokenomics['fair_distribution']
    )
    breakdown['Tokenomics & Fundamentals'] = t_score
    total += t_score
    # Whale concentration (-1 if yes)
    w_score = -1 if whale_concentration else 0
    breakdown['Whale Concentration'] = w_score
    total += w_score
    # Liquidity & Trading Volume (1)
    l_score = (
        0.4 * (liquidity['liquidity_usd'] >= 500000) +
        0.2 * liquidity['liquidity_locked'] +
        0.2 * (liquidity['daily_volume'] >= 100000) +
        0.2 * liquidity['organic']
    )
    breakdown['Liquidity & Trading Volume'] = l_score
    total += l_score
    # Social Sentiment & Community (2)
    s_score = (
        0.4 * social['trending'] +
        0.4 * social['active_community'] +
        0.4 * (social['meme_virality'] / 5) +
        0.4 * social['growth'] -
        0.4 * social['hype_volatility']
    )
    breakdown['Social Sentiment & Community'] = s_score
    total += s_score
    # Macroeconomic Tailwinds (1)
    m_score = (
        0.34 * macro['interest_rates_low'] +
        0.33 * macro['favorable_inflation'] +
        0.33 * macro['regulatory_news']
    )
    breakdown['Macroeconomic Tailwinds'] = m_score
    total += m_score
    # Transparency & Security (2)
    sec_score = (
        0.3 * security['audited'] +
        0.2 * security['doxxed_team'] +
        0.2 * security['open_source'] +
        0.2 * security['verified_contract'] +
        0.1 * security['active_dev']
    ) * 2
    breakdown['Transparency & Security'] = sec_score
    total += sec_score
    # Red Flags (-2 per flag)
    rf_score = -2 * (red_flags['renounced_ownership'] + red_flags['honeypot'] + red_flags['rugpull_pattern'])
    breakdown['Red Flags'] = rf_score
    total += rf_score
    # Normalize to 0-10
    total = max(0, min(10, total))
    return total, breakdown

def forecast(score):
    if score >= 8:
        return "High breakout potential with strong macro tailwinds."
    elif score >= 6:
        return "Moderate potential; monitor market conditions."
    else:
        return "High risk; weak macro support."

def calc_returns(series):
    return series.pct_change()

def calc_cumulative_returns(series):
    return (1 + series.pct_change()).cumprod() - 1

def calc_volatility(series, window=7):
    return series.pct_change().rolling(window=window).std() * (window ** 0.5)

def calc_sharpe(series, risk_free_rate=0.0, window=30):
    rets = series.pct_change()
    excess = rets - risk_free_rate/252
    return excess.rolling(window).mean() / excess.rolling(window).std()

def calc_sortino(series, risk_free_rate=0.0, window=30):
    rets = series.pct_change()
    downside = rets[rets < 0].rolling(window).std()
    excess = rets - risk_free_rate/252
    return excess.rolling(window).mean() / downside

def calc_max_drawdown(series):
    roll_max = series.cummax()
    drawdown = (series - roll_max) / roll_max
    return drawdown.cummin()

def calc_beta(asset_series, benchmark_series, window=30):
    asset_ret = asset_series.pct_change()
    bench_ret = benchmark_series.pct_change()
    cov = asset_ret.rolling(window).cov(bench_ret)
    var = bench_ret.rolling(window).var()
    return cov / var

def calc_rsi(series, window=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.rolling(window).mean()
    ma_down = down.rolling(window).mean()
    rs = ma_up / ma_down
    return 100 - (100 / (1 + rs))

def calc_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def calc_bollinger(series, window=20, num_std=2):
    sma = series.rolling(window).mean()
    std = series.rolling(window).std()
    upper = sma + num_std * std
    lower = sma - num_std * std
    return sma, upper, lower

def calc_rolling_stat(series, window=7, stat="mean"):
    if stat == "mean":
        return series.rolling(window).mean()
    if stat == "std":
        return series.rolling(window).std()
    if stat == "min":
        return series.rolling(window).min()
    if stat == "max":
        return series.rolling(window).max()
    return series

def calc_skew(series, window=30):
    return series.rolling(window).apply(lambda x: pd.Series(x).skew(), raw=False)

def calc_kurt(series, window=30):
    return series.rolling(window).apply(lambda x: pd.Series(x).kurt(), raw=False)

def calc_var(series, quantile=0.05, window=30):
    return series.pct_change().rolling(window).apply(lambda x: np.percentile(x, 100*quantile), raw=False)

def calc_stochastic_oscillator(series, window=14):
    low_min = series.rolling(window=window).min()
    high_max = series.rolling(window=window).max()
    return 100 * (series - low_min) / (high_max - low_min)

def calc_williams_r(series, window=14):
    high_max = series.rolling(window=window).max()
    low_min = series.rolling(window=window).min()
    return -100 * (high_max - series) / (high_max - low_min)

def calc_obv(price_series, volume_series):
    obv = [0]
    for i in range(1, len(price_series)):
        if price_series.iloc[i] > price_series.iloc[i-1]:
            obv.append(obv[-1] + volume_series.iloc[i])
        elif price_series.iloc[i] < price_series.iloc[i-1]:
            obv.append(obv[-1] - volume_series.iloc[i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=price_series.index)

def calc_cci(series, window=20):
    sma = series.rolling(window=window).mean()
    mad = series.rolling(window=window).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
    cci = (series - sma) / (0.015 * mad)
    return cci

def calc_adx(high, low, close, window=14):
    # Calculate the Average Directional Index (ADX)
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=window).mean()
    plus_di = 100 * (plus_dm.rolling(window=window).sum() / atr)
    minus_di = abs(100 * (minus_dm.rolling(window=window).sum() / atr))
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.rolling(window=window).mean()
    return adx

# --- Derivatives & Futures Analytics ---
# (Imports for new indicators and models)
from scipy.stats import norm
import numpy as np

# --- Black-Scholes Option Pricing ---
def black_scholes_price(S, K, T, r, sigma, option_type="call"):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

# --- Binomial Tree Option Pricing (simple version) ---
def binomial_tree_price(S, K, T, r, sigma, steps=50, option_type="call"):
    dt = T / steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(r * dt) - d) / (u - d)
    disc = np.exp(-r * dt)
    prices = np.zeros(steps + 1)
    prices[0] = S * d ** steps
    for i in range(1, steps + 1):
        prices[i] = prices[i - 1] * u / d
    values = np.maximum(0, (prices - K) if option_type == "call" else (K - prices))
    for i in range(steps - 1, -1, -1):
        values[:-1] = disc * (p * values[1:] + (1 - p) * values[:-1])
    return values[0]

# --- Kelly Criterion ---
def kelly_criterion(win_prob, win_loss_ratio):
    return max(0, win_prob - (1 - win_prob) / win_loss_ratio)

# --- Monte Carlo Simulation for Option Pricing ---
def monte_carlo_option_price(S, K, T, r, sigma, n_sim=10000, option_type="call"):
    np.random.seed(42)
    ST = S * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * np.random.randn(n_sim))
    if option_type == "call":
        payoffs = np.maximum(ST - K, 0)
    else:
        payoffs = np.maximum(K - ST, 0)
    return np.exp(-r * T) * np.mean(payoffs)

# (Integrate these into analytics/backtesting/options modules as needed)

def price_to_ath(series, ath):
    return series / ath

def price_to_volume(series, volume_series):
    return series / volume_series

def main():
    parser = argparse.ArgumentParser(description="Meme Coin Resilience Analyzer")
    parser.add_argument('--coin', type=str, help='Coin name')
    parser.add_argument('--auto', action='store_true', help='Auto fetch and use CoinGecko data')
    args = parser.parse_args()

    console.print("[bold cyan]Meme Coin Resilience Analyzer[/bold cyan]")
    coin_name = args.coin or input("Enter coin name: ")
    fetch = args.auto or get_input("Fetch data from CoinGecko? (yes/no): ", str, ['yes','no'], default='yes') == 'yes'
    prefill = fetch_coingecko_data(coin_name) if fetch else None
    utility, tokenomics, whale_concentration, liquidity, social, macro, security, red_flags = prompt_factors(coin_name, prefill)
    score, breakdown = weighted_score(utility, tokenomics, whale_concentration, liquidity, social, macro, security, red_flags)
    forecast_msg = forecast(score)

    table = Table(title=f"Resilience Analysis for {coin_name}")
    table.add_column("Factor", style="bold")
    table.add_column("Score")
    for k, v in breakdown.items():
        table.add_row(k, f"{v:.2f}")
    table.add_row("[bold]Total[/bold]", f"[bold]{score:.2f}/10[/bold]")
    table.add_row("Forecast", forecast_msg)
    if breakdown.get('Red Flags', 0) < 0:
        console.print("[red bold]Warning: High-risk red flags detected![/red bold]")
    console.print(table)

    meme_coins = fetch_live_meme_coins()
    meme_coins_table = Table(title="Live Meme Coins Feed")
    meme_coins_table.add_column("Name", style="bold")
    meme_coins_table.add_column("Symbol")
    meme_coins_table.add_column("Price (USD)")
    meme_coins_table.add_column("Market Cap (USD)")
    meme_coins_table.add_column("Volume (USD)")
    meme_coins_table.add_column("Price Change (24h)")
    meme_coins_table.add_column("ATH")
    meme_coins_table.add_column("ATL")
    meme_coins_table.add_column("Supply")
    meme_coins_table.add_column("Launch Date")
    for coin in meme_coins:
        meme_coins_table.add_row(coin["name"], coin["symbol"], f"{coin['price']:.2f}", f"{coin['market_cap']:.2f}", f"{coin['volume']:.2f}", f"{coin['price_change_24h']:.2f}%", f"{coin['ath']}", f"{coin['atl']}", f"{coin['supply']}", f"{coin['launch_date']}")
    console.print(meme_coins_table)

    large_cap_coins = fetch_large_cap_coins()
    large_cap_coins_table = Table(title="Top Large Cap Coins")
    large_cap_coins_table.add_column("Name", style="bold")
    large_cap_coins_table.add_column("Symbol")
    large_cap_coins_table.add_column("Price (USD)")
    large_cap_coins_table.add_column("Market Cap (USD)")
    large_cap_coins_table.add_column("Volume (USD)")
    large_cap_coins_table.add_column("Price Change (24h)")
    large_cap_coins_table.add_column("ATH")
    large_cap_coins_table.add_column("ATL")
    large_cap_coins_table.add_column("Supply")
    large_cap_coins_table.add_column("Launch Date")
    for coin in large_cap_coins:
        large_cap_coins_table.add_row(coin["name"], coin["symbol"], f"{coin['price']:.2f}", f"{coin['market_cap']:.2f}", f"{coin['volume']:.2f}", f"{coin['price_change_24h']:.2f}%", f"{coin['ath']}", f"{coin['atl']}", f"{coin['supply']}", f"{coin['launch_date']}")
    console.print(large_cap_coins_table)

    # Fetch historical price data for selected coins
    selected_coins = get_input("Enter comma-separated coin IDs for historical price analysis: ", str).split(',')
    price_dict = {}
    for coin_id in selected_coins:
        coin_id = coin_id.strip()
        history = fetch_coin_history(coin_id)
        if history is not None:
            price_dict[coin_id] = history['price']
    
    # Compute correlation matrix
    correlation_matrix = compute_correlation_matrix(price_dict)
    console.print(correlation_matrix)

if __name__ == "__main__":
    main()
