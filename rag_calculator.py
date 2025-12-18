import streamlit as st
import pandas as pd

st.set_page_config(page_title="Azure RAG Cost Canvas", layout="wide")
st.title("📊 Detailed AI Cost Canvas & RAG Calculator")

# --- SIDEBAR: UNIT PRICES ---
st.sidebar.header("🏷️ Azure Unit Pricing (2025)")
p_stt = st.sidebar.number_input("Speech-to-Text ($/hr)", value=0.36)
p_gpt_in = st.sidebar.number_input("GPT-4o Input ($/1M tokens)", value=2.50)
p_gpt_out = st.sidebar.number_input("GPT-4o Output ($/1M tokens)", value=10.00)
p_embed = st.sidebar.number_input("Embeddings ($/1M tokens)", value=0.02)

# --- INPUT SECTION ---
st.header("1️⃣ Input Parameters & Assumptions")
with st.expander("Adjust Volume & Behavior Assumptions", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("Ingestion (Phase 1)")
        total_sessions = st.number_input("Total Monthly Sessions", value=1000)
        avg_session_hr = st.number_input("Avg Session Duration (Hrs)", value=1.5)
        words_per_hr = st.number_input("Avg Speaking Rate (Words/Hr)", value=9000)
    with c2:
        st.subheader("RAG Queries (Phase 2)")
        total_users = st.number_input("Number of Active Users", value=500)
        queries_per_day = st.number_input("Queries per User/Day", value=30)
        days_per_month = st.number_input("Days per Month", value=30)
    with c3:
        st.subheader("Document Fidelity")
        # DETAILED SUD: Increased to 3,000 tokens for long-form technical docs
        sud_output_tokens = st.number_input("Tokens per Detailed SUD", value=3000)
        rag_context_tokens = st.number_input("Context per RAG Query", value=1500)

# --- CALCULATIONS ---
# Phase 1: Ingestion
total_hours = total_sessions * avg_session_hr
ingest_input_tokens = (total_hours * words_per_hr * 1.35) # Words to Tokens
ingest_output_tokens = (total_sessions * sud_output_tokens)
cost_p1_stt = total_hours * p_stt
cost_p1_gpt_in = (ingest_input_tokens / 1e6) * p_gpt_in
cost_p1_gpt_out = (ingest_output_tokens / 1e6) * p_gpt_out

# Phase 2: Monthly RAG
total_queries = total_users * queries_per_day * days_per_month
rag_input_tokens = total_queries * rag_context_tokens
rag_output_tokens = total_queries * 250 # Avg answer size
cost_p2_gpt_in = (rag_input_tokens / 1e6) * p_gpt_in
cost_p2_gpt_out = (rag_output_tokens / 1e6) * p_gpt_out
cost_p2_embed = (total_queries * 100 / 1e6) * p_embed

# Infrastructure (Fixed)
infra_total = 48.04 + 39.30 + 45.00 # APIM + NAT + Functions

# --- SUMMARY SECTION ---
st.header("2️⃣ Token Count & Detailed Cost Breakup")

# Create Summary Dataframe
summary_data = {
    "Workload": ["Phase 1: Ingestion (STT)", "Phase 1: Detailed SUD Generation", "Phase 2: RAG Queries (Monthly)", "Cloud Infrastructure"],
    "Input Tokens": [0, f"{ingest_input_tokens/1e6:.1f}M", f"{rag_input_tokens/1e6:.1f}M", 0],
    "Output Tokens": [0, f"{ingest_output_tokens/1e6:.1f}M", f"{rag_output_tokens/1e6:.1f}M", 0],
    "Cost Breakup": [
        f"${cost_p1_stt:,.2f} (STT)",
        f"${(cost_p1_gpt_in + cost_p1_gpt_out):,.2f} (GPT-4o)",
        f"${(cost_p2_gpt_in + cost_p2_gpt_out + cost_p2_embed):,.2f} (GPT-4o + Embed)",
        f"${infra_total:,.2f} (APIM/NAT/Func)"
    ],
    "Subtotal": [cost_p1_stt, (cost_p1_gpt_in + cost_p1_gpt_out), (cost_p2_gpt_in + cost_p2_gpt_out + cost_p2_embed), infra_total]
}

df_summary = pd.DataFrame(summary_data)
st.table(df_summary.drop(columns=["Subtotal"]))

total_monthly_bill = df_summary["Subtotal"].sum()

st.divider()
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Monthly Azure Bill", f"${total_monthly_bill:,.2f}")
kpi2.metric("Cost Per Detailed SUD", f"${(cost_p1_stt + cost_p1_gpt_in + cost_p1_gpt_out)/total_sessions:,.2f}")
kpi3.metric("Cost Per Active User", f"${total_monthly_bill/total_users:,.2f}")
