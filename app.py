from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import json
from groq import Groq

client = Groq(api_key="YOUR_GROQ_API_KEY_HERE")
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

# Load all 377 Data
try:
    with open("individual_test_solutions.json", "r", encoding="utf-8") as f:
        full_catalog = json.load(f)
except:
    full_catalog = []

def get_relevant_tests(user_input: str, catalog: list, top_n: int = 15):
    """User ke message ke keywords ko 377 records me dhundhega"""
    words = user_input.lower().replace('.', ' ').split()
    matches = []
    
    for test in catalog:
        test_name = test['name'].lower()
        # Agar user ka keyword test ke naam me hai, toh score badhao
        score = sum(1 for w in words if len(w) > 1 and w in test_name)
        if score > 0:
            matches.append((score, test))
            
    # Jiska score sabse zyada, usko upar rakho
    matches.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in matches[:top_n]]

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        # User ka aakhri message nikal kar database me search karo
        user_query = request.messages[-1].content if request.messages else ""
        relevant_tests = get_relevant_tests(user_query, full_catalog)

        # Dynamic System Prompt (Sirf relevant tests hi AI ko jayenge)
        SYSTEM_PROMPT = f"""You are a professional SHL Assessment Consultant. 
        We have {len(full_catalog)} tests in our full database. 
        Based on the user's latest message, here are the top matching tests:
        {json.dumps(relevant_tests)}

        RULES:
        1. GREETING: If they say 'hi', greet them and ask what skills they want to assess.
        2. NO MATCH: If the matching list is empty, tell them you need more specific keywords (e.g., Java, Sales, Accounting, .NET).
        3. MATCH FOUND: Recommend the tests from the matching list and provide their exact URLs.
        4. ALWAYS respond ONLY in this JSON format:
        {{
          "reply": "Your conversational message",
          "recommendations": [],
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
            temperature=0.6
        )

        ai_json = json.loads(completion.choices[0].message.content)
        
        return ChatResponse(
            reply=ai_json.get("reply", "How can I help you?"),
            recommendations=ai_json.get("recommendations", []),
            end_of_conversation=ai_json.get("end_of_conversation", False)
        )
    except Exception as e:
        print(f"\n❌ SERVER ERROR: {e}\n")
        return ChatResponse(reply="System busy. Please try again.", recommendations=[], end_of_conversation=False)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)