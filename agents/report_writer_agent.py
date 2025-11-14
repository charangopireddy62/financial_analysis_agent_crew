import os
import requests
from typing import List, Dict, Any

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class ReportWriterAgent:
    """
    Uses OpenRouter (gpt-oss-20b) to generate a structured financial report.
    """

    def __init__(self, model="openrouter/gpt-oss-20b"):
        self.model = model
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"

    def _format_news_section(self, news_items: List[Dict[str, Any]]) -> str:
        """
        Converts news list into a clean bullet-section for the LLM.
        """
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
        """
        Generate the final investment report using the LLM.
        """

        news_section = self._format_news_section(news_items)

        prompt = f"""
Write a professional, factual financial analysis report for the stock **{stock_symbol}**.
Date Range: {start_date} → {end_date}

Use EXACTLY this structure:

1. Executive Summary  
2. Price Performance Overview  
3. Key Indicators (KPIs)  
4. Market Sentiment Analysis  
5. Recent News Highlights  
6. Risks and Opportunities  
7. Final Recommendation  

### KPIs Provided:
{kpis}

### Sentiment Summary:
{sentiment_summary}

### Recent News Articles:
{news_section}

### Chart File Path (for reference):
{chart_path}

STRICT RULES:
- Use ONLY the data provided above.
- DO NOT guess numbers or invent additional information.
- DO NOT create extra news or events.
- Keep tone professional, like an equity research report.
- Keep paragraphs short and clear.
- Avoid dramatic or marketing tone.
"""

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert financial analyst."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,  # stable output, fewer hallucinations
        }

        response = requests.post(self.endpoint, headers=headers, json=body)

        if response.status_code != 200:
            raise RuntimeError(
                f"OpenRouter API error {response.status_code}: {response.text}"
            )

        data = response.json()
        return data["choices"][0]["message"]["content"]


# Smoke test (run: python -m agents.report_writer_agent)
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

    print("\n--- Running Test Report ---\n")
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
