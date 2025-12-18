import streamlit as st
import pandas as pd

st.set_page_config(page_title="Azure AI Token & Consumption Canvas", layout="wide")

# --- CUSTOM CSS FOR ALIGNMENT ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; }
    </style>
    """, unsafe_all_low_colors=True)

st.title("🤖 Azure AI Token & Multi-Month Consumption Canvas")
st.markdown("This calculator forecasts **AI Consumption Costs** scaled over time. Infrastructure costs are excluded.")

# --- SIDEBAR: UNIT PRICES ---
st.sidebar.header("🏷️ Azure Unit Pricing (GPT-4o)")
p_stt = st.sidebar.number_input("Speech-to-Text ($/hr)", value=0.36, format="%.2f")
p_gpt_in = st.sidebar.number_input("GPT-4o Input ($/1M tokens)", value=2.50, format="%.2f")
p_gpt_out = st.sidebar.number_input("GPT-4o Output ($/1M tokens)", value=10.00, format="%.2f")
p_embed = st.sidebar.number_input("Embeddings ($/1M tokens)", value=0.02, format="%.4f")

# --- PART 1: INPUT PARAMETERS & ASSUMPTIONS ---
st.header("1️⃣ Input Parameters & Assumptions")
col_time, col_empty = st.columns([1, 2])
with col_time:
    num_months = st.number_input("📅 Project Duration (Number of Months)", min_value=1, value=12, step=1)

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📥 Monthly Ingestion (Phase 1)")
    monthly_sessions = st.number_input("Monthly Sessions", value=1000)
    avg_session_hr = st.number_input("Avg Session Duration (Hrs)", value=1.5)
    words_per_hr = st.number_input("Avg Words per Hour", value=9000)
    sud_output_tokens = st.number_input("Tokens per Detailed SUD (Output)", value=3000)

with col_b:
    st.subheader("🔍 Monthly RAG Queries (Phase 2)")
    total_users = st.number_input("Number of Active Users", value=500)
    queries_per_day = st.number_input("Queries per User/Day", value=30)
    days_per_month = st.number_input("Days per Month", value=30)
    rag_context_tokens = st.number_input("Context Tokens per Query (Input)", value=1500)
    rag_answer_tokens = st.number_input("Answer Tokens per Query (Output)", value=250)

# --- CALCULATIONS (MONTHLY) ---
# Phase 1: Monthly Ingestion
monthly_hours = monthly_sessions * avg_session_hr
monthly_ingest_in_tokens = (monthly_hours * words_per_hr * 1.35)
monthly_ingest_out_tokens = (monthly_sessions * sud_output_tokens)

# Phase 2: Monthly RAG
monthly_total_queries = total_users * queries_per_day * days_per_month
monthly_rag_in_tokens = monthly_total_queries * (rag_context_tokens + 50)
monthly_rag_out_tokens = monthly_total_queries * rag_answer_tokens
monthly_rag_embed_tokens = monthly_total_queries * 100

# Monthly Costs
monthly_cost_stt = monthly_hours * p_stt
monthly_cost_ingest = ((monthly_ingest_in_tokens / 1e6) * p_gpt_in) + ((monthly_ingest_out_tokens / 1e6) * p_gpt_out)
monthly_cost_rag = ((monthly_rag_in_tokens / 1e6) * p_gpt_in) + ((monthly_rag_out_tokens / 1e6) * p_gpt_out) + ((monthly_rag_embed_tokens / 1e6) * p_embed)

monthly_total_tokens_in = monthly_ingest_in_tokens + monthly_rag_in_tokens
monthly_total_tokens_out = monthly_ingest_out_tokens + monthly_rag_out_tokens
monthly_total_cost = monthly_cost_stt + monthly_cost_ingest + monthly_cost_rag

# --- CALCULATIONS (OVERALL) ---
overall_total_cost = monthly_total_cost * num_months
overall_total_tokens_in = monthly_total_tokens_in * num_months
overall_total_tokens_out = monthly_total_tokens_out * num_months

# --- PART 2: TOKEN COUNT & COST BREAKUP ---
st.header("2️⃣ Token Count & Cost Breakup")

summary_df = pd.DataFrame([
    {
        "Workload": "Transcription (STT)",
        "Monthly Input Tokens": "N/A",
        "Monthly Output Tokens": "N/A",
        "Monthly Cost": monthly_cost_stt,
        f"Total ({num_months} mo) Cost": monthly_cost_stt * num_months
    },
    {
        "Workload": "Detailed SUD Generation",
        "Monthly Input Tokens": f"{monthly_ingest_in_tokens/1e6:.2f}M",
        "Monthly Output Tokens": f"{monthly_ingest_out_tokens/1e6:.2f}M",
        "Monthly Cost": monthly_cost_ingest,
        f"Total ({num_months} mo) Cost": monthly_cost_ingest * num_months
    },
    {
        "Workload": "RAG Knowledge Access",
        "Monthly Input Tokens": f"{monthly_rag_in_tokens/1e6:.2f}M",
        "Monthly Output Tokens": f"{monthly_rag_out_tokens/1e6:.2f}M",
        "Monthly Cost": monthly_cost_rag,
        f"Total ({num_months} mo) Cost": monthly_cost_rag * num_months
    }
])

# Formatting the dataframe for display
styled_df = summary_df.copy()
styled_df["Monthly Cost"] = styled_df["Monthly Cost"].map("${:,.2f}".format)
styled_df[f"Total ({num_months} mo) Cost"] = styled_df[f"Total ({num_months} mo) Cost"].map("${:,.2f}".format)

st.table(styled_df)

# --- FINAL FOOTER SUMMARY ---
st.divider()
st.subheader(f"📊 Final Aggregate Summary ({num_months} Months)")

c1, c2 = st.columns(2)

with c1:
    st.markdown("### **Monthly Totals**")
    st.write(f"**Input Tokens:** {monthly_total_tokens_in/1e6:.2f} Million")
    st.write(f"**Output Tokens:** {monthly_total_tokens_out/1e6:.2f} Million")
    st.markdown(f"#### **Monthly Total Cost: ${monthly_total_cost:,.2f}**")

with c2:
    st.markdown(f"### **Overall Totals ({num_months} Months)**")
    st.write(f"**Total Input Tokens:** {overall_total_tokens_in/1e6:.2f} Million")
    st.write(f"**Total Output Tokens:** {overall_total_tokens_out/1e6:.2f} Million")
    st.markdown(f"#### **Overall Project Cost: ${overall_total_cost:,.2f}**")

st.info("Calculations based on standard GPT-4o pricing. Actual costs may vary based on Region and Provisioned Throughput (PTU) availability.")
