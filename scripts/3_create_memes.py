import requests
import os
import json
import base64
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"
INPUT_DIR = "input_images"
OUTPUT_DIR = "output_memes"
PROMPTS_FILE = "prompts.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_caption(image_path, persona):
    base64_image = encode_image(image_path)
    
    prompt_text = (
        f"Look at this image. Write a short, funny meme caption in the style of: '{persona}'. "
        "The caption should be punchy and relatable. "
        "Return ONLY the caption text, nothing else. No quotes."
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
        caption = data['candidates'][0]['content']['parts'][0]['text'].strip()
        return caption
    except Exception as e:
        print(f"Error generating caption for {persona}: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")
        return None

def add_caption_to_image(image_path, caption, output_filename):
    try:
        img = Image.open(image_path)
        
        # Resize for consistent meme size if needed, but keeping original for quality is fine.
        # If image is too large, we might want to scale down, but let's keep it simple.
        
        draw = ImageDraw.Draw(img)
        
        # Load font - simpler to use default if custom not available, but let's try to find a nice one or use default
        # macOS usually has Helvetica or Arial
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size=40)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", size=40) 
            except:
                font = ImageFont.load_default() # Fallback

        # Calculate text compatibility
        width, height = img.size
        
        # Wrap text logic (simple)
        words = caption.split()
        lines = []
        current_line = []
        
        # Dynamic font scaling could be good but let's stick to basic wrapping
        # A simple wrap roughly every 25 chars
        
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 20: # Arbitrary char limit for wrap
                 lines.append(" ".join(current_line))
                 current_line = []
        if current_line:
            lines.append(" ".join(current_line))
            
        text = "\n".join(lines)
        
        # Position - Bottom Center
        # Text positioning logic is complex, simplify to standard bottom text
        
        # Calculate text size (approx)
        # For default font, getsize is not always perfect, so we rely on anchor
        
        # Advanced: Draw white text with black outline
        
        x = width / 2
        y = height - (len(lines) * 50) - 50 # 50px buffer from bottom
        
        # Draw with stroke (outline)
        # Pillow 10+ supports stroke_width, stroke_fill
        draw.multiline_text((x, y), text, font=font, fill="white", stroke_width=3, stroke_fill="black", anchor="mm", align="center")
        
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        img.save(output_path)
        print(f"Saved meme: {output_filename}")
        
    except Exception as e:
        print(f"Error creating meme image: {e}")

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"No input images found in {INPUT_DIR}")
        return

    if not os.path.exists(PROMPTS_FILE):
        print(f"No prompts file found at {PROMPTS_FILE}")
        return

    with open(PROMPTS_FILE, "r") as f:
        prompts = json.load(f)

    images = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not images:
        print("No images to process.")
        return

    print(f"Found {len(images)} images and {len(prompts)} prompts. Generating memes...")

    # For demo, match 1 image to 1 prompt specifically, or loops?
    # Let's generate 5 memes total (mixing images and prompts)
    
    for i in range(min(5, len(prompts))):
        image_name = images[i % len(images)]
        prompt = prompts[i]
        
        image_path = os.path.join(INPUT_DIR, image_name)
        print(f"Processing {image_name} with style: {prompt}")
        
        caption = generate_caption(image_path, prompt)
        
        if caption:
            print(f"Generated Caption: {caption}")
            output_filename = f"meme_{i+1}_{image_name}"
            add_caption_to_image(image_path, caption, output_filename)

    print("Meme generation complete!")

if __name__ == "__main__":
    main()
