import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# App setup
# -----------------------------
app = FastAPI(title="Scout AI API", version="1.0")

# -----------------------------
# OpenAI client
# -----------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# -----------------------------
# Request schema
# -----------------------------
class Question(BaseModel):
    question: str

# -----------------------------
# Web search (DuckDuckGo)
# -----------------------------
def scout_web_search(query: str) -> str:
    try:
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": f"Scouts BSA {query}",
                "format": "json",
                "no_redirect": 1,
                "no_html": 1
            },
            timeout=6
        )
        data = r.json()
        return data.get("AbstractText", "")
    except Exception:
        return ""

# -----------------------------
# AI reasoning
# -----------------------------
def scout_ai_answer(question: str, web_text: str) -> str:
    if not client:
        return "OpenAI API key not configured."

    prompt = f"""
You are a Scouts BSA expert.

RULES:
- Follow current Scouts BSA policies
- Be youth-safe
- Never invent requirements
- If unsure, say so

Web information:
{web_text if web_text else "No direct web info found."}

Question:
{question}

Provide a clear, accurate answer.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=400
    )

    return response.choices[0].message.content.strip()

# -----------------------------
# API endpoint
# -----------------------------
@app.post("/ask")
def ask_scout_ai(data: Question):
    if not data.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    web_text = scout_web_search(data.question)
    answer = scout_ai_answer(data.question, web_text)

    return {
        "question": data.question,
        "web_info": web_text,
        "answer": answer
    }
ith official Scouts BSA sources.")
