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
    
    st.markdown("---")
    sud_output_tokens = st.number_input("Tokens per Detailed SUD (Output)", value=3000)
    # NEW PARAMETER: SUD Iterations
    sud_iterations = st.slider("SUD Revision Iterations", min_value=1, max_value=5, value=1, 
                               help="Number of times the SUD is refined. Each iteration re-submits the context and generates a new output.")

with col_b:
    st.subheader("🔍 RAG Queries (Phase 2)")
    total_users = st.number_input("Number of Active Users", value=500)
    queries_per_day = st.number_input("Queries per User/Day", value=30)
    days_per_month = st.number_input("Days per Month", value=30)
    rag_context_tokens = st.number_input("Context Tokens per Query (Input)", value=1500)
    rag_answer_tokens = st.number_input("Answer Tokens per Query (Output)", value=250)

# --- CALCULATIONS ---

# 1. Phase 1: Ingestion & Iterative SUD Gen
# Base hours and transcription tokens
total_hours = (monthly_sessions * avg_session_hr) * num_months
transcription_in_tokens = (total_hours * words_per_hr * 1.35) 

# Iteration Logic: 
# Total Ingest Input = (Initial Transcription In) + (Subsequent iteration feedback loops)
# For simplicity and accuracy: each iteration requires sending the context back.
total_ingest_in_tokens = transcription_in_tokens * sud_iterations
total_ingest_out_tokens = (monthly_sessions * sud_output_tokens * sud_iterations) * num_months

# 2. Phase 2: RAG
total_queries = (total_users * queries_per_day * days_per_month) * num_months
total_rag_in_tokens = total_queries * (rag_context_tokens + 50)
total_rag_out_tokens = total_queries * rag_answer_tokens
total_rag_embed_tokens = total_queries * 100

# 3. Aggregated Totals for Report
grand_total_in_tokens = total_ingest_in_tokens + total_rag_in_tokens
grand_total_out_tokens = total_ingest_out_tokens + total_rag_out_tokens

# 4. Total Costs
cost_stt = total_hours * p_stt
cost_in_total = (grand_total_in_tokens / 1_000_000) * p_gpt_in
cost_out_total = (grand_total_out_tokens / 1_000_000) * p_gpt_out
cost_embed = (total_rag_embed_tokens / 1_000_000) * p_embed

grand_total_cost = cost_stt + cost_in_total + cost_out_total + cost_embed

# --- PART 2: SUMMARY TABLE ---
st.header(f"2️⃣ Cost Summary ({num_months} Months)")

summary_df = pd.DataFrame([
    {
        "Workload": "Speech-to-Text",
        "Details": f"{total_hours:,.0f} Total Hours",
        "Monthly Cost": cost_stt / num_months,
        "Total Cost": cost_stt
    },
    {
        "Workload": f"SUD Generation ({sud_iterations}x Iterations)",
        "Details": f"{(total_ingest_in_tokens + total_ingest_out_tokens)/1e6:.2f}M Tokens",
        "Monthly Cost": ((total_ingest_in_tokens/1e6 * p_gpt_in) + (total_ingest_out_tokens/1e6 * p_gpt_out)) / num_months,
        "Total Cost": (total_ingest_in_tokens/1e6 * p_gpt_in) + (total_ingest_out_tokens/1e6 * p_gpt_out)
    },
    {
        "Workload": "RAG Knowledge Access",
        "Details": f"{(total_rag_in_tokens + total_rag_out_tokens)/1e6:.2f}M Tokens",
        "Monthly Cost": ((total_rag_in_tokens/1e6 * p_gpt_in) + (total_rag_out_tokens/1e6 * p_gpt_out) + cost_embed/num_months),
        "Total Cost": (total_rag_in_tokens/1e6 * p_gpt_in) + (total_rag_out_tokens/1e6 * p_gpt_out) + cost_embed
    }
])

st.table(summary_df.style.format({"Monthly Cost": "${:,.2f}", "Total Cost": "${:,.2f}"}))

# --- PART 3: FINAL TECHNICAL REPORT ---
st.divider()
st.header("📋 Final Technical Report")
st.info(f"Report based on **{num_months} month(s)** and **{sud_iterations} revision cycle(s)** per SUD.")

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
st.markdown(f"### **Grand Total Cumulative Cost: ${grand_total_cost:,.2f}**")

# Progress bar to show Input vs Output cost distribution
st.write("Cost Distribution (Input vs Output)")
in_pct = cost_in_total / (cost_in_total + cost_out_total) if (cost_in_total + cost_out_total) > 0 else 0
st.progress(in_pct, text=f"Input: {in_pct:.1%} | Output: {1-in_pct:.1%}")
