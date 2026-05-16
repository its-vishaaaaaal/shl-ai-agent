import requests
import json


URL = "http://127.0.0.1:8000/chat"

def run_test(query):
    print(f"\n🔍 Testing Query: '{query}'")
    
    payload = {
        "messages": [
            {"role": "user", "content": query}
        ]
    }

    try:
        response = requests.post(URL, json=payload)
        
        if response.status_code == 200:
            print("✅ Status: Success (200)")
            print("--- AI RESPONSE ---")
            print(json.dumps(response.json(), indent=4))
        else:
            print(f"❌ Status: Failed ({response.status_code})")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    # Test 1: General Greeting
    run_test("Hi, help me find a test.")
    
    # Test 2: Specific keyword based on your scraped data
    run_test("I need a .NET assessment.")