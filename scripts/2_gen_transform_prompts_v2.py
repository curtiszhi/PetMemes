import requests
import os
import json
import base64
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={API_KEY}"
INPUT_DIR = "input_images_v2"
PROMPTS_FILE = "transform_prompts_v2.json"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_transform_prompt(image_path, image_name):
    base64_image = encode_image(image_path)
    
    # Prompt engineering for Imagen
    # usage: [breed/color] [action/clothes] [art style]
    
    prompt_text = (
        "Look at this pet. I want to generate a new image of this exact type of pet acting like a human. "
        "Create a detailed image generation prompt for a text-to-image model (like Imagen). "
        "The prompt should describe: "
        "1. The pet's key features (breed, color, markings) from the image. "
        "2. A funny, human-like activity or outfit (e.g., wearing a suit, DJing, reading, cooking). "
        "3. An art style (e.g., 'A cinematic 3D render', 'A high quality photo', 'A Pixar-style character'). "
        "Format the output as a SINGLE paragraph string. Do not use quotes or markdown."
    )

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt_text},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": base64_image
                    }
                }
            ]
        }]
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        prompt = data['candidates'][0]['content']['parts'][0]['text'].strip()
        return prompt
    except Exception as e:
        print(f"Error generating prompt for {image_name}: {e}")
        return None

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"No input images found in {INPUT_DIR}")
        return

    images = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    images.sort()
    
    if not images:
        print("No images to process.")
        return

    print(f"Found {len(images)} images. Generating transformation prompts...")
    
    results = []
    
    for image_name in images:
        image_path = os.path.join(INPUT_DIR, image_name)
        print(f"Analyzing {image_name}...")
        
        transform_prompt = generate_transform_prompt(image_path, image_name)
        
        if transform_prompt:
            print(f"Generated Prompt: {transform_prompt[:100]}...")
            results.append({
                "original_image": image_name,
                "transform_prompt": transform_prompt
            })
    
    with open(PROMPTS_FILE, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Saved {len(results)} prompts to {PROMPTS_FILE}")

if __name__ == "__main__":
    main()
