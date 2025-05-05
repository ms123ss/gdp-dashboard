import streamlit as st
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime

# Function to format AI signals for TradingView (Pine Script)
def format_pine_script(df):
    time_str = ",".join(df['formatted_time'])
    signal_str = ",".join(df['signal'])
    return time_str, signal_str

# Function to place a trade on Exness via MetaTrader5
def place_trade(symbol, action, lot_size):
    # Connect to MetaTrader 5
    if not mt5.initialize():
        st.error("MetaTrader 5 initialization failed")
        return
    # Create trade request
    if action == "buy":
        order_type = mt5.ORDER_TYPE_BUY
    elif action == "sell":
        order_type = mt5.ORDER_TYPE_SELL
    else:
        st.error("Invalid action")
        return

    price = mt5.symbol_info_tick(symbol).ask
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": order_type,
        "price": price,
        "sl": price - 10 * mt5.symbol_info(symbol).point,  # Example Stop Loss
        "tp": price + 10 * mt5.symbol_info(symbol).point,  # Example Take Profit
        "deviation": 10,
        "magic": 234000,
        "comment": "AI-generated trade",
        "type_filling": mt5.ORDER_FILLING_IOC,
        "type_time": mt5.ORDER_TIME_GTC,
    }

    # Send the trade request
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        st.error(f"Trade failed: {result.comment}")
    else:
        st.success(f"Trade executed: {action} at {price}")

# Web app UI (Streamlit)
st.title("AI Signal to TradingView + Exness/MT5")

# Upload CSV with AI signals (timestamp and buy/sell)
uploaded_file = st.file_uploader("Upload AI Signals CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df['formatted_time'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')

    # Display AI signals in the DataFrame
    st.write("AI Signals Data", df)

    # Format signals for TradingView Pine Script
    time_str, signal_str = format_pine_script(df)
    st.write(f"Copy these into Pine Script in TradingView:")
    st.text(f"Signal Times:\n\"{time_str}\"")
    st.text(f"Signal Directions:\n\"{signal_str}\"")

    # Optionally place trades in Exness (MT5) based on AI signal
    symbol = st.selectbox("Select Trading Symbol", ["XAUUSD", "EURUSD", "GBPUSD"])
    action = st.selectbox("Select Trade Action", ["buy", "sell"])
    lot_size = st.number_input("Enter Lot Size", min_value=0.01, max_value=100.0, value=0.1)
    
    if st.button("Place Trade on Exness/MT5"):
        place_trade(symbol, action, lot_size)

