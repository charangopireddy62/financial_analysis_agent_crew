import streamlit as st
from orchestrator import Orchestrator
import base64
import os

st.set_page_config(page_title="AI Financial Analyst", layout="wide")

st.title("📈 AI Financial Analysis Agent")
st.write("Your personal multi-agent system for financial research, KPI analysis, sentiment mining, and AI-generated insights.")

# Input Panel
st.sidebar.header("Analysis Settings")

stock_symbol = st.sidebar.text_input("Stock Symbol", value="TCS.NS")

start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

run_btn = st.sidebar.button("Run Analysis 🚀")

# When user clicks run
if run_btn:
    st.subheader(f"🚀 Running Analysis for **{stock_symbol}**")

    orchestrator = Orchestrator()

    with st.spinner("Fetching data, analyzing trends, generating report..."):
        result = orchestrator.run(
            stock_symbol=stock_symbol,
            start_date=str(start_date),
            end_date=str(end_date)
        )

    if "error" in result:
        st.error(f"❌ Error: {result['error']}")
    else:
        st.success("✅ Analysis Completed Successfully")

        # ----- KPIs -----
        st.header("📊 Key Performance Indicators")
        kpis = result["kpis"]

        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", kpis["current_price"])
        col2.metric("Day High", kpis["day_high"])
        col3.metric("Day Low", kpis["day_low"])

        col4, col5, col6 = st.columns(3)
        col4.metric("MA20", kpis["ma20"])
        col5.metric("MA50", kpis["ma50"])
        col6.metric("Volatility", kpis["volatility"])

        # ----- Chart -----
        st.header("📈 Price Chart")
        if os.path.exists(result["chart_path"]):
            st.image(result["chart_path"], use_column_width=True)
        else:
            st.warning("Chart image missing.")

        # ----- News -----
        st.header("📰 Recent News & Sentiment")
        for n in result["news_items"]:
            st.write(f"### {n['title']}")
            st.write(f"🔗 [{n['url']}]({n['url']})")
            st.write(f"Sentiment: **{n['sentiment']['label']}**")
            st.write("---")

        # ----- AI Report -----
        st.header("📝 AI-Generated Financial Report")
        st.write(result["report_text"])

        # ----- PDF Download -----
        st.header("📄 Download Report PDF")

        pdf_path = result["pdf_path"]

        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            st.download_button(
                label="⬇ Download PDF Report",
                data=pdf_bytes,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf"
            )
        else:
            st.warning("PDF not found.")
