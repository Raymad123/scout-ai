import streamlit as st
import requests
from openai import OpenAI

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="Scout AI", page_icon="⚜️")
st.title("⚜️ Scout AI Assistant")
st.write("Ask any Scouts BSA / Boy Scouts related question.")

# -----------------------------
# OpenAI client
# -----------------------------
api_key = st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

if not api_key:
    st.warning("OpenAI API key not found. AI reasoning will be limited.")

# -----------------------------
# Web search (DuckDuckGo)
# -----------------------------
@st.cache_data(show_spinner=False)
def scout_web_search(query):
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
# AI answer generation
# -----------------------------
def scout_ai_answer(question, web_text):
    if not client:
        return "AI reasoning is unavailable, but this question relates to Scouts BSA. Try refining your question."

    prompt = f"""
You are a Scouts BSA expert.

RULES:
- Be accurate
- Be youth-safe
- Follow BSA policies
- If unsure, say so
- Do NOT invent requirements

Web information:
{web_text if web_text else "No direct web result found."}

Question:
{question}

Answer clearly and concisely.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI error: {e}"

# -----------------------------
# UI – FORM (prevents reruns)
# -----------------------------
with st.form("scout_form"):
    question = st.text_input("Ask a Scout question:")
    submitted = st.form_submit_button("Ask Scout AI")

if submitted and question.strip():
    with st.spinner("Searching trusted Scout sources..."):
        web_text = scout_web_search(question)

    with st.spinner("Thinking like a Scout leader..."):
        answer = scout_ai_answer(question, web_text)

    st.subheader("📚 Scout AI Answer")
    st.write(answer)

st.caption("⚠️ Educational use only. Always verify requirements with official Scouts BSA sources.")
