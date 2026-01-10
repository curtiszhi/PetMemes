import requests
import os
import json
import base64
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
# Using the stable 4.0 model as verified
URL = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={API_KEY}"
PROMPTS_FILE = "transform_prompts_v2.json"
OUTPUT_DIR = "generated_images_v2"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_image(prompt, original_filename):
    if not API_KEY:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    payload = {
        "instances": [
            {
                "prompt": prompt
            }
        ],
        "parameters": {
            "sampleCount": 1
        }
    }

    headers = {"Content-Type": "application/json"}

    print(f"Generating image for {original_filename}...")
    
    try:
        response = requests.post(URL, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if 'predictions' in data and len(data['predictions']) > 0:
            b64_image = data['predictions'][0]['bytesBase64Encoded']
            
            output_filename = f"gen_{original_filename}"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(b64_image))
            print(f"Success! Saved to {output_filename}")
            return output_filename
        else:
            print(f"No predictions for {original_filename}")
            return None

    except Exception as e:
        print(f"Error calling Imagen API for {original_filename}: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")
        return None

def main():
    if not os.path.exists(PROMPTS_FILE):
        print(f"No prompts file found at {PROMPTS_FILE}")
        return

    with open(PROMPTS_FILE, "r") as f:
        prompts = json.load(f)

    print(f"Found {len(prompts)} prompts. Generating transformed images...")
    
    generated_count = 0
    
    for item in prompts:
        prompt = item.get("transform_prompt")
        original = item.get("original_image")
        
        if prompt and original:
            result = generate_image(prompt, original)
            if result:
                generated_count += 1
    
    print(f"Generation complete! {generated_count}/{len(prompts)} images generated.")

if __name__ == "__main__":
    main()
