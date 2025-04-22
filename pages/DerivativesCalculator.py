import streamlit as st
from main import black_scholes_price, binomial_tree_price, kelly_criterion, monte_carlo_option_price, black_scholes_greeks
import plotly.graph_objs as go
import plotly.express as px
from utils.coin_utils import get_coin_choices
from utils.ui import mobile_container, mobile_spacer
from io import BytesIO
import base64
import pandas as pd

with mobile_container():
    st.title("Derivatives & Options Calculator")
    st.markdown("""
    Calculate fair values, Greeks, optimal bet sizing, and risk metrics for meme-stock and crypto derivatives. Choose a model and enter your parameters below.
    """)
    st.caption("ℹ️ All results are for educational purposes. See the [Education page](/Education) for model explanations and scenario guides.")
    mobile_spacer(8)
    coin_choices = get_coin_choices()
    asset = st.selectbox(
        "Select Underlying Asset (autocomplete)",
        options=list(coin_choices.keys()),
        format_func=lambda x: coin_choices[x],
        help="Start typing to search for supported coins."
    )
    model = st.selectbox("Choose Model", [
        "Black-Scholes (European Option)",
        "Binomial Tree (American Option)",
        "Kelly Criterion (Position Sizing)",
        "Monte Carlo (Option Pricing)"
    ], help="Select a derivatives model. See the Education page for details.")

    if model == "Black-Scholes (European Option)":
        S = st.number_input("Spot Price (S)", min_value=0.0, value=100.0, help="Current price of the underlying asset.")
        K = st.number_input("Strike Price (K)", min_value=0.0, value=100.0, help="Strike price of the option contract.")
        T = st.number_input("Time to Expiry (years, T)", min_value=0.01, value=0.5, help="Time until expiry, in years.")
        r = st.number_input("Risk-Free Rate (r, decimal)", min_value=0.0, value=0.01, help="Annualized risk-free interest rate. E.g., 0.05 for 5%.")
        sigma = st.number_input("Volatility (sigma, decimal)", min_value=0.0, value=0.5, help="Annualized volatility of the underlying asset. E.g., 0.7 for 70%.")
        option_type = st.selectbox("Option Type", ["call", "put"], help="Call = right to buy, Put = right to sell.")
        if st.button("Calculate Black-Scholes Price", help="Compute the theoretical option price using Black-Scholes model."):
            price = black_scholes_price(S, K, T, r, sigma, option_type)
            st.success(f"Black-Scholes {option_type.capitalize()} Price: {price:.4f}")
            greeks = black_scholes_greeks(S, K, T, r, sigma, option_type)
            st.subheader("Greeks")
            st.write({k: f"{v:.4f}" for k, v in greeks.items()})
            st.caption("Greeks measure sensitivity to market changes. See the [Education page](/Education) for full definitions.")
        st.markdown("---")
        st.subheader("Quick Reference: Black-Scholes Formula")
        st.caption("The Black-Scholes model gives the theoretical price of European options. Inputs: Spot, Strike, Time to Expiry, Risk-Free Rate, Volatility. See the Education page for a step-by-step example and interpretation.")
        st.latex(r"""
        C = S N(d_1) - K e^{-rT} N(d_2) \\
        P = K e^{-rT} N(-d_2) - S N(-d_1)
        """)
        st.caption("Where: $d_1 = \frac{\ln(S/K) + (r + \sigma^2/2)T}{\sigma\sqrt{T}}$, $d_2 = d_1 - \sigma\sqrt{T}$")
        st.markdown("---")
        st.subheader("Scenario Analysis: Option Price & Greeks vs Spot Price")
        st.caption("Explore how price and risk metrics change as the underlying asset moves.")
        spot_range = st.slider("Spot Price Range", int(S*0.5), int(S*1.5), (int(S*0.8), int(S*1.2)), help="Range of spot prices for scenario analysis.")
        spot_prices = [x for x in range(spot_range[0], spot_range[1]+1)]
        prices = [black_scholes_price(s, K, T, r, sigma, option_type) for s in spot_prices]
        fig = go.Figure(data=go.Scatter(x=spot_prices, y=prices, mode='lines', name='Option Price'))
        fig.update_layout(xaxis_title='Spot Price', yaxis_title='Option Price', title='Option Price vs Spot Price')
        st.plotly_chart(fig, use_container_width=True)
        # Download option price scenario
        csv = "Spot,OptionPrice\n" + "\n".join(f"{s},{p}" for s,p in zip(spot_prices, prices))
        st.download_button("Download Price Scenario (CSV)", csv.encode(), file_name="option_price_scenario.csv", mime="text/csv")
        # Greeks scenario
        greeks_data = {g: [] for g in ["delta", "gamma", "vega", "theta", "rho"]}
        for s in spot_prices:
            g = black_scholes_greeks(s, K, T, r, sigma, option_type)
            for k in greeks_data:
                greeks_data[k].append(g[k])
        greeks_fig = go.Figure()
        for k, v in greeks_data.items():
            greeks_fig.add_trace(go.Scatter(x=spot_prices, y=v, mode='lines', name=k.capitalize()))
        greeks_fig.update_layout(xaxis_title='Spot Price', yaxis_title='Greek Value', title='Greeks vs Spot Price')
        st.plotly_chart(greeks_fig, use_container_width=True)
        # Download Greeks scenario
        greeks_df = pd.DataFrame({"Spot": spot_prices, **greeks_data})
        greeks_csv = greeks_df.to_csv(index=False)
        st.download_button("Download Greeks Scenario (CSV)", greeks_csv.encode(), file_name="option_greeks_scenario.csv", mime="text/csv")
        # Export chart as PNG
        buf = BytesIO()
        fig.write_image(buf, format="png")
        st.download_button("Download Option Price Chart (PNG)", buf.getvalue(), file_name="option_price_chart.png", mime="image/png")
        buf2 = BytesIO()
        greeks_fig.write_image(buf2, format="png")
        st.download_button("Download Greeks Chart (PNG)", buf2.getvalue(), file_name="option_greeks_chart.png", mime="image/png")
        st.caption("You can download scenario data and charts for further analysis or reporting.")
        st.markdown("---")
        st.caption("Try adjusting expiry or interest rate for advanced scenario analysis.")
        expiry_range = st.slider("Expiry Range (years)", 1, 365, (int(T*365*0.5), int(T*365*1.5)), help="Vary time to expiry for scenario analysis.")
        expiry_days = list(range(expiry_range[0], expiry_range[1]+1, 5))
        expiry_prices = [black_scholes_price(S, K, d/365, r, sigma, option_type) for d in expiry_days]
        fig3 = go.Figure(data=go.Scatter(x=expiry_days, y=expiry_prices, mode='lines', name='Option Price'))
        fig3.update_layout(xaxis_title='Days to Expiry', yaxis_title='Option Price', title='Option Price vs Expiry')
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("See how the option price decays as expiry approaches (theta decay). Download for further analysis.")
        buf3 = BytesIO()
        fig3.write_image(buf3, format="png")
        st.download_button("Download Expiry Chart (PNG)", buf3.getvalue(), file_name="option_expiry_chart.png", mime="image/png")
        st.markdown("---")
        st.subheader("Advanced: 3D Surface Plot - Option Price vs Spot & Volatility")
        st.caption("Visualize how option price changes with both spot price and volatility. Useful for sensitivity analysis and risk management. See the Education page for interpretation.")
        spot_grid = list(range(spot_range[0], spot_range[1]+1, max(1, (spot_range[1]-spot_range[0])//20)))
        vol_grid = [v/100 for v in range(10, 101, 5)]
        z = []
        for s in spot_grid:
            row = [black_scholes_price(s, K, T, r, v, option_type) for v in vol_grid]
            z.append(row)
        fig4 = px.surface(
            x=vol_grid,
            y=spot_grid,
            z=z,
            labels={'x': 'Volatility', 'y': 'Spot Price', 'z': 'Option Price'},
            title='Option Price Surface (Spot vs Volatility)'
        )
        st.plotly_chart(fig4, use_container_width=True)
        st.caption("Hover to see exact values. Download for presentations or research.")
        buf4 = BytesIO()
        fig4.write_image(buf4, format="png")
        st.download_button("Download 3D Surface Chart (PNG)", buf4.getvalue(), file_name="option_surface_chart.png", mime="image/png")

    elif model == "Binomial Tree (American Option)":
        S = st.number_input("Spot Price (S)", min_value=0.0, value=100.0, key="bin_s", help="Current price of the underlying asset.")
        K = st.number_input("Strike Price (K)", min_value=0.0, value=100.0, key="bin_k", help="Strike price of the option contract.")
        T = st.number_input("Time to Expiry (years, T)", min_value=0.01, value=0.5, key="bin_t", help="Time until expiry, in years.")
        r = st.number_input("Risk-Free Rate (r, decimal)", min_value=0.0, value=0.01, key="bin_r", help="Annualized risk-free interest rate. E.g., 0.05 for 5%.")
        sigma = st.number_input("Volatility (sigma, decimal)", min_value=0.0, value=0.5, key="bin_sigma", help="Annualized volatility of the underlying asset. E.g., 0.7 for 70%.")
        steps = st.slider("Tree Steps", 10, 200, 50, help="Number of steps in the binomial tree.")
        option_type = st.selectbox("Option Type", ["call", "put"], key="bin_type", help="Call = right to buy, Put = right to sell.")
        if st.button("Calculate Binomial Tree Price", help="Compute the theoretical option price using binomial tree model."):
            price = binomial_tree_price(S, K, T, r, sigma, steps, option_type)
            st.success(f"Binomial Tree {option_type.capitalize()} Price: {price:.4f}")
        # --- Visualization: Price vs Underlying ---
        st.subheader("Scenario: Option Price vs Spot Price (Binomial)")
        st.caption("Explore how price changes as the underlying asset moves.")
        spot_range = st.slider("Spot Price Range (Binomial)", int(S*0.5), int(S*1.5), (int(S*0.8), int(S*1.2)), key="bin_spot_range", help="Range of spot prices for scenario analysis.")
        spot_prices = [x for x in range(spot_range[0], spot_range[1]+1)]
        prices = [binomial_tree_price(s, K, T, r, sigma, steps, option_type) for s in spot_prices]
        fig = go.Figure(data=go.Scatter(x=spot_prices, y=prices, mode='lines', name='Option Price (Binomial)'))
        fig.update_layout(xaxis_title='Spot Price', yaxis_title='Option Price', title='Binomial Option Price vs Spot Price')
        st.plotly_chart(fig, use_container_width=True)
        # Download option price scenario
        csv = "Spot,OptionPrice\n" + "\n".join(f"{s},{p}" for s,p in zip(spot_prices, prices))
        st.download_button("Download Price Scenario (CSV)", csv.encode(), file_name="binomial_option_price_scenario.csv", mime="text/csv")
        # Export chart as PNG
        buf = BytesIO()
        fig.write_image(buf, format="png")
        st.download_button("Download Binomial Option Price Chart (PNG)", buf.getvalue(), file_name="binomial_option_price_chart.png", mime="image/png")

    elif model == "Monte Carlo (Option Pricing)":
        S = st.number_input("Spot Price (S)", min_value=0.0, value=100.0, key="mc_s", help="Current price of the underlying asset.")
        K = st.number_input("Strike Price (K)", min_value=0.0, value=100.0, key="mc_k", help="Strike price of the option contract.")
        T = st.number_input("Time to Expiry (years, T)", min_value=0.01, value=0.5, key="mc_t", help="Time until expiry, in years.")
        r = st.number_input("Risk-Free Rate (r, decimal)", min_value=0.0, value=0.01, key="mc_r", help="Annualized risk-free interest rate. E.g., 0.05 for 5%.")
        sigma = st.number_input("Volatility (sigma, decimal)", min_value=0.0, value=0.5, key="mc_sigma", help="Annualized volatility of the underlying asset. E.g., 0.7 for 70%.")
        n_sim = st.number_input("Simulations", min_value=100, max_value=100000, value=10000, step=100, help="Number of simulations for Monte Carlo pricing.")
        option_type = st.selectbox("Option Type", ["call", "put"], key="mc_type", help="Call = right to buy, Put = right to sell.")
        if st.button("Run Monte Carlo Simulation", help="Compute the theoretical option price using Monte Carlo simulation."):
            price = monte_carlo_option_price(S, K, T, r, sigma, int(n_sim), option_type)
            st.success(f"Monte Carlo {option_type.capitalize()} Price: {price:.4f}")
        # --- Visualization: Price Distribution ---
        st.subheader("Scenario: Simulated Payoff Distribution")
        st.caption("Explore the distribution of simulated payoffs.")
        import numpy as np
        np.random.seed(42)
        ST = S * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * np.random.randn(int(n_sim)))
        if option_type == "call":
            payoffs = np.maximum(ST - K, 0)
        else:
            payoffs = np.maximum(K - ST, 0)
        fig = go.Figure(data=go.Histogram(x=payoffs, nbinsx=50, name="Payoff Distribution"))
        fig.update_layout(xaxis_title='Payoff', yaxis_title='Frequency', title='Monte Carlo Simulated Payoff Distribution')
        st.plotly_chart(fig, use_container_width=True)
        # Download payoff distribution
        csv = "Payoff,Frequency\n" + "\n".join(f"{p},{f}" for p,f in zip(fig.data[0].x, fig.data[0].y))
        st.download_button("Download Payoff Distribution (CSV)", csv.encode(), file_name="monte_carlo_payoff_distribution.csv", mime="text/csv")
        # Export chart as PNG
        buf = BytesIO()
        fig.write_image(buf, format="png")
        st.download_button("Download Monte Carlo Payoff Distribution Chart (PNG)", buf.getvalue(), file_name="monte_carlo_payoff_distribution_chart.png", mime="image/png")

    elif model == "Kelly Criterion (Position Sizing)":
        win_prob = st.number_input("Win Probability (0-1)", min_value=0.0, max_value=1.0, value=0.55, help="Probability of winning the trade.")
        win_loss_ratio = st.number_input("Win/Loss Ratio", min_value=0.01, value=2.0, help="Ratio of win to loss.")
        if st.button("Calculate Kelly Fraction", help="Compute the optimal fraction of capital to risk using Kelly criterion."):
            fraction = kelly_criterion(win_prob, win_loss_ratio)
            st.success(f"Optimal Fraction of Capital to Risk: {fraction:.4f}")
        # --- Scenario: Kelly Fraction vs Win Probability ---
        st.subheader("Scenario: Kelly Fraction vs Win Probability")
        st.caption("Explore how the optimal fraction changes as the win probability changes.")
        win_probs = [p/100 for p in range(1, 100)]
        fractions = [kelly_criterion(p, win_loss_ratio) for p in win_probs]
        fig = go.Figure(data=go.Scatter(x=win_probs, y=fractions, mode='lines', name='Kelly Fraction'))
        fig.update_layout(xaxis_title='Win Probability', yaxis_title='Kelly Fraction', title='Kelly Fraction vs Win Probability')
        st.plotly_chart(fig, use_container_width=True)
        # Download Kelly fraction scenario
        csv = "WinProbability,KellyFraction\n" + "\n".join(f"{p},{f}" for p,f in zip(win_probs, fractions))
        st.download_button("Download Kelly Fraction Scenario (CSV)", csv.encode(), file_name="kelly_fraction_scenario.csv", mime="text/csv")
        # Export chart as PNG
        buf = BytesIO()
        fig.write_image(buf, format="png")
        st.download_button("Download Kelly Fraction Chart (PNG)", buf.getvalue(), file_name="kelly_fraction_chart.png", mime="image/png")

    st.caption("Learn more about these models on the [Education page](/Education). Calculators are for educational purposes only.")
    st.markdown("""
    <style>
    .stCaption { color: #6c757d; font-size: 0.95em; }
    </style>
    """, unsafe_allow_html=True)
