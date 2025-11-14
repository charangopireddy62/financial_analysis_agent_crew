import os
import pandas as pd
import matplotlib.pyplot as plt
from utils.fetch_stock_data import fetch_stock_data, extract_kpis, create_price_chart, fetch_fundamentals
from utils.fetch_stock_data import (
    get_stock_data,
    compute_indicators,
    extract_kpis,
)

class DataAnalystAgent:
    """
    Fetches stock data, computes KPIs,
    generates charts, and returns analysis.
    """

    def __init__(self, output_dir="data/raw"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    

    def analyze_stock(self, stock_symbol, start_date, end_date):

        df = fetch_stock_data(stock_symbol, start_date, end_date)
        kpis = extract_kpis(df)
        chart_path = create_price_chart(df, stock_symbol)

        fundamentals = fetch_fundamentals(stock_symbol)

        return {
            "dataframe": df,
            "kpis": kpis,
            "fundamentals": fundamentals,
            "chart_path": chart_path
    }



    def generate_chart(self, df: pd.DataFrame, symbol: str) -> str:
        """
        Generates a price + moving average chart.
        Saves it to /data/raw and returns path.
        """
        plt.figure(figsize=(10, 5))
        plt.plot(df["Date"], df["Close"], label="Close Price")
        plt.plot(df["Date"], df["MA20"], label="20-Day MA")
        plt.plot(df["Date"], df["MA50"], label="50-Day MA")
        plt.legend()
        plt.title(f"{symbol} Price with Moving Averages")
        plt.xlabel("Date")
        plt.ylabel("Price")

        chart_path = os.path.join(self.output_dir, f"{symbol}_chart.png")
        plt.savefig(chart_path, dpi=300)
        plt.close()

        return chart_path


# Smoke test when run directly
if __name__ == "__main__":
    agent = DataAnalystAgent()
    result = agent.analyze_stock("TCS.NS", "2024-01-01", "2024-12-31")
    print(result["kpis"])
    print("Chart saved at:", result["chart_path"])
