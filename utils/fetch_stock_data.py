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
    Safely extracts last row and converts indicators to scalar values.
    """
    # Safely get the latest row (returns a single Series)
    latest = df.tail(1).squeeze()

    def safe(val):
        try:
            return round(float(val), 2)
        except:
            return None

    kpis = {
        "current_price": safe(latest.get("Close")),
        "day_high": safe(latest.get("High")),
        "day_low": safe(latest.get("Low")),
        "ma20": safe(latest.get("MA20")),
        "ma50": safe(latest.get("MA50")),
        "volatility": safe(latest.get("Volatility")),
    }

    return kpis
def fetch_fundamentals(symbol):
    tk = yf.Ticker(symbol)
    info = tk.info
    
    return {
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "market_cap": info.get("marketCap"),
        "beta": info.get("beta"),
        "pb_ratio": info.get("priceToBook"),
        "eps": info.get("trailingEps"),
        "dividend_yield": info.get("dividendYield"),
        "industry": info.get("industry"),
        "sector": info.get("sector"),
    }
import yfinance as yf

def fetch_fundamentals(symbol: str) -> dict:
    """
    Fetch fundamental indicators such as P/E, EPS, Beta, Market Cap, etc.
    using yfinance's ticker.info() dictionary.
    """

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info  # dictionary of fundamentals

        return {
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "eps": info.get("trailingEps"),
            "market_cap": info.get("marketCap"),
            "beta": info.get("beta"),
            "pb_ratio": info.get("priceToBook"),
            "sector": info.get("sector"),
            "industry": info.get("industry")
        }

    except Exception as e:
        return {"error": str(e)}

