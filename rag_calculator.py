import streamlit as st
import pandas as pd

st.set_page_config(page_title="Azure AI Token Calculator", layout="wide")
st.title("🤖 Azure AI Token & Consumption Canvas")

# --- SIDEBAR: UNIT PRICES ---
st.sidebar.header("🏷️ Azure Unit Pricing")
model_name = st.sidebar.text_input("Model Name", value="GPT-4o")
p_stt = st.sidebar.number_input("Speech-to-Text ($/hr)", value=0.36, format="%.2f")
p_gpt_in = st.sidebar.number_input("Input ($/1M tokens)", value=2.50, format="%.2f")
p_gpt_out = st.sidebar.number_input("Output ($/1M tokens)", value=10.00, format="%.2f")
p_embed = st.sidebar.number_input("Embeddings ($/1M tokens)", value=0.02, format="%.4f")

# --- PART 1: INPUT PARAMETERS & DURATION ---
st.header("1️⃣ Projection Settings")
num_months = st.number_input("Number of Months for Projection", min_value=1, value=1, step=1)

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📥 Ingestion (Phase 1)")
    monthly_sessions = st.number_input("Monthly Sessions", value=1000)
    avg_session_hr = st.number_input("Avg Session Duration (Hrs)", value=1.5)
    words_per_hr = st.number_input("Avg Words per Hour", value=9000)
    sud_output_tokens = st.number_input("Tokens per Detailed SUD (Output)", value=3000)

with col_b:
    st.subheader("🔍 RAG Queries (Phase 2)")
    total_users = st.number_input("Number of Active Users", value=500)
    queries_per_day = st.number_input("Queries per User/Day", value=30)
    days_per_month = st.number_input("Days per Month", value=30)
    rag_context_tokens = st.number_input("Context Tokens per Query (Input)", value=1500)
    rag_answer_tokens = st.number_input("Answer Tokens per Query (Output)", value=250)

# --- CALCULATIONS ---

# 1. Total Token Counts (Total Duration)
# Ingestion
total_hours = (monthly_sessions * avg_session_hr) * num_months
total_ingest_in_tokens = (total_hours * words_per_hr * 1.35) 
total_ingest_out_tokens = (monthly_sessions * sud_output_tokens) * num_months

# RAG
total_queries = (total_users * queries_per_day * days_per_month) * num_months
total_rag_in_tokens = total_queries * (rag_context_tokens + 50)
total_rag_out_tokens = total_queries * rag_answer_tokens
total_rag_embed_tokens = total_queries * 100

# Aggregated Totals for Report
grand_total_in_tokens = total_ingest_in_tokens + total_rag_in_tokens
grand_total_out_tokens = total_ingest_out_tokens + total_rag_out_tokens

# 2. Total Costs (Total Duration)
cost_stt = total_hours * p_stt
cost_in_total = (grand_total_in_tokens / 1_000_000) * p_gpt_in
cost_out_total = (grand_total_out_tokens / 1_000_000) * p_gpt_out
cost_embed = (total_rag_embed_tokens / 1_000_000) * p_embed

grand_total_cost = cost_stt + cost_in_total + cost_out_total + cost_embed

# --- PART 2: SUMMARY TAB ---
st.header(f"2️⃣ Cost Summary ({num_months} Months)")

summary_df = pd.DataFrame([
    {
        "Workload": "Speech-to-Text",
        "Details": f"{total_hours:,.0f} Total Hours",
        "Monthly Cost": cost_stt / num_months,
        "Total Cost": cost_stt
    },
    {
        "Workload": f"LLM Processing ({model_name})",
        "Details": f"{(grand_total_in_tokens + grand_total_out_tokens)/1e6:.2f}M Tokens",
        "Monthly Cost": (cost_in_total + cost_out_total) / num_months,
        "Total Cost": cost_in_total + cost_out_total
    },
    {
        "Workload": "Embeddings & Others",
        "Details": f"{total_rag_embed_tokens/1e6:.2f}M Tokens",
        "Monthly Cost": cost_embed / num_months,
        "Total Cost": cost_embed
    }
])

st.table(summary_df.style.format({"Monthly Cost": "${:,.2f}", "Total Cost": "${:,.2f}"}))

# --- PART 3: FINAL REPORT ---
st.divider()
st.header("📋 Final Technical Report")
st.info(f"Report generated for a total duration of **{num_months} month(s)**.")

report_col1, report_col2 = st.columns(2)

with report_col1:
    st.markdown("### 📥 Input Metrics")
    st.write(f"**Total Input Tokens:** {grand_total_in_tokens:,.0f}")
    st.write(f"**Model Name:** {model_name}")
    st.write(f"**Total Input Cost:** ${cost_in_total:,.2f}")

with report_col2:
    st.markdown("### 📤 Output Metrics")
    st.write(f"**Total Output Tokens:** {grand_total_out_tokens:,.0f}")
    st.write(f"**Model Name:** {model_name}")
    st.write(f"**Total Output Cost:** ${cost_out_total:,.2f}")

st.markdown("---")
st.markdown(f"**Grand Total Cumulative Cost:** `${grand_total_cost:,.2f}`")

# Optional Download Button
report_text = f"""
Final AI Consumption Report ({num_months} Months)
Model: {model_name}
-------------------------------------------
Total Input Tokens: {grand_total_in_tokens:,.0f}
Total Output Tokens: {grand_total_out_tokens:,.0f}
Total Input Cost: ${cost_in_total:,.2f}
Total Output Cost: ${cost_out_total:,.2f}
STT & Embedding Costs: ${cost_stt + cost_embed:,.2f}
Grand Total Cost: ${grand_total_cost:,.2f}
"""
st.download_button("Download Report as TXT", report_text, file_name="ai_cost_report.txt")
