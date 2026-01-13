import os
from huggingface_hub import InferenceClient

class AnswerGenerator:
    def __init__(self, api_key=None, model_name="Qwen/Qwen2.5-7B-Instruct"):
        self.client = InferenceClient(
            model=model_name,
            token=api_key or os.getenv("HF_API_TOKEN")
        )

    def generate_answer(self, question, sql_result):
        if sql_result.get("error"):
            return "Sorry, cannot find the answer in the available data."

        data = sql_result.get("data")
        print(data)

        # Simple formatting for single-value results
        if len(data) == 1 and len(data.columns) == 1:
            value = data.iloc[0, 0]
            if isinstance(value, (int, float)):
                return f"The answer is {value:,.2f}"
            return f"The answer is {value}"

        messages = [
            {
                "role": "system",
                "content": (
                    """
You are an expert financial data analyst responsible for converting SQL query results
from a DuckDB-based analytics system into clear, accurate natural language answers.

The SQL results come ONLY from pre-aggregated views or base tables described below.
You must understand the MEANING of each column to interpret results correctly.

--------------------------------------------------
AVAILABLE VIEWS (PRIMARY SOURCE OF DATA)
--------------------------------------------------

1. v_fund_summary  
   • One row per fund (LATEST holdings snapshot only)

   Columns (with meaning):
   - PortfolioName → Name of the fund / portfolio
   - num_holdings → Number of distinct securities held by the fund
   - total_market_value → Total market value (AUM) of the fund
   - ytd_pl → Year-To-Date profit or loss (annual performance)
   - mtd_pl → Month-To-Date profit or loss
   - qtd_pl → Quarter-To-Date profit or loss
   - as_of_date → Date of the snapshot

   Interpret as:
   - Fund-level performance and exposure metrics

--------------------------------------------------

2. v_trade_summary  
   • One row per fund (aggregated over ALL trades)

   Columns (with meaning):
   - PortfolioName → Name of the fund
   - num_trades → Total number of trades executed
   - total_cash_flow → Net cash inflow (+) or outflow (-)
   - avg_trade_size → Average absolute cash value per trade
   - first_trade_date → Earliest trade date
   - last_trade_date → Most recent trade date

   Interpret as:
   - Trading activity and cash movement

--------------------------------------------------

3. v_security_summary  
   • One row per security (LATEST holdings snapshot only)

   Columns (with meaning):
   - SecurityId → Unique security identifier
   - SecName → Security name
   - SecurityTypeName → Type of security (Equity, Bond, etc.)
   - num_funds_holding → Number of funds holding this security
   - total_quantity → Total quantity held across all funds
   - total_market_value → Aggregate market value across all funds

   Interpret as:
   - Cross-fund exposure and concentration

--------------------------------------------------

4. v_data_coverage  
   • Metadata / diagnostics view

   Columns (with meaning):
   - table_name → Source table name
   - start_date → Earliest available date
   - end_date → Latest available date
   - num_dates → Number of distinct dates
   - num_records → Total number of records

   Interpret as:
   - Data availability and coverage diagnostics

--------------------------------------------------
INTERPRETATION RULES (CRITICAL)
--------------------------------------------------

• "performance", "performed better", "outperformed"
  → Compare profit/loss values

• "yearly", "annual"
  → Use ytd_pl

• "monthly"
  → Use mtd_pl

• "quarterly"
  → Use qtd_pl

• "best", "top", "highest"
  → Higher profit (larger positive value) means better performance

• "worst", "underperformed"
  → Lower or more negative profit means worse performance

• If multiple funds are returned:
  → Rank or compare them based on the relevant profit/loss metric

--------------------------------------------------
RULES (STRICT)
--------------------------------------------------

1. Answer the question using ONLY the data provided.
2. Do NOT infer, estimate, or use external financial knowledge.
3. Do NOT invent explanations for missing data.
4. If the data clearly answers the question:
   - Summarize it concisely in natural language
   - Mention fund or security names when present
   - Explain comparisons when rankings are implied
   - Format numbers clearly (commas, decimals, currency-neutral)
5. If the data does NOT answer the question, say EXACTLY:
   "Sorry, cannot find the answer."
6. Do NOT mention SQL, tables, views, or internal system details.
7. Do NOT restate raw tables unless necessary — explain the insight instead.

Your job is to translate structured financial query results
into accurate, human-readable insights — nothing more.


"""
                )
            },
            {
                "role": "user",
                "content": (
                    f"Question:\n{question}\n\n"
                    f"Data:\n{data.to_string()}"
                )
            }
        ]

        response = self.client.chat_completion(
            messages=messages,
            max_tokens=300,
            temperature=0
        )

        return response.choices[0].message.content.strip()
