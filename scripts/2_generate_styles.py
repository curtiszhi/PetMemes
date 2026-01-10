import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"

def generate_style_templates():
    if not API_KEY:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    prompt_text = (
        "Generate 10 diverse and creative image generation prompt templates for creating pet memes. "
        "Each template must include the placeholder '{pet_description}'. "
        "The styles should range from realistic/human-like to various art styles. "
        "CRITICAL: The prompt templates must describe the VISUALS ONLY. Do NOT include any instructions for text, captions, or words to be written in the image. "
        "The images should be clean, text-free visuals that can be used as a background for a meme later."
        "Examples: "
        "- 'A hyper-realistic photo of {pet_description} wearing a business suit and working at a laptop in a modern office.' "
        "- 'A cute 8-bit pixel art character of {pet_description} holding a sword.' "
        "- 'A dramatic oil painting of {pet_description} dressed as a Napoleonic general.' "
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
        
        styles = json.loads(clean_text)
        
        with open("meme_styles.json", "w") as f:
            json.dump(styles, f, indent=2)
            
        print("Successfully generated 10 meme style templates:")
        for s in styles:
            print(f"- {s}")
            
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")

if __name__ == "__main__":
    generate_style_templates()
