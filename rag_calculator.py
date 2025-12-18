import streamlit as st
import pandas as pd

st.set_page_config(page_title="Azure AI Token Calculator", layout="wide")
st.title("🤖 Azure AI Token & Consumption Canvas")
st.markdown("This calculator focuses strictly on **AI Service Costs** (STT & OpenAI Tokens). Infrastructure costs (APIM, Networking) have been removed.")

# --- SIDEBAR: UNIT PRICES ---
st.sidebar.header("🏷️ Azure Unit Pricing (GPT-4o)")
p_stt = st.sidebar.number_input("Speech-to-Text ($/hr)", value=0.36, format="%.2f")
p_gpt_in = st.sidebar.number_input("GPT-4o Input ($/1M tokens)", value=2.50, format="%.2f")
p_gpt_out = st.sidebar.number_input("GPT-4o Output ($/1M tokens)", value=10.00, format="%.2f")
p_embed = st.sidebar.number_input("Embeddings ($/1M tokens)", value=0.02, format="%.4f")

# --- PART 1: INPUT PARAMETERS & ASSUMPTIONS ---
st.header("1️⃣ Input Parameters & Assumptions")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📥 Ingestion (Phase 1)")
    total_sessions = st.number_input("Total Monthly Sessions", value=1000)
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
# Phase 1: Ingestion logic
total_hours = total_sessions * avg_session_hr
ingest_in_tokens = (total_hours * words_per_hr * 1.35) # Word to token multiplier
ingest_out_tokens = (total_sessions * sud_output_tokens)

# Phase 2: RAG logic
total_queries = total_users * queries_per_day * days_per_month
rag_in_tokens = total_queries * (rag_context_tokens + 50) # +50 for user question
rag_out_tokens = total_queries * rag_answer_tokens
rag_embed_tokens = total_queries * 100 # Question embedding

# Costs
cost_stt = total_hours * p_stt
cost_ingest_in = (ingest_in_tokens / 1_000_000) * p_gpt_in
cost_ingest_out = (ingest_out_tokens / 1_000_000) * p_gpt_out

cost_rag_in = (rag_in_tokens / 1_000_000) * p_gpt_in
cost_rag_out = (rag_out_tokens / 1_000_000) * p_gpt_out
cost_rag_embed = (rag_embed_tokens / 1_000_000) * p_embed

# Aggregates
total_in_tokens = ingest_in_tokens + rag_in_tokens
total_out_tokens = ingest_out_tokens + rag_out_tokens
total_ai_cost = cost_stt + cost_ingest_in + cost_ingest_out + cost_rag_in + cost_rag_out + cost_rag_embed

# --- PART 2: TOKEN COUNT & COST BREAKUP ---
st.header("2️⃣ Token Count & Total AI Cost Breakup")

summary_df = pd.DataFrame([
    {
        "Workload": "Phase 1: Transcription (STT)",
        "Input Tokens": "N/A",
        "Output Tokens": "N/A",
        "Metric": f"{total_hours:,.0f} Hours",
        "Cost": cost_stt
    },
    {
        "Workload": "Phase 1: Detailed SUD Gen",
        "Input Tokens": f"{ingest_in_tokens/1e6:.2f}M",
        "Output Tokens": f"{ingest_out_tokens/1e6:.2f}M",
        "Metric": "Processing",
        "Cost": cost_ingest_in + cost_ingest_out
    },
    {
        "Workload": "Phase 2: RAG Knowledge Access",
        "Input Tokens": f"{rag_in_tokens/1e6:.2f}M",
        "Output Tokens": f"{rag_out_tokens/1e6:.2f}M",
        "Metric": f"{total_queries:,.0f} Queries",
        "Cost": cost_rag_in + cost_rag_out + cost_rag_embed
    }
])

st.table(summary_df)

# Final Summary Metrics
st.divider()
m1, m2, m3 = st.columns(3)
m1.metric("Total Input Tokens", f"{total_in_tokens/1e6:.2f} Million")
m2.metric("Total Output Tokens", f"{total_out_tokens/1e6:.2f} Million")
m3.metric("Total AI Cost", f"${total_ai_cost:,.2f}")

st.info(f"**Efficiency Note:** Input tokens represent {(total_in_tokens/(total_in_tokens+total_out_tokens))*100:.1f}% of your volume. Consider Azure Prompt Caching to reduce costs for Phase 2.")
