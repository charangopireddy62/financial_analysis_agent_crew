from fpdf import FPDF
import os
from datetime import datetime


class PDFGenerator:
    """
    Converts a financial analysis report (text + chart) into a polished PDF.
    """

    def __init__(self, output_dir="data/reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_pdf(self, report_text: str, chart_path: str, stock_symbol: str) -> str:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Title
        pdf.set_font("Arial", "B", 18)
        pdf.cell(0, 10, f"Financial Analysis Report: {stock_symbol}", ln=True)
        pdf.ln(4)

        # Date
        pdf.set_font("Arial", "", 12)
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        pdf.cell(0, 10, f"Generated on: {date_str}", ln=True)
        pdf.ln(8)

        # Insert Chart Image (if exists)
        if chart_path and os.path.exists(chart_path):
            try:
                pdf.image(chart_path, x=10, w=180)
                pdf.ln(10)
            except Exception:
                pdf.ln(5)
                pdf.set_font("Arial", "I", 11)
                pdf.set_text_color(255, 0, 0)
                pdf.cell(0, 10, "Chart could not be loaded.", ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(5)

        # Body Text
        pdf.set_font("Arial", "", 12)

        for line in report_text.split("\n"):
            # Heading styling
            if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.")):
                pdf.set_font("Arial", "B", 13)
                pdf.multi_cell(0, 8, line)
                pdf.set_font("Arial", "", 12)
            else:
                pdf.multi_cell(0, 7, line)

        # Output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/REPORT_{stock_symbol}_{timestamp}.pdf"
        pdf.output(filename)

        return filename


# Test independently
if __name__ == "__main__":
    g = PDFGenerator()

    sample_text = """
1. Executive Summary
TCS performed steadily across the year...

2. KPIs
- Price: 4000
"""

    out = g.generate_pdf(
        report_text=sample_text,
        chart_path="data/raw/TCS.NS_chart.png",
        stock_symbol="TCS.NS"
    )

    print("PDF saved at:", out)
