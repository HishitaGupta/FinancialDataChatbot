import duckdb

class QueryExecutor:
    def __init__(self, db_path):
        self.conn = duckdb.connect(db_path, read_only=True)
    
    def execute(self, sql):
        # Safety check
        if not sql.upper().strip().startswith('SELECT'):
            return {"error": "Only SELECT allowed", "data": None}
        
        # Block dangerous keywords
        dangerous = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER']
        if any(word in sql.upper() for word in dangerous):
            return {"error": "Dangerous operation blocked", "data": None}
        
        try:
            result = self.conn.execute(sql).fetchdf()
            
            if result.empty:
                return {"error": "No data found", "data": None}
            
            return {"error": None, "data": result}
        except Exception as e:
            return {"error": str(e), "data": None}