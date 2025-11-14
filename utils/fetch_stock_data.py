import yfinance as yf
import pandas as pd
from datetime import datetime

def get_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch historical stock data using yfinance.
    Returns a DataFrame with OHLCV values.
    """
    try:
        df = yf.download(symbol, start=start_date, end=end_date)
        df = df.reset_index()
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to fetch stock data for {symbol}. Error: {e}")


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds indicators: daily returns, moving averages, volatility.
    """
    df["Daily Return"] = df["Close"].pct_change()
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    
    df["Volatility"] = df["Daily Return"].rolling(window=20).std()

    return df


def extract_kpis(df: pd.DataFrame) -> dict:
    """
    Compute key performance indicators.
    """
    latest = df.iloc[-1]

    kpis = {
        "current_price": round(latest["Close"], 2),
        "day_high": round(latest["High"], 2),
        "day_low": round(latest["Low"], 2),
        "ma20": round(latest["MA20"], 2) if not pd.isna(latest["MA20"]) else None,
        "ma50": round(latest["MA50"], 2) if not pd.isna(latest["MA50"]) else None,
        "volatility": round(latest["Volatility"], 4) if not pd.isna(latest["Volatility"]) else None,
    }

    return kpis
