import traceback

from agents.researcher_agent import ResearcherAgent
from agents.data_analyst_agent import DataAnalystAgent
from agents.report_writer_agent import ReportWriterAgent
from utils.pdf_generator import PDFGenerator


class Orchestrator:
    """
    The central controller that coordinates all agents:
      - ResearcherAgent
      - DataAnalystAgent
      - ReportWriterAgent
      - PDFGenerator
    """

    def __init__(self):
        self.researcher = ResearcherAgent(max_articles=8)
        self.analyst = DataAnalystAgent()
        self.writer = ReportWriterAgent()
        self.pdf = PDFGenerator()

    def run(self, stock_symbol: str, start_date: str, end_date: str) -> dict:
        """
        Executes the full multi-agent pipeline and returns
        all produced data along with final PDF path.

        Returns a dict with keys:
            - kpis
            - chart_path
            - news_items
            - sentiment_summary
            - report_text
            - pdf_path
        """
        try:
            print("\n🔍 Step 1: Fetching news...")
            news_items = self.researcher.gather_news(stock_symbol)
            sentiment_summary = self.researcher.analyze_sentiment_summary(news_items)

            print("\n📊 Step 2: Fetching stock data & KPIs...")
            kpis, chart_path = self.analyst.analyze_stock(stock_symbol, start_date, end_date)

            print("\n📝 Step 3: Generating financial report...")
            report_text = self.writer.write_report(
                stock_symbol=stock_symbol,
                kpis=kpis,
                news_items=news_items,
                sentiment_summary=sentiment_summary,
                chart_path=chart_path,
                start_date=start_date,
                end_date=end_date
            )

            print("\n📄 Step 4: Creating PDF...")
            pdf_path = self.pdf.generate_pdf(
                report_text=report_text,
                chart_path=chart_path,
                stock_symbol=stock_symbol
            )

            print("\n🎉 DONE. Full pipeline completed successfully.")

            return {
                "kpis": kpis,
                "chart_path": chart_path,
                "news_items": news_items,
                "sentiment_summary": sentiment_summary,
                "report_text": report_text,
                "pdf_path": pdf_path
            }

        except Exception as e:
            print("\n❌ ERROR OCCURRED!")
            traceback.print_exc()
            return {"error": str(e)}
            

# Allow direct terminal testing
if __name__ == "__main__":
    orch = Orchestrator()

    print("\n🚀 Running full pipeline for TCS.NS...")
    output = orch.run(
        stock_symbol="TCS.NS",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )

    print("\n\nOUTPUT SUMMARY:\n", output)
