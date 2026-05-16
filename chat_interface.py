import requests
import json
import os

URL = "http://127.0.0.1:8000/chat"

def get_db_count():
    try:
        with open("individual_test_solutions.json", "r", encoding="utf-8") as f:
            return len(json.load(f))
    except:
        return 0

def start_chat():
    os.system('cls' if os.name == 'nt' else 'clear')
    db_count = get_db_count()
    
    print("=====================================================")
    print("      🌐 SHL ASSESSMENT AI BOT IS ONLINE 🌐      ")
    print(f"       📊 Database Loaded: {db_count} Assessments Ready!  ")
    print("         (Type 'exit' to end conversation)           ")
    print("=====================================================\n")

    history = []

    while True:
        user_input = input("👤 You: ")
        if user_input.lower() in ['exit', 'quit', 'bye']: 
            print("\n🤖 AI: Goodbye! Best of luck with your hiring process.")
            break

        history.append({"role": "user", "content": user_input})

        try:
            response = requests.post(URL, json={"messages": history})
            if response.status_code == 200:
                data = response.json()
                reply = data.get("reply", "")
                recs = data.get("recommendations", [])

                print(f"\n🤖 AI: {reply}")

                if recs:
                    print("\n--- 📋 TOP MATCHES FOUND ---")
                    for i, t in enumerate(recs, 1):
                        print(f"{i}. {t['name']} (Type: {t['test_type']})")
                        print(f"   🔗 Link: {t['url']}")
                    print("----------------------------\n")

                history.append({"role": "assistant", "content": reply})
            else:
                print("\n❌ Error: Server not responding correctly.")
        except Exception as e:
            print("\n❌ Error: Could not connect to the API. Make sure app.py is running!")
            break

if __name__ == "__main__":
    start_chat()