import os
import requests
from typing import List, Dict, Any

# Load OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


class ReportWriterAgent:
    """
    Generates a clean, factual, structured financial analysis report
    using Google's Gemma 3 12B via OpenRouter.
    """

    def __init__(self, model="google/gemma-3-12b-it"):
        self.model = model
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"

    # Format news nicely before passing to LLM
    def _format_news_section(self, news_items: List[Dict[str, Any]]) -> str:
        lines = []
        for i, item in enumerate(news_items, 1):
            title = item.get("title", "")
            sentiment = item.get("sentiment", {}).get("label", "neutral")
            url = item.get("url", "")
            lines.append(
                f"{i}. {title}\n   Sentiment: {sentiment}\n   Link: {url}"
            )
        return "\n".join(lines)

    # Core method to generate report
    def write_report(
        self,
        stock_symbol: str,
        kpis: Dict[str, Any],
        news_items: List[Dict[str, Any]],
        sentiment_summary: Dict[str, Any],
        chart_path: str,
        start_date: str,
        end_date: str,
    ) -> str:

        news_section = self._format_news_section(news_items)

        # Highly optimized prompt for Gemma 3 12B
        prompt = f"""
You are a professional financial analyst. Write a **clean, factual, and structured** equity research–style report 
for the stock **{stock_symbol}** covering the date range **{start_date} → {end_date}**.

You MUST strictly follow this structure:

1. Executive Summary  
2. Price Performance Overview  
3. Key Indicators (KPIs)  
4. Market Sentiment Analysis  
5. Recent News Highlights  
6. Risks and Opportunities  
7. Final Recommendation  

Use the following provided data WITHOUT inventing anything:

### KPIs
{kpis}

### Sentiment Summary
{sentiment_summary}

### Recent News
{news_section}

### Chart File Path
{chart_path}

STRICT RULES:
- Do NOT hallucinate numbers, dates, news events, or prices.
- Base the ENTIRE report ONLY on the provided KPIs and news items.
- Keep every section factual and concise.
- Avoid dramatic language, speculation, or made-up reasoning.
- If data is missing, acknowledge it instead of inventing content.
- Write like a disciplined financial analyst preparing a client report.
"""

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a senior financial analyst who writes precise, factual reports without hallucination."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.05,  # Ultra-low randomness for accuracy
            "max_tokens": 2000,
        }

        response = requests.post(self.endpoint, headers=headers, json=body)

        if response.status_code != 200:
            raise RuntimeError(
                f"OpenRouter API error {response.status_code}: {response.text}"
            )

        return response.json()["choices"][0]["message"]["content"]


# Smoke test (run: python -m agents.report_writer_agent)
if __name__ == "__main__":
    agent = ReportWriterAgent()

    # Sample test inputs
    sample_news = [
        {"title": "TCS expands AI capabilities", "url": "https://example.com/a", "sentiment": {"label": "positive"}},
        {"title": "IT sector faces macroeconomic pressures", "url": "https://example.com/b", "sentiment": {"label": "negative"}},
    ]

    sample_sent = {"count": 2, "positive": 1, "negative": 1, "neutral": 0, "avg_polarity": 0.01}

    sample_kpis = {
        "current_price": 4000,
        "ma20": 4020,
        "ma50": 3950,
        "volatility": 0.02
    }

    print("\n--- Testing ReportWriterAgent (Gemma 3 12B) ---\n")

    report = agent.write_report(
        stock_symbol="TCS.NS",
        kpis=sample_kpis,
        news_items=sample_news,
        sentiment_summary=sample_sent,
        chart_path="data/raw/TCS.NS_chart.png",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )

    print(report)


