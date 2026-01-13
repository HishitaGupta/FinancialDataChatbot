import streamlit as st
import pandas as pd
import requests
import time

# ------------------------------
# CONFIG
# ------------------------------
API_URL = "https://financialdatachatbot-1.onrender.com/ask"  # Change to Render URL after deploy

st.set_page_config(
    page_title="Financial Analytics Chatbot",
    layout="wide",
    page_icon="📊"
)

# ------------------------------
# LOAD KNOWLEDGE
# ------------------------------
@st.cache_data
def load_data():
    holdings = pd.read_csv("./data/processed/holdings_clean.csv")
    trades = pd.read_csv("./data/processed/trades_clean.csv")
    return holdings, trades

holdings_df, trades_df = load_data()

# ------------------------------
# SIDEBAR – KNOWLEDGE BASE
# ------------------------------
with st.sidebar:
    st.title("📚 Knowledge Base")

    tab1, tab2 = st.tabs(["Holdings", "Trades"])

    with tab1:
        st.caption("Holdings snapshot data")
        st.dataframe(holdings_df, height=400)
        st.caption(f"Rows: {len(holdings_df):,}")

    with tab2:
        st.caption("Trades transaction data")
        st.dataframe(trades_df, height=400)
        st.caption(f"Rows: {len(trades_df):,}")

# ------------------------------
# MAIN CHAT UI
# ------------------------------
st.title("💬 Financial Chatbot")
st.caption("Ask questions about fund performance, trades, holdings, or securities")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------------------
# USER INPUT
# ------------------------------
if prompt := st.chat_input("Ask a question..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant placeholder
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            # Call FastAPI
            res = requests.post(
                API_URL,
                json={"question": prompt},
                timeout=60
            )
            print(res)
            res.raise_for_status()
            answer = res.json()["answer"]

            # Simulated streaming effect
            for token in answer.split(" "):
                full_response += token + " "
                response_placeholder.markdown(full_response)
                time.sleep(0.02)

        except Exception as e:
            full_response = f"❌ Error: {str(e)}"
            response_placeholder.markdown(full_response)

    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )

# ------------------------------
# FOOTER
# ------------------------------
st.markdown(
    """
    <hr>
    <center>
    <small>
    Powered by DuckDB • HuggingFace LLM • FastAPI • Streamlit
    </small>
    </center>
    """,
    unsafe_allow_html=True
)
