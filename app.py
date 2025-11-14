import streamlit as st
from orchestrator import Orchestrator
import base64
import os

# ------------------------ STREAMLIT CONFIG ------------------------
st.set_page_config(
    page_title="AI Financial Analyst",
    layout="wide",
    page_icon="📈"
)

st.title("📈 AI Financial Analysis Agent")
st.write("A multi-agent AI system for financial research, KPI analysis, sentiment mining, and automated report writing.")

st.sidebar.header("⚙️ Analysis Settings")

# Inputs
stock_symbol = st.sidebar.text_input("Stock Symbol (Example: TCS.NS, INFY.NS)", value="TCS.NS")

start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

run_btn = st.sidebar.button("🚀 Run Analysis")


# ------------------------ MAIN EXECUTION ------------------------
if run_btn:
    st.subheader(f"🚀 Running Analysis for **{stock_symbol}**")

    orchestrator = Orchestrator()

    with st.spinner("Fetching data, analyzing trends, generating report..."):
        result = orchestrator.run(
            stock_symbol=stock_symbol,
            start_date=str(start_date),
            end_date=str(end_date)
        )

    # -------------------------------------------------------------
    # ERROR HANDLING
    # -------------------------------------------------------------
    if "error" in result:
        st.error(f"❌ Error: {result['error']}")
        st.stop()

    st.success("✅ Analysis Completed Successfully")

    # -------------------------------------------------------------
    # 1. KPIs SECTION
    # -------------------------------------------------------------
    st.header("📊 Key Performance Indicators")
    kpis = result.get("kpis", {})

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", kpis.get("current_price"))
    col2.metric("Day High", kpis.get("day_high"))
    col3.metric("Day Low", kpis.get("day_low"))

    col4, col5, col6 = st.columns(3)
    col4.metric("MA20", kpis.get("ma20"))
    col5.metric("MA50", kpis.get("ma50"))
    col6.metric("Volatility", kpis.get("volatility"))

    # -------------------------------------------------------------
    # 2. FUNDAMENTALS SECTION
    # -------------------------------------------------------------
    st.header("📉 Fundamental Indicators (Yahoo Finance)")

    fund = result.get("fundamentals", {})

    if fund:
        f1, f2, f3 = st.columns(3)
        f1.metric("P/E Ratio", fund.get("pe_ratio"))
        f2.metric("Forward P/E", fund.get("forward_pe"))
        f3.metric("EPS", fund.get("eps"))

        f4, f5, f6 = st.columns(3)
        f4.metric("Market Cap", fund.get("market_cap"))
        f5.metric("Beta", fund.get("beta"))
        f6.metric("P/B Ratio", fund.get("pb_ratio"))

        st.write(f"**Sector:** {fund.get('sector')}")
        st.write(f"**Industry:** {fund.get('industry')}")
    else:
        st.info("⚠️ No fundamentals available for this stock.")

    # -------------------------------------------------------------
    # 3. CHART SECTION
    # -------------------------------------------------------------
    st.header("📈 Price Chart")
    chart_path = result.get("chart_path")

    if chart_path and os.path.exists(chart_path):
        st.image(chart_path, use_container_width=True)
    else:
        st.warning("⚠️ Chart image missing.")

    # -------------------------------------------------------------
    # 4. NEWS + SENTIMENT SECTION
    # -------------------------------------------------------------
    st.header("📰 Recent News & Sentiment")

    news_items = result.get("news_items", [])
    if not news_items:
        st.info("No recent news found for this stock.")
    else:
        for news in news_items:
            st.write(f"### {news['title']}")
            st.write(f"🔗 [{news['url']}]({news['url']})")
            st.write(f"🧠 Sentiment: **{news['sentiment']['label']}**")
            st.write("---")

    # -------------------------------------------------------------
    # 5. AI REPORT SECTION
    # -------------------------------------------------------------
    st.header("📝 AI-Generated Financial Report")

    report_text = result.get("report_text", "")
    st.write(report_text)

    # -------------------------------------------------------------
    # 6. PDF DOWNLOAD SECTION
    # -------------------------------------------------------------
    st.header("📄 Download Report PDF")

    pdf_path = result.get("pdf_path")

    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        st.download_button(
            label="⬇ Download Full PDF Report",
            data=pdf_bytes,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf"
        )
    else:
        st.warning("⚠️ PDF could not be generated.")


# -----------------------------------------------------------------
# END OF APP
# -----------------------------------------------------------------


