import os
from openai import OpenAI
from typing import List, Dict, Any

# Load key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

class ReportWriterAgent:
    """
    Uses OpenAI GPT-3.5 Turbo to generate a structured financial report.
    """

    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model

    def _format_news_section(self, news_items: List[Dict[str, Any]]) -> str:
        lines = []
        for i, item in enumerate(news_items, 1):
            title = item.get("title", "")
            sentiment = item.get("sentiment", {}).get("label", "neutral")
            url = item.get("url", "")
            lines.append(f"{i}. {title} — sentiment: {sentiment}\n   {url}")
        return "\n".join(lines)

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

        prompt = f"""
Write a highly structured, professional financial analysis report for **{stock_symbol}**.
Date Range: {start_date} → {end_date}

Use this exact outline:

1. Executive Summary  
2. Price Performance Overview  
3. Key Indicators (KPIs)  
4. Market Sentiment Analysis  
5. Recent News Highlights  
6. Risks and Opportunities  
7. Final Recommendation  

### KPIs:
{kpis}

### Market Sentiment Summary:
{sentiment_summary}

### Recent News:
{news_section}

### Chart File Path:
{chart_path}

RULES:
- Use ONLY the provided information. Do NOT invent numbers.
- Tone should match professional equity research reports.
- Keep the content concise, factual, and structured.
- Never hallucinate events or data not included above.
"""

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a senior financial analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2
        )

        return response.choices[0].message.content


# Standalone Test
if __name__ == "__main__":
    agent = ReportWriterAgent()

    sample_news = [
        {"title": "TCS expands AI services", "url": "https://example.com/a", "sentiment": {"label": "positive"}},
        {"title": "IT sector faces global slowdown", "url": "https://example.com/b", "sentiment": {"label": "negative"}},
    ]

    sample_sent = {"count": 2, "positive": 1, "negative": 1, "neutral": 0, "avg_polarity": 0.01}

    sample_kpis = {
        "current_price": 4000,
        "ma20": 4020,
        "ma50": 3950,
        "volatility": 0.02
    }

    print("\n--- Running Test Report (OpenAI GPT-3.5 Turbo) ---\n")

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

