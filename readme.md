#  Financial Data Chatbot

A production-ready **financial analytics chatbot** that answers natural-language questions over structured fund, holdings, and trade data using **LLMs + DuckDB SQL** — without RAG or embeddings.

This project converts user questions → optimized SQL → executes on a financial database → explains results in natural language.

---

##  Key Features

* **Natural Language → SQL** using LLMs (Qwen / Gemini)
* **Low-latency analytics** via DuckDB (columnar, in-process)
* **No RAG / No embeddings** – direct reasoning over structured data
* Supports **fund performance, P&L, holdings, trades, exposure**
* Modular architecture (SQL Gen, Executor, Answer Gen)
* **FastAPI backend** + **Streamlit UI**
* Transparent data views + raw CSV inspection

---

## Architecture Overview

```
User Question
    ↓
SQL Generator (LLM)
    ↓
DuckDB Query Executor
    ↓
Answer Generator (LLM)
    ↓
Natural Language Answer
```

Unlike RAG systems, the LLM does **not hallucinate** from documents — it reasons strictly over **query results**.

---

## Project Structure

```
FINANCIALDATACHATBOT/
│
├── api/
│   └── main.py                 # FastAPI entrypoint
│
├── core/
│   └── chatbot.py              # Orchestrates SQL → Exec → Answer
│
├── llm/
│   ├── sql_generator.py        # LLM-based SQL generation
│   └── answer_generator.py     # LLM-based answer generation
│
├── database/
│   ├── create_reference_tables.py  # Builds DuckDB tables & views
│   └── query_executor.py           # Executes SQL safely
│
├── data/
│   ├── raw/
│   │   ├── holdings.csv
│   │   └── trades.csv
│   │
│   └── processed/
│       ├── holdings_clean.csv
│       ├── trades_clean.csv
│       └── financial_data.db
│
├── notebooks/
│   ├── data_cleaning.ipynb
│   └── data_exploration.ipynb
│
├── streamlit_app.py             # Interactive UI
├── requirements.txt
├── Procfile                     # Deployment (Render)
├── .env
└── README.md
```

---

## Financial Database Contents

### Base Tables

#### `holdings`

| Column           | Meaning             |
| ---------------- | ------------------- |
| PortfolioName    | Fund name           |
| AsOfDate         | Snapshot date       |
| SecurityId       | Security identifier |
| SecName          | Security name       |
| SecurityTypeName | Equity, Bond, etc.  |
| Qty              | Quantity held       |
| MV_Base          | Market value        |
| PL_YTD           | Year-to-date P&L    |
| PL_MTD           | Month-to-date P&L   |
| PL_QTD           | Quarter-to-date P&L |

#### `trades`

| Column        | Meaning              |
| ------------- | -------------------- |
| PortfolioName | Fund name            |
| TradeDate     | Trade execution date |
| SecurityId    | Security identifier  |
| Name          | Security name        |
| Quantity      | Quantity traded      |
| TotalCash     | Trade cash value     |

---

### Analytical Views (Optional but Optimized)

* `v_fund_summary` → fund-level performance (latest snapshot)
* `v_trade_summary` → trading activity per fund
* `v_security_summary` → cross-fund exposure
* `v_data_coverage` → data diagnostics

> Warning: You can **disable views** and rely purely on base tables — the SQL generator adapts automatically.

---

## Running the Project

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Database & Views

```bash
python database/create_reference_tables.py
```

### 3. Start FastAPI Backend (Local)

```bash
uvicorn api.main:app --reload
```

Health check:

```
http://localhost:8000/health
```

---

### 4. Start Streamlit UI

```bash
streamlit run streamlit_app.py
```

---

## Why No RAG?

### Problems with RAG for Financial Analytics

* Embeddings **lose numeric precision**
* Aggregations (SUM, COUNT, GROUP BY) are unreliable
* Hallucinations from loosely matched text
* Higher latency + vector DB complexity

### Why This Approach Works Better

* Exact SQL aggregations (financial correctness)
* Deterministic answers
* Explainable logic
* Faster inference
* Production-safe for analytics

> **LLMs reason, databases compute.**

---

## Example Questions

* Which fund performed best this year?
* Funds with negative YTD P&L
* Total market value of each fund
* Which security is held by the most funds?
* Trading activity for Fund XYZ
* Best trade by cash value

---

## Latency & Performance

| Component         | Latency     |
| ----------------- | ----------- |
| SQL generation    | ~300–800 ms |
| DuckDB query      | ~5–50 ms    |
| Answer generation | ~300–700 ms |

No vector search. No re-ranking. No chunking.

---

## Deployment (Render)

**Procfile**

```
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

Make sure:

* App binds to `0.0.0.0`
* Uses `$PORT`

---

## Environment Variables

```
HF_API_TOKEN=your_huggingface_key

```

---

## Final Notes

This system is ideal for:

* Financial analytics
* Internal fund dashboards
* Data-driven chatbots
* Structured enterprise data

If your data is **tabular and numeric**, this approach beats RAG.

---

**Built with care using DuckDB, FastAPI, Streamlit & LLMs**

