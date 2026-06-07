"""
Vizuara Agent — Streamlit dashboard.
Run: streamlit run dashboard.py
"""

import json
import os
import time
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Reads from Streamlit Cloud secrets, env var, or falls back to localhost
API_URL = (
    st.secrets.get("API_URL", None)
    if hasattr(st, "secrets")
    else None
) or os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Vizuara Agent",
    page_icon="V",
    layout="wide",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Vizuara Agent")
    st.caption("Real-World Context-Engineered AI")
    st.divider()
    user_id = st.text_input("Your User ID", value="vinoodhini_d")
    st.divider()
    st.markdown("**Supported Topics:**")
    st.markdown("- IT Support\n- HR Queries\n- Ramco ERP\n- Project Management")
    st.divider()
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.meta = []
        st.rerun()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "meta" not in st.session_state:
    st.session_state.meta = []

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_chat, tab_metrics = st.tabs(["Chat", "Performance Metrics"])

# ── Tab 1: Chat ───────────────────────────────────────────────────────────────
with tab_chat:
    st.header("Ask Vizuara")

    # Chat history display
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and i // 2 < len(st.session_state.meta):
                m = st.session_state.meta[i // 2]
                col1, col2, col3, col4 = st.columns(4)
                score = m.get("confidence_score", 0)
                level = m.get("confidence_level", "")
                color = "green" if level == "HIGH" else ("orange" if level == "MEDIUM" else "red")
                col1.metric("Confidence", f"{score:.0%}")
                col2.metric("Intent", m.get("intent", ""))
                col3.metric("Latency", f"{m.get('latency_ms', 0)}ms")
                col4.metric("Tokens", m.get("tokens_used", 0))
                # Confidence bar
                st.progress(score, text=f"Confidence: {level}")

    # Input
    if prompt := st.chat_input("Type your question here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    history = [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages[:-1]
                    ]
                    resp = requests.post(
                        f"{API_URL}/chat",
                        json={"query": prompt, "user_id": user_id, "conversation_history": history},
                        timeout=30,
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    response_text = data["response"]
                    st.markdown(response_text)

                    # Metadata row
                    score = data["confidence_score"]
                    level = data["confidence_level"]
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Confidence", f"{score:.0%}")
                    col2.metric("Intent", data["intent"])
                    col3.metric("Latency", f"{data['latency_ms']}ms")
                    col4.metric("Tokens", data["tokens_used"])
                    st.progress(score, text=f"Confidence: {level}")

                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    st.session_state.meta.append(data)

                except requests.exceptions.ConnectionError:
                    msg = "Cannot connect to the API. Make sure `uvicorn main:app --reload` is running."
                    st.error(msg)
                    st.session_state.messages.append({"role": "assistant", "content": msg})
                    st.session_state.meta.append({})
                except Exception as e:
                    msg = f"Error: {e}"
                    st.error(msg)
                    st.session_state.messages.append({"role": "assistant", "content": msg})
                    st.session_state.meta.append({})

# ── Tab 2: Metrics ────────────────────────────────────────────────────────────
with tab_metrics:
    st.header("Performance Metrics")

    if st.button("Refresh Metrics"):
        st.rerun()

    try:
        resp = requests.get(f"{API_URL}/metrics", timeout=5)
        resp.raise_for_status()
        m = resp.json()

        total = m.get("total_queries", 0)
        if total == 0:
            st.info("No queries logged yet. Ask some questions in the Chat tab first.")
        else:
            # KPI row
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Queries",    total)
            col2.metric("Avg Confidence",   f"{m.get('avg_confidence', 0):.0%}")
            col3.metric("Avg Latency",      f"{m.get('avg_latency_ms', 0):.0f}ms")
            col4.metric("Avg Tokens",       f"{m.get('avg_tokens', 0):.0f}")

            st.divider()
            col_left, col_right = st.columns(2)

            # Intent distribution pie
            intent_data = m.get("intent_breakdown", {})
            if intent_data:
                fig1 = px.pie(
                    values=list(intent_data.values()),
                    names=list(intent_data.keys()),
                    title="Intent Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                )
                col_left.plotly_chart(fig1, use_container_width=True)

            # Confidence level bar
            level_data = m.get("confidence_breakdown", {})
            if level_data:
                colors = {"HIGH": "#2ecc71", "MEDIUM": "#f39c12", "LOW": "#e74c3c"}
                fig2 = go.Figure(go.Bar(
                    x=list(level_data.keys()),
                    y=list(level_data.values()),
                    marker_color=[colors.get(k, "#95a5a6") for k in level_data.keys()],
                ))
                fig2.update_layout(title="Confidence Level Distribution", xaxis_title="Level", yaxis_title="Count")
                col_right.plotly_chart(fig2, use_container_width=True)

            # Recent queries table
            st.subheader("Recent Queries")
            recent = m.get("recent_queries", [])
            if recent:
                rows = []
                for r in reversed(recent):
                    rows.append({
                        "Query":      r.get("query", "")[:60],
                        "Intent":     r.get("intent", ""),
                        "Confidence": f"{r.get('confidence_score', 0):.0%}",
                        "Level":      r.get("confidence_level", ""),
                        "Latency ms": r.get("latency_ms", 0),
                        "Tokens":     r.get("tokens_used", 0),
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True)

    except requests.exceptions.ConnectionError:
        st.warning("API not running. Start with: `uvicorn main:app --reload`")
    except Exception as e:
        st.error(f"Error loading metrics: {e}")
