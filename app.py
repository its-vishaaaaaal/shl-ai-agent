from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import json
from groq import Groq

# =====================================
# ENTER YOUR GROQ API KEY HERE
# =====================================
client = Groq(api_key="Enter you API KEY")

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class Recommendation(BaseModel):
    name: str
    url: str
    test_type: Optional[str] = ""

class ChatResponse(BaseModel):
    reply: str
    recommendations: List[Recommendation]
    end_of_conversation: bool

# Load catalog data safely
try:
    with open("individual_test_solutions.json", "r", encoding="utf-8") as f:
        full_catalog = json.load(f)
except Exception:
    full_catalog = []

def get_relevant_tests(user_input: str, catalog: list, top_n: int = 15):
    """Filters the 377-record catalog based on user keywords to manage context window"""
    words = user_input.lower().replace('.', ' ').split()
    matches = []
    for test in catalog:
        test_name = test['name'].lower()
        score = sum(1 for w in words if len(w) > 1 and w in test_name)
        if score > 0:
            matches.append((score, test))
    matches.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in matches[:top_n]]

# REQUIRED BY SHL AUTOMATED TESTER
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database_records": len(full_catalog),
        "llm_provider": "Groq (Llama-3.3-70b)"
    }

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        user_query = request.messages[-1].content if request.messages else ""
        relevant_tests = get_relevant_tests(user_query, full_catalog)

        SYSTEM_PROMPT = f"""You are a professional SHL Assessment Consultant. 
        Database context containing available tests: {json.dumps(relevant_tests)}

        CRITICAL INSTRUCTIONS:
        1. CLARIFY & REFINE: Ask clarifying questions if the user's intent is vague. Refine results if constraints change.
        2. COMPARE: Compare assessments directly using catalog evidence if requested.
        3. STRICT FORMAT: Always respond strictly in this JSON structure:
        {{
          "reply": "Your conversational response or comparison here",
          "recommendations": [
             {{"name": "Exact Test Name", "url": "Exact URL", "test_type": "K"}}
          ],
          "end_of_conversation": false
        }}
        """

        msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in request.messages:
            msgs.append({"role": m.role, "content": m.content})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=msgs,
            response_format={"type": "json_object"},
            temperature=0.4
        )

        ai_json = json.loads(completion.choices[0].message.content)
        return ChatResponse(
            reply=ai_json.get("reply", "How can I assist you with SHL products?"),
            recommendations=ai_json.get("recommendations", []),
            end_of_conversation=ai_json.get("end_of_conversation", False)
        )
    except Exception as e:
        return ChatResponse(reply="Service temporarily unavailable.", recommendations=[], end_of_conversation=False)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)