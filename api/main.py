from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.chatbot import FinancialChatbot

from dotenv import load_dotenv 
import os 

load_dotenv()

app = FastAPI()

# Initialize chatbot
chatbot = FinancialChatbot(
    api_key=os.getenv('HF_API_TOKEN'),
    db_path='data/processed/financial_data.db'
)



class Question(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(q: Question):
    try:
        answer = chatbot.answer(q.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Run: uvicorn api.main:app --reload