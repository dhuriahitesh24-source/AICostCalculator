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
    st.subheader("📥 Ingestion & Iterative SUD")
    monthly_sessions = st.number_input("Monthly Sessions", value=1000)
    avg_session_hr = st.number_input("Avg Session Duration (Hrs)", value=1.5)
    words_per_hr = st.number_input("Avg Words per Hour", value=9000)
    
    st.markdown("---")
    sud_output_tokens = st.number_input("Tokens per Detailed SUD (Output)", value=3000)
    sud_iterations = st.slider("SUD Revision Iterations", min_value=1, max_value=5, value=1, 
                               help="1 means initial gen only. 2+ means the transcript is re-processed with new instructions.")

with col_b:
    st.subheader("🔍 RAG Queries (Phase 2)")
    total_users = st.number_input("Number of Active Users", value=500)
    queries_per_day = st.number_input("Queries per User/Day", value=30)
    days_per_month = st.number_input("Days per Month", value=30)
    rag_context_tokens = st.number_input("Context Tokens per Query (Input)", value=1500)
    rag_answer_tokens = st.number_input("Answer Tokens per Query (Output)", value=250)

# --- CALCULATIONS ---

# 1. Phase 1: Ingestion Logic
# STT stays flat regardless of LLM iterations
total_hours = (monthly_sessions * avg_session_hr) * num_months
cost_stt = total_hours * p_stt

# LLM Tokens for Ingestion
# The base transcript tokens (calculated once)
base_transcript_tokens = (total_hours * words_per_hr * 1.35) 

# Total Ingest Input = Base transcript sent 'N' times (once per iteration) 
# We add 200 tokens per iteration for the "Revision Prompt/Instruction"
total_ingest_in_tokens = (base_transcript_tokens * sud_iterations) + (monthly_sessions * num_months * 200 * sud_iterations)
total_ingest_out_tokens = (monthly_sessions * num_months * sud_output_tokens * sud_iterations)

# 2. Phase 2: RAG Logic
total_queries = (total_users * queries_per_day * days_per_month) * num_months
total_rag_in_tokens = total_queries * (rag_context_tokens + 50)
total_rag_out_tokens = total_queries * rag_answer_tokens
total_rag_embed_tokens = total_queries * 100

# 3. Aggregated Totals
grand_total_in_tokens = total_ingest_in_tokens + total_rag_in_tokens
grand_total_out_tokens = total_ingest_out_tokens + total_rag_out_tokens

# 4. Final Costs
cost_in_total = (grand_total_in_tokens / 1_000_000) * p_gpt_in
cost_out_total = (grand_total_out_tokens / 1_000_000) * p_gpt_out
cost_embed = (total_rag_embed_tokens / 1_000_000) * p_embed
grand_total_cost = cost_stt + cost_in_total + cost_out_total + cost_embed

# --- PART 2: SUMMARY TABLE ---
st.header(f"2️⃣ Cost Summary ({num_months} Months)")

summary_df = pd.DataFrame([
    {
        "Workload": "Transcription (STT)",
        "Details": "Calculated once (no iterations)",
        "Monthly Cost": cost_stt / num_months,
        "Total Cost": cost_stt
    },
    {
        "Workload": f"SUD Gen ({sud_iterations} Iterations)",
        "Details": f"LLM re-processes transcript {sud_iterations}x",
        "Monthly Cost": ((total_ingest_in_tokens/1e6 * p_gpt_in) + (total_ingest_out_tokens/1e6 * p_gpt_out)) / num_months,
        "Total Cost": (total_ingest_in_tokens/1e6 * p_gpt_in) + (total_ingest_out_tokens/1e6 * p_gpt_out)
    },
    {
        "Workload": "RAG Knowledge Access",
        "Details": f"{total_queries:,.0f} Queries",
        "Monthly Cost": ((total_rag_in_tokens/1e6 * p_gpt_in) + (total_rag_out_tokens/1e6 * p_gpt_out) + (cost_embed/num_months)),
        "Total Cost": (total_rag_in_tokens/1e6 * p_gpt_in) + (total_rag_out_tokens/1e6 * p_gpt_out) + cost_embed
    }
])

st.table(summary_df.style.format({"Monthly Cost": "${:,.2f}", "Total Cost": "${:,.2f}"}))

# --- PART 3: FINAL TECHNICAL REPORT ---
st.divider()
st.header("📋 Final Technical Report")
st.info(f"Total projected cost for {num_months} months based on {sud_iterations} revision loop(s).")

rep_a, rep_b = st.columns(2)
with rep_a:
    st.markdown("### 📥 Input Metrics")
    st.write(f"**Total Input Tokens:** {grand_total_in_tokens:,.0f}")
    st.write(f"**Model Name:** {model_name}")
    st.write(f"**Total Input Cost:** ${cost_in_total:,.2f}")

with rep_b:
    st.markdown("### 📤 Output Metrics")
    st.write(f"**Total Output Tokens:** {grand_total_out_tokens:,.0f}")
    st.write(f"**Model Name:** {model_name}")
    st.write(f"**Total Output Cost:** ${cost_out_total:,.2f}")

st.markdown("---")
st.markdown(f"### **Grand Total Cumulative Cost: ${grand_total_cost:,.2f}**")
st.markdown(f"**Average Monthly Spend: ${grand_total_cost/num_months:,.2f}**")
