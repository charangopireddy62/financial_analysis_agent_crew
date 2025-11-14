import yfinance as yf
import pandas as pd
import os
import matplotlib.pyplot as plt


# ----------------------------------------------------
# 1. Fetch OHLCV Historical Prices + Add Indicators
# ----------------------------------------------------
def fetch_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    df = yf.download(symbol, start=start_date, end=end_date, auto_adjust=True)

    if df.empty:
        raise ValueError(f"No stock data found for {symbol}")

    # Reset index for easier manipulation
    df = df.reset_index()

    # -------------------------
    # Add Indicators (MA20/MA50)
    # -------------------------
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()

    # -------------------------
    # Volatility (20-day Std Dev)
    # -------------------------
    df["Volatility"] = df["Close"].rolling(window=20).std()

    return df


# ----------------------------------------------------
# 2. Compute KPIs Safely (Avoid Series ambiguity)
# ----------------------------------------------------
def extract_kpis(df):
    if df is None or df.empty:
        return {
            "current_price": None,
            "day_high": None,
            "day_low": None,
            "ma20": None,
            "ma50": None,
            "volatility": None
        }

    latest = df.iloc[-1]  # last row

    def safe_scalar(val):
        """Ensure the KPI value is always a scalar float."""
        if hasattr(val, "__len__") and not isinstance(val, (float, int)):
            val = val.iloc[-1]  # take last element if Series

        if pd.isna(val):
            return None

        return round(float(val), 4)

    return {
        "current_price": safe_scalar(latest["Close"]),
        "day_high": safe_scalar(latest["High"]),
        "day_low": safe_scalar(latest["Low"]),
        "ma20": safe_scalar(latest["MA20"]),
        "ma50": safe_scalar(latest["MA50"]),
        "volatility": safe_scalar(latest["Volatility"]),
    }


# ----------------------------------------------------
# 3. Price Chart PNG Generator
# ----------------------------------------------------
def create_price_chart(df: pd.DataFrame, symbol: str) -> str:
    os.makedirs("data/raw", exist_ok=True)
    chart_path = f"data/raw/{symbol}_chart.png"

    plt.figure(figsize=(10, 5))
    plt.plot(df["Date"], df["Close"], label="Close Price")

    # Add MAs if present
    if "MA20" in df.columns:
        plt.plot(df["Date"], df["MA20"], label="MA20")
    if "MA50" in df.columns:
        plt.plot(df["Date"], df["MA50"], label="MA50")

    plt.title(f"{symbol} Price Chart")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return chart_path


# ----------------------------------------------------
# 4. Fetch Company Fundamentals (P/E, EPS, MarketCap…)
# ----------------------------------------------------
def fetch_fundamentals(symbol: str) -> dict:
    ticker = yf.Ticker(symbol)

    try:
        info = ticker.info  # (yfinance fundamentals)
    except Exception:
        return {}

    fundamentals = {
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "eps": info.get("trailingEps"),
        "beta": info.get("beta"),
        "book_value": info.get("bookValue"),
        "dividend_yield": info.get("dividendYield"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
    }

    return fundamentals




