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
        fundamentals: Dict[str, Any] = None
    ) -> str:

        fundamentals = fundamentals or {}
        news_section = self._format_news_section(news_items)

        # Optimized no-hallucination prompt for Gemma-3 12B
        prompt = f"""
You are a professional financial analyst. Write a clean, factual, structured equity-research report 
for **{stock_symbol}**, analyzing the period **{start_date} → {end_date}**.

Follow EXACTLY this structure:

1. Executive Summary  
2. Price Performance Overview  
3. Key Indicators (KPIs)  
4. Market Sentiment Analysis  
5. Fundamental Valuation Overview  
6. Recent News Highlights  
7. Risks and Opportunities  
8. Final Recommendation  

Use ONLY the data provided below. Never invent values.

### KPIs
{kpis}

### Fundamentals
{fundamentals}

### Sentiment Summary
{sentiment_summary}

### Recent News
{news_section}

### Chart File Path
{chart_path}

STRICT RULES:
- No made-up data. No hallucinated events, numbers, or dates.
- If any KPI or fundamental value is missing, say so clearly.
- Keep the tone professional like a real equity analyst.
- Use short, factual paragraphs and bullet points.
- Do NOT over-speculate; conclusions must follow from provided data.
"""

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a senior financial analyst. "
                        "You write precise, factual, structured reports. "
                        "You strictly avoid inventing any information."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.05,      # For maximum factual accuracy
            "max_tokens": 2200,
        }

        response = requests.post(self.endpoint, headers=headers, json=body)

        if response.status_code != 200:
            raise RuntimeError(
                f"OpenRouter API error {response.status_code}: {response.text}"
            )

        return response.json()["choices"][0]["message"]["content"]


# Smoke test (python -m agents.report_writer_agent)
if __name__ == "__main__":
    agent = ReportWriterAgent()

    sample_news = [
        {"title": "TCS expands AI capabilities", "url": "https://example.com/a",
         "sentiment": {"label": "positive"}},
        {"title": "IT sector faces macroeconomic pressures", "url": "https://example.com/b",
         "sentiment": {"label": "negative"}},
    ]

    sample_sent = {
        "count": 2,
        "positive": 1,
        "negative": 1,
        "neutral": 0,
        "avg_polarity": 0.01,
    }

    sample_kpis = {
        "current_price": 4000,
        "ma20": 4020,
        "ma50": 3950,
        "volatility": 0.02,
    }

    sample_fundamentals = {
        "pe_ratio": 32.1,
        "eps": 104.5,
        "market_cap": 13_000_000_000,
        "beta": 0.91,
    }

    print("\n--- Testing ReportWriterAgent (Gemma 3 12B) ---\n")

    report = agent.write_report(
        stock_symbol="TCS.NS",
        kpis=sample_kpis,
        fundamentals=sample_fundamentals,
        news_items=sample_news,
        sentiment_summary=sample_sent,
        chart_path="data/raw/TCS.NS_chart.png",
        start_date="2024-01-01",
        end_date="2024-12-31",
    )

    print(report)



