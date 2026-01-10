import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"

def generate_prompts():
    if not API_KEY:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    # V2 Prompt: Specific request for human-like personas
    prompt_text = (
        "Generate 10 distinct, funny meme personas specifically for pets acting like humans. "
        "The personas should describe a pet doing a human activity or wearing human clothes. "
        "Examples: 'The Coffee Shop Screenwriter Dog', 'The Corporate Cat in a Tie', 'The Gym Rat Hamster'. "
        "Return the output as a JSON array of strings. Do not include markdown formatting."
    )

    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(URL, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        text_response = data['candidates'][0]['content']['parts'][0]['text']
        
        # Clean up potential markdown code blocks
        clean_text = text_response.replace("```json", "").replace("```", "").strip()
        
        prompts = json.loads(clean_text)
        
        with open("prompts_v2.json", "w") as f:
            json.dump(prompts, f, indent=2)
            
        print("Successfully generated 10 human-like meme prompts (V2):")
        for p in prompts:
            print(f"- {p}")
            
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")

if __name__ == "__main__":
    generate_prompts()
