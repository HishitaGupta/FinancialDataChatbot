import pandas as pd
import duckdb

def create_reference_tables():
    """Create pre-aggregated tables for fast queries"""
    
    conn = duckdb.connect('../data/processed/financial_data.db')

    # 1. Load cleaned CSVs
    holdings = pd.read_csv('../data/processed/holdings_clean.csv')
    trades = pd.read_csv('../data/processed/trades_clean.csv')
    
    # 2. Create tables
    conn.execute("CREATE TABLE holdings AS SELECT * FROM holdings")
    conn.execute("CREATE TABLE trades AS SELECT * FROM trades")
    
    # 3. Create indexes
    conn.execute("CREATE INDEX idx_holdings_portfolio ON holdings(PortfolioName)")
    conn.execute("CREATE INDEX idx_holdings_date ON holdings(AsOfDate)")
    conn.execute("CREATE INDEX idx_trades_portfolio ON trades(PortfolioName)")
    
    print("Creating reference tables...")
    
    # 1. Fund summary (latest)
    conn.execute("""
        CREATE OR REPLACE VIEW v_fund_summary AS
        WITH latest_holdings AS (
            SELECT * FROM holdings
            WHERE AsOfDate = (SELECT MAX(AsOfDate) FROM holdings)
        )
        SELECT 
            PortfolioName,
            COUNT(DISTINCT SecurityId) as num_holdings,
            SUM(MV_Base) as total_market_value,
            SUM(PL_YTD) as ytd_pl,
            SUM(PL_MTD) as mtd_pl,
            SUM(PL_QTD) as qtd_pl,
            MAX(AsOfDate) as as_of_date
        FROM latest_holdings
        GROUP BY PortfolioName
    """)
    
    # 2. Trade summary by fund
    conn.execute("""
        CREATE OR REPLACE VIEW v_trade_summary AS
        SELECT 
            PortfolioName,
            COUNT(*) as num_trades,
            SUM(TotalCash) as total_cash_flow,
            AVG(ABS(TotalCash)) as avg_trade_size,
            MIN(TradeDate) as first_trade_date,
            MAX(TradeDate) as last_trade_date
        FROM trades
        GROUP BY PortfolioName
    """)
    
    # # 3. Monthly performance
    # conn.execute("""
    #     CREATE OR REPLACE VIEW v_monthly_performance AS
    #     SELECT 
    #         PortfolioName,
    #         DATE_TRUNC('month', AsOfDate) as month,
    #         SUM(PL_MTD) as monthly_pl,
    #         SUM(MV_Base) as month_end_value
    #     FROM holdings
    #     GROUP BY PortfolioName, DATE_TRUNC('month', AsOfDate)
    # """)
    
    # 4. Security holdings summary
    conn.execute("""
        CREATE OR REPLACE VIEW v_security_summary AS
        WITH latest_holdings AS (
            SELECT * FROM holdings
            WHERE AsOfDate = (SELECT MAX(AsOfDate) FROM holdings)
        )
        SELECT 
            SecurityId,
            SecName,
            SecurityTypeName,
            COUNT(DISTINCT PortfolioName) as num_funds_holding,
            SUM(Qty) as total_quantity,
            SUM(MV_Base) as total_market_value
        FROM latest_holdings
        GROUP BY SecurityId, SecName, SecurityTypeName
    """)
    
    # 5. Date range reference
    conn.execute("""
        CREATE OR REPLACE VIEW v_data_coverage AS
        SELECT 
            'holdings' as table_name,
            MIN(AsOfDate) as start_date,
            MAX(AsOfDate) as end_date,
            COUNT(DISTINCT AsOfDate) as num_dates,
            COUNT(*) as num_records
        FROM holdings
        UNION ALL
        SELECT 
            'trades' as table_name,
            MIN(TradeDate) as start_date,
            MAX(TradeDate) as end_date,
            COUNT(DISTINCT TradeDate) as num_dates,
            COUNT(*) as num_records
        FROM trades
    """)
    
    # Verify views
    print("\nCreated views:")
    views = conn.execute("SHOW TABLES").fetchdf()
    print(views)
    
    # Sample queries
    print("\nSample fund summary:")
    print(conn.execute("SELECT * FROM v_fund_summary LIMIT 5").fetchdf())
    
    conn.close()
    print("\n✓ Reference tables created successfully")

if __name__ == "__main__":
    create_reference_tables()