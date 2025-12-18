import streamlit as st
import pandas as pd

st.set_page_config(page_title="Azure AI Token Calculator", layout="wide")
st.title("🤖 Azure AI Token & Consumption Canvas")
st.markdown("This calculator estimates **AI Service Costs** over a specific duration.")

# --- SIDEBAR: UNIT PRICES ---
st.sidebar.header("🏷️ Azure Unit Pricing (GPT-4o)")
p_stt = st.sidebar.number_input("Speech-to-Text ($/hr)", value=0.36, format="%.2f")
p_gpt_in = st.sidebar.number_input("GPT-4o Input ($/1M tokens)", value=2.50, format="%.2f")
p_gpt_out = st.sidebar.number_input("GPT-4o Output ($/1M tokens)", value=10.00, format="%.2f")
p_embed = st.sidebar.number_input("Embeddings ($/1M tokens)", value=0.02, format="%.4f")

# --- PART 1: INPUT PARAMETERS & ASSUMPTIONS ---
st.header("1️⃣ Input Parameters & Duration")
# New Parameter for Duration
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

# --- CALCULATIONS (Updated for Months) ---

# Monthly Totals
m_total_hours = monthly_sessions * avg_session_hr
m_ingest_in = (m_total_hours * words_per_hr * 1.35) 
m_ingest_out = (monthly_sessions * sud_output_tokens)

m_queries = total_users * queries_per_day * days_per_month
m_rag_in = m_queries * (rag_context_tokens + 50)
m_rag_out = m_queries * rag_answer_tokens
m_rag_embed = m_queries * 100

# Total Period Totals (Months * Monthly)
total_hours = m_total_hours * num_months
ingest_in_tokens = m_ingest_in * num_months
ingest_out_tokens = m_ingest_out * num_months
total_queries = m_queries * num_months
rag_in_tokens = m_rag_in * num_months
rag_out_tokens = m_rag_out * num_months
rag_embed_tokens = m_rag_embed * num_months

# Costs (Total for the period)
cost_stt = total_hours * p_stt
cost_ingest = ((ingest_in_tokens / 1e6) * p_gpt_in) + ((ingest_out_tokens / 1e6) * p_gpt_out)
cost_rag = ((rag_in_tokens / 1e6) * p_gpt_in) + ((rag_out_tokens / 1e6) * p_gpt_out) + ((rag_embed_tokens / 1e6) * p_embed)

total_ai_cost = cost_stt + cost_ingest + cost_rag

# --- PART 2: SUMMARY TAB ---
st.header(f"2️⃣ Cost Summary ({num_months} Months)")

summary_data = [
    {
        "Workload": "Phase 1: Transcription (STT)",
        "Metric": f"{total_hours:,.0f} Total Hours",
        "Monthly Cost": cost_stt / num_months,
        "Total Cost": cost_stt
    },
    {
        "Workload": "Phase 1: Detailed SUD Gen",
        "Metric": f"{ingest_in_tokens/1e6:.2f}M In / {ingest_out_tokens/1e6:.2f}M Out",
        "Monthly Cost": cost_ingest / num_months,
        "Total Cost": cost_ingest
    },
    {
        "Workload": "Phase 2: RAG Access",
        "Metric": f"{total_queries:,.0f} Total Queries",
        "Monthly Cost": cost_rag / num_months,
        "Total Cost": cost_rag
    },
    {
        "Workload": "**Grand Total**",
        "Metric": "-",
        "Monthly Cost": total_ai_cost / num_months,
        "Total Cost": total_ai_cost
    }
]

summary_df = pd.DataFrame(summary_data)
# Format as currency
st.table(summary_df.style.format({
    "Monthly Cost": "${:,.2f}",
    "Total Cost": "${:,.2f}"
}))

# Metrics
st.divider()
m1, m2, m3 = st.columns(3)
m1.metric("Avg Monthly Cost", f"${(total_ai_cost / num_months):,.2f}")
m2.metric(f"Total Cost ({num_months}mo)", f"${total_ai_cost:,.2f}")
m3.metric("Total Tokens (In/Out)", f"{(ingest_in_tokens + ingest_out_tokens + rag_in_tokens + rag_out_tokens)/1e6:.2f}M")

st.info(f"The calculation assumes usage remains constant over the **{num_months} month(s)**.")
