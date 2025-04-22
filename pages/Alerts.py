import streamlit as st
import pandas as pd
import os
from utils.ui import mobile_container, mobile_spacer

with mobile_container():
    st.title("Alerting & Notifications")
    st.markdown("""
    Set up price, volume, or indicator-based alerts for meme coins and large caps. (Email/Telegram integration coming soon!)
    """)
    mobile_spacer(8)

    ALERTS_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'alerts.csv')

    def load_alerts():
        if os.path.exists(ALERTS_CSV):
            return pd.read_csv(ALERTS_CSV)
        else:
            return pd.DataFrame(columns=["asset", "type", "threshold", "direction", "created_on"])

    def save_alerts(df):
        df.to_csv(ALERTS_CSV, index=False)

    df = load_alerts()

    asset = st.text_input("Asset Name (as in app)")
    alert_type = st.selectbox("Alert Type", ["Price", "Volume", "Indicator"])
    direction = st.selectbox("Direction", [">", "<"])
    threshold = st.number_input("Threshold Value", min_value=0.0, format="%f")

    if st.button("Add Alert") and asset:
        df = pd.concat([df, pd.DataFrame([[asset, alert_type, threshold, direction, pd.Timestamp.now()]], columns=df.columns)])
        save_alerts(df)
        st.success("Alert added!")

    if not df.empty:
        st.subheader("Current Alerts")
        st.dataframe(df)
        remove_idx = st.selectbox("Remove Alert (row index)", df.index.tolist())
        if st.button("Remove Selected Alert"):
            df = df.drop(remove_idx)
            save_alerts(df)
            st.experimental_rerun()

    st.info("Email/Telegram notifications require API key setup. See documentation for details.")
