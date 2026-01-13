from llm.sql_generator import SQLGenerator
from database.query_executor import QueryExecutor
from llm.answer_generator import AnswerGenerator
import hashlib
from datetime import datetime, timedelta

class FinancialChatbot:
    def __init__(self, api_key, db_path):
        print("api",api_key)
        self.sql_gen = SQLGenerator(api_key)
        self.executor = QueryExecutor(db_path)
        self.answer_gen = AnswerGenerator(api_key)
        self.cache = {}
    
    def answer(self, question):
        # 1. Check cache
        cache_key = hashlib.md5(question.lower().encode()).hexdigest()
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            print(cached)
            if (datetime.now() - cached['time']) < timedelta(hours=1):
                return cached['answer']
        
        # 2. Generate SQL
        sql_result = self.sql_gen.generate_sql(question)
        print(sql_result)
        
        if not sql_result.get('sql'):
            return "Sorry, cannot find the answer in the available data."
        
        # 3. Execute query
        query_result = self.executor.execute(sql_result['sql'])
        print(query_result)
        
        # 4. Generate answer
        answer = self.answer_gen.generate_answer(question, query_result)
        
        # 5. Cache result
        self.cache[cache_key] = {
            'answer': answer,
            'time': datetime.now()
        }
        print(self.cache)

        return answer