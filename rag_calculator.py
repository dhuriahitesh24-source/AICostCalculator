import streamlit as st
import pandas as pd

st.set_page_config(page_title="Azure AI Token Calculator", layout="wide")
st.title("🤖 Azure AI Token & Consumption Canvas")
st.markdown("This calculator focuses strictly on **AI Service Costs** (STT & OpenAI Tokens).")

# --- SIDEBAR: GLOBAL SETTINGS & UNIT PRICES ---
st.sidebar.header("⚙️ Global Settings")
# Added duration parameter
num_months = st.sidebar.slider("Calculation Period (Months)", min_value=1, max_value=36, value=1)

st.sidebar.divider()
st.sidebar.header("🏷️ Azure Unit Pricing (GPT-4o)")
p_stt = st.sidebar.number_input("Speech-to-Text ($/hr)", value=0.36, format="%.2f")
p_gpt_in = st.sidebar.number_input("GPT-4o Input ($/1M tokens)", value=2.50, format="%.2f")
p_gpt_out = st.sidebar.number_input("GPT-4o Output ($/1M tokens)", value=10.00, format="%.2f")
p_embed = st.sidebar.number_input("Embeddings ($/1M tokens)", value=0.02, format="%.4f")

# --- PART 1: INPUT PARAMETERS & ASSUMPTIONS ---
st.header("1️⃣ Input Parameters & Assumptions (Per Month)")
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
    queries_per_user_day = st.number_input("Queries per User/Day", value=30)
    days_per_month = st.number_input("Days per Month", value=30)
    rag_context_tokens = st.number_input("Context Tokens per Query (Input)", value=1500)
    rag_answer_tokens = st.number_input("Answer Tokens per Query (Output)", value=250)

# --- CALCULATIONS (Scaled by num_months) ---
# Multiplier for total period
total_sessions = monthly_sessions * num_months
total_queries = total_users * queries_per_user_day * days_per_month * num_months

# Phase 1: Ingestion logic (Total over period)
total_hours = total_sessions * avg_session_hr
ingest_in_tokens = (total_hours * words_per_hr * 1.35) 
ingest_out_tokens = (total_sessions * sud_output_tokens)

# Phase 2: RAG logic (Total over period)
rag_in_tokens = total_queries * (rag_context_tokens + 50) 
rag_out_tokens = total_queries * rag_answer_tokens
rag_embed_tokens = total_queries * 100 

# Total Period Costs
cost_stt = total_hours * p_stt
cost_ingest = ((ingest_in_tokens / 1e6) * p_gpt_in) + ((ingest_out_tokens / 1e6) * p_gpt_out)
cost_rag = ((rag_in_tokens / 1e6) * p_gpt_in) + ((rag_out_tokens / 1e6) * p_gpt_out) + ((rag_embed_tokens / 1e6) * p_embed)

total_ai_cost = cost_stt + cost_ingest + cost_rag
total_in_tokens = ingest_in_tokens + rag_in_tokens
total_out_tokens = ingest_out_tokens + rag_out_tokens

# --- PART 2: TOKEN COUNT & COST BREAKUP ---
st.header(f"2️⃣ Total Consumption & Cost for {num_months} Month(s)")

summary_df = pd.DataFrame([
    {
        "Workload": "Phase 1: Transcription (STT)",
        "Total Tokens (In/Out)": "N/A",
        "Metric": f"{total_hours:,.0f} Total Hrs",
        "Monthly Cost": f"${(cost_stt / num_months):,.2f}",
        "Total Cost": cost_stt
    },
    {
        "Workload": "Phase 1: Detailed SUD Gen",
        "Total Tokens (In/Out)": f"{(ingest_in_tokens + ingest_out_tokens)/1e6:.2f}M",
        "Metric": f"{total_sessions:,.0f} Sessions",
        "Monthly Cost": f"${(cost_ingest / num_months):,.2f}",
        "Total Cost": cost_ingest
    },
    {
        "Workload": "Phase 2: RAG Knowledge Access",
        "Total Tokens (In/Out)": f"{(rag_in_tokens + rag_out_tokens)/1e6:.2f}M",
        "Metric": f"{total_queries:,.0f} Queries",
        "Monthly Cost": f"${(cost_rag / num_months):,.2f}",
        "Total Cost": cost_rag
    }
])

st.table(summary_df)

# Final Summary Metrics
st.divider()
st.subheader(f"📊 Summary for {num_months} Month Period")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Tokens", f"{(total_in_tokens + total_out_tokens)/1e6:.2f}M")
m2.metric("Avg. Monthly Cost", f"${(total_ai_cost / num_months):,.2f}")
m3.metric("Total Period Cost", f"${total_ai_cost:,.2f}", delta=None)
m4.metric("Cost per Session", f"${(total_ai_cost / total_sessions):,.2f}" if total_sessions > 0 else 0)

st.info(f"**Note:** Calculations are based on a **{num_months} month** duration. Input tokens represent {(total_in_tokens/(total_in_tokens+total_out_tokens))*100:.1f}% of your volume.")
