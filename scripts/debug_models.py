import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

def list_models():
    try:
        response = requests.get(URL)
        response.raise_for_status()
        models = response.json().get('models', [])
        print("Available Models:")
        for m in models:
            print(f"- {m['name']}")
    except Exception as e:
        print(f"Error listing models: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")

if __name__ == "__main__":
    list_models()
